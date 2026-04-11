from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models.documents import DocumentChunk

model = SentenceTransformer("all-MiniLM-L6-v2")

# ── 1. Embed ──────────────────────────────────────────────
def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return model.encode(chunks).tolist()   # batch encode ✅

# ── 2. Store ──────────────────────────────────────────────
def store_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    document_id: int,
    user_id: int,
    db: Session
) -> None:
    for chunk, embedding in zip(chunks, embeddings):
        new_chunk = DocumentChunk(
            document_id=document_id,
            user_id=user_id,
            chunk_text=chunk,
            embedding=embedding
        )
        db.add(new_chunk)
    db.commit()   # commit once after all inserts ✅

# ── 3. Retrieve ───────────────────────────────────────────
def retrieve_relevant_chunks(
    query: str,
    user_id: int,
    db: Session,
    top_k: int = 5
) -> list[str]:
    query_embedding = model.encode(query).tolist()
    
    results = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.user_id == user_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )
    return [r.chunk_text for r in results]