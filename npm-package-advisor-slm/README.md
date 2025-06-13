# NPM Package Advisor SLM 🛡️

![Project Banner](https://i.imgur.com/JQ9w6Bk.png)

An AI-powered Small Language Model (SLM) that analyzes your Node.js project dependencies, identifies vulnerabilities, and recommends updates with risk assessment.

## Features ✨

- **Automated Dependency Scanning**: Collects complete NPM package information
- **AI-Powered Analysis**: Evaluates updates with priority ranking (critical/major/minor)
- **Vulnerability Detection**: Identifies security risks using npm audit
- **Smart Recommendations**: Provides update commands with changelog summaries
- **Professional Reporting**: Generates HTML reports with actionable insights
- **Email Notifications**: Sends reports to developers and SRE teams

## Installation ⚙️

### Prerequisites
- Node.js 16+
- Python 3.8+
- NPM 9+
- OpenAI API key

### Setup
```bash
# Clone the repository
git clone https://github.com/krishnmoorthi/ai-projects.git
cd npm-package-advisor-slm

# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```
### Configuration 🛠

1. Create .env file in project root:

# Required
`OPENAI_API_KEY=your_openai_key`
`SMTP_SERVER=smtp.yourprovider.com`
`SMTP_USER=your@email.com`
`SMTP_PASSWORD=yourpassword`

# Optional (defaults shown)
`SCAN_PROJECT_PATH=./`  # Path to Node.js project to analyze
`EMAIL_RECIPIENTS=dev@company.com,sre@company.com`
`AI_MODEL=gpt-4-1106-preview`

### Usage 🚀
#### Basic Usage
```bash
# Analyze your Node.js project
python python/main.py

# Reports will be saved in reports/ directory
```
### CI/CD Integration
#### Add to your GitHub Actions workflow:
```yaml
- name: Run NPM Advisor
  run: |
    cd npm-package-advisor-slm
    python python/main.py
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
    SCAN_PROJECT_PATH: ${{ github.workspace }}
```
### Scheduled Scanning (Linux/Mac)
#### Add to crontab for weekly scans: 
```bash
0 9 * * 1 cd /path/to/npm-package-advisor-slm && python python/main.py
```
### Advanced Options ⚡
#### Scan Specific Project
```bash
SCAN_PROJECT_PATH=/path/to/your/project python python/main.py
```
### Custom Report Output
```bash
REPORT_OUTPUT_DIR=custom_reports python python/main.py
```
### Disable Email Notifications
```bash
EMAIL_ENABLED=false python python/main.py
```
### Sample Report 📊

### Reports include:

- Priority-ranked update recommendations
- Version comparisons
- Risk assessments
- Security vulnerabilities
- Ready-to-run update commands