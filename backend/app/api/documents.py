from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session


import os
import uuid

from app.database.database import get_db
from app.models.user import User
from app.models.document import Document
from app.core.security import get_current_user
from app.services.document_processor import process_document, delete_document_from_vectorstore

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    filename_lower = file.filename.lower()
    if not (filename_lower.endswith('.pdf') or filename_lower.endswith('.txt')):
        raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
    
    file_ext = filename_lower.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    # Create DB record
    db_doc = Document(
        file_name=file.filename,
        file_path=file_path,
        user_id=current_user.id
    )
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # Process the document for RAG (extraction, chunking, embedding)
    try:
        process_document(file_path, db_doc.id, current_user.id)
    except Exception as e:
        print(f"Error processing document: {e}")
        # Clean up database record and file on failure
        db.delete(db_doc)
        db.commit()
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

    return {"message": "Document uploaded and processed successfully", "document_id": db_doc.id}

@router.get("/")
def get_user_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    docs = db.query(Document).filter(Document.user_id == current_user.id).all()
    return [{"id": d.id, "file_name": d.file_name, "upload_date": d.upload_date} for d in docs]

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_doc = db.query(Document).filter(Document.id == document_id, Document.user_id == current_user.id).first()
    if not db_doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Delete from filesystem
    if os.path.exists(db_doc.file_path):
        try:
            import gc
            gc.collect() # Force garbage collection to release file handles from PyPDFLoader
            os.remove(db_doc.file_path)
        except Exception as e:
            print(f"Failed to delete file {db_doc.file_path}: {e}")
            
    # Delete from ChromaDB
    try:
        delete_document_from_vectorstore(document_id)
    except Exception as e:
        print(f"Failed to delete document from vectorstore: {e}")
        
    # Delete from database
    db.delete(db_doc)
    db.commit()
    
    return {"message": "Document deleted successfully"}
