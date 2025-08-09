import os
from dotenv import load_dotenv
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()

# API key from env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# URLs from env (split by comma)
urls = os.getenv("ENGAGE_URLS").split(",")

# Step 1: Load documents once
loader = UnstructuredURLLoader(urls=urls)
docs = loader.load()

# Step 2: Create embeddings and vector store
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=GEMINI_API_KEY
)
vectorstore = Chroma.from_documents(documents=docs, embedding=embedding_model)

# Step 3: Create retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Step 4: Setup LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.4,
    google_api_key=GEMINI_API_KEY
)

# Step 5: Prompt template
system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Keep the answer concise.\n\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

# Step 6: RAG chain
documents_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = create_retrieval_chain(retriever, documents_chain)

# Public function
def get_services_info(query: str):
    """Run the RAG chain on the given query."""
    response = rag_chain.invoke({"input": query})
    return response["answer"]
