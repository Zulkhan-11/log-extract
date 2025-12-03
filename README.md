# log-extract

Extract structured data from unstructured log files using pattern matching

## Features

- Extract timestamps in multiple formats (ISO 8601, RFC 3339, custom patterns)
- Extract IPv4 and IPv6 addresses from log lines
- Extract HTTP status codes and methods
- Extract user agents and referrer URLs
- Predefined extractors for Apache Common/Combined Log Format
- Predefined extractors for Nginx access logs
- Predefined extractors for syslog format
- Custom regex pattern support for application-specific logs
- Filter extracted data by date range
- Filter by pattern match on specific fields
- Output results as JSON (array of objects)
- Output results as CSV with headers
- Output results as plain text (tab-separated)
- Read from file or stdin for pipe support
- Line number tracking for debugging
- Summary statistics (total lines, matched lines, extraction counts)

## Installation

```bash
# Clone the repository
git clone https://github.com/KurtWeston/log-extract.git
cd log-extract

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Built With

- python

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
