# Fine-Tuning Guide

## Overview

Fine-tuning adapts pre-trained models to specific tasks or domains, improving performance on specialized data.

## Methods

### 1. Full Fine-Tuning

Updates all model parameters.

**Pros:**
- Maximum performance gains
- No architectural changes
- Works for any model

**Cons:**
- High computational cost
- Large storage requirements
- Risk of catastrophic forgetting

**Use case:**
- Critical tasks requiring maximum accuracy
- Sufficient compute resources
- Domain-specific models

### 2. LoRA (Low-Rank Adaptation)

Adds trainable rank decomposition matrices.

**Pros:**
- 100-1000x faster training
- Small storage (1-100MB)
- No performance degradation
- Easy to switch between adapters

**Cons:**
- Slightly lower performance than full fine-tuning
- Requires LoRA-supporting codebase

**Use case:**
- Most production use cases
- Multiple task adapters
- Resource-constrained environments

**Configuration:**
```python
lora_config = LoraConfig(
    r=8,  # Rank (4-16 typical)
    lora_alpha=32,  # Scaling factor
    target_modules=["q_proj", "v_proj"],  # Target layers
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
```

### 3. Prefix Tuning

Learns continuous prompt embeddings.

**Pros:**
- No gradient through model
- Very efficient

**Cons:**
- More complex to implement
- Lower performance than LoRA

### 4. P-Tuning (Prompt Tuning)

Learns soft prompts.

**Pros:**
- Simple implementation
- Parameter efficient

**Cons:**
- Limited to prompt-based learning

## Data Preparation

### Dataset Format

```json
[
    {
        "text": "The capital of France is Paris."
    },
    {
        "text": "Machine learning enables computers to learn from data."
    }
]
```

### Data Quality Requirements

1. **Relevance**: Data must match target task
2. **Diversity**: Cover edge cases and variations
3. **Size**: 100-10,000+ examples depending on task
4. **Balance**: Balanced classes for classification
5. **Cleanliness**: Remove duplicates and errors

### Data Augmentation

```python
def augment_data(text):
    variations = []

    # Paraphrasing
    variations.append(paraphrase(text))

    # Back-translation
    variations.append(back_translate(text))

    # Synonym replacement
    variations.append(replace_synonyms(text))

    return variations
```

## Training Process

### Step 1: Prepare Data

```python
from finetune_model import ModelFinetuner, FinetuningConfig

config = FinetuningConfig(
    model_name="gpt2",
    output_dir="./finetuned_model",
    train_file="train_data.json",
    validation_file="validation_data.json",
    use_lora=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-4
)

finetuner = ModelFinetuner(config)
finetuner.load_model()
```

### Step 2: Train

```python
finetuner.train()
```

### Step 3: Evaluate

```python
# Use validation set
validation_loss = finetuner.evaluate()

# Or test on held-out examples
test_results = finetuner.test(test_data)
```

### Step 4: Save Model

```python
finetuner.save_model()
```

## Hyperparameter Tuning

### Key Parameters

| Parameter | Typical Range | Impact |
|-----------|---------------|--------|
| Learning Rate | 1e-5 to 5e-4 | High impact |
| Batch Size | 1-16 | Moderate impact |
| Epochs | 1-10 | Depends on data size |
| LoRA Rank (r) | 4-32 | Low-Moderate impact |
| LoRA Alpha | 16-128 | Low impact |
| Warmup Steps | 100-1000 | Moderate impact |

### Tuning Strategy

```python
# Grid search
learning_rates = [1e-5, 5e-5, 1e-4]
batch_sizes = [4, 8]

for lr in learning_rates:
    for bs in batch_sizes:
        config.learning_rate = lr
        config.per_device_train_batch_size = bs
        finetuner.train()
        results.append(evaluate())
```

## Evaluation

### Metrics

**Language Generation:**
- Perplexity
- BLEU score
- ROUGE score
- Human evaluation

**Classification:**
- Accuracy
- F1 score
- Precision/Recall
- Confusion matrix

**Question Answering:**
- Exact match
- F1 score (token-level)
- Semantic similarity

### Evaluation Framework

```python
from evaluate_model import ModelEvaluator

evaluator = ModelEvaluator()

# Add metrics
evaluator.add_metric(EvaluationMetric(
    name="perplexity",
    metric_type=MetricType.CUSTOM,
    description="Model perplexity"
))

# Run evaluation
report = evaluator.evaluate_model(
    model_name="finetuned_model",
    generate_func=generate_with_model,
    dataset=test_dataset
)
```

## Deployment

### Loading Fine-Tuned Models

```python
finetuner.load_finetuned_model("path/to/model")

# Generate
response = finetuner.generate(
    prompt="Your prompt here",
    max_new_tokens=100,
    temperature=0.7
)
```

### Serving Fine-Tuned Models

```python
from serve_model import ModelServer

server = ModelServer(config)
server.load_model("finetuned_model", "path/to/model")
server.start()
```

### Multi-Adapter Deployment

```python
# Switch between adapters
model.set_adapter("adapter_1")
output_1 = model.generate(prompt)

model.set_adapter("adapter_2")
output_2 = model.generate(prompt)
```

## Advanced Techniques

### Instruction Tuning

```python
# Format: instruction + input + output
data = [
    {
        "instruction": "Summarize the following text.",
        "input": "Long text here...",
        "output": "Summary here..."
    }
]
```

### Multi-Task Learning

```python
# Train on multiple tasks simultaneously
tasks = ["summarization", "translation", "qa"]

for task in tasks:
    task_data = load_task_data(task)
    finetuner.train(task_data)
```

### Continual Learning

```python
# Learn new tasks without forgetting
for task in new_tasks:
    finetuner.train(task_data, replay_buffer=old_data)
```

## Common Issues

### Catastrophic Forgetting
- **Symptom**: Performance on old tasks degrades
- **Solution**: Use replay buffer, elastic weight consolidation

### Overfitting
- **Symptom**: Training loss decreases, validation loss increases
- **Solution**: Reduce epochs, increase dropout, add regularization

### Underfitting
- **Symptom**: Both training and validation loss high
- **Solution**: Increase model capacity, train longer

### Poor Convergence
- **Symptom**: Loss oscillates or doesn't decrease
- **Solution**: Adjust learning rate, check data quality

## Best Practices

1. **Start with LoRA**: Most cases don't need full fine-tuning
2. **Monitor validation loss**: Stop before overfitting
3. **Use checkpoints**: Save best performing model
4. **Evaluate on held-out data**: Don't trust training metrics alone
5. **Test on edge cases**: Validate model robustness
6. **Document hyperparameters**: Enable reproducibility
7. **Version control models**: Track model iterations
