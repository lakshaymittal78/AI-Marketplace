
from sqlalchemy import Column, ForeignKey, Integer, String, Text, UniqueConstraint, UniqueConstraint
from app.database import Base
from sqlalchemy import DateTime
from pgvector.sqlalchemy import Vector
from datetime import datetime

class Document(Base):
    __tablename__ = "documents"
    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, index=True)
    content    = Column(Text)
    user_id    = Column(Integer, ForeignKey("users.id"))
    filename   = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_hash =  Column(String, index=True)
    
    __table_args__ = (
        UniqueConstraint("file_hash","user_id",name="uq_document_hash_per_user"),
    )

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id          = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    user_id     = Column(Integer, ForeignKey("users.id"))
    chunk_text  = Column(Text)
    embedding   = Column(Vector(384))
    created_at  = Column(DateTime, default=datetime.utcnow)
    
