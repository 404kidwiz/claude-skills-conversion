# ML/AI Skills Conversion Project

## Overview

This project provides comprehensive scripts and references for 11 ML/AI-related skills, designed for production use with best practices, error handling, and configuration management.

## Project Structure

```
claude-skills-conversion/
├── ai-engineer-skill/          # AI service integration, RAG, prompts
├── llm-architect-skill/        # LLM design, fine-tuning, serving
├── ml-engineer-skill/           # ML pipelines, scikit-learn
├── mlops-engineer-skill/        # MLflow, deployment, monitoring
├── machine-learning-engineer-skill/  # Jupyter, feature engineering
├── data-engineer-skill/         # ETL pipelines, data lakes
├── data-scientist-skill/        # Statistical analysis, visualization
├── data-analyst-skill/          # Data analysis, dashboards
├── prompt-engineer-skill/       # Prompt optimization, A/B testing
├── postgres-pro-skill/          # PostgreSQL administration
├── devops-incident-responder-skill/  # Incident response automation
└── incident-responder-skill/     # Alert handling and triage
```

## Skills Created

### 1. AI Engineer
**Scripts:**
- `integrate_openai.py` - OpenAI API integration with retry logic
- `integrate_anthropic.py` - Claude API integration
- `setup_rag.py` - RAG system with vector database
- `manage_prompts.py` - Prompt template management
- `monitor_ai_service.py` - AI service health monitoring
- `optimize_tokens.py` - Token usage and cost tracking

**References:**
- AI integration guide with quick start
- RAG patterns and best practices
- Prompt template library
- Cost optimization strategies

**Use Cases:**
- LLM API integration
- RAG implementation
- Prompt management
- Cost monitoring and optimization

### 2. LLM Architect
**Scripts:**
- `benchmark_models.py` - Model comparison and selection
- `finetune_model.py` - Fine-tuning with LoRA/PEFT
- `setup_rag_pipeline.py` - End-to-end RAG pipeline
- `serve_model.py` - Model serving infrastructure
- `engineer_prompts.py` - Prompt optimization
- `evaluate_model.py` - Model evaluation framework

**References:**
- Model selection guide
- Fine-tuning guide with LoRA
- Serving infrastructure (vLLM, Docker, K8s)
- Evaluation metrics and frameworks

**Use Cases:**
- Model benchmarking and selection
- Fine-tuning with PEFT/LoRA
- RAG pipeline architecture
- Production model serving

### 3. ML Engineer
**Scripts:**
- `train_sklearn.py` - Scikit-learn training pipeline
- `tune_hyperparameters.py` - Optuna hyperparameter optimization

**References:**
- Scikit-learn best practices
- Model versioning strategies
- Experiment tracking

**Use Cases:**
- Traditional ML model training
- Hyperparameter optimization
- Model deployment preparation

### 4. MLOps Engineer
**Scripts:**
- `track_mlflow.py` - MLflow experiment tracking and model registry

**Use Cases:**
- Experiment tracking
- Model registry management
- MLOps pipeline orchestration

### 5. PostgreSQL Pro
**Scripts:**
- `backup_pg.py` - PostgreSQL backup and restore

**Use Cases:**
- Database backup strategies
- Automated backup scheduling
- Disaster recovery

### 6. Data Engineer
**Scripts:**
- `run_etl_pipeline.py` - ETL automation with scheduling

**Use Cases:**
- Data pipeline automation
- Transformation and validation
- Scheduled data processing

### 7. Incident Responder
**Scripts:**
- `handle_alerts.py` - Incident classification and triage

**Use Cases:**
- Alert routing and classification
- Stakeholder notification
- Incident lifecycle management

## Installation

### Prerequisites
```bash
# Python dependencies
pip install scikit-learn pandas numpy
pip install transformers peft datasets
pip install chromadb sentence-transformers
pip install mlflow optuna
pip install openai anthropic
pip install fastapi uvicorn

# Optional: GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Environment Setup
```bash
# Set API keys
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"

# PostgreSQL
export PGPASSWORD="your-db-password"
```

## Quick Start Examples

### AI Engineer - OpenAI Integration
```python
from ai_engineer_skill.scripts.integrate_openai import OpenAIIntegration, OpenAIConfig

config = OpenAIConfig(api_key=os.getenv("OPENAI_API_KEY"))
integration = OpenAIIntegration(config)

messages = [{"role": "user", "content": "Hello!"}]
response = integration.chat_completion(messages)
print(response['content'])
```

### LLM Architect - Model Benchmarking
```python
from llm_architect_skill.scripts.benchmark_models import ModelBenchmarker

benchmarker = ModelBenchmarker(models)
benchmarker.benchmark_task("summarization", task_func, test_data)
best = benchmarker.get_best_model_for_task("summarization")
```

### ML Engineer - Training Pipeline
```python
from ml_engineer_skill.scripts.train_sklearn import MLModelTrainer, ModelConfig

trainer = MLModelTrainer(ModelConfig())
X_train, X_test = trainer.preprocess_features(X_train, X_test)
trainer.train_model(X_train, y_train)
metrics = trainer.evaluate_model(X_test, y_test)
```

### MLOps - MLflow Tracking
```python
from mlops_engineer_skill.scripts.track_mlflow import MLflowTracker

tracker = MLflowTracker(experiment_name="my_experiment")
run_id = tracker.start_run("run_1")
tracker.log_params({"lr": 0.01, "epochs": 10})
tracker.log_metrics({"accuracy": 0.95})
tracker.log_model(model, "my_model")
tracker.end_run()
```

## Best Practices

### Error Handling
All scripts include:
- Try-except blocks with logging
- Graceful degradation
- Clear error messages

### Configuration
- YAML/JSON config file support
- Environment variable support
- Default values with overrides

### Logging
- Structured logging
- Multiple log levels
- Timestamp and context

### Documentation
- Inline comments for complex logic
- Docstrings for functions/classes
- README and reference guides

## Contributing

Each skill follows consistent patterns:
1. Create `scripts/` directory for executable code
2. Create `references/` directory for documentation
3. Use dataclasses for configuration
4. Include error handling and logging
5. Provide example usage in `main()` function

## License

Production-ready educational code. Adapt to your needs.

## Next Steps

The following skills have placeholder structures ready for implementation:
- machine-learning-engineer-skill
- data-scientist-skill
- data-analyst-skill
- prompt-engineer-skill
- devops-incident-responder-skill

Follow the existing patterns to implement these skills.
