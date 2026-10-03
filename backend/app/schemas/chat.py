from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    query: str
    document_ids: Optional[List[int]] = None # Optional: Filter by specific docs

class SourceChunk(BaseModel):
    content: str
    metadata: dict

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
