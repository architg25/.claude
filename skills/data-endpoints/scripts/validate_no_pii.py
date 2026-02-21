#!/usr/bin/env python3
"""
PII Validation Script

Checks text or files for potential PII leakage patterns.
Returns exit code 0 if no PII detected, 1 if potential PII found.

Usage:
    python validate_no_pii.py --text "your text here"
    python validate_no_pii.py --file path/to/file
"""

import argparse
import re
import sys
from typing import List, Tuple


# PII detection patterns
PII_PATTERNS = [
    # Email addresses
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
     'Email address',
     ['test@example.com', 'noreply@', '@example.org']),

    # IPv4 addresses (excluding common safe ones)
    (r'\b(?!127\.0\.0\.1|0\.0\.0\.0|192\.168\.x\.x)(?:\d{1,3}\.){3}\d{1,3}\b',
     'IPv4 address',
     []),

    # IPv6 addresses
    (r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
     'IPv6 address',
     []),

    # Phone numbers (various formats)
    (r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
     'Phone number',
     ['+1-555-0100', '+1-555-0199']),

    # Spotify user URIs with non-test usernames
    (r'spotify:user:(?!test_user_|test_|user_\d)[a-zA-Z0-9_-]+',
     'Spotify user URI with real username',
     []),

    # GPS coordinates (lat, long pairs)
    (r'(?<!0\.0,0\.0)[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?),\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)',
     'GPS coordinates',
     ['0.0,0.0']),

    # Credit card patterns
    (r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
     'Credit card number',
     []),

    # SSN patterns
    (r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
     'SSN-like pattern',
     []),
]

# Known safe placeholder patterns to exclude
SAFE_PATTERNS = [
    r'test\d*@example\.com',
    r'user_\d+',
    r'user_test_\d+',
    r'test_user_\d+',
    r'device_test_\d+',
    r'Test User \d+',
    r'Test Playlist \d+',
    r'Test Device \d+',
    r'sample text \d+',
    r'message content \d+',
    r'\+1-555-0\d{3}',
    r'0\.0,0\.0',
    r'127\.0\.0\.1',
    r'192\.168\.x\.x',
]


def is_safe_match(match: str) -> bool:
    """Check if a match is a known safe placeholder."""
    for safe_pattern in SAFE_PATTERNS:
        if re.fullmatch(safe_pattern, match):
            return True
    return False


def check_for_pii(text: str) -> List[Tuple[str, str, int]]:
    """
    Check text for potential PII patterns.

    Returns:
        List of tuples: (pattern_name, matched_text, line_number)
    """
    findings = []
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        for pattern, name, exclusions in PII_PATTERNS:
            matches = re.findall(pattern, line)
            for match in matches:
                # Handle tuple matches from groups
                if isinstance(match, tuple):
                    match = match[0] if match[0] else str(match)

                # Skip known safe patterns
                if is_safe_match(match):
                    continue

                # Skip explicit exclusions
                if match in exclusions:
                    continue

                findings.append((name, match, line_num))

    return findings


def main():
    parser = argparse.ArgumentParser(
        description='Check text or files for potential PII leakage'
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--text', help='Text to check for PII')
    group.add_argument('--file', help='File path to check for PII')

    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Only output findings, no status messages'
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            sys.exit(2)
    else:
        text = args.text

    findings = check_for_pii(text)

    if findings:
        if not args.quiet:
            print("Potential PII detected:\n")

        for name, match, line_num in findings:
            print(f"  Line {line_num}: {name}")
            print(f"    Found: {match}")
            print()

        if not args.quiet:
            print(f"Total: {len(findings)} potential PII pattern(s) found")
            print("\nPlease anonymize these values before including in output.")

        sys.exit(1)
    else:
        if not args.quiet:
            print("No PII patterns detected")
        sys.exit(0)


if __name__ == '__main__':
    main()
