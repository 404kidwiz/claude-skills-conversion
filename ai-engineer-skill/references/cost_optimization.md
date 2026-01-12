# Cost Optimization Strategies

## Understanding Token Costs

### Token Pricing (per 1K tokens)

| Model | Input | Output | Context |
|-------|-------|--------|---------|
| GPT-4 | $0.03 | $0.06 | 8K |
| GPT-4 Turbo | $0.01 | $0.03 | 128K |
| GPT-3.5 Turbo | $0.0005 | $0.0015 | 16K |
| Claude 3.5 Sonnet | $0.003 | $0.015 | 200K |
| Claude 3 Opus | $0.015 | $0.075 | 200K |

### Cost Estimation

**Approximate tokens:**
```python
def estimate_tokens(text):
    # Rough estimate: 1 token ≈ 0.75 words
    return len(text.split()) * 1.3
```

**Full request cost:**
```python
def calculate_cost(model, input_tokens, output_tokens):
    pricing = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
    }

    input_cost = (input_tokens / 1000) * pricing[model]['input']
    output_cost = (output_tokens / 1000) * pricing[model]['output']

    return input_cost + output_cost
```

## Optimization Techniques

### 1. Model Selection

**Use the right model for the task:**

```python
def select_model(task_complexity, budget):
    if task_complexity == 'simple' and budget < 0.01:
        return 'gpt-3.5-turbo'
    elif task_complexity == 'medium' and budget < 0.10:
        return 'gpt-4-turbo'
    elif task_complexity == 'complex':
        return 'gpt-4'
    else:
        return 'gpt-3.5-turbo'  # Default cheapest
```

**Tiered approach:**
1. Start with smallest model
2. Escalate if quality insufficient
3. Cache results to avoid repeat calls

### 2. Prompt Optimization

**Reduce prompt length:**
```python
def optimize_prompt(prompt, target_length=500):
    while estimate_tokens(prompt) > target_length:
        # Remove redundancies
        prompt = remove_redundancies(prompt)
        # Use abbreviations
        prompt = abbreviate_common_terms(prompt)
        # Simplify language
        prompt = simplify_language(prompt)

    return prompt
```

**Use system prompts:**
```python
# Bad: Repeats context in every prompt
prompt = "You are a helpful assistant. Be concise. " + user_message

# Good: Set once, then use minimal prompts
client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a helpful, concise assistant."},
        {"role": "user", "content": user_message}
    ]
)
```

### 3. Caching Strategies

**Response caching:**
```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def cached_llm_call(prompt_hash):
    return client.generate(original_prompt)

def generate_with_cache(prompt):
    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
    return cached_llm_call(prompt_hash)
```

**Embedding caching:**
```python
embedding_cache = {}

def get_embeddings(texts):
    uncached = [t for t in texts if t not in embedding_cache]

    if uncached:
        new_embeddings = client.embeddings.create(uncached)
        for text, emb in zip(uncached, new_embeddings):
            embedding_cache[text] = emb

    return [embedding_cache[t] for t in texts]
```

### 4. Batching

**Batch requests:**
```python
def batch_generate(prompts, batch_size=10):
    results = []

    for i in range(0, len(prompts), batch_size):
        batch = prompts[i:i+batch_size]
        # Use batch API if available
        batch_results = client.batch.generate(batch)
        results.extend(batch_results)

    return results
```

### 5. Streaming for Long Outputs

```python
def generate_streaming(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    full_content = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            content = chunk.choices[0].delta.content
            full_content += content
            # Process chunk as it arrives
            process_chunk(content)

    return full_content
```

### 6. Token Limit Management

**Smart truncation:**
```python
def smart_truncate(text, max_tokens, preserve_intro=True):
    if estimate_tokens(text) <= max_tokens:
        return text

    if preserve_intro:
        # Keep first and last parts
        intro_tokens = max_tokens * 0.3
        outro_tokens = max_tokens * 0.7
        return truncate_ends(text, intro_tokens, outro_tokens)
    else:
        return truncate_from_start(text, max_tokens)
```

**Context window optimization:**
```python
def optimize_context_window(query, context, max_tokens):
    query_tokens = estimate_tokens(query)
    available_tokens = max_tokens - query_tokens - 100  # Buffer

    # Select most relevant context
    ranked_contexts = rank_relevance(query, context)
    selected_contexts = []

    for ctx in ranked_contexts:
        ctx_tokens = estimate_tokens(ctx)
        if sum(estimate_tokens(c) for c in selected_contexts) + ctx_tokens <= available_tokens:
            selected_contexts.append(ctx)
        else:
            break

    return "\n\n".join(selected_contexts)
```

## Monitoring and Alerts

### Cost Tracking

```python
class CostMonitor:
    def __init__(self, budget_limit):
        self.total_cost = 0
        self.budget_limit = budget_limit
        self.alerts = []

    def track_usage(self, model, input_tokens, output_tokens):
        cost = calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost

        if self.total_cost > self.budget_limit * 0.8:
            self.alerts.append(f"Budget warning: {self.total_cost:.2f}")

        if self.total_cost > self.budget_limit:
            self.alerts.append(f"Budget exceeded: {self.total_cost:.2f}")

    def get_report(self):
        return {
            'total_cost': self.total_cost,
            'budget_limit': self.budget_limit,
            'utilization': self.total_cost / self.budget_limit,
            'alerts': self.alerts
        }
```

### Optimization Recommendations

```python
def analyze_usage(usage_data):
    recommendations = []

    # High cost per request
    avg_cost = usage_data['total_cost'] / usage_data['request_count']
    if avg_cost > 0.10:
        recommendations.append("Consider using smaller models")

    # High error rate leads to retries
    if usage_data['error_rate'] > 0.05:
        recommendations.append("Improve error handling to reduce retries")

    # Low cache hit rate
    if usage_data['cache_hit_rate'] < 0.30:
        recommendations.append("Implement response caching")

    return recommendations
```

## Cost-Saving Patterns

### 1. Tiered LLM Strategy
```
Level 1: Small model for simple tasks (gpt-3.5-turbo)
Level 2: Medium model for complex tasks (gpt-4-turbo)
Level 3: Large model for critical tasks (gpt-4)
```

### 2. Hybrid Approach
- Use local models for simple tasks
- Use API models for complex reasoning
- Cache everything possible

### 3. Fallback Patterns
```python
def generate_with_fallbacks(prompt, models=['gpt-4', 'gpt-3.5-turbo']):
    for model in models:
        try:
            return generate(model, prompt)
        except RateLimitError:
            continue

    raise Exception("All models failed")
```

## Best Practices

1. **Monitor continuously**: Track costs in real-time
2. **Set budgets**: Enforce limits per user/project
3. **Optimize prompts**: Remove unnecessary context
4. **Cache aggressively**: Avoid repeat computations
5. **Choose right model**: Match model to task complexity
6. **Use streaming**: Reduce latency for long outputs
7. **Batch requests**: When API supports it
8. **Test with small models**: Before scaling to expensive ones
