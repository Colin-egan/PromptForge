"""
Documentation and Example Ingestion for PromptForge RAG Pipeline

This module handles:
- Scraping and chunking CadQuery documentation
- Processing design patterns and examples
- Generating embeddings and storing in ChromaDB
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class DocumentChunker:
    """
    Intelligent document chunking for CadQuery documentation.
    
    Chunks documents by semantic units (functions, classes, sections)
    while maintaining context and relationships.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize the document chunker.
        
        Args:
            chunk_size: Target size for each chunk in characters
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_by_headers(self, text: str, source: str) -> List[Dict[str, Any]]:
        """
        Chunk documentation by markdown headers.
        
        Args:
            text: Document text to chunk
            source: Source identifier (URL or file path)
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        chunks = []
        
        # Split by headers (## or ###)
        sections = re.split(r'\n(#{2,3})\s+(.+?)\n', text)
        
        current_section = ""
        current_header = ""
        
        for i in range(0, len(sections), 3):
            if i == 0:
                # Content before first header
                current_section = sections[i].strip()
                continue
            
            if i + 2 < len(sections):
                header_level = sections[i]
                header_text = sections[i + 1]
                content = sections[i + 2].strip()
                
                # Create chunk for previous section if it exists
                if current_section:
                    chunk_id = self._generate_chunk_id(source, current_header)
                    chunks.append({
                        "text": current_section,
                        "metadata": {
                            "source": source,
                            "header": current_header,
                            "type": "documentation",
                            "chunk_id": chunk_id
                        }
                    })
                
                # Start new section
                current_header = header_text
                current_section = f"{header_level} {header_text}\n\n{content}"
        
        # Add final section
        if current_section:
            chunk_id = self._generate_chunk_id(source, current_header)
            chunks.append({
                "text": current_section,
                "metadata": {
                    "source": source,
                    "header": current_header,
                    "type": "documentation",
                    "chunk_id": chunk_id
                }
            })
        
        return chunks
    
    def chunk_code_example(self, code: str, description: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a chunk for a code example.
        
        Args:
            code: CadQuery code
            description: Description of what the code does
            metadata: Additional metadata (category, parameters, etc.)
            
        Returns:
            Chunk dictionary with combined text and metadata
        """
        # Combine description and code for better semantic search
        combined_text = f"{description}\n\n```python\n{code}\n```"
        
        chunk_id = self._generate_chunk_id(
            metadata.get("source", "example"),
            description[:50]
        )
        
        return {
            "text": combined_text,
            "metadata": {
                **metadata,
                "type": "code_example",
                "chunk_id": chunk_id,
                "code": code,
                "description": description
            }
        }
    
    def _generate_chunk_id(self, source: str, identifier: str) -> str:
        """Generate a unique ID for a chunk."""
        content = f"{source}:{identifier}"
        return hashlib.md5(content.encode()).hexdigest()


class CadQueryDocIngestion:
    """
    Handles ingestion of CadQuery documentation and examples.
    """
    
    def __init__(self, chroma_client):
        """
        Initialize the ingestion pipeline.
        
        Args:
            chroma_client: ChromaDB client instance
        """
        self.chroma_client = chroma_client
        self.chunker = DocumentChunker()
    
    def ingest_documentation(self, docs_dir: Path) -> int:
        """
        Ingest CadQuery documentation from a directory.
        
        Args:
            docs_dir: Path to directory containing markdown docs
            
        Returns:
            Number of chunks ingested
        """
        if not docs_dir.exists():
            logger.warning(f"Documentation directory not found: {docs_dir}")
            return 0
        
        chunks = []
        
        # Process all markdown files
        for md_file in docs_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Chunk the document
                file_chunks = self.chunker.chunk_by_headers(
                    content,
                    source=str(md_file.relative_to(docs_dir))
                )
                chunks.extend(file_chunks)
                
                logger.info(f"Processed {md_file.name}: {len(file_chunks)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to process {md_file}: {e}")
        
        # Add to ChromaDB
        if chunks:
            self._add_chunks_to_db(chunks, "cadquery_docs")
        
        return len(chunks)
    
    def ingest_design_patterns(self, patterns_dir: Path) -> int:
        """
        Ingest design patterns from JSON files.
        
        Args:
            patterns_dir: Path to directory containing pattern JSON files
            
        Returns:
            Number of patterns ingested
        """
        if not patterns_dir.exists():
            logger.warning(f"Patterns directory not found: {patterns_dir}")
            return 0
        
        chunks = []
        
        # Process all JSON files
        for json_file in patterns_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    pattern = json.load(f)
                
                # Create chunk from pattern
                chunk = self.chunker.chunk_code_example(
                    code=pattern.get("code", ""),
                    description=pattern.get("description", ""),
                    metadata={
                        "source": str(json_file.relative_to(patterns_dir)),
                        "category": pattern.get("category", "unknown"),
                        "parameters": pattern.get("parameters", []),
                        "print_notes": pattern.get("print_notes", ""),
                        "tags": pattern.get("tags", [])
                    }
                )
                chunks.append(chunk)
                
                logger.info(f"Processed pattern: {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {json_file}: {e}")
        
        # Add to ChromaDB
        if chunks:
            self._add_chunks_to_db(chunks, "design_patterns")
        
        return len(chunks)
    
    def ingest_few_shot_examples(self, examples_dir: Path) -> int:
        """
        Ingest few-shot learning examples.
        
        Args:
            examples_dir: Path to directory containing example JSON files
            
        Returns:
            Number of examples ingested
        """
        if not examples_dir.exists():
            logger.warning(f"Examples directory not found: {examples_dir}")
            return 0
        
        chunks = []
        
        # Process all JSON files
        for json_file in examples_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    example = json.load(f)
                
                # Create chunk from example
                chunk = self.chunker.chunk_code_example(
                    code=example.get("code", ""),
                    description=example.get("description", ""),
                    metadata={
                        "source": str(json_file.relative_to(examples_dir)),
                        "category": example.get("category", "unknown"),
                        "parameters": example.get("parameters", []),
                        "print_notes": example.get("print_notes", ""),
                        "difficulty": example.get("difficulty", "medium"),
                        "validated": example.get("validated", False)
                    }
                )
                chunks.append(chunk)
                
                logger.info(f"Processed example: {json_file.name}")
                
            except Exception as e:
                logger.error(f"Failed to process {json_file}: {e}")
        
        # Add to ChromaDB
        if chunks:
            self._add_chunks_to_db(chunks, "few_shot_examples")
        
        return len(chunks)
    
    def _add_chunks_to_db(self, chunks: List[Dict[str, Any]], collection_name: str) -> None:
        """
        Add chunks to ChromaDB collection.
        
        Args:
            chunks: List of chunk dictionaries
            collection_name: Name of the collection to add to
        """
        try:
            documents = [chunk["text"] for chunk in chunks]
            metadatas = [chunk["metadata"] for chunk in chunks]
            ids = [chunk["metadata"]["chunk_id"] for chunk in chunks]
            
            self.chroma_client.add_documents(
                collection_name=collection_name,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to '{collection_name}'")
            
        except Exception as e:
            logger.error(f"Failed to add chunks to '{collection_name}': {e}")
            raise
    
    def get_ingestion_stats(self) -> Dict[str, Any]:
        """
        Get statistics about ingested data.
        
        Returns:
            Dictionary with counts for each collection
        """
        stats = {}
        
        for collection_name in ["cadquery_docs", "design_patterns", "few_shot_examples"]:
            try:
                count = self.chroma_client.get_collection_count(collection_name)
                stats[collection_name] = count
            except Exception as e:
                logger.error(f"Failed to get count for '{collection_name}': {e}")
                stats[collection_name] = 0
        
        stats["total"] = sum(stats.values())
        return stats


def initialize_knowledge_base(chroma_client, data_dir: Path) -> Dict[str, int]:
    """
    Initialize the knowledge base with all available data.
    
    Args:
        chroma_client: ChromaDB client instance
        data_dir: Root data directory containing docs, patterns, and examples
        
    Returns:
        Dictionary with ingestion counts for each data type
    """
    ingestion = CadQueryDocIngestion(chroma_client)
    
    results = {
        "documentation": 0,
        "design_patterns": 0,
        "few_shot_examples": 0
    }
    
    # Ingest documentation
    docs_dir = data_dir / "cadquery_docs"
    if docs_dir.exists():
        results["documentation"] = ingestion.ingest_documentation(docs_dir)
    
    # Ingest design patterns
    patterns_dir = data_dir / "patterns"
    if patterns_dir.exists():
        results["design_patterns"] = ingestion.ingest_design_patterns(patterns_dir)
    
    # Ingest few-shot examples
    examples_dir = data_dir / "few_shot"
    if examples_dir.exists():
        results["few_shot_examples"] = ingestion.ingest_few_shot_examples(examples_dir)
    
    results["total"] = sum(results.values())
    
    logger.info(f"Knowledge base initialized: {results}")
    return results

# Made with Bob
