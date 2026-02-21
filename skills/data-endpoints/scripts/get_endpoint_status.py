#!/usr/bin/env python3
"""
Get Data Endpoint Partition Status

Retrieves partition status information from partition-status-service.
Shows OK, WARNING, and ERROR states for data endpoint partitions.

Usage:
    python get_endpoint_status.py <endpoint_id>
    python get_endpoint_status.py <endpoint_id> --from 2025-01-01 --to 2025-01-23
    python get_endpoint_status.py <endpoint_id> --state ERROR
    python get_endpoint_status.py <endpoint_id> --format json
"""

import argparse
import json
import sys
from typing import Any

# Try to import from utils, fall back to inline if not available
try:
    from utils.api_client import PartitionStatusClient
except ImportError:
    import requests

    class PartitionStatusClient:
        BASE_URL = "http://data-status-service.spotify.net:8080/v0"

        def get_statuses(
            self,
            endpoint_id: str,
            partition_min: str | None = None,
            partition_max: str | None = None,
            state: str | None = None,
            limit: int = 100
        ) -> list[dict[str, Any]]:
            params: dict[str, str | int] = {"endpoint": endpoint_id, "limit": limit}
            if partition_min:
                params["partition_min"] = partition_min
            if partition_max:
                params["partition_max"] = partition_max
            if state:
                params["state"] = state

            response = requests.get(f"{self.BASE_URL}/statuses", params=params, timeout=30)
            response.raise_for_status()
            return response.json()


def format_status_table(statuses: list[dict[str, Any]]) -> str:
    """Format statuses as a table."""
    if not statuses:
        return "No statuses found."

    lines = []
    lines.append("=" * 80)
    lines.append(f"{'Partition':<25} {'State':<10} {'Effective':<10} {'Updated':<20}")
    lines.append("-" * 80)

    for status in statuses:
        partition = status.get("partition", "N/A")[:25]
        state = status.get("state", "N/A")
        effective = status.get("effectiveState", "N/A")
        updated = status.get("updatedAt", "N/A")[:20]

        # Color indicators
        state_icon = {"OK": "✓", "WARNING": "⚠", "ERROR": "❌"}.get(state, "?")

        lines.append(f"{partition:<25} {state_icon} {state:<8} {effective:<10} {updated:<20}")

    lines.append("=" * 80)
    lines.append(f"Total: {len(statuses)} partition(s)")

    return "\n".join(lines)


def format_summary(statuses: list[dict[str, Any]]) -> str:
    """Format a summary of status counts."""
    if not statuses:
        return "No statuses found."

    counts = {"OK": 0, "WARNING": 0, "ERROR": 0}
    for status in statuses:
        state = status.get("state", "UNKNOWN")
        if state in counts:
            counts[state] += 1

    lines = [
        "Status Summary:",
        f"  ✓ OK:      {counts['OK']}",
        f"  ⚠ WARNING: {counts['WARNING']}",
        f"  ❌ ERROR:   {counts['ERROR']}",
        f"  Total:     {len(statuses)}"
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Get partition status for a data endpoint",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search.metrics.dataset
  %(prog)s search.metrics.dataset --from 2025-01-01 --to 2025-01-23
  %(prog)s search.metrics.dataset --state ERROR
  %(prog)s search.metrics.dataset --format json
  %(prog)s search.metrics.dataset --summary
        """
    )

    parser.add_argument("endpoint_id", help="Data endpoint ID")
    parser.add_argument("--from", dest="from_date",
                        help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="to_date",
                        help="End date (YYYY-MM-DD)")
    parser.add_argument("--state", choices=["OK", "WARNING", "ERROR"],
                        help="Filter by state")
    parser.add_argument("--limit", type=int, default=100,
                        help="Maximum results (default: 100)")
    parser.add_argument("--format", choices=["table", "json", "summary"],
                        default="table", help="Output format")

    args = parser.parse_args()

    try:
        client = PartitionStatusClient()

        # Convert dates to ISO 8601 format
        partition_min = f"{args.from_date}T00:00:00Z" if args.from_date else None
        partition_max = f"{args.to_date}T23:59:59Z" if args.to_date else None

        print(f"🔄 Fetching status for: {args.endpoint_id}")

        statuses = client.get_statuses(
            args.endpoint_id,
            partition_min=partition_min,
            partition_max=partition_max,
            state=args.state,
            limit=args.limit
        )

        if args.format == "json":
            print(json.dumps(statuses, indent=2))
        elif args.format == "summary":
            print(format_summary(statuses))
        else:
            print(format_status_table(statuses))

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
