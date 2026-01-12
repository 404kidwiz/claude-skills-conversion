"""
OpenAI API Integration with retry logic, rate limiting, and monitoring
Production-ready wrapper for OpenAI API calls
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml

try:
    import openai
    from openai import OpenAI, APIError, RateLimitError, APITimeoutError
except ImportError:
    raise ImportError("OpenAI package required: pip install openai")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class OpenAIConfig:
    api_key: str
    model: str = "gpt-4"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 120
    organization: Optional[str] = None
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    rate_limit_delay: float = 0.5

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'OpenAIConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class OpenAIIntegration:
    def __init__(self, config: OpenAIConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            organization=config.organization,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries
        )
        self.usage_stats = {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                response = self.client.chat.completions.create(
                    model=kwargs.get('model', self.config.model),
                    messages=messages,
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                    temperature=kwargs.get('temperature', self.config.temperature),
                    **{k: v for k, v in kwargs.items() 
                       if k not in ['model', 'max_tokens', 'temperature']}
                )

                self._update_usage(response.usage)
                self.usage_stats['successful_requests'] += 1
                self.usage_stats['total_requests'] += 1

                return {
                    'content': response.choices[0].message.content,
                    'usage': {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    },
                    'model': response.model,
                    'finish_reason': response.choices[0].finish_reason
                }

            except RateLimitError as e:
                logger.warning(f"Rate limit hit (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise

            except APITimeoutError as e:
                logger.warning(f"Timeout (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise

            except APIError as e:
                logger.error(f"API error: {e}")
                self.usage_stats['failed_requests'] += 1
                self.usage_stats['total_requests'] += 1
                raise

    def streaming_chat_completion(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)
                
                stream = self.client.chat.completions.create(
                    model=kwargs.get('model', self.config.model),
                    messages=messages,
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                    temperature=kwargs.get('temperature', self.config.temperature),
                    stream=True,
                    **{k: v for k, v in kwargs.items() 
                       if k not in ['model', 'max_tokens', 'temperature', 'stream']}
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        yield chunk.choices[0].delta.content

                return

            except (RateLimitError, APITimeoutError) as e:
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise

    def embed_text(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
        **kwargs
    ) -> List[List[float]]:
        try:
            response = self.client.embeddings.create(
                model=model,
                input=texts,
                **kwargs
            )
            return [embedding.embedding for embedding in response.data]
        except APIError as e:
            logger.error(f"Embedding error: {e}")
            raise

    def _update_usage(self, usage: Any):
        if usage:
            self.usage_stats['total_tokens'] += usage.total_tokens
            self.usage_stats['prompt_tokens'] += usage.prompt_tokens
            self.usage_stats['completion_tokens'] += usage.completion_tokens

    def get_usage_stats(self) -> Dict[str, Any]:
        return self.usage_stats.copy()

    def estimate_cost(self, pricing: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        input_cost = (self.usage_stats['prompt_tokens'] / 1000) * \
                    pricing.get(self.config.model, {}).get('input', 0.01)
        output_cost = (self.usage_stats['completion_tokens'] / 1000) * \
                     pricing.get(self.config.model, {}).get('output', 0.03)
        
        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost
        }


def main():
    config = OpenAIConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4"
    )

    integration = OpenAIIntegration(config)

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain machine learning in one sentence."}
    ]

    response = integration.chat_completion(messages)
    print("Response:", response['content'])
    print("Usage:", response['usage'])
    print("Stats:", integration.get_usage_stats())


if __name__ == "__main__":
    main()
