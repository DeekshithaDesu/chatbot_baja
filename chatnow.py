import streamlit as st
import google.generativeai as genai

# ✅ Set Streamlit page config FIRST
st.set_page_config(page_title="RoboDrive Chatbot", layout="centered")

# 🔐 Configure Gemini with your actual API key
genai.configure(api_key="AIzaSyB12TlCtLRHJjHECYdHzG8Ze_8KzpC3BKQ")

# 📘 Load Rulebook Text (from preprocessed 1 PDF)
@st.cache_resource
def load_rulebook():
    with open("rulebook.txt", "r", encoding="utf-8") as f:
        return f.read()

rulebook_context = load_rulebook()

# 💬 Function to query Gemini
def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text

# 🤖 Chatbot UI
st.title("🤖 RoboDrive Chatbot")
st.markdown("Ask any question related to the **BAJA SAEINDIA Rulebook**!")

# 🗨️ Show chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 💬 User input
user_input = st.chat_input("Ask a question...")

if user_input:
    # Store user's question
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 🔍 Prompt for Gemini
    prompt = f"""
You are an expert assistant for the RoboDrive team helping them understand the BAJA SAEINDIA Rulebook.
Use the following rulebook content to answer the question accurately.

Rulebook Content:
{rulebook_context}

Question:
{user_input}
"""
    response = ask_gemini(prompt)

    # Show Gemini's answer
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
