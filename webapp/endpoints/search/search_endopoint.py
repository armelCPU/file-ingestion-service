from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from fastapi.openapi.models import APIKey
from webapp.database.db import SessionLocal
from webapp.database.models import DocumentChunk
from webapp.auth_middleware import check_auth_token
from webapp.services.mock_openai import mock_embedding
from settings import settings
import openai
import numpy as np
import logging

router = APIRouter()

class SearchQuery(BaseModel):
    question: str
    user_id: int

def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@router.post("/search", tags=["Search"], summary="Semantic search of documents")
def search_documents(query: SearchQuery, api_key: APIKey = Depends(check_auth_token)):
    """
    Perform a semantic search over the documents using embeddings.
    """
    try:
        logging.info(f"Performing search for question: {query.question}")

        # Retrieve the embedding for the query, either from mock or OpenAI
        if settings.MOCK_MODE:
            logging.info("Using mock embeddings")
            embedding = mock_embedding(query.question)
        else:
            openai.api_key = settings.OPENAI_API_KEY
            logging.info("Using OpenAI embeddings")
            embedding = openai.Embedding.create(
                input=query.question,
                model="text-embedding-ada-002"
            )["data"][0]["embedding"]

        # Query the database for the document chunks
        db = SessionLocal()
        chunks = db.query(DocumentChunk).filter(DocumentChunk.user_id == query.user_id).all()

        if not chunks:
            raise HTTPException(status_code=404, detail="Aucun chunk trouvé")

        # Calculate cosine similarity for each chunk
        scored_chunks = []
        for chunk in chunks:
            score = cosine_similarity(embedding, chunk.embedding)
            scored_chunks.append((score, chunk))

        # Get the top 5 most relevant chunks
        top_chunks = sorted(scored_chunks, key=lambda x: x[0], reverse=True)[:5]

        return [
            {
                "document_id": chunk.document_id,
                "document_name": chunk.document_name,
                "chunk_index": chunk.chunk_index,
                "score": round(score, 4),
                "excerpt": smart_excerpt(chunk.text),
                "mock_used": settings.MOCK_MODE
            }
            for score, chunk in top_chunks
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def smart_excerpt(text, max_len=500):
    """
    Create an excerpt from the document text.
    It cuts off at the last sentence if possible.
    """
    excerpt = text[:max_len]
    last_dot = excerpt.rfind(".")
    if last_dot != -1 and last_dot > 80:
        return excerpt[:last_dot + 1]  # coupe à la dernière phrase complète
    return excerpt + "..."
