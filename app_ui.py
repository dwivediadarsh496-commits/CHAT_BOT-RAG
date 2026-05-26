from flask import Flask, render_template, request, jsonify
import sys
import os

# windows console errors se bachne ke liye encoding fix ki
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

print("[*] Initializing RAG pipeline... This may take a moment.")

# pdf document fetch karke load kar rahe hain
loader = PyPDFLoader("https://arxiv.org/pdf/1706.03762.pdf")
docs = loader.load()
print(f"[+] Loaded {len(docs)} pages from PDF.")

# document ko chote text chunks me split kiya
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
splits = text_splitter.split_documents(docs)
print(f"[+] Split into {len(splits)} chunks.")

# embeddings generate karke db setup kiya
embedding = HuggingFaceEmbeddings()
print("[+] Embeddings model loaded.")

vectorstore = Chroma.from_documents(documents=splits, embedding=embedding)
retriever = vectorstore.as_retriever()
print("[+] Vector store created.")

# gpt-2 model loading step local generation ke liye
pipe = pipeline("text-generation", model="gpt2", max_new_tokens=200)
llm = HuggingFacePipeline(pipeline=pipe)
print("[+] LLM loaded.")

prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the context:

{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

# query retrieve aur generator model integration chain
rag_chain = (
    {"context": retriever | format_docs, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)
print("[+] RAG pipeline ready.")

# template load karne ka normal route endpoint
@app.route("/")
def index():
    return render_template("index.html")

# post request check karke user chat responding route
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    try:
        result = rag_chain.invoke(question)
        return jsonify({"answer": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=False)
