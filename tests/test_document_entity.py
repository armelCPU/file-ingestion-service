from domain.entities.document import Document


def test_document_default_status_is_pending():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.status == "pending"


def test_document_optional_fields_default_to_none():
    doc = Document(document_id=1, workspace_id=10, user_id=42, url="https://example.com/a.pdf")
    assert doc.id is None
    assert doc.name is None
    assert doc.text is None
    assert doc.embedding is None
