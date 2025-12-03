"""Tests for output formatters."""

import json
import pytest
from datetime import datetime
from log_extract.formatters import JSONFormatter, CSVFormatter, PlainTextFormatter


class TestJSONFormatter:
    """Test JSON output formatter."""

    def test_format_basic_data(self):
        formatter = JSONFormatter()
        data = [
            {"ip": "192.168.1.1", "status": "200", "method": "GET"},
            {"ip": "10.0.0.1", "status": "404", "method": "POST"}
        ]
        output = formatter.format(data)
        parsed = json.loads(output)
        
        assert len(parsed) == 2
        assert parsed[0]["ip"] == "192.168.1.1"
        assert parsed[1]["status"] == "404"

    def test_format_with_datetime(self):
        formatter = JSONFormatter()
        data = [{"timestamp": datetime(2023, 11, 15, 10, 30, 0), "event": "login"}]
        output = formatter.format(data)
        parsed = json.loads(output)
        
        assert "2023-11-15" in parsed[0]["timestamp"]
        assert parsed[0]["event"] == "login"

    def test_format_empty_data(self):
        formatter = JSONFormatter()
        output = formatter.format([])
        parsed = json.loads(output)
        
        assert parsed == []


class TestCSVFormatter:
    """Test CSV output formatter."""

    def test_format_basic_data(self):
        formatter = CSVFormatter()
        data = [
            {"ip": "192.168.1.1", "status": "200"},
            {"ip": "10.0.0.1", "status": "404"}
        ]
        output = formatter.format(data)
        lines = output.split("\n")
        
        assert len(lines) == 3
        assert "ip" in lines[0]
        assert "status" in lines[0]
        assert "192.168.1.1" in lines[1]

    def test_format_with_datetime(self):
        formatter = CSVFormatter()
        data = [{"timestamp": datetime(2023, 11, 15, 10, 30, 0), "user": "admin"}]
        output = formatter.format(data)
        
        assert "2023-11-15" in output
        assert "admin" in output

    def test_format_empty_data(self):
        formatter = CSVFormatter()
        output = formatter.format([])
        
        assert output == ""


class TestPlainTextFormatter:
    """Test plain text output formatter."""

    def test_format_basic_data(self):
        formatter = PlainTextFormatter()
        data = [
            {"ip": "192.168.1.1", "status": "200"},
            {"ip": "10.0.0.1", "status": "404"}
        ]
        output = formatter.format(data)
        lines = output.split("\n")
        
        assert len(lines) == 3
        assert "\t" in lines[0]
        assert "192.168.1.1" in lines[1]
        assert "404" in lines[2]

    def test_format_with_datetime(self):
        formatter = PlainTextFormatter()
        data = [{"timestamp": datetime(2023, 11, 15, 10, 30, 0), "action": "delete"}]
        output = formatter.format(data)
        
        assert "2023-11-15" in output
        assert "delete" in output

    def test_format_empty_data(self):
        formatter = PlainTextFormatter()
        output = formatter.format([])
        
        assert output == ""