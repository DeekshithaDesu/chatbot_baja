import streamlit as st
import google.generativeai as genai


st.set_page_config(page_title="RoboDrive Chatbot", layout="centered")

# Configure Gemini
genai.configure(api_key="AIzaSyB121TcLtRHJjHECYdHzG8Ze_8KzpC3BKQ")


# Load preprocessed Rulebook context
@st.cache_resource
def load_rulebook():
    with open("rulebook.txt", "r", encoding="utf-8") as f:
        return f.read()

rulebook_context = load_rulebook()

# Chat state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "welcomed" not in st.session_state:
    st.session_state.welcomed = False

# Gemini answer function
def ask_gemini(context, query):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"Answer the following question using this rulebook context:\n\n{context}\n\nQuestion: {query}"
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠️ Error from Gemini: {e}"

# Page UI
st.set_page_config(page_title="RoboDrive Chatbot", layout="centered")
st.title("🤖 RoboDrive - aBAJA 2024 Rulebook Assistant")
st.caption("Created by Desu Deekshitha 💡")

# Initial greeting
if not st.session_state.welcomed:
    with st.chat_message("assistant"):
        st.markdown("Hello! I'm **RoboDrive**, your assistant for the aBAJA SAEINDIA 2024 Rulebook. 🚗💡\n\nAsk me anything about rules, eligibility, scoring, vehicle requirements, and more!")
    st.session_state.welcomed = True

# Chat input
query = st.chat_input("Ask something about aBAJA 2024...")

if query:
    st.session_state.chat_history.append({"role": "user", "message": query})

    with st.spinner("Thinking..."):
        answer = ask_gemini(rulebook_context, query)
        st.session_state.chat_history.append({"role": "bot", "message": answer})

# Display chat
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        with st.chat_message("user"):
            st.markdown(chat["message"])
    else:
        with st.chat_message("assistant"):
            st.markdown(chat["message"])
