"""
Prompt Engineering and Optimization
Tests and optimizes prompts for better performance
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from statistics import mean, stdev
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PromptVariant:
    name: str
    template: str
    description: str = ""


@dataclass
class TestCase:
    input_data: Dict[str, Any]
    expected_output: Any
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    prompt_variant: str
    test_case: str
    output: str
    score: float
    metrics: Dict[str, float]
    latency: float


class PromptOptimizer:
    def __init__(self, llm_func: Callable):
        self.llm_func = llm_func
        self.variants: List[PromptVariant] = []
        self.test_cases: List[TestCase] = []
        self.results: List[EvaluationResult] = []

    def add_variant(self, variant: PromptVariant):
        self.variants.append(variant)
        logger.info(f"Added prompt variant: {variant.name}")

    def add_test_case(self, test_case: TestCase):
        self.test_cases.append(test_case)
        logger.info(f"Added test case: {test_case.metadata.get('name', 'unnamed')}")

    def evaluate(
        self,
        scoring_func: Callable[[str, Any], float],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        logger.info(f"Evaluating {len(self.variants)} prompt variants on {len(self.test_cases)} test cases")

        import time

        total_evaluations = len(self.variants) * len(self.test_cases)
        current = 0

        for variant in self.variants:
            variant_scores = []
            variant_latencies = []

            for test_case in self.test_cases:
                try:
                    prompt = self._render_template(variant.template, test_case.input_data)

                    start_time = time.time()
                    output = self.llm_func(prompt)
                    latency = time.time() - start_time

                    score = scoring_func(output, test_case.expected_output)

                    result = EvaluationResult(
                        prompt_variant=variant.name,
                        test_case=test_case.metadata.get('name', 'unnamed'),
                        output=output,
                        score=score,
                        metrics={'latency': latency},
                        latency=latency
                    )

                    self.results.append(result)
                    variant_scores.append(score)
                    variant_latencies.append(latency)

                    current += 1
                    if progress_callback:
                        progress_callback(current, total_evaluations)

                except Exception as e:
                    logger.error(f"Error evaluating {variant.name} on {test_case.metadata.get('name')}: {e}")

        return self._generate_report()

    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        try:
            return template.format(**variables)
        except KeyError as e:
            logger.error(f"Missing variable in template: {e}")
            raise

    def _generate_report(self) -> Dict[str, Any]:
        variant_stats = {}

        for variant in self.variants:
            variant_results = [r for r in self.results if r.prompt_variant == variant.name]

            if variant_results:
                scores = [r.score for r in variant_results]
                latencies = [r.latency for r in variant_results]

                variant_stats[variant.name] = {
                    'mean_score': mean(scores),
                    'std_score': stdev(scores) if len(scores) > 1 else 0,
                    'mean_latency': mean(latencies),
                    'best_score': max(scores),
                    'worst_score': min(scores),
                    'total_tests': len(variant_results)
                }

        best_variant = max(
            variant_stats.items(),
            key=lambda x: x[1]['mean_score']
        ) if variant_stats else None

        return {
            'variant_stats': variant_stats,
            'best_variant': best_variant[0] if best_variant else None,
            'best_score': best_variant[1]['mean_score'] if best_variant else 0,
            'total_evaluations': len(self.results)
        }

    def ab_test(
        self,
        variant_a: PromptVariant,
        variant_b: PromptVariant,
        test_cases: List[TestCase],
        scoring_func: Callable,
        sample_size: Optional[int] = None
    ) -> Dict[str, Any]:
        """Perform A/B test between two variants"""
        logger.info(f"A/B testing: {variant_a.name} vs {variant_b.name}")

        if sample_size:
            test_cases = test_cases[:sample_size]

        self.variants = [variant_a, variant_b]
        self.test_cases = test_cases

        results = self.evaluate(scoring_func)

        stats_a = results['variant_stats'].get(variant_a.name, {})
        stats_b = results['variant_stats'].get(variant_b.name, {})

        return {
            'variant_a': variant_a.name,
            'variant_b': variant_b.name,
            'score_a': stats_a.get('mean_score', 0),
            'score_b': stats_b.get('mean_score', 0),
            'winner': variant_a.name if stats_a.get('mean_score', 0) > stats_b.get('mean_score', 0) else variant_b.name,
            'improvement': abs(stats_a.get('mean_score', 0) - stats_b.get('mean_score', 0)),
            'is_significant': self._check_significance(
                [r.score for r in self.results if r.prompt_variant == variant_a.name],
                [r.score for r in self.results if r.prompt_variant == variant_b.name]
            )
        }

    def _check_significance(self, scores_a: List[float], scores_b: List[float]) -> bool:
        """Simple significance check using z-test approximation"""
        try:
            from scipy import stats
            _, p_value = stats.ttest_ind(scores_a, scores_b)
            return p_value < 0.05
        except ImportError:
            logger.warning("scipy not available for significance testing")
            return False

    def export_results(self, filepath: str):
        data = {
            'results': [
                {
                    'variant': r.prompt_variant,
                    'test_case': r.test_case,
                    'output': r.output,
                    'score': r.score,
                    'latency': r.latency,
                    'metrics': r.metrics
                }
                for r in self.results
            ],
            'summary': self._generate_report()
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported results to {filepath}")


def create_prompt_variants() -> List[PromptVariant]:
    """Create example prompt variants"""
    return [
        PromptVariant(
            name="basic",
            template="Summarize: {text}",
            description="Basic summarization prompt"
        ),
        PromptVariant(
            name="detailed",
            template="Provide a detailed summary of the following text:\n\n{text}\n\nInclude key points and main ideas.",
            description="Detailed summarization prompt"
        ),
        PromptVariant(
            name="structured",
            template="Summarize the following text in 3 bullet points:\n\n{text}",
            description="Structured output prompt"
        ),
        PromptVariant(
            name="role_based",
            template="You are a professional editor. Create a concise summary of:\n\n{text}",
            description="Role-based prompt"
        )
    ]


def create_test_cases() -> List[TestCase]:
    """Create example test cases"""
    sample_text = "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."

    return [
        TestCase(
            input_data={'text': sample_text},
            expected_output="Machine learning enables computers to learn from experience without explicit programming.",
            metadata={'name': 'simple_summary'}
        ),
        TestCase(
            input_data={'text': sample_text},
            expected_output="Machine learning: a subset of AI for learning from experience.",
            metadata={'name': 'concise_summary'}
        )
    ]


def mock_llm(prompt: str) -> str:
    """Mock LLM function for demonstration"""
    return f"Generated response for: {prompt[:50]}..."


def mock_scoring(output: str, expected: str) -> float:
    """Mock scoring function - simple word overlap"""
    output_words = set(output.lower().split())
    expected_words = set(expected.lower().split())

    overlap = len(output_words & expected_words)
    total = len(expected_words)

    return overlap / total if total > 0 else 0


def main():
    optimizer = PromptOptimizer(mock_llm)

    variants = create_prompt_variants()
    for variant in variants:
        optimizer.add_variant(variant)

    test_cases = create_test_cases()
    for tc in test_cases:
        optimizer.add_test_case(tc)

    results = optimizer.evaluate(mock_scoring)

    print("\n=== Prompt Optimization Results ===")
    print(f"Best variant: {results['best_variant']}")
    print(f"Best score: {results['best_score']:.2%}")

    print("\n--- Variant Statistics ---")
    for name, stats in results['variant_stats'].items():
        print(f"{name}:")
        print(f"  Mean score: {stats['mean_score']:.2%}")
        print(f"  Mean latency: {stats['mean_latency']:.3f}s")


if __name__ == "__main__":
    main()
