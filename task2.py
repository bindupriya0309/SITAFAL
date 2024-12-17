# -*- coding: utf-8 -*-
"""Task2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1xCY0jH1Rn4KzxJMQFe-4uk4QucLsN3jG
"""

!pip install -U langchain-community

!pip install fitz

!pip install pytesseract

import os
import pickle
import time
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

# Initialize LLM
llm = ChatGroq(temperature=0, groq_api_key="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", model_name="llama-3.1-70b-versatile")

file_path = "faiss_store_openai.pkl"

# Function to scrape content from a website
def scrape_website(url):
    try:
        # Send a request to the website
        response = requests.get(url)

        if response.status_code == 200:
            # Parse the HTML content of the page
            soup = BeautifulSoup(response.content, 'html.parser')
            # Extract text from all paragraph tags (you can adjust this as needed)
            paragraphs = soup.find_all('p')
            text = ' '.join([para.get_text() for para in paragraphs])
            return text
        else:
            print(f"Failed to retrieve the webpage: {url} with status code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# Process websites after input
def process_websites(urls):
    all_text = ""

    # Scrape text from all websites
    for url in urls:
        print(f"Processing website: {url}")
        extracted_text = scrape_website(url)
        all_text += extracted_text + "\n"

    if not all_text:
        print("No text was extracted from the websites.")
        return

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_text(all_text)

    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore_openai = FAISS.from_texts(text_chunks, embeddings)

    # Save FAISS index
    print("Embedding Vector Started Building...✅✅✅")
    time.sleep(2)

    # Save the FAISS index to a pickle file
    try:
        with open(file_path, "wb") as f:
            pickle.dump(vectorstore_openai, f)
        print("Text extracted and FAISS index saved.")
    except Exception as e:
        print(f"Error saving FAISS index: {e}")

# User input for URLs
urls_input = input("Enter the website URLs (comma-separated): ")
urls = [url.strip() for url in urls_input.split(',')]

if not urls:
    print("No URLs provided.")
else:
    # Run processing after URL input
    process_websites(urls)

    # Query input
    query = input("Ask a Question: ")
    if query:
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    vectorstore = pickle.load(f)
                    chain = RetrievalQA.from_llm(llm=llm, retriever=vectorstore.as_retriever())

                # Get response
                result = chain.run(query)

                # Display answer
                print("Answer:")
                print(result)
            except Exception as e:
                print(f"Error processing query: {e}")
        else:
            print(f"FAISS index file not found at {file_path}. Please ensure you run the scraping process first.")