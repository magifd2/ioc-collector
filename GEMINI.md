## Project Overview

`ioc_collector` is a CLI tool that autonomously researches security incidents and produces:
- A Markdown report summarizing the incident, timeline, impact, and mitigations
- A STIX 2.1 JSON file containing structured IoC data

## Building and Running

This project uses `uv` for dependency management with Python 3.11+.

### Setup

```bash
uv venv --python 3.11
uv pip install -e ".[dev]"
```

### Running the tool

```bash
# Set up Google Cloud credentials
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Run with a URL
uv run ioc-collector --target "https://example.com/incident-report"

# Run with natural language
uv run ioc-collector --target "2023年に発生した〇〇社のランサムウェアインシデント"

# Run from file
uv run ioc-collector --file incident_query.txt

# Run from stdin
cat incident_query.txt | uv run ioc-collector

# Skip confirmation prompt
uv run ioc-collector --target "..." --non-interactive

# Specify output directory
uv run ioc-collector --target "..." --output ./reports
```

### Running tests

```bash
uv run pytest
```

## Development Conventions

Development policies, coding standards, and commit rules are documented in `AGENTS.md`.
Detailed specifications and milestone progress are in `DOCUMENT.md`.
