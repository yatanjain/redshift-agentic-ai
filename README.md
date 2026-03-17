# Redshift Agentic AI Assistant

A LangGraph-powered Agentic AI module that enables **natural language querying** of Amazon Redshift — retrieve DDLs, run SELECT queries, check record counts, inspect table ownership, and explore column metadata via plain English prompts.

Built as a POC using **Gemini 1.5 Flash (free)** + **SQLite** — swap one line to connect to real Redshift.

---

## Features

- Natural language to SQL conversion via Gemini 1.5 Flash
- List all accessible tables
- Retrieve DDL (table structure and schema)
- Count records in any table
- Inspect table ownership
- Execute ad-hoc SELECT queries with results
- Get detailed column metadata
- SELECT-only guardrail — no data modification possible
- User-based connection — inherits database permissions automatically

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Agent framework | LangGraph |
| LLM | Google Gemini 1.5 Flash (free tier) |
| Database (POC) | SQLite |
| Database (Production) | Amazon Redshift |
| Language | Python 3.10+ |

---

## Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/yatanjain/redshift-agentic-ai
cd redshift-agentic-ai
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your API key
```bash
cp .env.example .env
```
Then open `.env` and add your free Gemini API key from https://aistudio.google.com

### 5. Run the agent
```bash
python main.py
```

---

## Example Prompts

```
You: Show me all tables
You: How many records are in the orders table?
You: Show me the DDL for the customers table
You: Who owns the products table?
You: Show me top 5 orders from the West region
You: What columns does the orders table have?
You: Show me all completed orders with their total value
You: Which customers are from the USA?
```

---

## Project Structure

```
redshift-agentic-ai/
│
├── agent/
│   ├── __init__.py
│   ├── database.py     # DB connection + sample data setup
│   ├── tools.py        # Core tools: DDL, SELECT, count, owner
│   └── agent.py        # LangGraph agent + Gemini LLM + CLI
│
├── main.py             # Entry point
├── requirements.txt
├── .env.example        # Template — copy to .env
├── .gitignore
└── README.md
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
        user=username,      # user's own credentials
        password=password   # enforces Redshift permissions
    )
```

By connecting as the actual user, Redshift automatically enforces all table, row, and column-level permissions — the agent never needs to know what's restricted.

---

## Security Design

- **SELECT only** — agent rejects INSERT, UPDATE, DELETE, DROP
- **User-based auth** — each user connects with their own credentials
- **Permission enforcement at DB level** — restricted data is blocked by Redshift, not the agent
- **No credentials in code** — all secrets stored in `.env`
- **Row limit** — queries capped at 50 rows by default

---

## Author

Yatan Jain — Senior Data Engineer  
linkedin.com/in/yatanjain
