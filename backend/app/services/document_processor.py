from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

# Initialize Embeddings model lazily
_embeddings = None

def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return _embeddings

def get_vectorstore():
    return Chroma(
        persist_directory=settings.CHROMA_PERSIST_DIR,
        embedding_function=get_embeddings()
    )

def process_document(file_path: str, document_id: int, user_id: int):
    """
    Extracts text, chunks it, generates embeddings, and stores in ChromaDB.
    """
    ext = file_path.split('.')[-1].lower()
    
    # 1. Text Extraction using LangChain Loaders
    if ext == "pdf":
        loader = PyPDFLoader(file_path)
    elif ext == "txt":
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
        
    docs = loader.load()
    
    # 2. Chunking
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(docs)
    
    # Add metadata to each chunk for filtering
    for i, chunk in enumerate(chunks):
        chunk.metadata["document_id"] = document_id
        chunk.metadata["user_id"] = user_id
        chunk.metadata["chunk_index"] = i
        
    # 3. Store in Vector DB (ChromaDB)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents=chunks)

def delete_document_from_vectorstore(document_id: int):
    """
    Deletes all chunks associated with a specific document from ChromaDB.
    """
    vectorstore = get_vectorstore()
    # ChromaDB collection supports deleting by metadata filter
    vectorstore._collection.delete(where={"document_id": document_id})
