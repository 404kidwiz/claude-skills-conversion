"""
Anthropic Claude API Integration with retry logic and monitoring
Production-ready wrapper for Anthropic API calls
"""

import os
import time
import json
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path
import yaml

try:
    import anthropic
    from anthropic import Anthropic, APIError, RateLimitError, APITimeoutError
except ImportError:
    raise ImportError("Anthropic package required: pip install anthropic")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnthropicConfig:
    api_key: str
    model: str = "claude-3-5-sonnet-20241022"
    max_retries: int = 3
    retry_delay: float = 1.0
    timeout: int = 120
    max_tokens: int = 4096
    temperature: float = 0.7
    rate_limit_delay: float = 0.5

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'AnthropicConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class AnthropicIntegration:
    def __init__(self, config: AnthropicConfig):
        self.config = config
        self.client = Anthropic(
            api_key=config.api_key,
            max_retries=config.max_retries,
            timeout=config.timeout
        )
        self.usage_stats = {
            'total_tokens': 0,
            'input_tokens': 0,
            'output_tokens': 0,
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0
        }

    def messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)

                response = self.client.messages.create(
                    model=kwargs.get('model', self.config.model),
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                    temperature=kwargs.get('temperature', self.config.temperature),
                    messages=messages,
                    **{k: v for k, v in kwargs.items()
                       if k not in ['model', 'max_tokens', 'temperature']}
                )

                content = response.content[0].text
                self._update_usage(response.usage)
                self.usage_stats['successful_requests'] += 1
                self.usage_stats['total_requests'] += 1

                return {
                    'content': content,
                    'usage': {
                        'input_tokens': response.usage.input_tokens,
                        'output_tokens': response.usage.output_tokens,
                        'total_tokens': response.usage.input_tokens + response.usage.output_tokens
                    },
                    'model': response.model,
                    'stop_reason': response.stop_reason
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

    def streaming_messages(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        for attempt in range(self.config.max_retries):
            try:
                time.sleep(self.config.rate_limit_delay)

                with self.client.messages.stream(
                    model=kwargs.get('model', self.config.model),
                    max_tokens=kwargs.get('max_tokens', self.config.max_tokens),
                    temperature=kwargs.get('temperature', self.config.temperature),
                    messages=messages,
                    **{k: v for k, v in kwargs.items()
                       if k not in ['model', 'max_tokens', 'temperature']}
                ) as stream:
                    for text in stream.text_stream:
                        yield text

                return

            except (RateLimitError, APITimeoutError) as e:
                if attempt < self.config.max_retries - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise

    def _update_usage(self, usage: Any):
        if usage:
            self.usage_stats['input_tokens'] += usage.input_tokens
            self.usage_stats['output_tokens'] += usage.output_tokens
            self.usage_stats['total_tokens'] += usage.input_tokens + usage.output_tokens

    def get_usage_stats(self) -> Dict[str, Any]:
        return self.usage_stats.copy()

    def estimate_cost(self, pricing: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        input_cost = (self.usage_stats['input_tokens'] / 1000000) * \
                    pricing.get(self.config.model, {}).get('input', 3.0)
        output_cost = (self.usage_stats['output_tokens'] / 1000000) * \
                     pricing.get(self.config.model, {}).get('output', 15.0)

        return {
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': input_cost + output_cost
        }


def main():
    config = AnthropicConfig(
        api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        model="claude-3-5-sonnet-20241022"
    )

    integration = AnthropicIntegration(config)

    messages = [
        {"role": "user", "content": "Explain machine learning in one sentence."}
    ]

    response = integration.messages(messages)
    print("Response:", response['content'])
    print("Usage:", response['usage'])
    print("Stats:", integration.get_usage_stats())


if __name__ == "__main__":
    main()
