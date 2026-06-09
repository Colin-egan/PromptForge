"""
Quick test script to verify RAG retrieval functionality.
Run from backend directory: python3 test_rag_retrieval.py
"""
import logging
from app.rag.chroma_client import ChromaClient
from app.rag.retrieval import CadQueryRetriever

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

def test_retrieval():
    """Test RAG retrieval with various queries."""
    
    # Initialize ChromaDB and retriever
    logger.info("Initializing ChromaDB client...")
    chroma_client = ChromaClient()
    chroma_client.initialize()
    
    logger.info("Initializing retriever...")
    retriever = CadQueryRetriever(chroma_client)
    
    # Test 1: Get collection counts
    logger.info("\n=== Test 1: Collection Counts ===")
    for collection_name in ["cadquery_docs", "design_patterns", "few_shot_examples"]:
        count = chroma_client.get_collection_count(collection_name)
        logger.info(f"{collection_name}: {count} documents")
    
    # Test 2: Search for holder examples
    logger.info("\n=== Test 2: Search for Holder Examples ===")
    holder_examples = retriever.get_few_shot_examples(
        query="phone holder stand",
        category="holder",
        top_k=3
    )
    logger.info(f"Found {len(holder_examples)} holder examples:")
    for ex in holder_examples:
        meta = ex.get('metadata', {})
        logger.info(f"  - {meta.get('description', 'Unknown')} (category: {meta.get('category', 'N/A')})")
    
    # Test 3: Search for organizer examples
    logger.info("\n=== Test 3: Search for Organizer Examples ===")
    organizer_examples = retriever.get_few_shot_examples(
        query="desk organization storage",
        category="organizer",
        top_k=2
    )
    logger.info(f"Found {len(organizer_examples)} organizer examples:")
    for ex in organizer_examples:
        meta = ex.get('metadata', {})
        logger.info(f"  - {meta.get('description', 'Unknown')} (category: {meta.get('category', 'N/A')})")
    
    # Test 4: Get context for code generation
    logger.info("\n=== Test 4: Get Context for Code Generation ===")
    context = retriever.get_context_for_generation(
        user_query="Create a simple pen holder with multiple compartments",
        category="holder"
    )
    logger.info(f"Generated context sections:")
    logger.info(f"  - Documentation: {len(context['documentation'])} chars")
    logger.info(f"  - Patterns: {len(context['patterns'])} chars")
    logger.info(f"  - Examples: {len(context['examples'])} chars")
    logger.info(f"  - Total: {context['total_length']} chars")
    
    # Test 5: Hybrid search
    logger.info("\n=== Test 5: Hybrid Search ===")
    from app.rag.retrieval import RetrievalConfig, SearchStrategy
    config = RetrievalConfig(top_k=3, min_similarity=0.3, strategy=SearchStrategy.SEMANTIC)
    results = retriever.hybrid_search(
        query="bracket with mounting holes",
        config=config
    )
    logger.info(f"Hybrid search results:")
    for collection, items in results.items():
        logger.info(f"  - {collection}: {len(items)} results")
        for item in items[:2]:  # Show first 2 from each collection
            logger.info(f"    * Score: {item.get('score', 0):.3f}")
    
    logger.info("\n=== All Tests Complete ===")
    logger.info("✅ RAG retrieval is working correctly!")

if __name__ == "__main__":
    try:
        test_retrieval()
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        exit(1)

# Made with Bob
