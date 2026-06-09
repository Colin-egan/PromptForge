"""
Retrieval Module for PromptForge RAG Pipeline

This module handles:
- Semantic search across CadQuery documentation
- Hybrid search (keyword + semantic)
- Context-aware retrieval for code generation
- Few-shot example selection
"""

import logging
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class SearchStrategy(str, Enum):
    """Search strategies for retrieval."""
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    KEYWORD = "keyword"


class RetrievalConfig:
    """Configuration for retrieval operations."""
    
    def __init__(
        self,
        top_k: int = 5,
        min_similarity: float = 0.5,
        strategy: SearchStrategy = SearchStrategy.SEMANTIC,
        include_code: bool = True,
        include_docs: bool = True
    ):
        """
        Initialize retrieval configuration.
        
        Args:
            top_k: Number of results to retrieve
            min_similarity: Minimum similarity threshold (0-1)
            strategy: Search strategy to use
            include_code: Include code examples in results
            include_docs: Include documentation in results
        """
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.strategy = strategy
        self.include_code = include_code
        self.include_docs = include_docs


class CadQueryRetriever:
    """
    Retrieval system for CadQuery knowledge base.
    
    Provides semantic search, hybrid search, and context-aware retrieval
    for code generation and documentation lookup.
    """
    
    def __init__(self, chroma_client):
        """
        Initialize the retriever.
        
        Args:
            chroma_client: ChromaDB client instance
        """
        self.chroma_client = chroma_client
    
    def search_documentation(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search CadQuery documentation.
        
        Args:
            query: Search query
            top_k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of relevant documentation chunks
        """
        try:
            # Build metadata filter
            where = None
            if category:
                where = {
                    "$and": [
                        {"type": "documentation"},
                        {"category": category}
                    ]
                }
            else:
                where = {"type": "documentation"}
            
            # Query ChromaDB
            results = self.chroma_client.query(
                collection_name="cadquery_docs",
                query_texts=[query],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = self._format_results(results)
            
            logger.info(f"Documentation search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Documentation search failed: {e}")
            return []
    
    def search_design_patterns(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search design patterns and examples.
        
        Args:
            query: Search query describing desired pattern
            top_k: Number of results to return
            category: Optional category filter (holder, bracket, etc.)
            tags: Optional list of tags to filter by
            
        Returns:
            List of relevant design patterns with code
        """
        try:
            # Build metadata filter
            where = None
            if category:
                where = {"category": category}
            
            # Query ChromaDB
            results = self.chroma_client.query(
                collection_name="design_patterns",
                query_texts=[query],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = self._format_results(results)
            
            # Filter by tags if provided
            if tags:
                formatted_results = [
                    r for r in formatted_results
                    if any(tag in r.get("metadata", {}).get("tags", []) for tag in tags)
                ]
            
            logger.info(f"Pattern search returned {len(formatted_results)} results")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Pattern search failed: {e}")
            return []
    
    def get_few_shot_examples(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve few-shot examples for code generation.
        
        Args:
            query: Description of desired functionality
            top_k: Number of examples to return
            category: Optional category filter
            difficulty: Optional difficulty filter (easy, medium, hard)
            
        Returns:
            List of relevant few-shot examples
        """
        try:
            # Build metadata filter with proper ChromaDB syntax
            conditions = [{"validated": True}]  # Only return validated examples
            if category:
                conditions.append({"category": category})
            if difficulty:
                conditions.append({"difficulty": difficulty})
            
            # Use $and operator if multiple conditions
            where = {"$and": conditions} if len(conditions) > 1 else conditions[0]
            
            # Query ChromaDB
            results = self.chroma_client.query(
                collection_name="few_shot_examples",
                query_texts=[query],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = self._format_results(results)
            
            logger.info(f"Few-shot search returned {len(formatted_results)} examples")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Few-shot search failed: {e}")
            return []
    
    def hybrid_search(
        self,
        query: str,
        config: RetrievalConfig
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform hybrid search across all collections.
        
        Args:
            query: Search query
            config: Retrieval configuration
            
        Returns:
            Dictionary with results from each collection
        """
        results = {
            "documentation": [],
            "patterns": [],
            "examples": []
        }
        
        try:
            # Search documentation
            if config.include_docs:
                results["documentation"] = self.search_documentation(
                    query=query,
                    top_k=config.top_k
                )
            
            # Search patterns
            if config.include_code:
                results["patterns"] = self.search_design_patterns(
                    query=query,
                    top_k=config.top_k
                )
            
            # Get few-shot examples
            if config.include_code:
                results["examples"] = self.get_few_shot_examples(
                    query=query,
                    top_k=min(3, config.top_k)  # Limit examples to 3
                )
            
            # Filter by similarity threshold
            for key in results:
                results[key] = [
                    r for r in results[key]
                    if r.get("score", 0) >= config.min_similarity
                ]
            
            total_results = sum(len(v) for v in results.values())
            logger.info(f"Hybrid search returned {total_results} total results")
            
            return results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return results
    
    def get_context_for_generation(
        self,
        user_query: str,
        category: Optional[str] = None,
        max_context_length: int = 4000
    ) -> Dict[str, Any]:
        """
        Get relevant context for code generation.
        
        Retrieves documentation, patterns, and examples that are relevant
        to the user's request, formatted for inclusion in LLM prompts.
        
        Args:
            user_query: User's description of what they want to create
            category: Optional category hint
            max_context_length: Maximum total context length in characters
            
        Returns:
            Dictionary with formatted context sections
        """
        try:
            # Get relevant documentation (API reference)
            docs = self.search_documentation(
                query=user_query,
                top_k=3,
                category=category
            )
            
            # Get similar design patterns
            patterns = self.search_design_patterns(
                query=user_query,
                top_k=2,
                category=category
            )
            
            # Get few-shot examples
            examples = self.get_few_shot_examples(
                query=user_query,
                top_k=2,
                category=category
            )
            
            # Format context sections
            context = {
                "documentation": self._format_docs_for_prompt(docs),
                "patterns": self._format_patterns_for_prompt(patterns),
                "examples": self._format_examples_for_prompt(examples),
                "total_length": 0
            }
            
            # Calculate total length
            context["total_length"] = sum(
                len(context[key]) for key in ["documentation", "patterns", "examples"]
            )
            
            # Truncate if needed
            if context["total_length"] > max_context_length:
                context = self._truncate_context(context, max_context_length)
            
            logger.info(f"Generated context: {context['total_length']} characters")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get generation context: {e}")
            return {
                "documentation": "",
                "patterns": "",
                "examples": "",
                "total_length": 0
            }
    
    def _format_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format ChromaDB query results.
        
        Args:
            results: Raw results from ChromaDB
            
        Returns:
            List of formatted result dictionaries
        """
        formatted = []
        
        if not results or not results.get("ids"):
            return formatted
        
        # ChromaDB returns lists of lists
        ids = results["ids"][0] if results["ids"] else []
        documents = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []
        
        for i in range(len(ids)):
            # Convert distance to similarity score (0-1)
            similarity = 1 - (distances[i] if i < len(distances) else 1.0)
            
            formatted.append({
                "id": ids[i],
                "text": documents[i] if i < len(documents) else "",
                "metadata": metadatas[i] if i < len(metadatas) else {},
                "score": similarity
            })
        
        return formatted
    
    def _format_docs_for_prompt(self, docs: List[Dict[str, Any]]) -> str:
        """Format documentation for inclusion in prompt."""
        if not docs:
            return ""
        
        sections = ["## Relevant CadQuery Documentation\n"]
        for doc in docs:
            sections.append(f"### {doc['metadata'].get('header', 'Reference')}")
            sections.append(doc['text'])
            sections.append("")
        
        return "\n".join(sections)
    
    def _format_patterns_for_prompt(self, patterns: List[Dict[str, Any]]) -> str:
        """Format design patterns for inclusion in prompt."""
        if not patterns:
            return ""
        
        sections = ["## Similar Design Patterns\n"]
        for pattern in patterns:
            meta = pattern['metadata']
            sections.append(f"### {meta.get('description', 'Pattern')}")
            sections.append(f"Category: {meta.get('category', 'unknown')}")
            if meta.get('print_notes'):
                sections.append(f"Print Notes: {meta['print_notes']}")
            sections.append(f"\n```python\n{meta.get('code', '')}\n```\n")
        
        return "\n".join(sections)
    
    def _format_examples_for_prompt(self, examples: List[Dict[str, Any]]) -> str:
        """Format few-shot examples for inclusion in prompt."""
        if not examples:
            return ""
        
        sections = ["## Example Code\n"]
        for example in examples:
            meta = example['metadata']
            sections.append(f"### Example: {meta.get('description', 'Code')}")
            sections.append(f"\n```python\n{meta.get('code', '')}\n```\n")
        
        return "\n".join(sections)
    
    def _truncate_context(
        self,
        context: Dict[str, Any],
        max_length: int
    ) -> Dict[str, Any]:
        """
        Truncate context to fit within max_length.
        
        Priority: examples > patterns > documentation
        """
        # Keep examples (highest priority)
        examples_len = len(context["examples"])
        remaining = max_length - examples_len
        
        if remaining <= 0:
            return {
                "documentation": "",
                "patterns": "",
                "examples": context["examples"][:max_length],
                "total_length": max_length
            }
        
        # Add patterns
        patterns_len = min(len(context["patterns"]), remaining)
        remaining -= patterns_len
        
        # Add documentation
        docs_len = min(len(context["documentation"]), remaining)
        
        return {
            "documentation": context["documentation"][:docs_len],
            "patterns": context["patterns"][:patterns_len],
            "examples": context["examples"],
            "total_length": examples_len + patterns_len + docs_len
        }

# Made with Bob
