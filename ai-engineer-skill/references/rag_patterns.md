# RAG Patterns

## Core Components

### 1. Document Chunking

**Fixed-size chunks:**
```python
chunk_size = 512
chunk_overlap = 50
```

**Semantic chunks:**
- Use sentence boundaries
- Preserve paragraph structure
- Maintain context coherence

### 2. Embedding Models

**Fast/Small:**
- `all-MiniLM-L6-v2` (384 dims, fast)
- `all-mpnet-base-v2` (768 dims, balanced)

**Large/Accurate:**
- `text-embedding-3-large` (OpenAI)
- `text-embedding-3-small` (OpenAI)

### 3. Retrieval Strategies

**Simple:**
```python
results = rag.query(query_text, n_results=5)
```

**Filtered:**
```python
results = rag.query(
    query_text,
    n_results=5,
    where={'category': 'technical'}
)
```

**Hybrid Search:**
- Combine semantic search with keyword search
- Re-rank results with cross-encoder

## Advanced Patterns

### Multi-hop RAG

Retrieve information across multiple steps:
```python
def multi_hop_query(initial_query):
    # First hop
    results1 = rag.query(initial_query)
    context1 = " ".join(r['text'] for r in results1)

    # Second hop based on first results
    followup = f"Based on: {context1}\nQuery: {followup_question}"
    results2 = rag.query(followup)

    return results1 + results2
```

### Agentic RAG

Let the agent decide what to retrieve:
```python
def agentic_rag(query):
    # Agent decides retrieval strategy
    strategy = agent.analyze_query(query)

    if strategy['needs_retrieval']:
        results = rag.query(query, **strategy['params'])
    else:
        results = []

    # Generate answer with retrieved context
    return agent.generate_answer(query, results)
```

### Reranking

Improve retrieval quality:
```python
def rerank(query, results, top_k=5):
    from sentence_transformers import CrossEncoder

    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    pairs = [[query, r['text']] for r in results]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
    return [r for r, s in ranked[:top_k]]
```

### Citation Management

Track source information:
```python
def generate_with_citations(query):
    results = rag.query(query)

    response = llm.generate(
        f"Answer: {query}\n\nContext: {[r['text'] for r in results]}"
    )

    citations = [
        {'source': r['metadata']['source'], 'chunk_id': r['metadata']['chunk_id']}
        for r in results
    ]

    return {'answer': response, 'citations': citations}
```

## Evaluation

### RAGAS Framework
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

metrics = [faithfulness, answer_relevancy]
results = evaluate(dataset, metrics)
```

### Custom Metrics
```python
def retrieval_accuracy(expected_docs, retrieved_docs):
    expected_ids = set(d['id'] for d in expected_docs)
    retrieved_ids = set(d['id'] for d in retrieved_docs)

    recall = len(expected_ids & retrieved_ids) / len(expected_ids)
    precision = len(expected_ids & retrieved_ids) / len(retrieved_ids)

    return {'recall': recall, 'precision': precision}
```

## Performance Optimization

### Vector Index Tuning
```python
# Use IVF for large collections
index_params = {
    "index_type": "IVF_FLAT",
    "nlist": 100,
    "metric_type": "IP"
}
```

### Cache Frequently Asked Questions
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_query(query_hash):
    return rag.query(query_hash)
```

## Best Practices

1. **Chunk size**: 500-1000 tokens usually works well
2. **Overlap**: 10-20% overlap maintains context
3. **Embeddings**: Choose based on speed vs accuracy needs
4. **Reranking**: Always rerank top 20-50 results
5. **Evaluation**: Regularly test retrieval quality
6. **Update strategy**: Implement incremental updates
