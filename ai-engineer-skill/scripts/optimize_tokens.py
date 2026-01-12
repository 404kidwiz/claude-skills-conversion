"""
Token Usage and Cost Optimization
Tracks token usage, estimates costs, and suggests optimizations
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TokenPricing:
    model: str
    input_price_per_1k: float
    output_price_per_1k: float


@dataclass
class TokenUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class UsageRecord:
    model: str
    usage: TokenUsage
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


class TokenTracker:
    def __init__(self):
        self.records: List[UsageRecord] = []
        self.pricing: Dict[str, TokenPricing] = {
            'gpt-4': TokenPricing('gpt-4', 0.03, 0.06),
            'gpt-4-turbo': TokenPricing('gpt-4-turbo', 0.01, 0.03),
            'gpt-3.5-turbo': TokenPricing('gpt-3.5-turbo', 0.0005, 0.0015),
            'claude-3-5-sonnet-20241022': TokenPricing('claude-3-5-sonnet-20241022', 0.003, 0.015),
            'claude-3-opus-20240229': TokenPricing('claude-3-opus-20240229', 0.015, 0.075)
        }

    def record_usage(
        self,
        model: str,
        usage: Dict[str, int],
        metadata: Optional[Dict[str, Any]] = None
    ):
        record = UsageRecord(
            model=model,
            usage=TokenUsage(
                prompt_tokens=usage.get('prompt_tokens', 0),
                completion_tokens=usage.get('completion_tokens', 0),
                total_tokens=usage.get('total_tokens', 0)
            ),
            timestamp=__import__('datetime').datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )
        self.records.append(record)
        logger.debug(f"Recorded usage: {model} - {usage.get('total_tokens', 0)} tokens")

    def get_total_tokens(self, model: Optional[str] = None) -> int:
        total = 0
        for record in self.records:
            if model is None or record.model == model:
                total += record.usage.total_tokens
        return total

    def get_total_cost(self, model: Optional[str] = None) -> float:
        total_cost = 0.0

        for record in self.records:
            if model is not None and record.model != model:
                continue

            pricing = self.pricing.get(record.model)
            if pricing:
                input_cost = (record.usage.prompt_tokens / 1000) * pricing.input_price_per_1k
                output_cost = (record.usage.completion_tokens / 1000) * pricing.output_price_per_1k
                total_cost += input_cost + output_cost

        return total_cost

    def get_cost_by_model(self) -> Dict[str, float]:
        costs = defaultdict(float)
        for record in self.records:
            pricing = self.pricing.get(record.model)
            if pricing:
                input_cost = (record.usage.prompt_tokens / 1000) * pricing.input_price_per_1k
                output_cost = (record.usage.completion_tokens / 1000) * pricing.output_price_per_1k
                costs[record.model] += input_cost + output_cost
        return dict(costs)

    def get_average_tokens_per_request(self, model: Optional[str] = None) -> float:
        records = [r for r in self.records if model is None or r.model == model]
        if not records:
            return 0.0
        return sum(r.usage.total_tokens for r in records) / len(records)

    def get_statistics(self) -> Dict[str, Any]:
        total_tokens = self.get_total_tokens()
        total_cost = self.get_total_cost()
        total_requests = len(self.records)

        avg_tokens = 0.0
        if total_requests > 0:
            avg_tokens = total_tokens / total_requests

        return {
            'total_requests': total_requests,
            'total_tokens': total_tokens,
            'total_cost': total_cost,
            'average_tokens_per_request': avg_tokens,
            'cost_by_model': self.get_cost_by_model(),
            'requests_by_model': self._count_by_model()
        }

    def _count_by_model(self) -> Dict[str, int]:
        counts = defaultdict(int)
        for record in self.records:
            counts[record.model] += 1
        return dict(counts)

    def export_report(self, filepath: str):
        report = {
            'statistics': self.get_statistics(),
            'records': [
                {
                    'model': r.model,
                    'usage': {
                        'prompt_tokens': r.usage.prompt_tokens,
                        'completion_tokens': r.usage.completion_tokens,
                        'total_tokens': r.usage.total_tokens
                    },
                    'timestamp': r.timestamp,
                    'metadata': r.metadata
                }
                for r in self.records
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Exported report to {filepath}")


class TokenOptimizer:
    @staticmethod
    def optimize_prompt(prompt: str, target_tokens: int) -> tuple[str, Dict[str, Any]]:
        approx_tokens = len(prompt.split()) * 1.3

        suggestions = []

        if approx_tokens > target_tokens:
            suggestions.append("Reduce prompt length")
            suggestions.append("Use more concise language")
            suggestions.append("Remove redundant information")
            suggestions.append("Use system prompt for static context")

        return prompt, {
            'estimated_tokens': approx_tokens,
            'target_tokens': target_tokens,
            'optimizations': suggestions
        }

    @staticmethod
    def suggest_model(
        tokens_needed: int,
        budget: float,
        complexity: str = 'medium'
    ) -> Dict[str, Any]:
        models = [
            {'name': 'gpt-3.5-turbo', 'cost_per_1k': 0.002, 'context': 16384, 'quality': 'low'},
            {'name': 'gpt-4-turbo', 'cost_per_1k': 0.04, 'context': 128000, 'quality': 'high'},
            {'name': 'gpt-4', 'cost_per_1k': 0.09, 'context': 8192, 'quality': 'very-high'},
            {'name': 'claude-3-5-sonnet-20241022', 'cost_per_1k': 0.018, 'context': 200000, 'quality': 'high'},
            {'name': 'claude-3-opus-20240229', 'cost_per_1k': 0.09, 'context': 200000, 'quality': 'very-high'}
        ]

        suitable = []
        for model in models:
            if tokens_needed <= model['context']:
                suitable.append(model)

        suitable.sort(key=lambda m: m['cost_per_1k'])

        quality_ranking = {'low': 1, 'medium': 2, 'high': 3, 'very-high': 4}
        min_quality = quality_ranking.get(complexity, 2)

        for model in suitable:
            if quality_ranking.get(model['quality'], 0) >= min_quality:
                estimated_cost = (tokens_needed / 1000) * model['cost_per_1k']
                if estimated_cost <= budget:
                    return {
                        'recommended': model['name'],
                        'estimated_cost': estimated_cost,
                        'reason': 'Best fit for complexity and budget'
                    }

        return {
            'recommended': suitable[0]['name'] if suitable else 'gpt-3.5-turbo',
            'estimated_cost': (tokens_needed / 1000) * suitable[0]['cost_per_1k'] if suitable else 0,
            'reason': 'Best available option'
        }


def main():
    tracker = TokenTracker()

    sample_usages = [
        {'model': 'gpt-4', 'usage': {'prompt_tokens': 100, 'completion_tokens': 50, 'total_tokens': 150}},
        {'model': 'gpt-3.5-turbo', 'usage': {'prompt_tokens': 200, 'completion_tokens': 100, 'total_tokens': 300}},
        {'model': 'gpt-4', 'usage': {'prompt_tokens': 150, 'completion_tokens': 75, 'total_tokens': 225}},
    ]

    for usage in sample_usages:
        tracker.record_usage(**usage)

    print("=== Token Usage Statistics ===")
    stats = tracker.get_statistics()
    print(json.dumps(stats, indent=2))

    print("\n=== Model Suggestion ===")
    suggestion = TokenOptimizer.suggest_model(tokens_needed=5000, budget=0.50, complexity='high')
    print(json.dumps(suggestion, indent=2))


if __name__ == "__main__":
    main()
