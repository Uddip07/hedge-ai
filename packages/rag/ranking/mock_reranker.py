"""
Mock Reranker Implementation.

Reranks search results using exact term keyword match scoring boosts for testing and development.
"""

from packages.rag.models.search import QueryResult
from packages.rag.ranking.base import BaseReranker


class MockReranker(BaseReranker):
    """
    Mock Reranker boosting score based on query term frequency inside chunk text.
    """

    def rerank(self, query: str, results: list[QueryResult]) -> list[QueryResult]:
        if not results:
            return []

        query_terms = [t.lower() for t in query.split() if len(t) > 2]
        scored_results: list[tuple[QueryResult, float]] = []

        for item in results:
            chunk_text = item.chunk.text.lower()
            keyword_matches = sum(1 for term in query_terms if term in chunk_text)
            boost = 0.1 * keyword_matches
            new_score = min(1.0, item.score + boost)
            scored_results.append((item, new_score))

        scored_results.sort(key=lambda r: r[1], reverse=True)

        reranked: list[QueryResult] = []
        for rank, (item, score) in enumerate(scored_results, start=1):
            reranked.append(
                QueryResult(
                    chunk=item.chunk,
                    score=round(score, 4),
                    rank=rank,
                )
            )

        return reranked
