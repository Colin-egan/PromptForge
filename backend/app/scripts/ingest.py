"""
RAG ingestion script — loads the 21 few-shot examples into ChromaDB.

Run from the backend directory:
    python3 -m app.scripts.ingest
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

EXAMPLES_DIR = Path(__file__).resolve().parents[3] / "examples" / "few_shot"


def ingest():
    # Verify examples directory exists
    if not EXAMPLES_DIR.exists():
        logger.error(f"Examples directory not found: {EXAMPLES_DIR}")
        sys.exit(1)

    try:
        from app.rag.chroma_client import ChromaClient
        from app.rag.ingestion import CadQueryDocIngestion
        
        # Initialize ChromaDB client
        logger.info("Initializing ChromaDB client...")
        chroma_client = ChromaClient()
        chroma_client.initialize()
        
        # Initialize ingestion pipeline
        logger.info("Initializing ingestion pipeline...")
        ingestion = CadQueryDocIngestion(chroma_client)
        
        # Ingest few-shot examples
        logger.info(f"Ingesting examples from {EXAMPLES_DIR}...")
        count = ingestion.ingest_few_shot_examples(EXAMPLES_DIR)
        logger.info(f"Ingestion complete: {count} examples ingested")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    ingest()
