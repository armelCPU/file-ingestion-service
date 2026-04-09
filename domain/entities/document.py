from typing import Optional
from pydantic import BaseModel


class Document(BaseModel):
    id: Optional[int] = None
    document_id: int
    workspace_id: int
    user_id: int
    name: Optional[str] = None
    url: str
    text: Optional[str] = None
    embedding: Optional[list[float]] = None
    status: str = "pending"
