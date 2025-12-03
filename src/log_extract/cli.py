#!/usr/bin/env python3
"""CLI entry point for log-extract."""

import argparse
import sys
from datetime import datetime
from typing import Optional

from .extractors import LogExtractor
from .formatters import CSVFormatter, JSONFormatter, PlainTextFormatter


def parse_date(date_str: str) -> datetime:
    """Parse date string in ISO format."""
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_str}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract structured data from log files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "file", nargs="?", help="Log file to process (default: stdin)"
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["apache", "nginx", "syslog", "custom"],
        default="apache",
        help="Log format to parse",
    )
    parser.add_argument(
        "-p", "--pattern", help="Custom regex pattern (use with -f custom)"
    )
    parser.add_argument(
        "-o",
        "--output",
        choices=["json", "csv", "text"],
        default="json",
        help="Output format",
    )
    parser.add_argument("--start-date", type=parse_date, help="Filter start date")
    parser.add_argument("--end-date", type=parse_date, help="Filter end date")
    parser.add_argument(
        "--filter", help="Filter pattern (field:value or field:regex)"
    )
    parser.add_argument(
        "-s", "--stats", action="store_true", help="Show summary statistics"
    )

    args = parser.parse_args()

    if args.format == "custom" and not args.pattern:
        parser.error("--pattern required when using -f custom")

    try:
        input_file = open(args.file, "r") if args.file else sys.stdin

        extractor = LogExtractor(args.format, args.pattern)
        results = extractor.extract(input_file)

        if args.start_date or args.end_date:
            results = extractor.filter_by_date(results, args.start_date, args.end_date)

        if args.filter:
            results = extractor.filter_by_pattern(results, args.filter)

        formatters = {
            "json": JSONFormatter(),
            "csv": CSVFormatter(),
            "text": PlainTextFormatter(),
        }
        formatter = formatters[args.output]
        output = formatter.format(results)
        print(output)

        if args.stats:
            total = extractor.stats["total_lines"]
            matched = extractor.stats["matched_lines"]
            print(
                f"\n--- Statistics ---\nTotal lines: {total}\nMatched lines: {matched}\nMatch rate: {matched/total*100:.1f}%",
                file=sys.stderr,
            )

        if args.file:
            input_file.close()

        return 0

    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
