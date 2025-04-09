import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# ✅ Setup
st.set_page_config(page_title="RoboDrive AI Chatbot", layout="centered")
st.title("🤖 RoboDrive - aBAJA 2024 Rulebook Assistant")
st.caption("Built by Desu Deekshitha 💡")

# ✅ Gemini Setup
genai.configure(api_key="AIzaSyB121TcLtRHJjHECYdHzG8Ze_8KzpC3BKQ")
model = genai.GenerativeModel("gemini-pro")

# ✅ Load rulebook.txt
@st.cache_resource
def load_rulebook():
    try:
        with open("rulebook.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Rulebook not found. Please ensure rulebook.txt is in the same folder."

rulebook_context = load_rulebook()

# ✅ Handle greetings separately
def is_greeting(msg):
    return msg.lower().strip() in ["hi", "hello", "hey", "hai", "yo", "hola"]

# ✅ Rulebook QA
def ask_from_rulebook(user_input):
    prompt = f"""
You are a BAJA SAEINDIA rulebook expert. Answer based ONLY on the following rulebook content.
If the answer is NOT present in this document, reply: 'Not found in rulebook.'

Rulebook:
{rulebook_context}

Question: {user_input}
"""
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Gemini Error: {e}"

# ✅ Web Fallback
def search_google(query):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:saeindia.org"
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code != 200:
            return ""
        soup = BeautifulSoup(res.text, "html.parser")
        snippets = soup.select("div.BNeawe.s3v9rd.AP7Wnd")
        return "\n".join([s.get_text() for s in snippets[:2]]) if snippets else ""
    except:
        return ""

# ✅ Session history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Chat input
user_input = st.chat_input("Ask me anything about the aBAJA Rulebook...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # 🔹 Step 0: Handle greetings
    if is_greeting(user_input):
        reply = "👋 Hello! I'm RoboDrive – your assistant for the aBAJA SAEINDIA 2024 Rulebook. Ask me anything technical, about rules, events, or eligibility!"
    
    # 🔹 Step 1: Skip short invalid inputs
    elif len(user_input.strip()) <= 2:
        reply = "🤖 Can you please ask a complete question? For example: *What are the eligibility criteria for the team?*"

    else:
        # 🔹 Step 2: Try rulebook
        rulebook_reply = ask_from_rulebook(user_input)

        if "not found" in rulebook_reply.lower():
            with st.spinner("Not found in rulebook. Searching the web..."):
                web_data = search_google(user_input)

            if not web_data.strip():
                reply = "❌ Sorry, I couldn't find any relevant info in the rulebook or online."
            else:
                web_prompt = f"""
The user asked: {user_input}
Using this web content, provide a helpful answer:

Web Info:
{web_data}
"""
                try:
                    reply = model.generate_content(web_prompt).text.strip()
                except:
                    reply = "⚠️ Sorry, Gemini couldn't understand the web data."
        else:
            reply = rulebook_reply

    st.session_state.chat_history.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.markdown(reply)

# 🔁 Chat history display
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
