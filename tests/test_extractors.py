"""Tests for log extraction functionality."""

import pytest
from datetime import datetime
from io import StringIO
from log_extract.extractors import LogExtractor


class TestLogExtractor:
    """Test LogExtractor class."""

    def test_apache_format_extraction(self):
        log_line = '192.168.1.1 - user123 [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 1234'
        extractor = LogExtractor("apache")
        file = StringIO(log_line)
        results = extractor.extract(file)
        
        assert len(results) == 1
        assert results[0]["ip"] == "192.168.1.1"
        assert results[0]["user"] == "user123"
        assert results[0]["method"] == "GET"
        assert results[0]["status"] == "200"
        assert results[0]["line_number"] == 1

    def test_nginx_format_extraction(self):
        log_line = '10.0.0.1 - admin [15/Nov/2023:08:30:00 +0000] "POST /api/data HTTP/1.1" 201 512 "https://example.com" "Mozilla/5.0"'
        extractor = LogExtractor("nginx")
        file = StringIO(log_line)
        results = extractor.extract(file)
        
        assert len(results) == 1
        assert results[0]["ip"] == "10.0.0.1"
        assert results[0]["method"] == "POST"
        assert results[0]["referrer"] == "https://example.com"
        assert results[0]["user_agent"] == "Mozilla/5.0"

    def test_syslog_format_extraction(self):
        log_line = "Nov 15 10:23:45 server1 sshd[12345]: Connection from 192.168.1.100"
        extractor = LogExtractor("syslog")
        file = StringIO(log_line)
        results = extractor.extract(file)
        
        assert len(results) == 1
        assert results[0]["host"] == "server1"
        assert results[0]["process"] == "sshd"
        assert results[0]["pid"] == "12345"
        assert "Connection from" in results[0]["message"]

    def test_custom_pattern(self):
        log_line = "ERROR 2023-11-15 user=john action=login"
        pattern = r"(?P<level>\w+) (?P<date>[\d-]+) user=(?P<user>\w+) action=(?P<action>\w+)"
        extractor = LogExtractor("custom", pattern)
        file = StringIO(log_line)
        results = extractor.extract(file)
        
        assert len(results) == 1
        assert results[0]["level"] == "ERROR"
        assert results[0]["user"] == "john"
        assert results[0]["action"] == "login"

    def test_custom_format_without_pattern_raises_error(self):
        with pytest.raises(ValueError, match="Custom pattern required"):
            LogExtractor("custom")

    def test_unknown_format_raises_error(self):
        with pytest.raises(ValueError, match="Unknown format"):
            LogExtractor("invalid_format")

    def test_ip_version_detection(self):
        extractor = LogExtractor("apache")
        assert extractor._detect_ip_version("192.168.1.1") == "v4"
        assert extractor._detect_ip_version("2001:0db8::1") == "v6"

    def test_timestamp_parsing_iso8601(self):
        extractor = LogExtractor("apache")
        ts = extractor._parse_timestamp("2023-11-15T10:30:00+00:00")
        assert ts is not None
        assert ts.year == 2023
        assert ts.month == 11

    def test_filter_by_date(self):
        extractor = LogExtractor("apache")
        data = [
            {"parsed_timestamp": datetime(2023, 11, 10, 10, 0)},
            {"parsed_timestamp": datetime(2023, 11, 15, 10, 0)},
            {"parsed_timestamp": datetime(2023, 11, 20, 10, 0)}
        ]
        
        filtered = extractor.filter_by_date(
            data,
            datetime(2023, 11, 12, 0, 0),
            datetime(2023, 11, 18, 0, 0)
        )
        
        assert len(filtered) == 1
        assert filtered[0]["parsed_timestamp"].day == 15

    def test_filter_by_pattern(self):
        extractor = LogExtractor("apache")
        data = [
            {"status": "200", "method": "GET"},
            {"status": "404", "method": "POST"},
            {"status": "200", "method": "PUT"}
        ]
        
        filtered = extractor.filter_by_pattern(data, "status:200")
        assert len(filtered) == 2

    def test_stats_tracking(self):
        log_lines = """192.168.1.1 - user1 [10/Oct/2023:13:55:36 +0000] "GET / HTTP/1.1" 200 1234
invalid line
192.168.1.2 - user2 [10/Oct/2023:13:55:37 +0000] "POST /api HTTP/1.1" 201 512"""
        extractor = LogExtractor("apache")
        file = StringIO(log_lines)
        results = extractor.extract(file)
        
        assert extractor.stats["total_lines"] == 3
        assert extractor.stats["matched_lines"] == 2
        assert len(results) == 2

    def test_empty_file(self):
        extractor = LogExtractor("apache")
        file = StringIO("")
        results = extractor.extract(file)
        
        assert len(results) == 0
        assert extractor.stats["total_lines"] == 0
        assert extractor.stats["matched_lines"] == 0