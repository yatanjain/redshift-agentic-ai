import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from agent.tools import (
    get_all_tables,
    get_ddl,
    get_record_count,
    get_table_owner,
    run_select_query,
    get_column_info,
)

load_dotenv()

# Current user — in production, this comes from login/auth
CURRENT_USER = os.getenv("DB_USER", "default_user")


# ── Wrap tools with @tool decorator so LangGraph can use them ──

@tool
def tool_get_all_tables() -> str:
    """List all tables available in the database that the user can access."""
    return get_all_tables(CURRENT_USER)


@tool
def tool_get_ddl(table_name: str) -> str:
    """
    Get the DDL (CREATE TABLE definition) for a specific table.
    Shows all columns, data types, primary keys, and constraints.
    Use this when the user asks about table structure or schema.
    """
    return get_ddl(table_name, CURRENT_USER)


@tool
def tool_get_record_count(table_name: str) -> str:
    """
    Get the total number of records (rows) in a table.
    Use this when the user asks 'how many records', 'how many rows',
    or 'what is the size of a table'.
    """
    return get_record_count(table_name, CURRENT_USER)


@tool
def tool_get_table_owner(table_name: str) -> str:
    """
    Get the owner of a specific table.
    Use this when the user asks who owns a table or who created it.
    """
    return get_table_owner(table_name, CURRENT_USER)


@tool
def tool_run_select(query: str) -> str:
    """
    Execute a SELECT SQL query against the database.
    Only SELECT statements are allowed — no data modification.
    Use this when the user wants to fetch or filter actual data.
    Always write valid SQL. Results are limited to 50 rows.
    """
    return run_select_query(query, CURRENT_USER)


@tool
def tool_get_column_info(table_name: str) -> str:
    """
    Get detailed column metadata for a table —
    column names, data types, nullable, default values.
    Use this when user asks about specific columns in a table.
    """
    return get_column_info(table_name, CURRENT_USER)


# ── Build the agent ──

def build_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0,
    )

    tools = [
        tool_get_all_tables,
        tool_get_ddl,
        tool_get_record_count,
        tool_get_table_owner,
        tool_run_select,
        tool_get_column_info,
    ]

    system_prompt = """You are a helpful database assistant for Amazon Redshift (simulated with SQLite for this POC).

Your job is to help users explore and query the database using plain English.

You have access to these tools:
- List all available tables
- Get DDL (table structure/schema) for any table  
- Count records in a table
- Find out who owns a table
- Run SELECT queries to fetch data
- Get detailed column metadata

Rules:
1. NEVER modify data — only SELECT and metadata operations are allowed
2. Always use the correct tool for the job — don't guess answers
3. If a table doesn't exist, tell the user clearly
4. Format results clearly and explain what was found
5. If the user asks something vague, ask for clarification
6. Always remind the user that results respect their database permissions

When writing SQL queries:
- Use standard SQL syntax
- Keep queries efficient
- Add LIMIT if the user doesn't specify a row count
- Use WHERE clauses when the user mentions filters
"""

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_prompt,
    )
    return agent


# ── Interactive CLI loop ──

def run_interactive():
    print("\n" + "="*60)
    print("  Redshift Agentic AI Assistant (POC)")
    print("  Powered by: Gemini 1.5 Flash + LangGraph + SQLite")
    print("  Type 'exit' or 'quit' to stop")
    print("="*60)
    print("\nExample prompts:")
    print("  - Show me all tables")
    print("  - How many records are in the orders table?")
    print("  - Show me the DDL for the customers table")
    print("  - Who owns the products table?")
    print("  - Show me top 5 orders from the West region")
    print("  - What columns does the orders table have?")
    print()

    agent = build_agent()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            print("\nAssistant: ", end="", flush=True)
            response = agent.invoke({
                "messages": [("user", user_input)]
            })

            # Extract the final message
            final_message = response["messages"][-1].content
            print(final_message)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}\n")


if __name__ == "__main__":
    run_interactive()
