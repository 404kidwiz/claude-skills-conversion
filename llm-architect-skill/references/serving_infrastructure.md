# Serving Infrastructure Guide

## Overview

Production model serving requires careful consideration of performance, scalability, and reliability.

## Serving Options

### 1. API-Based Serving

Use provider APIs (OpenAI, Anthropic, etc.)

**Pros:**
- Zero infrastructure
- Automatic scaling
- Built-in monitoring
- Regular updates

**Cons:**
- Ongoing costs
- Data privacy concerns
- Rate limits
- Dependency on external services

**Best for:**
- Proof of concept
- Low to medium traffic
- No ML infrastructure team
- Rapid prototyping

### 2. Self-Hosted Serving

Deploy models on your own infrastructure

**Pros:**
- Full control
- Data privacy
- Predictable costs
- Custom optimizations

**Cons:**
- Infrastructure setup
- Maintenance overhead
- Scaling complexity
- Higher initial cost

**Best for:**
- High volume production
- Sensitive data
- Custom models
- Cost optimization at scale

## Serving Frameworks

### vLLM

High-throughput serving with PagedAttention.

**Installation:**
```bash
pip install vllm
```

**Usage:**
```bash
python -m vllm.entrypoints.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --port 8000 \
    --tensor-parallel-size 4
```

**Pros:**
- 10-20x higher throughput
- Low latency
- Continuous batching
- OpenAI-compatible API

**Cons:**
- Newer, less battle-tested
- Limited model support

### Text Generation WebUI (Oobabooga)

Feature-rich web interface for model serving.

**Features:**
- Web UI
- Multiple model support
- Extensions ecosystem
- API access

**Setup:**
```bash
git clone https://github.com/oobabooga/text-generation-webui
cd text-generation-webui
python server.py --model-path /path/to/model --listen
```

### LocalAI

OpenAI-compatible API for local models.

**Setup:**
```bash
docker run -p 8080:8080 \
    -v /models:/models \
    localai/localai \
    --models-path /models
```

**Use OpenAI client:**
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed"
)
```

## Deployment Strategies

### Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

RUN pip install fastapi uvicorn transformers accelerate torch

COPY model.py .
COPY ./models ./models

CMD ["uvicorn", "model:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and Run:**
```bash
docker build -t model-server .
docker run -p 8000:8000 --gpus all model-server
```

### Kubernetes Deployment

**Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      containers:
      - name: model-server
        image: model-server:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            nvidia.com/gpu: 1
```

**Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: model-server
spec:
  selector:
    app: model-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

### Serverless Deployment

**AWS Lambda:**
```python
import json

def lambda_handler(event, context):
    prompt = event['prompt']
    response = generate_with_model(prompt)
    return {
        'statusCode': 200,
        'body': json.dumps({'output': response})
    }
```

## Performance Optimization

### Batch Processing

```python
@app.post("/batch_generate")
async def batch_generate(requests: List[GenerationRequest]):
    outputs = []
    for request in requests:
        output = generate(request)
        outputs.append(output)
    return outputs
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def cached_generate(prompt_hash):
    return generate(original_prompt)
```

### Quantization

```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True
)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    quantization_config=quantization_config
)
```

### Stream Responses

```python
async def stream_generate(prompt):
    for token in model.generate_stream(prompt):
        yield token
```

## Monitoring

### Key Metrics

1. **Throughput**: Requests per second
2. **Latency**: P50, P95, P99 response times
3. **Error Rate**: Failed requests
4. **GPU Utilization**: Compute efficiency
5. **Memory Usage**: VRAM consumption

### Prometheus Integration

```python
from prometheus_client import Counter, Histogram

request_counter = Counter('model_requests_total', 'Total requests')
latency_histogram = Histogram('model_latency_seconds', 'Request latency')

@app.post("/generate")
async def generate(request: GenerationRequest):
    with latency_histogram.time():
        output = generate_with_model(request)
        request_counter.inc()
        return output
```

### Health Checks

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "memory_used": torch.cuda.memory_allocated()
    }
```

## Scaling

### Horizontal Scaling

Add more instances to handle increased load.

**Kubernetes HPA:**
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
```

### Vertical Scaling

Increase resources per instance.

**GPU Types:**
- A100 (40GB/80GB): Best performance
- V100 (16GB/32GB): Good balance
- T4 (16GB): Cost-effective
- L4 (24GB): Newer option

### Load Balancing

```nginx
upstream model_servers {
    least_conn;
    server server1:8000;
    server server2:8000;
    server server3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://model_servers;
    }
}
```

## Best Practices

1. **Use FastAPI**: Async, type-safe, automatic docs
2. **Implement rate limiting**: Prevent abuse
3. **Add authentication**: Secure endpoints
4. **Log everything**: Debugging and monitoring
5. **Version models**: Easy rollbacks
6. **Graceful shutdown**: Handle connections properly
7. **Health checks**: Kubernetes ready
8. **Resource limits**: Prevent memory leaks
9. **Request validation**: Use Pydantic models
10. **Monitor continuously**: Detect issues early
