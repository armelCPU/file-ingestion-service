import logging
from webapp.database.db import Base, engine
from webapp.database.models import DocumentEmbedding, DocumentChunk, IngestionTask

logging.info("Creating database tables...")
Base.metadata.create_all(bind=engine)
logging.info("Done.")