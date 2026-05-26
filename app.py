import sys
# windows output console crash prevention code
sys.stdout.reconfigure(encoding='utf-8')

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# target link load aur extraction process loader
loader = PyPDFLoader("https://arxiv.org/pdf/1706.03762.pdf")
docs = loader.load()
print(f"[+] Loaded {len(docs)} pages from PDF.")

# document breaks parsing 500 limit chunk config
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
splits = text_splitter.split_documents(docs)
print(f"[+] Split into {len(splits)} chunks.")

# vector computation settings embeddings engine
embedding = HuggingFaceEmbeddings()
print("[+] Embeddings model loaded.")

# database vectors storage database init
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=embedding
)
retriever = vectorstore.as_retriever()
print("[+] Vector store created and retriever ready.")

# local gpt2 base runner loading config
pipe = pipeline(
    "text-generation",
    model="gpt2",
    max_new_tokens=200
)
llm = HuggingFacePipeline(pipeline=pipe)
print("[+] LLM loaded.")

prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the context:

{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])

# user inquiry match extraction mapping flow logic
rag_chain = (
    {"context": retriever | format_docs, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)
print("[+] RAG chain ready.\n")

print("=" * 50)
print("  RAG PDF Chatbot  (type 'exit' to quit)")
print("=" * 50)

# local shell iteration loop chat query process
while True:
    question = input("\nAsk a question: ").strip()
    if question.lower() in ("exit", "quit", "q"):
        print("Goodbye!")
        break
    if not question:
        continue

    print("\nThinking...\n")
    result = rag_chain.invoke(question)
    print(f"Answer:\n{result}")
