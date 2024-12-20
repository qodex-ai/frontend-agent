# QodexAI frontend agent

Open-Source AI-Powered QA Tool for Automated UI Testing and Navigation. 

Accelerate your quality assurance process with our AI-driven QA tool that automates UI testing and navigation using input files. Streamline your testing workflows, enhance software quality, and boost productivity with this easy-to-use open-source solution.

## Prerequisites

- Python 3.10 or higher
- Docker installed and running
- A valid Anthropic API key for AI-based validation

## Installation
```bash
cp .env.sample .env
```
Set your Anthropic API key as an environment variable in .env file.
ANTHROPIC_API_KEY=<your_anthropic_api_key>

## Running
Add your test scenarios description and steps required in the format provided in the `test_scenario.json` file.

Run run.sh file
```bash
./run.sh
```

### Logging and Response
- Writes the scenario details and validation results to `output` folder along with the screenshot. Checkout sample output file for a sample response:
  
- https://github.com/qodex-ai/frontend-agent/blob/main/sample_output/2024-12-09_18-19-02/index.html
<img width="1509" alt="image" src="https://github.com/user-attachments/assets/403297c9-89d9-4e26-a385-e803073d4d87">

