#!/usr/bin/env python3
"""
Data Endpoint Data Viewer

This script retrieves and displays actual data records from Spotify data endpoints.
It handles the full workflow from endpoint ID to viewing formatted data records.

Supports AVRO, Parquet, and TFRecords formats with automatic format detection.

Usage:
    python view_endpoint_data.py <endpoint_id>
    python view_endpoint_data.py <endpoint_id> --num-records 10
    python view_endpoint_data.py <endpoint_id> --partition 2025-10-22
"""

import sys
import subprocess
import argparse
import re
import shutil
import os
from typing import List, Dict, Optional, Tuple
import json as json_module


# Anonymization mappings for semantic types by tier
# These replace real PII with safe placeholder values
ANONYMIZATION_MAP = {
    # Strict tier - highest sensitivity
    'freeTextField': lambda i: f'sample text {i}',
    'username': lambda i: f'user_{i:03d}',
    'email': lambda i: f'test{i}@example.com',
    'phoneNumber': lambda i: '+1-555-0100',
    'ipAddress': lambda i: '127.0.0.1',
    'geolocation': lambda i: '0.0,0.0',
    'postalCode': lambda i: '00000',
    'fullAddress': lambda i: f'123 Test Street {i}',
    'messageContent': lambda i: f'message content {i}',
    'sensitiveContent': lambda i: 'sensitive_placeholder',
    'voice': lambda i: 'voice_placeholder',
    'picture': lambda i: 'picture_placeholder',
    'paymentInfo': lambda i: 'payment_placeholder',
    'healthInfo': lambda i: 'health_placeholder',
    'religion': lambda i: 'religion_placeholder',
    'ethnicity': lambda i: 'ethnicity_placeholder',
    'politicalOpinion': lambda i: 'political_placeholder',
    'sexualOrientation': lambda i: 'orientation_placeholder',
    'income': lambda i: 'income_placeholder',
    'personality': lambda i: 'personality_placeholder',
    'ssn': lambda i: 'ssn_placeholder',
    'cryptoKey': lambda i: 'key_placeholder',
    'password': lambda i: 'password_placeholder',
    'externalId': lambda i: f'external_id_{i:03d}',
    'criminalRecord': lambda i: 'criminal_placeholder',
    'fraudRecord': lambda i: 'fraud_placeholder',
    'ageAssurance': lambda i: 'age_assurance_placeholder',

    # Narrow tier - moderate sensitivity
    'personalName': lambda i: f'Test User {i}',
    'personalDataURI': lambda i: f'spotify:user:test_user_{i:03d}',
    'city': lambda i: 'Test City',
    'region': lambda i: 'XX',
    'birthday': lambda i: '1990-01-01',
    'deviceId': lambda i: f'device_test_{i:03d}',
    'deviceName': lambda i: f'Test Device {i}',
    'partnerId': lambda i: f'partner_{i:03d}',
    'socialMediaUserId': lambda i: f'social_{i:03d}',
    'playlistName': lambda i: f'Test Playlist {i}',
    'anomaly': lambda i: 'anomaly_placeholder',
    'employee': lambda i: f'employee_{i:03d}',
    'truncatedIpAddress': lambda i: '192.168.x.x',
    'university': lambda i: 'Test University',
}

# Semantic types that don't need anonymization (Broad tier)
BROAD_TIER_TYPES = {
    'userId', 'age', 'gender', 'country', 'language',
    'noUsernameURI', 'nullData', 'internalUniqueId'
}


def get_schema_semantic_types(endpoint_id: str) -> Dict[str, str]:
    """
    Fetch schema and extract semantic type annotations for each field.

    Returns:
        Dict mapping field name to semantic type (e.g., {"query": "freeTextField"})
    """
    schema_script = os.path.expanduser(
        '~/.claude/skills/data-endpoints/scripts/get_endpoint_schema.py'
    )

    try:
        result = subprocess.run(
            ['python3', schema_script, endpoint_id, '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"⚠️  Could not fetch schema for anonymization: {result.stderr}")
            return {}

        # Parse JSON output and extract semantic types
        schema_data = json_module.loads(result.stdout)

        semantic_types = {}

        # Extract semantic types from schema fields recursively
        def extract_semantic_types(obj, prefix=''):
            if isinstance(obj, dict):
                # Check for semantic_type field
                if 'semantic_type' in obj:
                    field_name = prefix.rstrip('.')
                    if field_name:
                        semantic_types[field_name] = obj['semantic_type']

                # Check for semanticType field (alternative casing)
                if 'semanticType' in obj:
                    field_name = prefix.rstrip('.')
                    if field_name:
                        semantic_types[field_name] = obj['semanticType']

                # Check for name/type pairs with semantic info
                if 'name' in obj and 'semantic_type' in obj:
                    semantic_types[obj['name']] = obj['semantic_type']
                if 'name' in obj and 'semanticType' in obj:
                    semantic_types[obj['name']] = obj['semanticType']

                # Recurse into fields
                for key, value in obj.items():
                    if key == 'fields' and isinstance(value, list):
                        for field in value:
                            if isinstance(field, dict) and 'name' in field:
                                new_prefix = field['name']
                                extract_semantic_types(field, new_prefix + '.')
                    elif key not in ['name', 'type', 'semantic_type', 'semanticType']:
                        extract_semantic_types(value, prefix)
            elif isinstance(obj, list):
                for item in obj:
                    extract_semantic_types(item, prefix)

        extract_semantic_types(schema_data)
        return semantic_types

    except subprocess.TimeoutExpired:
        print("⚠️  Schema fetch timed out")
        return {}
    except json_module.JSONDecodeError as e:
        print(f"⚠️  Error parsing schema JSON: {e}")
        return {}
    except Exception as e:
        print(f"⚠️  Error fetching schema: {e}")
        return {}


def anonymize_record(record: dict, semantic_types: Dict[str, str], record_index: int) -> dict:
    """
    Anonymize a single record based on semantic type mappings.

    Args:
        record: The data record to anonymize
        semantic_types: Mapping of field name to semantic type
        record_index: Index for generating unique placeholder values

    Returns:
        Anonymized copy of the record
    """
    anonymized = {}

    for field, value in record.items():
        semantic_type = semantic_types.get(field)

        if semantic_type and semantic_type not in BROAD_TIER_TYPES:
            # Need to anonymize this field
            anonymizer = ANONYMIZATION_MAP.get(semantic_type)
            if anonymizer:
                anonymized[field] = anonymizer(record_index)
            else:
                # Unknown sensitive type - use generic placeholder
                anonymized[field] = f'[REDACTED-{semantic_type}]'
        elif isinstance(value, dict):
            # Recursively anonymize nested objects
            anonymized[field] = anonymize_record(value, semantic_types, record_index)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            # Anonymize lists of objects
            anonymized[field] = [
                anonymize_record(item, semantic_types, record_index) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            # Broad tier or unknown type - keep as-is
            anonymized[field] = value

    return anonymized


def anonymize_json_output(json_lines: List[str], semantic_types: Dict[str, str]) -> List[str]:
    """
    Anonymize JSON output lines based on semantic types.

    Args:
        json_lines: List of JSON strings (one per record)
        semantic_types: Mapping of field name to semantic type

    Returns:
        List of anonymized JSON strings
    """
    anonymized_lines = []

    for i, line in enumerate(json_lines):
        try:
            record = json_module.loads(line)
            anonymized = anonymize_record(record, semantic_types, i + 1)
            anonymized_lines.append(json_module.dumps(anonymized, indent=2))
        except json_module.JSONDecodeError:
            # Not valid JSON, pass through unchanged
            anonymized_lines.append(line)

    return anonymized_lines


# Required tools for this script
REQUIRED_TOOLS = {
    'hades': 'brew install hades-cli',
    'gsutil': 'gcloud components install gsutil',
    'avro-tools': 'brew install gcs-avro-tools',
    'parquet-cli': 'brew install gcs-parquet-cli',
    'tfr': 'brew install tfreader',
    'jq': 'brew install jq'
}

# Get Java 17 path for parquet-cli compatibility
JAVA17_PATH = os.path.expanduser('~/.sdkman/candidates/java/17.0.12-amzn')

# Format-specific viewing commands
# Note: Using explicit java path for avro-tools and parquet-cli to ensure Java 17 compatibility
FORMAT_COMMANDS = {
    'avro': f'export JAVA_HOME={JAVA17_PATH} && avro-tools tojson {{filepath}} 2>/dev/null | head -{{num_records}} | jq .',
    'parquet': f'export JAVA_HOME={JAVA17_PATH} && parquet-cli cat {{filepath}} 2>/dev/null | head -{{num_records}} | jq .',
    'tfrecords': 'tfr -n {num_records} --flat {filepath} | jq .'
}


def check_required_tools(skip_optional=False) -> Tuple[bool, List[str]]:
    """
    Check if required tools are installed.

    Args:
        skip_optional: If True, only check hades and gsutil (core tools)

    Returns:
        Tuple of (all_present, missing_tools_list)
    """
    tools_to_check = ['hades', 'gsutil']
    if not skip_optional:
        tools_to_check.extend(['avro-tools', 'parquet-cli', 'tfr', 'jq'])

    missing = []
    for tool in tools_to_check:
        if shutil.which(tool) is None:
            missing.append(tool)

    return len(missing) == 0, missing


def print_missing_tools(missing_tools: List[str]):
    """Print installation instructions for missing tools."""
    print("\n❌ Missing required tools:\n")
    for tool in missing_tools:
        install_cmd = REQUIRED_TOOLS.get(tool, 'Unknown installation')
        print(f"  • {tool}")
        print(f"    Install: {install_cmd}\n")

    print("Please install the missing tools and try again.")


def check_java_version() -> Tuple[Optional[int], bool]:
    """
    Check current Java version.

    Returns:
        Tuple of (major_version, is_compatible)
        is_compatible is True if version <= 17 (required for avro-tools/parquet-cli)
    """
    try:
        result = subprocess.run(
            ['java', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        # Java version output goes to stderr
        output = result.stderr

        # Parse version from output like: java version "17.0.12" or openjdk version "17.0.12"
        version_match = re.search(r'version "(\d+)\.', output)
        if not version_match:
            # Try newer format: java 17.0.12
            version_match = re.search(r'java (\d+)\.', output)

        if version_match:
            major_version = int(version_match.group(1))
            is_compatible = major_version <= 17
            return major_version, is_compatible

        return None, False

    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        return None, False


def print_java_warning(java_version: Optional[int]):
    """Print warning about Java version compatibility."""
    print("\n⚠️  Java Version Compatibility Warning")
    print("=" * 80)

    if java_version is None:
        print("Could not detect Java version.")
    else:
        print(f"Current Java version: {java_version}")
        print("Required for avro-tools/parquet-cli: Java 17 or earlier")

    print("\nTo switch to Java 17 using sdkman:")
    print("  source ~/.sdkman/bin/sdkman-init.sh")
    print("  sdk use java 17.0.12-amzn")
    print("\nOr install Java 17:")
    print("  brew install openjdk@17")
    print("=" * 80 + "\n")


def run_command(cmd: str, description: str = "", timeout: int = 30) -> Tuple[bool, str, str]:
    """
    Run a shell command and return success status and output.

    Args:
        cmd: Command to run
        description: Human-readable description for logging
        timeout: Command timeout in seconds

    Returns:
        Tuple of (success, stdout, stderr)
    """
    if description:
        print(f"\n🔄 {description}...")

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return result.returncode == 0, result.stdout, result.stderr

    except subprocess.TimeoutExpired:
        return False, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return False, "", str(e)


def get_partitions(endpoint_id: str) -> List[str]:
    """
    Get list of available partitions for an endpoint.

    Args:
        endpoint_id: Data endpoint ID

    Returns:
        List of partition dates (sorted, most recent first)
    """
    cmd = f"hades partitions {endpoint_id}"
    success, stdout, stderr = run_command(cmd, f"Fetching partitions for {endpoint_id}")

    if not success:
        print(f"❌ Failed to get partitions: {stderr}")
        sys.exit(1)

    # Parse output - skip header line and cursor lines
    lines = stdout.strip().split('\n')
    partitions = []

    for line in lines:
        line = line.strip()
        # Skip empty lines, header lines (all caps), and cursor lines
        if not line or line.startswith('ENDPOINT') or line.startswith('CURSOR') or line.startswith('AQAAAA'):
            continue

        # Parse table row: endpoint_id  partition  revisions
        parts = line.split()
        if len(parts) >= 2:
            # Second column is the partition
            partition = parts[1]
            partitions.append(partition)

    if not partitions:
        print(f"❌ No partitions found for endpoint: {endpoint_id}")
        sys.exit(1)

    # Sort in reverse chronological order (most recent first)
    partitions.sort(reverse=True)

    return partitions


def parse_hades_revisions_output(output: str) -> Optional[Dict[str, str]]:
    """
    Parse output from 'hades revisions' command to extract revision information.

    Args:
        output: Raw output from hades revisions (tabular format)

    Returns:
        Dictionary with keys: revision_id, creation_time, expiration_time, storage_uri
        Or None if parsing failed
    """
    # Parse tabular output
    # Format: REVISION_ID  CREATION_TIME  EXPIRATION_TIME  URI
    lines = output.strip().split('\n')

    for line in lines:
        line = line.strip()
        # Skip empty lines, header lines, and cursor lines
        if not line or line.startswith('REVISION_ID') or line.startswith('CURSOR') or line.startswith('AQAAAA'):
            continue

        # Parse table row
        parts = line.split()
        if len(parts) >= 4:
            revision_id = parts[0]
            creation_time = parts[1]
            expiration_time = parts[2]
            storage_uri = parts[3]

            # Validate it's a GCS or marker URI
            if storage_uri.startswith('gs://') or storage_uri.startswith('marker://'):
                return {
                    'revision_id': revision_id,
                    'creation_time': creation_time,
                    'expiration_time': expiration_time,
                    'storage_uri': storage_uri
                }

    return None


def get_gcs_uri(endpoint_id: str, partition: str) -> Tuple[str, str]:
    """
    Get GCS URI for a specific endpoint and partition.

    Args:
        endpoint_id: Data endpoint ID
        partition: Partition date (e.g., "2025-10-22")

    Returns:
        Tuple of (gcs_uri, detected_format)
    """
    cmd = f"hades revisions {endpoint_id} {partition}"
    success, stdout, stderr = run_command(
        cmd,
        f"Fetching revision info for partition {partition}"
    )

    if not success:
        print(f"❌ Failed to get revision info: {stderr}")
        sys.exit(1)

    # Parse the output
    revision_info = parse_hades_revisions_output(stdout)

    if not revision_info:
        print("❌ Failed to parse hades revisions output. Could not extract Storage URI.")
        print("Output was:")
        print(stdout)
        sys.exit(1)

    storage_uri = revision_info['storage_uri']

    # Check if this is a marker URI (which typically doesn't contain viewable data)
    if storage_uri.startswith('marker://'):
        print(f"\n⚠️  WARNING: Marker URI Detected")
        print("=" * 80)
        print(f"Storage URI: {storage_uri}")
        print("\nThis endpoint uses a 'marker://' URI, which typically indicates metadata")
        print("or catalog information rather than actual data files.")
        print("\nMarker URIs usually don't contain viewable parquet/avro/tfrecords files.")
        print("This endpoint likely doesn't have data that can be viewed with this tool.")
        print("=" * 80)
        print("\nAttempting to continue anyway...\n")

    print(f"✓ Found revision: {revision_info['revision_id']}")
    print(f"  Created: {revision_info['creation_time']}")
    print(f"  Expires: {revision_info['expiration_time']}")
    print(f"  Storage URI: {storage_uri}")

    # Detect format from URI (format is not in hades revisions output)
    detected_format = 'unknown'

    return storage_uri, detected_format


def list_gcs_files(gcs_uri: str) -> List[str]:
    """
    List files in a GCS directory.

    Args:
        gcs_uri: GCS URI (gs://bucket/path/)

    Returns:
        List of file paths
    """
    # Ensure URI ends with /
    if not gcs_uri.endswith('/'):
        gcs_uri += '/'

    cmd = f"gsutil ls {gcs_uri}"
    success, stdout, stderr = run_command(cmd, f"Listing files in {gcs_uri}")

    if not success:
        print(f"❌ Failed to list GCS files: {stderr}")
        sys.exit(1)

    # Parse output - each line is a file path
    files = [line.strip() for line in stdout.strip().split('\n') if line.strip()]

    # Filter out directories (they end with /)
    files = [f for f in files if not f.endswith('/')]

    # Filter out metadata files (manifest, success markers, etc.)
    files = [f for f in files if not any([
        f.endswith('_MANIFEST.json'),
        f.endswith('_SUCCESS'),
        f.endswith('.crc'),
        '/_MANIFEST' in f,
        '/_SUCCESS' in f,
        'metadata.json' in f.lower()
    ])]

    # Only keep data files (avro, parquet, tfrecords - including compressed versions)
    data_files = [f for f in files if any([
        f.endswith('.avro'),
        f.endswith('.avro.gz'),
        f.endswith('.parquet'),
        f.endswith('.parquet.gz'),
        f.endswith('.tfrecords'),
        f.endswith('.tfrecords.gz'),
        f.endswith('.tfrecord'),
        f.endswith('.tfrecord.gz')
    ])]

    if not data_files:
        print(f"❌ No data files found in {gcs_uri}")
        print(f"   Found {len(files)} files, but none were avro/parquet/tfrecords")
        sys.exit(1)

    return data_files


def detect_format_from_filepath(filepath: str) -> str:
    """
    Detect file format from filepath extension.

    Args:
        filepath: Full file path

    Returns:
        Format string: 'avro', 'parquet', or 'tfrecords'
    """
    # Handle compressed files by removing .gz extension first
    path_lower = filepath.lower()
    if path_lower.endswith('.gz'):
        path_lower = path_lower[:-3]

    if path_lower.endswith('.avro'):
        return 'avro'
    elif path_lower.endswith('.parquet'):
        return 'parquet'
    elif path_lower.endswith('.tfrecords') or path_lower.endswith('.tfrecord'):
        return 'tfrecords'
    else:
        # Try to guess from common patterns
        if 'avro' in path_lower:
            return 'avro'
        elif 'parquet' in path_lower:
            return 'parquet'
        elif 'tfrecord' in path_lower:
            return 'tfrecords'
        else:
            raise ValueError(f"Unknown file format for: {filepath}")


def view_data(filepath: str, format_type: str, num_records: int,
              anonymize: bool = False, endpoint_id: Optional[str] = None):
    """
    View data from a file using the appropriate tool.

    Args:
        filepath: GCS filepath
        format_type: 'avro', 'parquet', or 'tfrecords'
        num_records: Number of records to display
        anonymize: If True, anonymize PII fields based on schema semantic types
        endpoint_id: Endpoint ID for fetching schema (required if anonymize=True)
    """
    print(f"\n📊 Viewing {num_records} record(s) from {format_type.upper()} file...")
    print(f"   File: {filepath}")
    if anonymize:
        print("🔒 Anonymization enabled")
    print("=" * 80)

    # Get semantic types if anonymizing
    semantic_types = {}
    if anonymize:
        if not endpoint_id:
            print("⚠️  Cannot anonymize without endpoint ID for schema lookup")
            anonymize = False
        else:
            print("🔒 Fetching schema for semantic types...")
            semantic_types = get_schema_semantic_types(endpoint_id)
            if not semantic_types:
                print("⚠️  Could not fetch semantic types - proceeding without anonymization")
                print("   Data will be displayed as-is. Review for PII before sharing.")
            else:
                print(f"   Found {len(semantic_types)} semantic type annotation(s)")

    # Get command template for this format
    cmd_template = FORMAT_COMMANDS.get(format_type)
    if not cmd_template:
        print(f"❌ Unknown format: {format_type}")
        sys.exit(1)

    # Format the command
    cmd = cmd_template.format(filepath=filepath, num_records=num_records)

    # Run the command and optionally anonymize output
    try:
        if anonymize and semantic_types:
            # Capture output for anonymization
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)

            if result.returncode == 0:
                # Parse and anonymize the JSON output
                lines = [line for line in result.stdout.strip().split('\n') if line.strip()]

                # Try to parse as individual JSON objects
                # The output is typically one JSON object per line (after jq formatting)
                # or a formatted multi-line JSON
                if lines:
                    try:
                        # Try parsing as array of JSON objects
                        json_objects = []
                        current_obj = []
                        brace_count = 0

                        for line in lines:
                            current_obj.append(line)
                            brace_count += line.count('{') - line.count('}')

                            if brace_count == 0 and current_obj:
                                obj_str = '\n'.join(current_obj)
                                try:
                                    obj = json_module.loads(obj_str)
                                    json_objects.append(obj)
                                except json_module.JSONDecodeError:
                                    pass
                                current_obj = []

                        # Anonymize each object
                        for i, obj in enumerate(json_objects):
                            anonymized = anonymize_record(obj, semantic_types, i + 1)
                            print(json_module.dumps(anonymized, indent=2))
                            if i < len(json_objects) - 1:
                                print()  # Separator between records

                    except Exception as e:
                        # Fallback: just print the output with a warning
                        print(f"⚠️  Could not anonymize output: {e}")
                        print(result.stdout)
            else:
                print(f"\n⚠️  Command exited with code {result.returncode}")
                print("This may indicate a data reading error or incompatible Java version.")
                if result.stderr:
                    print(result.stderr)
        else:
            # Stream output directly without anonymization
            result = subprocess.run(cmd, shell=True, timeout=120)

            if result.returncode != 0:
                print(f"\n⚠️  Command exited with code {result.returncode}")
                print("This may indicate a data reading error or incompatible Java version.")

        print("=" * 80)

    except subprocess.TimeoutExpired:
        print("\n❌ Command timed out after 120 seconds")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='View actual data records from Spotify data endpoints',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View 5 records (default) from most recent partition
  python view_endpoint_data.py search.offline.candidates.ClickedItems

  # View 20 records
  python view_endpoint_data.py search.offline.candidates.ClickedItems --num-records 20

  # View specific partition
  python view_endpoint_data.py search.offline.candidates.ClickedItems --partition 2025-10-21

  # List available partitions
  python view_endpoint_data.py search.offline.candidates.ClickedItems --list-partitions

  # View a specific file (by index)
  python view_endpoint_data.py search.offline.candidates.ClickedItems --file-index 5

  # List files for a partition
  python view_endpoint_data.py search.offline.candidates.ClickedItems --list-files

  # View anonymized data (PII replaced with safe placeholders)
  python view_endpoint_data.py search.offline.candidates.ClickedItems --anonymize
        """
    )

    parser.add_argument(
        'endpoint_id',
        help='Data endpoint ID (e.g., search.offline.candidates.ClickedItems)'
    )

    parser.add_argument(
        '--partition',
        help='Specific partition to view (default: most recent)'
    )

    parser.add_argument(
        '--num-records',
        type=int,
        default=5,
        help='Number of records to view (default: 5)'
    )

    parser.add_argument(
        '--file-index',
        type=int,
        default=0,
        help='Index of file to view (default: 0, first file)'
    )

    parser.add_argument(
        '--list-partitions',
        action='store_true',
        help='Only list available partitions'
    )

    parser.add_argument(
        '--list-files',
        action='store_true',
        help='Only list files for the partition'
    )

    parser.add_argument(
        '--check-tools',
        action='store_true',
        help='Check if required tools are installed'
    )

    parser.add_argument(
        '--skip-java-check',
        action='store_true',
        help='Skip Java version compatibility check'
    )

    parser.add_argument(
        '--anonymize',
        action='store_true',
        help='Anonymize PII fields based on schema semantic types. Replaces Narrow/Strict tier values with safe placeholders.'
    )

    args = parser.parse_args()

    # Check tools if requested
    if args.check_tools:
        print("🔍 Checking required tools...\n")
        all_present, missing = check_required_tools(skip_optional=False)
        if all_present:
            print("✓ All required tools are installed!")
        else:
            print_missing_tools(missing)
        sys.exit(0 if all_present else 1)

    # Check for core tools (hades, gsutil)
    all_present, missing = check_required_tools(skip_optional=True)
    if not all_present:
        print("❌ Missing core tools required for this script:")
        print_missing_tools(missing)
        sys.exit(1)

    # Check Java version unless skipped
    if not args.skip_java_check:
        java_version, is_compatible = check_java_version()
        if java_version is not None and not is_compatible:
            print_java_warning(java_version)
            response = input("Continue anyway? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                print("Aborted.")
                sys.exit(1)

    print(f"\n📋 Endpoint: {args.endpoint_id}")

    # Step 1: Get partitions
    partitions = get_partitions(args.endpoint_id)

    if args.list_partitions:
        print(f"\n📅 Available partitions ({len(partitions)} total):\n")
        for i, partition in enumerate(partitions, 1):
            marker = "← most recent" if i == 1 else ""
            print(f"  {i:3d}. {partition} {marker}")
        print()
        return

    # Select partition
    selected_partition = args.partition or partitions[0]

    if selected_partition not in partitions:
        print(f"⚠️  Warning: Partition {selected_partition} not in available list")
        print(f"   Available partitions: {', '.join(partitions[:5])}...")

    print(f"✓ Selected partition: {selected_partition}")

    # Step 2: Get GCS URI
    gcs_uri, detected_format = get_gcs_uri(args.endpoint_id, selected_partition)

    # Step 3: List files
    files = list_gcs_files(gcs_uri)

    print(f"\n📁 Found {len(files)} file(s)")

    if args.list_files:
        print("\nFiles:")
        for i, file in enumerate(files):
            marker = "← will view" if i == args.file_index else ""
            filename = file.split('/')[-1]
            print(f"  {i:3d}. {filename} {marker}")
        print()
        return

    # Select file
    if args.file_index >= len(files):
        print(f"❌ File index {args.file_index} out of range (0-{len(files)-1})")
        sys.exit(1)

    selected_file = files[args.file_index]

    # Step 4: Detect format (from filepath, fallback to hades-detected format)
    try:
        format_type = detect_format_from_filepath(selected_file)
    except ValueError:
        # Use format from hades if we can't detect from filepath
        format_type = detected_format.lower() if detected_format != 'unknown' else None
        if not format_type:
            print(f"❌ Could not detect file format for: {selected_file}")
            sys.exit(1)

    # Check if we have the required tool for this format
    format_tool_map = {
        'avro': 'avro-tools',
        'parquet': 'parquet-cli',
        'tfrecords': 'tfr'
    }

    required_tool = format_tool_map.get(format_type)
    if required_tool and shutil.which(required_tool) is None:
        print(f"\n❌ Required tool '{required_tool}' not found for {format_type.upper()} format")
        print(f"   Install: {REQUIRED_TOOLS.get(required_tool)}")
        sys.exit(1)

    # Step 5: View the data
    view_data(selected_file, format_type, args.num_records,
              anonymize=args.anonymize, endpoint_id=args.endpoint_id)


if __name__ == '__main__':
    main()
