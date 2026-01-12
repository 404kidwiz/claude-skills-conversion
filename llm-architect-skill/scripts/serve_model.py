"""
Model Serving Infrastructure
Sets up model serving with various backends
"""

import logging
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import json
import subprocess
from dataclasses import dataclass

try:
    import uvicorn
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import torch
except ImportError:
    raise ImportError("fastapi and uvicorn required: pip install fastapi uvicorn")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerationRequest(BaseModel):
    model: str
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50


class GenerationResponse(BaseModel):
    generated_text: str
    model: str
    tokens_generated: int
    generation_time: float


@dataclass
class ServingConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    model_path: str = "./models"
    device: str = "auto"  # "cuda", "cpu", "auto"
    max_batch_size: int = 8
    max_sequence_length: int = 2048

    @classmethod
    def from_json(cls, path: str) -> 'ServingConfig':
        with open(path, 'r') as f:
            config = json.load(f)
        return cls(**config)


class ModelServer:
    def __init__(self, config: ServingConfig):
        self.config = config
        self.models: Dict[str, Any] = {}
        self.app = FastAPI(title="Model Server")

        self._setup_routes()

    def load_model(self, model_name: str, model_path: Optional[str] = None):
        """Load a model for serving"""
        logger.info(f"Loading model: {model_name}")

        if model_path is None:
            model_path = Path(self.config.model_path) / model_name

        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM

            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.config.device == "cuda" else torch.float32,
                device_map=self.config.device
            )

            self.models[model_name] = {
                'model': model,
                'tokenizer': tokenizer
            }

            logger.info(f"Model {model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def _setup_routes(self):
        @self.app.get("/")
        async def root():
            return {
                "status": "running",
                "models": list(self.models.keys())
            }

        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "models_loaded": len(self.models)
            }

        @self.app.post("/generate")
        async def generate(request: GenerationRequest) -> GenerationResponse:
            import time

            if request.model not in self.models:
                raise HTTPException(status_code=404, detail=f"Model {request.model} not found")

            model_data = self.models[request.model]
            model = model_data['model']
            tokenizer = model_data['tokenizer']

            try:
                start_time = time.time()

                inputs = tokenizer(
                    request.prompt,
                    return_tensors="pt",
                    max_length=self.config.max_sequence_length,
                    truncation=True
                ).to(model.device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=request.max_tokens,
                        temperature=request.temperature,
                        top_p=request.top_p,
                        top_k=request.top_k,
                        do_sample=True,
                        pad_token_id=tokenizer.pad_token_id or tokenizer.eos_token_id
                    )

                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                generated_text = generated_text[len(request.prompt):]

                generation_time = time.time() - start_time
                tokens_generated = len(tokenizer.encode(generated_text))

                return GenerationResponse(
                    generated_text=generated_text,
                    model=request.model,
                    tokens_generated=tokens_generated,
                    generation_time=generation_time
                )

            except Exception as e:
                logger.error(f"Generation error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/models")
        async def list_models():
            return {
                "models": [
                    {
                        "name": name,
                        "device": str(next(model['model'].parameters()).device)
                    }
                    for name, model in self.models.items()
                ]
            }

    def start(self):
        """Start the model server"""
        logger.info(f"Starting server on {self.config.host}:{self.config.port}")
        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info"
        )


def setup_docker_serving(model_path: str, port: int = 8000):
    """Setup model serving with Docker"""

    dockerfile = """
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    git \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \\
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \\
    transformers \\
    fastapi \\
    uvicorn[standard] \\
    accelerate

COPY ./model_server.py .
COPY ./models ./models

EXPOSE 8000

CMD ["python", "model_server.py", "--host", "0.0.0.0", "--port", "8000"]
"""

    with open("Dockerfile", 'w') as f:
        f.write(dockerfile)

    logger.info("Dockerfile created. Build with: docker build -t model-server .")


def setup_vllm_serving(model_name: str, port: int = 8000):
    """Setup model serving with vLLM (optimized for throughput)"""

    command = [
        "python", "-m", "vllm.entrypoints.api_server",
        "--model", model_name,
        "--port", str(port),
        "--tensor-parallel-size", "1",
        "--gpu-memory-utilization", "0.9"
    ]

    logger.info(f"Starting vLLM server: {' '.join(command)}")
    # subprocess.run(command, check=True)


def setup_text_generation_webui(model_path: str):
    """Setup with Text Generation WebUI (Oobabooga)"""

    logger.info("Setting up Text Generation WebUI")
    logger.info("Clone: https://github.com/oobabooga/text-generation-webui")
    logger.info("Run: python server.py --model-path {model_path} --listen")


def setup_localai(model_path: str, port: int = 8080):
    """Setup LocalAI (OpenAI-compatible API)"""

    logger.info("Setting up LocalAI")
    logger.info("See: https://localai.io/")
    logger.info("Provides OpenAI-compatible API for local models")


def main():
    config = ServingConfig(port=8000)

    server = ModelServer(config)

    server.load_model("gpt2", "gpt2")

    server.start()


if __name__ == "__main__":
    main()
