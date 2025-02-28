import os
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader

# Configure Google Gemini API key
genai.configure(api_key="AIzaSyB121TcLtRHJjHECYdHzG8Ze_8KzpC3BKQ")

# Function to read multiple PDFs and extract text
def read_pdfs(files):
    """Reads text from multiple PDF files and combines them."""
    text = ""
    for file in files:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"  # Separate PDFs with newlines
    return text

# Function to query the Gemini LLM with preloaded context
def query_with_cag(context: str, query: str) -> str:
    """
    Query the Gemini LLM with preloaded context using Cache-Augmented Generation.
    """
    prompt = f"Context:\n{context}\n\nQuery: {query}\nAnswer:"
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

# Streamlit app interface
st.title("RoboDrive - by Desu Deekshitha")
st.header("Upload PDFs and Ask Your Query")

# Step 1: Ask the user to upload multiple PDF files
uploaded_files = st.file_uploader("Upload one or more PDFs", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Step 2: Extract text from the uploaded PDFs
    pdf_text = read_pdfs(uploaded_files)

    # Step 3: Show a preview of the content of the PDFs (optional)
    st.text_area("PDF Content Preview", value=pdf_text[:1000], height=150)

    # Step 4: Ask the user to enter a query based on the uploaded PDFs
    query = st.text_input("Ask a question based on the content of the PDFs:")

    if query:
        # Step 5: Get the answer from Gemini LLM with the context of the PDFs
        response = query_with_cag(pdf_text, query)
        st.write("Answer:", response)
