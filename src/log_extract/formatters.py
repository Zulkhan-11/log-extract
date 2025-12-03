"""Output formatters for extracted log data."""

import csv
import json
from io import StringIO
from typing import Any, Dict, List


class BaseFormatter:
    """Base class for output formatters."""

    def format(self, data: List[Dict[str, Any]]) -> str:
        raise NotImplementedError


class JSONFormatter(BaseFormatter):
    """Format output as JSON."""

    def format(self, data: List[Dict[str, Any]]) -> str:
        serializable_data = []
        for item in data:
            serializable_item = {}
            for key, value in item.items():
                if hasattr(value, "isoformat"):
                    serializable_item[key] = value.isoformat()
                else:
                    serializable_item[key] = value
            serializable_data.append(serializable_item)

        return json.dumps(serializable_data, indent=2)


class CSVFormatter(BaseFormatter):
    """Format output as CSV."""

    def format(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return ""

        output = StringIO()
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(output, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            serialized_row = {}
            for key, value in row.items():
                if hasattr(value, "isoformat"):
                    serialized_row[key] = value.isoformat()
                else:
                    serialized_row[key] = value
            writer.writerow(serialized_row)

        return output.getvalue().rstrip("\n")


class PlainTextFormatter(BaseFormatter):
    """Format output as plain text (tab-separated)."""

    def format(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return ""

        lines = []
        fieldnames = list(data[0].keys())
        lines.append("\t".join(fieldnames))

        for row in data:
            values = []
            for key in fieldnames:
                value = row[key]
                if hasattr(value, "isoformat"):
                    values.append(value.isoformat())
                else:
                    values.append(str(value))
            lines.append("\t".join(values))

        return "\n".join(lines)
