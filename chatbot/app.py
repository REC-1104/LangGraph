import streamlit as st
from bot import chatbot
import time

# Initialize the chatbot
mybot = chatbot()
workflow = mybot()

# Set up session state to store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS for styling
st.markdown("""
    <style>
    .chat-container {
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 10px;
        max-height: 400px;
        overflow-y: auto;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 10px;
        max-width: 70%;
        align-self: flex-end;
        text-align: right;
    }
    .bot-message {
        background-color: #e9ecef;
        color: black;
        padding: 10px;
        border-radius: 15px;
        margin: 5px 10px;
        max-width: 70%;
        align-self: flex-start;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
        padding: 10px;
    }
    .stButton > button {
        border-radius: 20px;
        background-color: #007bff;
        color: white;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #0056b3;
    }
    .sidebar .sidebar-content {
        background-color: #f1f3f5;
    }
    </style>
""", unsafe_allow_html=True)

# Set up the Streamlit app UI
st.title("💬 Smart ChatBot")
st.subheader("Powered by LangGraph & Groq")

# Sidebar for additional information
with st.sidebar:
    st.header("About")
    st.markdown("""
        This chatbot uses **LangGraph** and **Groq** to answer your questions intelligently.
        - Ask anything, and the bot will respond with accurate answers.
        - Use the 'Clear Chat' button to reset the conversation.
        - Ensure API keys are set in the `.env` file for Groq and Tavily.
    """)
    st.markdown("---")
    st.caption("Built with Streamlit | © 2025")

# Chat container for conversation history
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="bot-message">{message["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input form for user question
with st.form(key="chat_form", clear_on_submit=True):
    question = st.text_input("Ask your question here:", placeholder="Type your question...")
    col1, col2 = st.columns([1, 1])
    with col1:
        submit_button = st.form_submit_button("Send")
    with col2:
        clear_button = st.form_submit_button("Clear Chat")

# Handle form submission
if submit_button and question.strip():
    # Add user message to session state
    st.session_state.messages.append({"role": "user", "content": question})

    # Show loading spinner while processing
    with st.spinner("Thinking..."):
        # Prepare input for the workflow
        input_data = {"messages": [question]}
        config = {"configurable": {"thread_id": "1"}}

        # Invoke the workflow
        try:
            response = workflow.invoke(input_data, config=config)
            bot_response = response['messages'][-1].content
        except Exception as e:
            bot_response = f"Error: {str(e)}"

        # Add bot response to session state
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    # Rerun to update the UI
    st.rerun()

elif submit_button and not question.strip():
    st.warning("Please enter a question to get an answer.")

# Handle clear chat button
if clear_button:
    st.session_state.messages = []
    st.rerun()