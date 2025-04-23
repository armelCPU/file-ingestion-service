from sqlalchemy import Column, Integer, String, Text, JSON, DateTime, Enum, func
import enum
from webapp.database.db import Base

# Enum class to represent Task statuses
class TaskStatus(str, enum.Enum):
    running = "running"
    completed = "completed"
    failed = "failed"

# DocumentEmbedding model to store the document metadata
class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    workspace_id = Column(Integer, nullable=False)
    document_name = Column(String, nullable=True)
    text = Column(Text, nullable=True)

# DocumentChunk model to store chunks of the document
class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, nullable=False)
    document_name = Column(String, nullable=True)
    user_id = Column(Integer, nullable=False)
    workspace_id = Column(Integer, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(JSON, nullable=False)

# IngestionTask model to store the task status and metadata
class IngestionTask(Base):
    __tablename__ = "ingestion_tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    document_id = Column(Integer, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.running, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
