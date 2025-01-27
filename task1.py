# -*- coding: utf-8 -*-
"""Task1

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1f1A1WKVXy4uKtw0CVIdWLmg1-bMWlysd
"""

# Install necessary libraries
!pip install pymupdf
!pip install pdfminer.six
!pip install streamlit
!pip install pickle5
!pip install langchain
!pip install langchain-groq
!pip install faiss-cpu
!pip install huggingface_hub
!pip install -U langchain-community
!pip install pdf2image
!pip install pytesseract
# Uninstall fitz if previously installed
!pip uninstall -y fitz

# Import required libraries
from pdfminer.high_level import extract_text
import pymupdf as fitz  # Import pymupdf and alias it as fitz
import os
import pickle
import time
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from google.colab import files

# Initialize LLM
llm = ChatGroq(temperature=0, groq_api_key="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", model_name="llama-3.1-70b-versatile")

# File upload in Colab
uploaded_files = files.upload()

# Path to save FAISS index
file_path = "faiss_store_openai.pkl"

# Process PDFs after upload
def process_pdfs():
    all_text = ""
    image_dir = "extracted_images"

    # Create directory for extracted images
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    # Extract text and images from all PDFs
    for uploaded_file in uploaded_files.keys():
        # Extract text using pdfminer
        extracted_text = extract_text(uploaded_file)
        all_text += extracted_text + "\n"

        # Extract images using PyMuPDF
        doc = fitz.open(uploaded_file)  # Using fitz (which is now pymupdf)
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = os.path.join(image_dir, f"{uploaded_file}_page{page_num+1}_img{img_index+1}.{image_ext}")

                # Save the image
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
        doc.close()

    # Split text into chunks for embedding
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    text_chunks = text_splitter.split_text(all_text)

    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore_openai = FAISS.from_texts(text_chunks, embeddings)

    # Save FAISS index
    print("Embedding Vector Started Building...✅✅✅")
    time.sleep(2)

    # Save the FAISS index to a pickle file
    with open(file_path, "wb") as f:
        pickle.dump(vectorstore_openai, f)

    print("Text and images extracted. FAISS index saved.")
    print(f"Images saved in: {image_dir}")

# Run processing after file upload
process_pdfs()

# Query input
query = input("Ask a Question: ")
if query:
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            vectorstore = pickle.load(f)
            chain = RetrievalQA.from_llm(llm=llm, retriever=vectorstore.as_retriever())

        # Get response from the RAG pipeline using invoke()
        # Use invoke instead of run to avoid LangChainDeprecationWarning
        result = chain.invoke({"query": query})

        # Display the answer
        print("Answer:")
        print(result['result']) # Print the 'result' key from the output
    else:
        print(f"FAISS index file not found at {file_path}. Please ensure you run the PDF processing first.")