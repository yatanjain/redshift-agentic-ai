# Redshift Agentic AI Assistant

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-purple)
![Gemini](https://img.shields.io/badge/Gemini-2.5Flash-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

A LangGraph-powered Agentic AI module that enables **natural language querying** of Amazon Redshift — retrieve DDLs, run SELECT queries, check record counts, inspect table ownership, and explore column metadata via plain English prompts.

Built as a POC using **Gemini 2.5 Flash (free)** + **SQLite** — swap one line to connect to real Redshift.

---

## Features

- Natural language to SQL conversion via Gemini 2.5 Flash
- Beautiful chat UI powered by Streamlit
- List all accessible tables
- Retrieve DDL (table structure and schema)
- Count records in any table
- Inspect table ownership
- Execute ad-hoc SELECT queries with results
- Get detailed column metadata
- SELECT-only guardrail — no data modification possible
- User-based connection — inherits database permissions automatically
- Conversation memory — agent remembers context within a session

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent framework | LangGraph |
| LLM | Google Gemini 2.5 Flash (free tier) |
| UI | Streamlit |
| Database (POC) | SQLite |
| Database (Production) | Amazon Redshift |
| Language | Python 3.9+ |

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/yatanjain/redshift-agentic-ai
cd redshift-agentic-ai
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your .env file

**This step is required — the app will not run without it.**

Create a `.env` file in the root of the project:
```bash
touch .env
```

Open `.env` and add the following:
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_USER=your_username
```

**How to get a free Gemini API key:**
1. Go to https://aistudio.google.com
2. Sign in with your Google account
3. Click **Get API Key** on the left panel
4. Click **Create API Key**
5. Copy the key and paste it into your `.env` file

> Important: Never share your `.env` file or commit it to GitHub.
> The `.gitignore` file in this repo already excludes it automatically.

You can also use the provided template:
```bash
cp .env.example .env
```
Then open `.env` and fill in your own values.

### 5. Run the Streamlit Chat UI (recommended)
```bash
streamlit run app.py
```
Opens a beautiful chat interface at `http://localhost:8501` in your browser.

### 5b. Run the Terminal CLI (alternative)
```bash
python3 main.py
```
Runs the agent directly in your terminal without a UI.

---

## Streamlit Chat UI

The app includes a full chat interface built with Streamlit:

- Type questions in plain English in the chat box
- Agent responds with results, DDLs, record counts, and query output
- Conversation history is maintained within the session
- Example prompts available via the expandable help section
- Runs locally at `http://localhost:8501`

---

## Example Prompts

```
Show me all tables
How many records are in the orders table?
Show me the DDL for the customers table
Who owns the products table?
Show me top 5 orders from the West region
What columns does the orders table have?
Show me all completed orders with their total value
Which customers are from the USA?
```

---

## Project Structure

```
redshift-agentic-ai/
|
|-- agent/
|   |-- __init__.py
|   |-- database.py     # DB connection + sample data setup
|   |-- tools.py        # Core tools: DDL, SELECT, count, owner
|   |-- agent.py        # LangGraph agent + Gemini LLM
|
|-- app.py              # Streamlit chat UI
|-- main.py             # Terminal CLI entry point
|-- requirements.txt    # All dependencies
|-- .env.example        # Template - copy to .env and fill in your keys
|-- .gitignore          # Excludes .env and sensitive files from GitHub
|-- README.md
```

---

## Setting Up Your .env File

The `.env` file stores your secret API keys and is **never uploaded to GitHub**.

**Step 1 - Create the file:**
```bash
touch .env
```

**Step 2 - Add your credentials:**
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_USER=your_username
```

**Step 3 - For production Redshift (optional):**
```
GEMINI_API_KEY=your_gemini_api_key_here
DB_USER=your_redshift_username

REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DBNAME=your_database
REDSHIFT_PASSWORD=your_redshift_password
```

---

## Switching to Real Redshift

In `agent/database.py`, replace the `get_connection` function:

```python
import psycopg2

def get_connection(username: str, password: str):
    return psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        dbname=os.getenv("REDSHIFT_DBNAME"),
        user=username,
        password=password
    )
```

By connecting as the actual user, Redshift automatically enforces all table, row, and column-level permissions.

---

## SSO Authentication (Enterprise / Corporate Identity)

In enterprise environments like large insurance or banking companies, users authenticate via **SSO (Single Sign-On)** using their corporate identity (Active Directory, Okta, Azure AD) instead of a username/password.

### How SSO works with Redshift

```
User logs in with Corporate SSO (AD / Okta / Azure AD)
        |
        v
AWS IAM generates temporary credentials
(Access Key + Secret Key + Session Token)
        |
        v
Redshift accepts temporary credentials
        |
        v
User's Redshift permissions still apply automatically
(same row/column/table level access as always)
        |
        v
Credentials expire automatically after 1 hour
```

### Pattern 1 — AWS IAM Identity Center (most common in enterprise)

```python
import boto3
import psycopg2
import os

def get_redshift_connection_sso(username: str):
    # Step 1 - Get temporary credentials via AWS IAM
    client = boto3.client(
        'redshift',
        region_name=os.getenv("AWS_REGION", "us-east-1")
    )

    response = client.get_cluster_credentials(
        DbUser=username,
        DbName=os.getenv("REDSHIFT_DBNAME"),
        ClusterIdentifier=os.getenv("REDSHIFT_CLUSTER_ID"),
        DurationSeconds=3600,   # credentials valid for 1 hour
        AutoCreate=False        # do not auto-create user
    )

    # Step 2 - Connect using temporary credentials
    conn = psycopg2.connect(
        host=os.getenv("REDSHIFT_HOST"),
        port=int(os.getenv("REDSHIFT_PORT", 5439)),
        dbname=os.getenv("REDSHIFT_DBNAME"),
        user=response['DbUser'],        # temporary IAM user
        password=response['DbPassword'] # temporary password
    )
    return conn
```

### Switching between Password and SSO mode

Set `AUTH_MODE` in your `.env` file to switch modes — no code changes needed:

```python
AUTH_MODE = os.getenv("AUTH_MODE", "password")  # "password" or "sso"

def get_redshift_connection(username: str, password: str = None):
    if AUTH_MODE == "sso":
        return get_redshift_connection_sso(username)
    else:
        return get_redshift_connection_password(username, password)
```

### .env setup for SSO

Add these variables to your `.env` file when using SSO:

```
# Auth mode - set to "sso" for corporate SSO, "password" for direct login
AUTH_MODE=sso

# Redshift connection
REDSHIFT_HOST=your-cluster.redshift.amazonaws.com
REDSHIFT_PORT=5439
REDSHIFT_DBNAME=your_database

# Required for SSO - AWS IAM Identity Center
REDSHIFT_CLUSTER_ID=your-cluster-name
AWS_REGION=us-east-1

# AWS credentials (if not using AWS CLI profile)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

> If you are using AWS CLI and already logged in via `aws configure` or AWS SSO,
> you do not need `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` — boto3 picks
> up the credentials automatically from your AWS CLI profile.

### Why SSO is more secure than password auth

| | Password Auth | SSO / IAM Auth |
|--|---------------|----------------|
| Credential type | Permanent password | Temporary token (1 hour) |
| Risk if leaked | High — works forever | Low — expires automatically |
| Password management | User manages | AWS/Okta manages |
| Rotation | Manual | Automatic |
| Enterprise compliance | Basic | Full audit trail |

---



- **SELECT only** - agent rejects INSERT, UPDATE, DELETE, DROP
- **User-based auth** - each user connects with their own credentials
- **Permission enforcement at DB level** - restricted data is blocked by Redshift, not the agent
- **No credentials in code** - all secrets stored in `.env` which is excluded from GitHub via `.gitignore`
- **Row limit** - queries capped at 50 rows by default

---

## Troubleshooting

**App not starting?**
- Make sure virtual environment is active: `source venv/bin/activate`
- Make sure `.env` file exists with a valid `GEMINI_API_KEY`
- Run `pip install -r requirements.txt` to ensure all dependencies are installed

**Gemini API errors?**
- Verify your API key is correct in `.env`
- Check your free tier quota at aistudio.google.com
- Make sure there are no spaces around the `=` in your `.env` file

**Slow responses?**
- This is normal for LLM-powered apps - expect 2-5 seconds per response
- Gemini 2.5 Flash is the fastest free model available

---

## Author

Yatan Jain - Senior Data Engineer
linkedin.com/in/yatanjain
