import os
from typing import List, Dict, Any
from opensearchpy import OpenSearch, RequestsHttpConnection

class RAGRetriever:
    def __init__(self):
        host = os.environ.get("OPENSEARCH_HOST", "localhost")
        port = int(os.environ.get("OPENSEARCH_PORT", "9200"))
        
        # In a real environment, use proper auth. For MVP local, DISABLE_SECURITY_PLUGIN=true might be used
        auth = (os.environ.get("OPENSEARCH_USER", "admin"), os.environ.get("OPENSEARCH_PASSWORD", "admin"))
        
        self.client = OpenSearch(
            hosts=[{'host': host, 'port': port}],
            http_auth=auth if os.environ.get("OPENSEARCH_USER") else None,
            use_ssl=False,
            verify_certs=False,
            connection_class=RequestsHttpConnection
        )
        self.index_name = os.environ.get("OPENSEARCH_KNOWLEDGE_INDEX", "autosoc-knowledge")

    def search_knowledge(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search (keyword + kNN vector search).
        Since we rely on local embedding, we assume the embeddings are generated locally 
        and passed to OpenSearch, or we use standard BM25 for text search as a fallback MVP.
        For Phase 15 MVP, we'll do a simple match query simulating RAG retrieval.
        """
        try:
            # Check if index exists
            if not self.client.indices.exists(index=self.index_name):
                return []
                
            body = {
                "size": top_k,
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["content^3", "title^2", "tags"]
                    }
                }
            }
            
            response = self.client.search(
                body=body,
                index=self.index_name
            )
            
            hits = response.get("hits", {}).get("hits", [])
            results = []
            for hit in hits:
                source = hit.get("_source", {})
                results.append({
                    "id": hit.get("_id"),
                    "title": source.get("title", "Unknown"),
                    "content": source.get("content", ""),
                    "url": source.get("url", ""),
                    "score": hit.get("_score", 0.0)
                })
            return results
        except Exception as e:
            # We silently fail or log it, returning empty context
            print(f"Failed to retrieve from OpenSearch: {e}")
            return []

# Singleton retriever
retriever = RAGRetriever()
