"""
RAG Pipeline Setup
End-to-end RAG pipeline with retrieval and generation
"""

import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import yaml
import json

try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("chromadb and sentence-transformers required")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGPipelineConfig:
    collection_name: str = "documents"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    rerank: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    generation_model: str = "gpt-3.5-turbo"
    generation_temperature: float = 0.7
    generation_max_tokens: int = 500

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'RAGPipelineConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class RAGPipeline:
    def __init__(self, config: RAGPipelineConfig):
        self.config = config

        self._setup_vector_store()
        self._setup_embeddings()

        if config.rerank:
            self._setup_reranker()

        logger.info("RAG pipeline initialized")

    def _setup_vector_store(self):
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=self.config.collection_name
        )

    def _setup_embeddings(self):
        self.embedding_model = SentenceTransformer(self.config.embedding_model)

    def _setup_reranker(self):
        from sentence_transformers import CrossEncoder

        self.reranker = CrossEncoder(self.config.rerank_model)

    def add_documents(self, documents: List[Dict[str, str]]):
        """Add documents to the RAG pipeline"""
        chunked_docs = self._chunk_documents(documents)

        texts = [doc['text'] for doc in chunked_docs]
        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=[doc['metadata'] for doc in chunked_docs],
            ids=[doc['id'] for doc in chunked_docs]
        )

        logger.info(f"Added {len(chunked_docs)} document chunks")

    def _chunk_documents(self, documents: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        chunked = []

        for doc in documents:
            text = doc.get('text', '')
            chunks = self._chunk_text(text)

            for i, chunk in enumerate(chunks):
                chunked.append({
                    'id': f"{doc.get('id', 'doc')}_{i}",
                    'text': chunk,
                    'metadata': {
                        **doc.get('metadata', {}),
                        'chunk_id': i,
                        'source': doc.get('source', 'unknown')
                    }
                })

        return chunked

    def _chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.config.chunk_size
            chunk = text[start:end]

            if start > 0:
                chunk = text[max(0, start - self.config.chunk_overlap):end]

            chunks.append(chunk.strip())
            start = end

        return [c for c in chunks if c]

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        if top_k is None:
            top_k = self.config.top_k

        query_embedding = self.embedding_model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k * 2 if self.config.rerank else top_k
        )

        retrieved = []
        for i in range(len(results['ids'][0])):
            retrieved.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        if self.config.rerank:
            retrieved = self._rerank(query, retrieved)[:top_k]

        return retrieved

    def _rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pairs = [[query, doc['text']] for doc in documents]
        scores = self.reranker.predict(pairs)

        ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
        return [doc for doc, score in ranked]

    def generate(
        self,
        query: str,
        context: Optional[List[Dict[str, Any]]] = None,
        **generation_kwargs
    ) -> str:
        """Generate response using retrieved context"""
        if context is None:
            context = self.retrieve(query)

        context_text = "\n\n".join([
            f"[{i}] {doc['text']}"
            for i, doc in enumerate(context)
        ])

        prompt = self._build_prompt(query, context_text)

        response = self._call_llm(prompt, **generation_kwargs)
        return response

    def _build_prompt(self, query: str, context: str) -> str:
        return f"""Answer the following question based on the provided context.

Context:
{context}

Question: {query}

Answer:"""

    def _call_llm(self, prompt: str, **kwargs) -> str:
        """Call LLM for generation"""
        temperature = kwargs.get('temperature', self.config.generation_temperature)
        max_tokens = kwargs.get('max_tokens', self.config.generation_max_tokens)

        try:
            from integrate_openai import OpenAIIntegration, OpenAIConfig
        except ImportError:
            logger.warning("OpenAI integration not available, returning mock response")
            return f"Based on the context, here's an answer to your query: {prompt[:100]}..."

        config = OpenAIConfig(
            api_key="",
            model=self.config.generation_model,
            temperature=temperature,
            max_tokens=max_tokens
        )

        integration = OpenAIIntegration(config)

        messages = [{"role": "user", "content": prompt}]
        response = integration.chat_completion(messages)

        return response['content']

    def query(self, query: str, **kwargs) -> Dict[str, Any]:
        """Full RAG query: retrieve and generate"""
        retrieved = self.retrieve(query)

        response = self.generate(query, context=retrieved, **kwargs)

        return {
            'query': query,
            'response': response,
            'sources': [
                {
                    'id': doc['id'],
                    'text': doc['text'],
                    'metadata': doc['metadata'],
                    'score': doc['distance']
                }
                for doc in retrieved
            ]
        }

    def delete_documents(self, ids: List[str]):
        """Delete documents by ID"""
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents")

    def clear_collection(self):
        """Clear all documents from collection"""
        self.client.delete_collection(name=self.config.collection_name)
        self.collection = self.client.create_collection(name=self.config.collection_name)
        logger.info("Collection cleared")


def main():
    config = RAGPipelineConfig()

    pipeline = RAGPipeline(config)

    sample_docs = [
        {
            'id': 'doc1',
            'text': 'Python is a high-level programming language known for its simplicity and readability.',
            'metadata': {'category': 'programming', 'source': 'intro'}
        },
        {
            'id': 'doc2',
            'text': 'Machine learning is a branch of artificial intelligence that enables computers to learn from data.',
            'metadata': {'category': 'AI', 'source': 'intro'}
        },
        {
            'id': 'doc3',
            'text': 'Natural Language Processing (NLP) deals with the interaction between computers and human language.',
            'metadata': {'category': 'AI', 'source': 'advanced'}
        }
    ]

    pipeline.add_documents(sample_docs)

    query = "What is machine learning?"
    result = pipeline.query(query)

    print(f"Query: {query}")
    print(f"\nResponse:\n{result['response']}")
    print(f"\nSources used: {len(result['sources'])}")


if __name__ == "__main__":
    main()
