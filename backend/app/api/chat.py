from fastapi import APIRouter, Depends, HTTPException


from app.models.user import User
from app.core.security import get_current_user
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.document_processor import get_vectorstore
from app.core.config import settings

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

router = APIRouter()

# Initialize Ollama LLM lazily
_llm = None

def get_llm():
    global _llm
    if _llm is None:
        _llm = OllamaLLM(model=settings.OLLAMA_MODEL, base_url=settings.OLLAMA_BASE_URL)
    return _llm

prompt_template = """
You are an intelligent assistant for a document analysis system. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer based on the context, just say that you don't know. 
Do not hallucinate or make up information.

Context:
{context}

Question:
{input}

Answer:
"""
prompt = PromptTemplate.from_template(prompt_template)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

import json
from fastapi.responses import StreamingResponse

@router.post("/")
async def chat_with_documents(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    vectorstore = get_vectorstore()
    
    search_kwargs = {"filter": {"user_id": current_user.id}}
    
    if request.document_ids:
        search_kwargs["filter"] = {
            "$and": [
                {"user_id": current_user.id},
                {"document_id": {"$in": request.document_ids}}
            ]
        }
        
    retriever = vectorstore.as_retriever(search_kwargs=search_kwargs)
    
    docs = []
    try:
        docs = await retriever.ainvoke(request.query)
        context = format_docs(docs)
        generation_chain = prompt | get_llm() | StrOutputParser()
        
        sources = [
            {"content": doc.page_content, "metadata": doc.metadata} 
            for doc in docs
        ]
        
        async def generate():
            # First yield the sources
            yield f"data: {json.dumps({'sources': sources})}\n\n"
            
            try:
                # Stream the answer
                async for chunk in generation_chain.astream({
                    "context": context,
                    "input": request.query
                }):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            except Exception as e:
                err_str = str(e)
                if "Max retries exceeded" in err_str or "Failed to establish a new connection" in err_str or "actively refused it" in err_str:
                    error_msg = f"[OLLAMA OFFLINE] Unable to connect to Ollama at {settings.OLLAMA_BASE_URL}. Please ensure Ollama is installed and running (`ollama serve`)."
                    yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                elif "not found" in err_str.lower() and "model" in err_str.lower():
                    error_msg = f"[MODEL NOT FOUND] The model '{settings.OLLAMA_MODEL}' is not pulled in Ollama. Please open your terminal and run: ollama pull {settings.OLLAMA_MODEL}"
                    yield f"data: {json.dumps({'chunk': error_msg})}\n\n"
                else:
                    yield f"data: {json.dumps({'chunk': f'[ERROR] {err_str}'})}\n\n"
                    
            yield "data: [DONE]\n\n"
            
        return StreamingResponse(generate(), media_type="text/event-stream")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
