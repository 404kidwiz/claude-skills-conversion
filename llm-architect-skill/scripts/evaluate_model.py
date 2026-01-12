"""
Model Evaluation Framework
Comprehensive evaluation of model performance
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
import time

try:
    from rouge_score import rouge_scorer
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("rouge-score and nltk not available for NLP metrics")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(Enum):
    EXACT_MATCH = "exact_match"
    ROUGE = "rouge"
    BLEU = "bleu"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    CUSTOM = "custom"


@dataclass
class EvaluationMetric:
    name: str
    metric_type: MetricType
    description: str = ""
    higher_is_better: bool = True


@dataclass
class EvaluationResult:
    model_name: str
    metric_name: str
    score: float
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dataset:
    name: str
    inputs: List[str]
    references: List[str]
    metadata: Optional[List[Dict[str, Any]]] = None


class ModelEvaluator:
    def __init__(self):
        self.metrics: List[EvaluationMetric] = []
        self.results: List[EvaluationResult] = []

    def add_metric(self, metric: EvaluationMetric):
        self.metrics.append(metric)
        logger.info(f"Added metric: {metric.name}")

    def evaluate_model(
        self,
        model_name: str,
        generate_func: Callable[[str], str],
        dataset: Dataset,
        metrics: Optional[List[EvaluationMetric]] = None
    ) -> Dict[str, Any]:
        logger.info(f"Evaluating model {model_name} on dataset {dataset.name}")

        if metrics is None:
            metrics = self.metrics

        predictions = []
        for i, input_text in enumerate(dataset.inputs):
            try:
                prediction = generate_func(input_text)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error generating for input {i}: {e}")
                predictions.append("")

        evaluation_results = []

        for metric in metrics:
            logger.info(f"  Computing {metric.name}")
            scores = []

            for i, (pred, ref) in enumerate(zip(predictions, dataset.references)):
                try:
                    if metric.metric_type == MetricType.EXACT_MATCH:
                        score = self._exact_match(pred, ref)
                    elif metric.metric_type == MetricType.ROUGE:
                        score = self._rouge_score(pred, ref)
                    elif metric.metric_type == MetricType.BLEU:
                        score = self._bleu_score(pred, ref)
                    elif metric.metric_type == MetricType.SEMANTIC_SIMILARITY:
                        score = self._semantic_similarity(pred, ref)
                    elif metric.metric_type == MetricType.CUSTOM:
                        continue
                    else:
                        score = 0.0

                    scores.append(score)

                except Exception as e:
                    logger.error(f"Error computing {metric.name} for sample {i}: {e}")
                    scores.append(0.0)

            if scores:
                mean_score = sum(scores) / len(scores)
                evaluation_results.append(EvaluationResult(
                    model_name=model_name,
                    metric_name=metric.name,
                    score=mean_score,
                    details={
                        'individual_scores': scores,
                        'min': min(scores),
                        'max': max(scores)
                    }
                ))

        self.results.extend(evaluation_results)

        return self._generate_report(model_name, dataset.name, evaluation_results)

    def _exact_match(self, prediction: str, reference: str) -> float:
        prediction = prediction.strip().lower()
        reference = reference.strip().lower()
        return 1.0 if prediction == reference else 0.0

    def _rouge_score(self, prediction: str, reference: str) -> float:
        try:
            scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            scores = scorer.score(reference, prediction)
            return scores['rougeL'].fmeasure
        except:
            return 0.0

    def _bleu_score(self, prediction: str, reference: str) -> float:
        try:
            reference_tokens = [reference.split()]
            prediction_tokens = prediction.split()

            smoothing = SmoothingFunction().method1
            score = sentence_bleu(reference_tokens, prediction_tokens, smoothing_function=smoothing)
            return score
        except:
            return 0.0

    def _semantic_similarity(self, prediction: str, reference: str) -> float:
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            model = SentenceTransformer('all-MiniLM-L6-v2')

            emb1 = model.encode(prediction, convert_to_tensor=True)
            emb2 = model.encode(reference, convert_to_tensor=True)

            similarity = torch.cosine_similarity(emb1.unsqueeze(0), emb2.unsqueeze(0)).item()
            return (similarity + 1) / 2
        except:
            return 0.0

    def _generate_report(
        self,
        model_name: str,
        dataset_name: str,
        results: List[EvaluationResult]
    ) -> Dict[str, Any]:
        return {
            'model_name': model_name,
            'dataset_name': dataset_name,
            'metrics': {
                r.metric_name: {
                    'score': r.score,
                    'details': r.details
                }
                for r in results
            },
            'average_score': sum(r.score for r in results) / len(results) if results else 0
        }

    def compare_models(
        self,
        model_names: List[str],
        generate_funcs: Dict[str, Callable],
        dataset: Dataset
    ) -> Dict[str, Any]:
        logger.info(f"Comparing {len(model_names)} models")

        reports = {}
        for model_name in model_names:
            if model_name in generate_funcs:
                report = self.evaluate_model(model_name, generate_funcs[model_name], dataset)
                reports[model_name] = report

        comparison = self._generate_comparison(reports)
        return comparison

    def _generate_comparison(self, reports: Dict[str, Any]) -> Dict[str, Any]:
        comparison = {'models': reports, 'winners': {}}

        metric_scores = {}
        for model_name, report in reports.items():
            for metric_name, metric_data in report['metrics'].items():
                if metric_name not in metric_scores:
                    metric_scores[metric_name] = {}
                metric_scores[metric_name][model_name] = metric_data['score']

        for metric_name, scores in metric_scores.items():
            metric = next((m for m in self.metrics if m.name == metric_name), None)
            if metric and metric.higher_is_better:
                winner = max(scores.items(), key=lambda x: x[1])
            else:
                winner = min(scores.items(), key=lambda x: x[1])

            comparison['winners'][metric_name] = {
                'model': winner[0],
                'score': winner[1]
            }

        return comparison

    def export_results(self, filepath: str):
        data = {
            'results': [
                {
                    'model': r.model_name,
                    'metric': r.metric_name,
                    'score': r.score,
                    'details': r.details
                }
                for r in self.results
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Exported results to {filepath}")


def create_default_metrics() -> List[EvaluationMetric]:
    return [
        EvaluationMetric(
            name="exact_match",
            metric_type=MetricType.EXACT_MATCH,
            description="Exact match of prediction and reference"
        ),
        EvaluationMetric(
            name="rouge_l",
            metric_type=MetricType.ROUGE,
            description="ROUGE-L F1 score"
        ),
        EvaluationMetric(
            name="bleu",
            metric_type=MetricType.BLEU,
            description="BLEU score"
        )
    ]


def create_sample_dataset() -> Dataset:
    return Dataset(
        name="sample",
        inputs=[
            "What is the capital of France?",
            "Explain machine learning.",
            "Who wrote Hamlet?"
        ],
        references=[
            "Paris",
            "Machine learning enables computers to learn from data.",
            "William Shakespeare"
        ]
    )


def main():
    evaluator = ModelEvaluator()

    metrics = create_default_metrics()
    for metric in metrics:
        evaluator.add_metric(metric)

    dataset = create_sample_dataset()

    def mock_generate(input_text: str) -> str:
        if "France" in input_text:
            return "Paris"
        elif "machine learning" in input_text:
            return "Machine learning enables computers to learn from data."
        else:
            return "William Shakespeare"

    report = evaluator.evaluate_model("mock-model", mock_generate, dataset)

    print("\n=== Evaluation Report ===")
    print(f"Model: {report['model_name']}")
    print(f"Dataset: {report['dataset_name']}")
    print(f"Average Score: {report['average_score']:.2%}")

    print("\n--- Metrics ---")
    for metric_name, metric_data in report['metrics'].items():
        print(f"{metric_name}: {metric_data['score']:.2%}")


if __name__ == "__main__":
    main()
