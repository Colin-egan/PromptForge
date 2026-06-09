"""
Chroma Vector Database Client for PromptForge RAG Pipeline

This module provides a wrapper around ChromaDB for storing and retrieving
CadQuery documentation, design patterns, and few-shot examples.
"""

import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)


class ChromaClient:
    """
    Singleton client for ChromaDB vector database operations.
    
    Manages collections for:
    - CadQuery API documentation
    - Design patterns and examples
    - Few-shot learning examples
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize ChromaDB client with persistent storage."""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.client = None
        self.collections = {}
        self._embedding_function = None
        
    def initialize(
        self,
        persist_directory: str = "./data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ) -> None:
        """
        Initialize ChromaDB client and create collections.
        
        Args:
            persist_directory: Directory for persistent storage
            embedding_model: Sentence transformer model for embeddings
        """
        try:
            # Create persist directory if it doesn't exist
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client with persistent storage
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Set up embedding function
            self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model
            )
            
            # Create or get collections
            self._setup_collections()
            
            logger.info(f"ChromaDB initialized with persist directory: {persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    def _setup_collections(self) -> None:
        """Create or retrieve ChromaDB collections."""
        collection_configs = {
            "cadquery_docs": {
                "metadata": {"description": "CadQuery API documentation and reference"},
            },
            "design_patterns": {
                "metadata": {"description": "Curated CadQuery design patterns and examples"},
            },
            "few_shot_examples": {
                "metadata": {"description": "Few-shot learning examples for code generation"},
            }
        }
        
        for name, config in collection_configs.items():
            try:
                self.collections[name] = self.client.get_or_create_collection(
                    name=name,
                    embedding_function=self._embedding_function,
                    metadata=config["metadata"]
                )
                logger.info(f"Collection '{name}' ready")
            except Exception as e:
                logger.error(f"Failed to create collection '{name}': {e}")
                raise
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> None:
        """
        Add documents to a collection.
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            metadatas: List of metadata dicts for each document
            ids: List of unique IDs for each document
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        try:
            collection = self.collections[collection_name]
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added {len(documents)} documents to '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {e}")
            raise
    
    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query a collection for similar documents.
        
        Args:
            collection_name: Name of the collection to query
            query_texts: List of query texts
            n_results: Number of results to return per query
            where: Metadata filter conditions
            where_document: Document content filter conditions
            
        Returns:
            Query results with documents, metadatas, and distances
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        try:
            collection = self.collections[collection_name]
            results = collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                where_document=where_document
            )
            logger.info(f"Query returned {len(results['ids'][0])} results from '{collection_name}'")
            return results
        except Exception as e:
            logger.error(f"Failed to query '{collection_name}': {e}")
            raise
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get the number of documents in a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents in the collection
        """
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' not found")
        
        try:
            collection = self.collections[collection_name]
            return collection.count()
        except Exception as e:
            logger.error(f"Failed to get count for '{collection_name}': {e}")
            raise
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete a collection and all its documents.
        
        Args:
            collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Failed to delete collection '{collection_name}': {e}")
            raise
    
    def reset(self) -> None:
        """Reset the database (delete all collections). Use with caution!"""
        try:
            self.client.reset()
            self.collections = {}
            logger.warning("ChromaDB reset - all collections deleted")
        except Exception as e:
            logger.error(f"Failed to reset ChromaDB: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the ChromaDB client.
        
        Returns:
            Dictionary with health status and collection info
        """
        try:
            if self.client is None:
                return {
                    "status": "unhealthy",
                    "error": "Client not initialized"
                }
            
            collection_info = {}
            for name, collection in self.collections.items():
                collection_info[name] = {
                    "count": collection.count(),
                    "metadata": collection.metadata
                }
            
            return {
                "status": "healthy",
                "collections": collection_info,
                "total_documents": sum(info["count"] for info in collection_info.values())
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


# Singleton instance
_chroma_client = ChromaClient()


def get_chroma_client() -> ChromaClient:
    """Get the singleton ChromaDB client instance."""
    return _chroma_client

# Made with Bob
