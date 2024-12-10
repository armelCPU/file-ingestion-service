from typing import Optional

from pydantic import BaseModel


class DocumentIngestionIn(BaseModel):
    document_id: int
    workspace_id: int
    document_url: str
    user_id: int
    document_name: Optional[str]
