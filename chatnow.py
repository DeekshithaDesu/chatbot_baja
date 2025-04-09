import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# ✅ Streamlit Setup
st.set_page_config(page_title="RoboDrive AI Chatbot", layout="centered")
st.title("🤖 RoboDrive - aBAJA 2024 Rulebook Assistant")
st.caption("Built by Desu Deekshitha 💡")

# ✅ Gemini API Key Setup
genai.configure(api_key="AIzaSyB121TcLtRHJjHECYdHzG8Ze_8KzpC3BKQ")
model = genai.GenerativeModel("gemini-pro")

# ✅ Load Rulebook (must be pre-converted to rulebook.txt)
@st.cache_resource
def load_rulebook():
    with open("rulebook.txt", "r", encoding="utf-8") as f:
        return f.read()
rulebook_context = load_rulebook()

# ✅ Gemini Answer from Rulebook
def ask_from_rulebook(user_input):
    prompt = f"""
You are a BAJA SAEINDIA rulebook expert. Answer based ONLY on the following rulebook content.
If the answer is NOT present in this document, reply: 'Not found in rulebook.'

Rulebook Content:
{rulebook_context}

Question: {user_input}
"""
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"⚠️ Gemini Error: {e}"

# ✅ Web Search if not found in rulebook
def search_google(query):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+site:saeindia.org"
    res = requests.get(search_url, headers=headers)

    if res.status_code != 200:
        return "Sorry, I couldn't fetch web results."

    soup = BeautifulSoup(res.text, "html.parser")
    snippets = soup.select("div.BNeawe.s3v9rd.AP7Wnd")
    if snippets:
        return "\n".join([s.get_text() for s in snippets[:3]])
    return "Sorry, I didn't find anything useful on the web."

# ✅ Streamlit Chat UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Ask anything about the BAJA SAEINDIA 2024 Rulebook or event...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Step 1: Try to answer from rulebook
    rulebook_reply = ask_from_rulebook(user_input)

    if "not found" in rulebook_reply.lower():
        # Step 2: Try web search
        with st.spinner("Not in rulebook. Searching the web..."):
            web_data = search_google(user_input)

        # Step 3: Send web result to Gemini to summarize
        final_prompt = f"""
Here is some information from the web about the question: {user_input}
Try to answer the question clearly based on this info:

Web Info:
{web_data}

Question: {user_input}
"""
        try:
            final_response = model.generate_content(final_prompt).text.strip()
        except:
            final_response = "Sorry, I couldn't get a good answer from the web."
    else:
        final_response = rulebook_reply

    st.session_state.chat_history.append({"role": "assistant", "content": final_response})
    with st.chat_message("assistant"):
        st.markdown(final_response)

# 🔁 Show chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
