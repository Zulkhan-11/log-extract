"""Core extraction logic with pattern matching."""

import re
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, TextIO


class LogExtractor:
    """Extract structured data from log files using patterns."""

    PATTERNS = {
        "apache": r'(?P<ip>[\d.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\S+)',
        "nginx": r'(?P<ip>[\d.]+) - (?P<user>\S+) \[(?P<timestamp>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) (?P<protocol>\S+)" (?P<status>\d+) (?P<size>\d+) "(?P<referrer>[^"]*)" "(?P<user_agent>[^"]*)"',
        "syslog": r'(?P<timestamp>\w+\s+\d+\s+[\d:]+) (?P<host>\S+) (?P<process>\S+?)(?:\[(?P<pid>\d+)\])?: (?P<message>.*)',
    }

    TIMESTAMP_PATTERNS = [
        (r"\d{4}-\d{2}-\d{2}T[\d:.]+(?:Z|[+-]\d{2}:\d{2})", "%Y-%m-%dT%H:%M:%S%z"),
        (r"\d{2}/\w+/\d{4}:[\d:]+\s+[+-]\d{4}", "%d/%b/%Y:%H:%M:%S %z"),
        (r"\w+\s+\d+\s+[\d:]+", "%b %d %H:%M:%S"),
    ]

    def __init__(self, format_type: str = "apache", custom_pattern: Optional[str] = None):
        if format_type == "custom":
            if not custom_pattern:
                raise ValueError("Custom pattern required for custom format")
            self.pattern = re.compile(custom_pattern)
        else:
            if format_type not in self.PATTERNS:
                raise ValueError(f"Unknown format: {format_type}")
            self.pattern = re.compile(self.PATTERNS[format_type])

        self.stats = {"total_lines": 0, "matched_lines": 0}

    def extract(self, file: TextIO) -> List[Dict[str, Any]]:
        """Extract data from log file."""
        results = []
        for line_num, line in enumerate(file, 1):
            self.stats["total_lines"] += 1
            line = line.rstrip("\n")
            match = self.pattern.search(line)
            if match:
                data = match.groupdict()
                data["line_number"] = line_num
                data["raw_line"] = line

                if "timestamp" in data:
                    data["parsed_timestamp"] = self._parse_timestamp(data["timestamp"])

                if "ip" in data:
                    data["ip_version"] = self._detect_ip_version(data["ip"])

                results.append(data)
                self.stats["matched_lines"] += 1

        return results

    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse timestamp using multiple patterns."""
        for pattern, fmt in self.TIMESTAMP_PATTERNS:
            if re.match(pattern, timestamp_str):
                try:
                    return datetime.strptime(timestamp_str, fmt)
                except ValueError:
                    continue
        return None

    def _detect_ip_version(self, ip: str) -> str:
        """Detect IP version (v4 or v6)."""
        if ":" in ip:
            return "v6"
        return "v4"

    def filter_by_date(
        self,
        results: List[Dict[str, Any]],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
    ) -> List[Dict[str, Any]]:
        """Filter results by date range."""
        if not start_date and not end_date:
            return results

        filtered = []
        for result in results:
            ts = result.get("parsed_timestamp")
            if not ts:
                continue

            if start_date and ts < start_date:
                continue
            if end_date and ts > end_date:
                continue

            filtered.append(result)

        return filtered

    def filter_by_pattern(
        self, results: List[Dict[str, Any]], filter_str: str
    ) -> List[Dict[str, Any]]:
        """Filter results by field pattern (field:value)."""
        if ":" not in filter_str:
            return results

        field, pattern = filter_str.split(":", 1)
        regex = re.compile(pattern)

        return [
            r for r in results if field in r and regex.search(str(r[field]))
        ]
