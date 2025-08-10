# from dotenv import load_dotenv
# import os
# from langchain_community.document_loaders import UnstructuredURLLoader
# from langchain_chroma import Chroma
# from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
# from langchain.chains import create_retrieval_chain
# from langchain.chains.combine_documents import create_stuff_documents_chain
# from langchain_core.prompts import ChatPromptTemplate

# # Load .env file
# load_dotenv()

# # ----------------------
# # API key from .env
# # ----------------------
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# # Step 1: Load documents once (so we don't re-embed every request)
# urls = [
#     "https://www.engagepeo.com/our-services",
#     "https://www.engagepeo.com/about-us",
#     "https://www.engagepeo.com/engage-brokers",
#     "https://www.engagepeo.com/blog-newsroom",
#     "https://www.engagepeo.com/contact-us",
#     "https://www.linkedin.com/company/engage-peo/"
# ]
# loader = UnstructuredURLLoader(urls=urls)
# docs = loader.load()

# # Step 2: Create embeddings and vector store
# embedding_model = GoogleGenerativeAIEmbeddings(
#     model="models/embedding-001",
#     google_api_key=GEMINI_API_KEY
# )
# vectorstore = Chroma.from_documents(documents=docs, embedding=embedding_model)

# # Step 3: Create retriever
# retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# # Step 4: Setup LLM
# llm = ChatGoogleGenerativeAI(
#     model="gemini-1.5-flash",
#     temperature=0.4,
#     google_api_key=GEMINI_API_KEY
# )

# # Step 5: Prompt template
# system_prompt = (
#     "You are an assistant for question-answering tasks. "
#     "Use the following pieces of retrieved context to answer "
#     "the question. If you don't know the answer, say that you "
#     "don't know. Keep the answer concise.\n\n"
#     "{context}"
# )

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", system_prompt),
#         ("human", "{input}"),
#     ]
# )

# # Step 6: RAG chain (prebuilt at import time)
# documents_chain = create_stuff_documents_chain(llm, prompt)
# rag_chain = create_retrieval_chain(retriever, documents_chain)

# # ----------------------
# # Public function to call in views
# # ----------------------
# def get_services_info(query: str):
#     """Run the RAG chain on the given query."""
#     response = rag_chain.invoke({"input": query})
#     return response["answer"]
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# ----------------------
# Step 1: Define Engage PEO endpoint URLs
# ----------------------
urls = [
    "https://www.engagepeo.com/our-services",
    "https://www.engagepeo.com/about-us",
    "https://www.engagepeo.com/engage-brokers",
    "https://www.engagepeo.com/blog-newsroom",
    "https://www.engagepeo.com/contact-us",
    # LinkedIn page won't have service info, but you can keep it if needed
    "https://www.linkedin.com/company/engage-peo/",
    "https://www.engagepeo.com/news/press-releases/welcome-matthew-cochran"
]

# ----------------------
# Step 2: Load documents from URLs (only once)
# ----------------------
print("Loading Engage PEO pages...")
loader = UnstructuredURLLoader(urls=urls)
docs = loader.load()
print(f"Loaded {len(docs)} documents.")

# ----------------------
# Step 3: Create embeddings and vector store
# ----------------------
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    collection_name="engage_peo_faq"
)

# ----------------------
# Step 4: Create retriever (fetch multiple relevant chunks)
# ----------------------
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # fetch more chunks to cover multi-endpoint answers
)

# ----------------------
# Step 5: Setup LLM
# ----------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.4,
    google_api_key=GEMINI_API_KEY
)

# ----------------------
# Step 6: System prompt (Production-grade, hallucination-resistant)
# ----------------------
system_prompt = (
    "You are a highly reliable question-answering assistant for Engage PEO's FAQ chatbot. "
    "Answer questions based ONLY on the retrieved context from Engage PEO's verified website content. "
    "Do not use outside knowledge, assumptions, or fabricated information. "
    "If the answer is not explicitly available in the context, respond with exactly: 'I don't know.'\n\n"
    "Rules:\n"
    "1. Use concise, user-friendly language.\n"
    "2. If the question matches multiple pieces of context, combine relevant facts without repetition.\n"
    "3. If the question is ambiguous, ask the user to clarify.\n"
    "4. Never invent names, numbers, pricing, or dates not stated in the context.\n"
    "5. If contact info is relevant, include it.\n"
    "6. If unrelated to Engage PEO, respond with 'I don't know.'\n"
    "7. Maintain a professional, helpful tone at all times.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# ----------------------
# Step 7: Create RAG chain
# ----------------------
documents_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, documents_chain)

# ----------------------
# Step 8: Public function for use in chatbot view
# ----------------------
def get_services_info(query: str):
    """Run the RAG chain on the given query."""
    response = rag_chain.invoke({"input": query})
    return response["answer"]


