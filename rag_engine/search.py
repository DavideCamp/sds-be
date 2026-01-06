import logging
from typing import Literal, Optional
from dataclasses import dataclass

from weaviate.collections.classes.filters import Filter
from .weaviate_client import WeaviateClient
from .embeddings import embed


@dataclass
class SearchResult:
    """Unified search result structure."""
    id: str
    text: str
    document_id: str
    user_id: int
    score: float
    search_type: str  # "semantic", "keyword", "hybrid"

    def to_dict(self) -> dict:
        return {
            "_id": self.id,
            "text": self.text,
            "document_id": self.document_id,
            "user_id": self.user_id,
            "score": self.score,
            "search_type": self.search_type,
        }


class SearchRag:
    """
    Service for handling different search strategies on document chunks.

    Strategies:
    - semantic: Vector similarity search using embeddings
    - keyword: BM25/keyword-based text search
    - hybrid: Combination of semantic and keyword with configurable weights
    """

    def __init__(self):
        self.client = WeaviateClient()
        self.logger = logging.getLogger(__name__)
        self.text_key = self.client.text_key

    def semantic_search(
            self,
            query: str,
            user_id: int,
            limit: int = 5,
            document_ids: Optional[list[str]] = None,
            min_score: Optional[float] = None,
    ) -> list[SearchResult]:
        """
        Perform semantic similarity search using vector embeddings.

        Args:
            query: Search query
            user_id: User ID to filter results
            limit: Maximum number of results
            document_ids: Optional list of document IDs to search within
            min_score: Optional minimum similarity score (lower distance = higher similarity)

        Returns:
            List of SearchResult objects
        """
        try:
            # Build filters
            filters = Filter.by_property("user_id").equal(user_id)

            # Add document ID filters if specified
            if document_ids:
                doc_filters = [
                    Filter.by_property("document_id").equal(doc_id)
                    for doc_id in document_ids
                ]
                if len(doc_filters) == 1:
                    filters = filters & doc_filters[0]
                else:
                    combined = doc_filters[0]
                    for f in doc_filters[1:]:
                        combined = combined | f
                    filters = filters & combined

            # Perform vector search
            response = self.client.chunks_collection.query.near_vector(
                near_vector=embed(query),
                limit=limit,
                filters=filters,
                return_metadata=["distance"],
                return_properties=[self.text_key, "document_id", "user_id", "object_id"],
            )

            results = []
            for obj in response.objects:
                props = obj.properties or {}
                distance = obj.metadata.distance if obj.metadata else None

                # Filter by minimum score if specified
                if min_score is not None and distance is not None:
                    if distance > min_score:
                        continue

                results.append(SearchResult(
                    id=props.get("object_id"),
                    text=props.get(self.text_key),
                    document_id=props.get("document_id"),
                    user_id=props.get("user_id"),
                    score=distance if distance is not None else 1.0,
                    search_type="semantic"
                ))

            self.logger.info(
                f"Semantic search for user {user_id}: {len(results)} results"
            )
            return results

        except Exception as e:
            self.logger.error(f"Error in semantic search for user {user_id}", exc_info=True)
            return []

    def keyword_search(
            self,
            query: str,
            user_id: int,
            limit: int = 5,
            document_ids: Optional[list[str]] = None,
    ) -> list[SearchResult]:
        """
        Perform BM25 keyword-based text search.

        Args:
            query: Search query
            user_id: User ID to filter results
            limit: Maximum number of results
            document_ids: Optional list of document IDs to search within

        Returns:
            List of SearchResult objects
        """
        try:
            # Build filters
            filters = Filter.by_property("user_id").equal(user_id)

            # Add document ID filters if specified
            if document_ids:
                doc_filters = [
                    Filter.by_property("document_id").equal(doc_id)
                    for doc_id in document_ids
                ]
                if len(doc_filters) == 1:
                    filters = filters & doc_filters[0]
                else:
                    combined = doc_filters[0]
                    for f in doc_filters[1:]:
                        combined = combined | f
                    filters = filters & combined

            # Perform BM25 keyword search
            response = self.client.chunks_collection.query.bm25(
                query=query,
                limit=limit,
                filters=filters,
                return_metadata=["score"],
                return_properties=[self.text_key, "document_id", "user_id", "object_id"],
            )

            results = []
            for obj in response.objects:
                props = obj.properties or {}
                score = obj.metadata.score if obj.metadata else 0.0

                results.append(SearchResult(
                    id=props.get("object_id"),
                    text=props.get(self.text_key),
                    document_id=props.get("document_id"),
                    user_id=props.get("user_id"),
                    score=score,
                    search_type="keyword"
                ))

            self.logger.info(
                f"Keyword search for user {user_id}: {len(results)} results"
            )
            return results

        except Exception as e:
            self.logger.error(f"Error in keyword search for user {user_id}", exc_info=True)
            return []

    def hybrid_search(
            self,
            query: str,
            user_id: int,
            limit: int = 5,
            alpha: float = 0.5,
            document_ids: Optional[list[str]] = None,
            fusion_type: Literal["weighted", "rrf"] = "weighted",
    ) -> list[SearchResult]:
        """
        Perform hybrid search combining semantic and keyword search.

        Args:
            query: Search query
            user_id: User ID to filter results
            limit: Maximum number of results
            alpha: Weight between semantic (1.0) and keyword (0.0) search.
                   0.5 = equal weight. Only used if fusion_type="weighted"
            document_ids: Optional list of document IDs to search within
            fusion_type: "weighted" or "rrf" (Reciprocal Rank Fusion)

        Returns:
            List of SearchResult objects sorted by combined score
        """
        try:
            return self._hybrid_rrf(query, user_id, limit, document_ids)
        except Exception as e:
            self.logger.error(f"Error in hybrid search for user {user_id}, error: {e}", exc_info=True)
            return []

    def _hybrid_rrf(
            self,
            query: str,
            user_id: int,
            limit: int,
            document_ids: Optional[list[str]] = None,
            k: int = 60,
    ) -> list[SearchResult]:
        """
        Hybrid search using Reciprocal Rank Fusion (RRF).
        RRF combines rankings from multiple search methods.

        RRF score = sum(1 / (k + rank_i)) for each search method
        where k is a constant (typically 60) and rank_i is the rank in method i
        """
        semantic_results = self.semantic_search(
            query=query,
            user_id=user_id,
            limit=limit * 2,
            document_ids=document_ids,
        )

        keyword_results = self.keyword_search(
            query=query,
            user_id=user_id,
            limit=limit * 2,
            document_ids=document_ids,
        )

        # Build RRF scores
        rrf_scores = {}

        # Add semantic rankings
        for rank, result in enumerate(semantic_results, start=1):
            chunk_id = result.id
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (k + rank))

        # Add keyword rankings
        for rank, result in enumerate(keyword_results, start=1):
            chunk_id = result.id
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0) + (1 / (k + rank))

        # Create unified results with RRF scores
        all_results = {r.id: r for r in semantic_results + keyword_results}

        results = []
        for chunk_id, score in sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:limit]:
            if chunk_id in all_results:
                result = all_results[chunk_id]
                results.append(SearchResult(
                    id=result.id,
                    text=result.text,
                    document_id=result.document_id,
                    user_id=result.user_id,
                    score=score,
                    search_type="hybrid"
                ))

        self.logger.info(
            f"Hybrid search (RRF, k={k}) for user {user_id}: {len(results)} results"
        )
        return results

    def search(
            self,
            query: str,
            user_id: int,
            limit: int = 5,
            strategy: Literal["semantic", "keyword", "hybrid"] = "semantic",
            **kwargs
    ) -> list[dict]:
        """
        Unified search interface with multiple strategies.

        Args:
            query: Search query
            user_id: User ID to filter results
            limit: Maximum number of results
            strategy: Search strategy ("semantic", "keyword", "hybrid")
            **kwargs: Additional parameters passed to the specific search method
                - For hybrid: alpha (float), fusion_type (str)
                - For all: document_ids (list[str]), min_score (float)

        Returns:
            List of result dictionaries
        """
        if strategy == "semantic":
            results = self.semantic_search(query, user_id, limit, **kwargs)
        elif strategy == "keyword":
            results = self.keyword_search(query, user_id, limit, **kwargs)
        elif strategy == "hybrid":
            results = self.hybrid_search(query, user_id, limit, **kwargs)
        else:
            raise ValueError(f"Unknown search strategy: {strategy}")

        return [r.to_dict() for r in results]