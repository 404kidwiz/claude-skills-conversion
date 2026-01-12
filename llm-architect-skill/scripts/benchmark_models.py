"""
Model Benchmarking and Selection
Compares different models on tasks and metrics
"""

import time
import logging
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass, field
import json
import yaml
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    model_name: str
    task_name: str
    accuracy: float
    latency: float
    cost: float
    token_usage: int
    additional_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ModelSpec:
    name: str
    context_window: int
    input_price_per_1k: float
    output_price_per_1k: float
    capabilities: List[str]


class ModelBenchmarker:
    def __init__(self, models: List[ModelSpec]):
        self.models = {m.name: m for m in models}
        self.results: List[BenchmarkResult] = []

    def benchmark_task(
        self,
        task_name: str,
        task_func: Callable,
        test_data: List[Any],
        ground_truth: Optional[List[Any]] = None
    ):
        logger.info(f"Benchmarking task: {task_name}")

        for model_name, model_spec in self.models.items():
            logger.info(f"  Testing model: {model_name}")

            accuracies = []
            latencies = []
            costs = []
            token_usages = []

            for i, test_case in enumerate(test_data):
                start_time = time.time()

                try:
                    result = task_func(model_name, test_case)

                    latency = time.time() - start_time
                    latencies.append(latency)

                    if 'usage' in result:
                        token_usages.append(result['usage'].get('total_tokens', 0))
                        cost = self._calculate_cost(model_spec, result['usage'])
                        costs.append(cost)

                    if ground_truth and i < len(ground_truth):
                        accuracy = self._evaluate_accuracy(result, ground_truth[i])
                        accuracies.append(accuracy)

                except Exception as e:
                    logger.error(f"  Error on test case {i}: {e}")
                    continue

            if accuracies:
                avg_accuracy = sum(accuracies) / len(accuracies)
            else:
                avg_accuracy = 0.0

            avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
            avg_cost = sum(costs) / len(costs) if costs else 0.0
            avg_tokens = sum(token_usages) / len(token_usages) if token_usages else 0

            result = BenchmarkResult(
                model_name=model_name,
                task_name=task_name,
                accuracy=avg_accuracy,
                latency=avg_latency,
                cost=avg_cost,
                token_usage=int(avg_tokens),
                additional_metrics={
                    'test_cases': len(test_data),
                    'successful_cases': len(latencies)
                }
            )

            self.results.append(result)
            logger.info(f"  Result: accuracy={avg_accuracy:.2%}, latency={avg_latency:.2f}s")

    def _calculate_cost(self, model_spec: ModelSpec, usage: Dict[str, int]) -> float:
        input_cost = (usage.get('prompt_tokens', 0) / 1000) * model_spec.input_price_per_1k
        output_cost = (usage.get('completion_tokens', 0) / 1000) * model_spec.output_price_per_1k
        return input_cost + output_cost

    def _evaluate_accuracy(self, result: Dict[str, Any], ground_truth: Any) -> float:
        if isinstance(ground_truth, str):
            return 1.0 if result.get('output', '').strip() == ground_truth.strip() else 0.0
        elif isinstance(ground_truth, list):
            output = result.get('output', [])
            correct = sum(1 for o, g in zip(output, ground_truth) if o == g)
            return correct / max(len(ground_truth), 1)
        else:
            return 1.0 if result.get('output') == ground_truth else 0.0

    def get_best_model_for_task(
        self,
        task_name: str,
        metric: str = 'accuracy'
    ) -> Optional[BenchmarkResult]:
        task_results = [r for r in self.results if r.task_name == task_name]

        if not task_results:
            return None

        if metric == 'accuracy':
            return max(task_results, key=lambda r: r.accuracy)
        elif metric == 'latency':
            return min(task_results, key=lambda r: r.latency)
        elif metric == 'cost':
            return min(task_results, key=lambda r: r.cost)
        else:
            return task_results[0]

    def get_comparison_table(self, task_name: str) -> str:
        task_results = [r for r in self.results if r.task_name == task_name]

        if not task_results:
            return f"No results for task: {task_name}"

        lines = []
        lines.append(f"\n{'Model':<25} {'Accuracy':<10} {'Latency':<10} {'Cost':<10} {'Tokens':<10}")
        lines.append("-" * 65)

        for r in sorted(task_results, key=lambda x: x.accuracy, reverse=True):
            lines.append(
                f"{r.model_name:<25} "
                f"{r.accuracy:>9.2%} "
                f"{r.latency:>9.2f}s "
                f"${r.cost:>8.4f} "
                f"{r.token_usage:>9d}"
            )

        return "\n".join(lines)

    def export_results(self, filepath: str):
        data = {
            'results': [
                {
                    'model': r.model_name,
                    'task': r.task_name,
                    'accuracy': r.accuracy,
                    'latency': r.latency,
                    'cost': r.cost,
                    'token_usage': r.token_usage,
                    'additional_metrics': r.additional_metrics
                }
                for r in self.results
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported results to {filepath}")


# Default model specifications
DEFAULT_MODELS = [
    ModelSpec(
        name="gpt-4",
        context_window=8192,
        input_price_per_1k=0.03,
        output_price_per_1k=0.06,
        capabilities=["reasoning", "coding", "analysis"]
    ),
    ModelSpec(
        name="gpt-4-turbo",
        context_window=128000,
        input_price_per_1k=0.01,
        output_price_per_1k=0.03,
        capabilities=["reasoning", "coding", "vision"]
    ),
    ModelSpec(
        name="gpt-3.5-turbo",
        context_window=16384,
        input_price_per_1k=0.0005,
        output_price_per_1k=0.0015,
        capabilities=["coding", "text-generation"]
    ),
    ModelSpec(
        name="claude-3-5-sonnet-20241022",
        context_window=200000,
        input_price_per_1k=0.003,
        output_price_per_1k=0.015,
        capabilities=["reasoning", "coding", "vision"]
    ),
]


def sample_task(model_name: str, test_case: str) -> Dict[str, Any]:
    """Sample task function for demonstration"""
    return {
        'output': test_case.upper(),
        'usage': {
            'prompt_tokens': len(test_case.split()),
            'completion_tokens': len(test_case.split()),
            'total_tokens': len(test_case.split()) * 2
        }
    }


def main():
    benchmarker = ModelBenchmarker(DEFAULT_MODELS)

    test_data = ["hello", "world", "test"]
    ground_truth = ["HELLO", "WORLD", "TEST"]

    benchmarker.benchmark_task(
        task_name="uppercase_conversion",
        task_func=sample_task,
        test_data=test_data,
        ground_truth=ground_truth
    )

    print(benchmarker.get_comparison_table("uppercase_conversion"))

    best = benchmarker.get_best_model_for_task("uppercase_conversion", metric="accuracy")
    print(f"\nBest model: {best.model_name}")


if __name__ == "__main__":
    main()
