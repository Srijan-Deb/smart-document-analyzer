import os
import sys

# Setup paths
sys.path.insert(0, os.path.abspath("."))
from app.database.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.document import Document
from app.services.document_processor import process_document, delete_document_from_vectorstore
import traceback

def test_delete():
    # Setup test DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # 1. Create a user
    import uuid
    from app.core.security import get_password_hash
    user = db.query(User).filter(User.username == "test_delete").first()
    if not user:
        user = User(username="test_delete", email=f"test_{uuid.uuid4()}@test.com", hashed_password=get_password_hash("password123"))
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # 2. Create dummy pdf file
    file_path = "uploaded_docs/test_delete.pdf"
    from reportlab.pdfgen import canvas
    c = canvas.Canvas(file_path)
    c.drawString(100, 100, "This is a dummy PDF file for deletion testing.")
    c.save()
        
    # 3. Create document record
    doc = Document(file_name="test_delete.pdf", file_path=file_path, user_id=user.id)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 4. Process document (adds to vectorstore)
    try:
        process_document(file_path, doc.id, user.id)
        print("Processed successfully")
    except Exception as e:
        print(f"Process failed: {e}")
        
    # 5. Delete document
    print("Attempting to delete...")
    # simulate the deletion route
    db_doc = db.query(Document).filter(Document.id == doc.id).first()
    
    if os.path.exists(db_doc.file_path):
        try:
            os.remove(db_doc.file_path)
            print("File deleted from OS")
        except Exception as e:
            print(f"Failed to delete file from OS: {e}")
            traceback.print_exc()
            
    try:
        delete_document_from_vectorstore(doc.id)
        print("Deleted from vectorstore")
    except Exception as e:
        print(f"Failed to delete from vectorstore: {e}")
        traceback.print_exc()
        
    db.delete(db_doc)
    db.commit()
    print("Deleted from DB")

if __name__ == "__main__":
    test_delete()
