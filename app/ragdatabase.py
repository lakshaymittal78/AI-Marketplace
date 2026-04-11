from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pgvector.sqlalchemy import Vector
from sqlalchemy import text
from datetime import datetime
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    username        = Column(String, unique=True, index=True)
    email           = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Document(Base):
    __tablename__ = "documents"
    id         = Column(Integer, primary_key=True, index=True)
    title      = Column(String, index=True)
    content    = Column(Text)
    user_id    = Column(Integer, ForeignKey("users.id"))
    filename   = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    file_hash = Column(String, index=True)
    
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
    
def init_db():
    with engine.connect() as conn:
         conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
         conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        