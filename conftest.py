# conftest.py
import sys
import os
import pytest
from dotenv import load_dotenv
load_dotenv("test.env")
sys.path.insert(0, os.path.dirname(__file__))
def clean_db():
    from app.database import engine
    from app.models.user import User
    from app.models.documents import Document, DocumentChunk
    from sqlalchemy.orm import Session
    
    yield
    with Session(engine) as db:
        db.query(DocumentChunk).delete()
        db.query(Document).delete()
        db.query(User).delete()
        db.commit()