# AI Integration Guide

## Quick Start

### Installation
```bash
pip install openai anthropic chromadb sentence-transformers
```

### Environment Variables
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

## OpenAI Integration

### Basic Usage
```python
from integrate_openai import OpenAIIntegration, OpenAIConfig

config = OpenAIConfig(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4"
)

integration = OpenAIIntegration(config)

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
]

response = integration.chat_completion(messages)
print(response['content'])
```

### Configuration Options
- `max_retries`: Number of retry attempts (default: 3)
- `retry_delay`: Delay between retries in seconds (default: 1.0)
- `timeout`: Request timeout (default: 120)
- `rate_limit_delay`: Delay to avoid rate limiting (default: 0.5)

## Anthropic Integration

### Basic Usage
```python
from integrate_anthropic import AnthropicIntegration, AnthropicConfig

config = AnthropicConfig(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-3-5-sonnet-20241022"
)

integration = AnthropicIntegration(config)

messages = [{"role": "user", "content": "Explain AI"}]
response = integration.messages(messages)
```

## RAG Setup

### Quick Start
```python
from setup_rag import RAGSystem, RAGConfig

config = RAGConfig(
    collection_name="my_docs",
    embedding_model="all-MiniLM-L6-v2"
)

rag = RAGSystem(config)

# Add documents
documents = [
    {
        'id': 'doc1',
        'text': 'Your document text here',
        'metadata': {'source': 'doc.txt'}
    }
]
rag.add_documents(documents)

# Query
results = rag.query("What is machine learning?")
for result in results:
    print(result['text'])
```

## Prompt Management

```python
from manage_prompts import PromptManager, PromptTemplate

manager = PromptManager()

template = PromptTemplate(
    name="summary",
    template="Summarize: {text}",
    variables=["text"],
    description="Text summarization"
)

manager.add_template(template)

# Render
rendered = template.render(text="Your text here")
```

## Monitoring

```python
from monitor_ai_service import AIMonitor

monitor = AIMonitor(window_size=1000)

monitor.record_request(
    success=True,
    response_time=1.5,
    token_usage=1000
)

status = monitor.get_health_status()
print(f"Healthy: {status.is_healthy}")
```

## Cost Optimization

```python
from optimize_tokens import TokenTracker

tracker = TokenTracker()
tracker.record_usage(
    model="gpt-4",
    usage={'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150}
)

cost = tracker.get_total_cost()
print(f"Total cost: ${cost:.4f}")
```

## Best Practices

1. **Rate Limiting**: Always implement rate limiting to avoid API limits
2. **Error Handling**: Use retry logic with exponential backoff
3. **Token Tracking**: Monitor usage to control costs
4. **Fallback Systems**: Implement fallback to alternative models
5. **Monitoring**: Track health metrics and response times
6. **Security**: Never commit API keys to version control

## Pricing Reference

| Model | Input (per 1K) | Output (per 1K) |
|-------|---------------|----------------|
| GPT-4 | $0.03 | $0.06 |
| GPT-4 Turbo | $0.01 | $0.03 |
| GPT-3.5 Turbo | $0.0005 | $0.0015 |
| Claude 3.5 Sonnet | $0.003 | $0.015 |
| Claude 3 Opus | $0.015 | $0.075 |
