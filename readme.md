# Test Scenario Executor

This project automates the execution and validation of test scenarios by interacting with a bot via a chat interface of claude-computer-use. It retrieves results from a Docker container and uses AI to determine if the scenario was successfully validated.

## Prerequisites

- Python 3.10 or higher
- Docker installed and running
- A valid Anthropic API key for AI-based validation

## Installation

Set your Anthropic API key as an environment variable in .env file using reference of .env.sample:
ANTHROPIC_API_KEY=<your_anthropic_api_key>

## Running
Add your test scenarios description and steps required in the format provided in the `test_scenario.json` file.
Run run.sh file
```bash
./run.sh
```

### Logging and Response
- Writes the scenario details and validation results to `output` folder
