import streamlit as st
import os
from dotenv import load_dotenv
from agent.database import setup_sample_database

load_dotenv()

# Setup database if not exists
if not os.path.exists("poc_database.db"):
    setup_sample_database()

# Page config
st.set_page_config(
    page_title="Redshift AI Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Redshift Agentic AI Assistant")
st.caption("Ask anything about your database in plain English")

# Example prompts
with st.expander("💡 Example prompts"):
    st.markdown("""
    - Show me all tables
    - How many records are in the orders table?
    - Show me the DDL for the customers table
    - Who owns the products table?
    - Show me top 5 orders from the West region
    - What columns does the orders table have?
    - Show all completed orders
    """)

# Initialize agent once and store in session
@st.cache_resource
def get_agent():
    from agent.agent import build_agent
    return build_agent()

if "ai_agent" not in st.session_state:
    with st.spinner("Initializing AI agent..."):
        st.session_state.ai_agent = get_agent()
        
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hi! I'm your Redshift AI Assistant. Ask me anything about your database!"
    })

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about your database..."):

    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.ai_agent.invoke({
                    "messages": [("user", prompt)]
                })
                answer = response["messages"][-1].content
            except Exception as e:
                answer = f"Sorry, I encountered an error: {str(e)}"

        st.markdown(answer)
        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })