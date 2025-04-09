import os
import streamlit as st
from PyPDF2 import PdfReader
import google.generativeai as genai

# Setup Gemini API
genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Replace with your key

# Extract text from multiple PDFs
def read_pdfs(files):
    text = ""
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content + "\n\n"
    return text.strip()

# Chunk text to avoid token overflow
def chunk_text(text, max_words=250):
    words = text.split()
    return [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

# Use Gemini to find relevant chunks
def get_relevant_chunks(chunks, query):
    relevant = []
    model = genai.GenerativeModel("gemini-1.5-flash")
    for chunk in chunks:
        prompt = f"Does this text help answer the query?\n\nText:\n{chunk}\n\nQuery:\n{query}\nAnswer Yes or No."
        try:
            res = model.generate_content(prompt)
            if "yes" in res.text.lower():
                relevant.append(chunk)
        except:
            continue
    return relevant

# Final answer generator using relevant chunks
def query_with_context(context, query):
    prompt = f"Use the following context to answer the query:\n\n{context}\n\nQuery: {query}\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    try:
        res = model.generate_content(prompt)
        return res.text.strip()
    except Exception as e:
        return f"Error: {e}"

# Streamlit App
st.set_page_config(page_title="RoboDrive - Chat with PDF", layout="centered")
st.title("🤖 RoboDrive - Chat with PDF")
st.caption("Created by Desu Deekshitha 💡")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# Upload PDF
uploaded_files = st.file_uploader("📄 Upload PDF(s)", type="pdf", accept_multiple_files=True)
if uploaded_files:
    st.session_state.pdf_text = read_pdfs(uploaded_files)
    st.success("PDFs uploaded and processed successfully!")

# Chat interface
st.subheader("💬 Ask Questions")
query = st.chat_input("Ask something about the uploaded PDF...")

if query:
    # Append user message
    st.session_state.chat_history.append({"role": "user", "message": query})

    with st.spinner("Thinking..."):
        chunks = chunk_text(st.session_state.pdf_text)
        relevant = get_relevant_chunks(chunks, query)

        if not relevant:
            response = "❌ I couldn't find relevant information in the PDF."
        else:
            context = "\n\n".join(relevant)
            response = query_with_context(context, query)

    # Append bot response
    st.session_state.chat_history.append({"role": "bot", "message": response})

# Display full conversation like ChatGPT
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        with st.chat_message("user"):
            st.markdown(chat["message"])
    else:
        with st.chat_message("assistant"):
            st.markdown(chat["message"])
