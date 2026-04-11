import hashlib
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.documents import Document
from app.utils.pdf import parse_pdf, chunk_text
from app.agent.tools.rag import embed_chunks, store_chunks
from app.dependencies.auth import get_current_user  
from app.models.documents import DocumentChunk
from main import limiter

router = APIRouter()

@router.post("/upload")
@limiter.limit("10/minute")
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    file_bytes = await file.read()
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    existing = db.query(Document).filter_by(file_hash=file_hash, user_id=current_user.id).first()
    if existing:
        return {"message": "This document has already been uploaded.", "document_id": existing.id}
    text = parse_pdf(file_bytes)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    # Save document first → get real document_id
    
    document = Document(
        title=file.filename,
        filename=file.filename,
        user_id=current_user.id,
        file_hash=file_hash
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    store_chunks(chunks, embeddings, document_id=document.id, user_id=current_user.id, db=db)
    
    return {
        "message": "uploaded successfully",
        "document_id": document.id,
        "chunks_stored": len(chunks)
    }
    
@router.get("/documents")
async def List_documents(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    documents = db.query(Document).filter_by(user_id=current_user.id).all()
    return [{"id": doc.id, "title": doc.title, "filename": doc.filename} for doc in documents]

@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # First check if document exists and belongs to current user
    document = db.query(Document).filter_by(id=document_id, user_id=current_user.id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    
    # Delete all chunks associated with this document
    db.query(DocumentChunk).filter_by(document_id=document_id).delete()
    
    # Delete the document
    db.query(Document).filter_by(id=document_id).delete()
    db.commit()
    return {"message": "Document deleted successfully."}

