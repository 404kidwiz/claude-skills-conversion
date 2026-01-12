"""
RAG (Retrieval-Augmented Generation) Setup Script
Handles vector database, document chunking, and retrieval
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass
import json
import yaml

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    raise ImportError("chromadb required: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError("sentence-transformers required: pip install sentence-transformers")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    collection_name: str = "documents"
    embedding_model: str = "all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    persist_directory: str = "./chroma_db"
    top_k: int = 5

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'RAGConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class DocumentChunker:
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str) -> List[str]:
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk = text[start:end]

            if start > 0:
                chunk = text[max(0, start - self.overlap):end]

            chunks.append(chunk.strip())
            start = end

        return [c for c in chunks if c]

    def chunk_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunked_docs = []

        for doc in documents:
            text = doc.get('text', '')
            chunks = self.chunk_text(text)

            for i, chunk in enumerate(chunks):
                chunked_docs.append({
                    'text': chunk,
                    'metadata': {
                        **doc.get('metadata', {}),
                        'chunk_id': i,
                        'source': doc.get('source', 'unknown')
                    },
                    'id': f"{doc.get('id', 'doc')}_{i}"
                })

        return chunked_docs


class RAGSystem:
    def __init__(self, config: RAGConfig):
        self.config = config
        self.chunker = DocumentChunker(config.chunk_size, config.chunk_overlap)

        Path(config.persist_directory).mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=config.persist_directory,
            settings=Settings(anonymized_telemetry=False)
        )

        self.collection = self.client.get_or_create_collection(
            name=config.collection_name
        )

        logger.info(f"Loading embedding model: {config.embedding_model}")
        self.embedding_model = SentenceTransformer(config.embedding_model)

    def add_documents(self, documents: List[Dict[str, Any]]):
        chunked_docs = self.chunker.chunk_documents(documents)

        texts = [doc['text'] for doc in chunked_docs]
        embeddings = self.embedding_model.encode(texts).tolist()

        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=[doc['metadata'] for doc in chunked_docs],
            ids=[doc['id'] for doc in chunked_docs]
        )

        logger.info(f"Added {len(chunked_docs)} chunks to collection")

    def query(
        self,
        query_text: str,
        n_results: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        if n_results is None:
            n_results = self.config.top_k

        query_embedding = self.embedding_model.encode([query_text]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            where=where
        )

        retrieved_docs = []
        for i in range(len(results['ids'][0])):
            retrieved_docs.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i]
            })

        return retrieved_docs

    def delete_documents(self, ids: List[str]):
        self.collection.delete(ids=ids)
        logger.info(f"Deleted {len(ids)} documents")

    def get_collection_stats(self) -> Dict[str, Any]:
        return {
            'count': self.collection.count(),
            'name': self.config.collection_name,
            'embedding_model': self.config.embedding_model
        }

    def clear_collection(self):
        self.client.delete_collection(name=self.config.collection_name)
        self.collection = self.client.create_collection(name=self.config.collection_name)
        logger.info("Collection cleared")


def load_documents_from_directory(directory: Union[str, Path]) -> List[Dict[str, Any]]:
    documents = []
    directory = Path(directory)

    for file_path in directory.rglob("*.txt"):
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()

        documents.append({
            'id': file_path.stem,
            'text': text,
            'metadata': {
                'source': str(file_path),
                'filename': file_path.name
            }
        })

    return documents


def main():
    config = RAGConfig()
    rag = RAGSystem(config)

    sample_docs = [
        {
            'id': 'doc1',
            'text': 'Machine learning is a subset of artificial intelligence that focuses on building systems that can learn from data.',
            'metadata': {'category': 'ML', 'source': 'intro'}
        },
        {
            'id': 'doc2',
            'text': 'Deep learning uses neural networks with multiple layers to model complex patterns in data.',
            'metadata': {'category': 'DL', 'source': 'advanced'}
        }
    ]

    rag.add_documents(sample_docs)

    query = "What is machine learning?"
    results = rag.query(query)

    print(f"Query: {query}")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Text: {result['text']}")
        print(f"Distance: {result['distance']:.4f}")

    print(f"\nStats: {rag.get_collection_stats()}")


if __name__ == "__main__":
    main()
