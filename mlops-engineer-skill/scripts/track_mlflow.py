"""
MLflow Experiment Tracking
Track ML experiments, parameters, metrics, and models
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict

try:
    import mlflow
    from mlflow.tracking import MlflowClient
    from mlflow.entities import ViewType
except ImportError:
    raise ImportError("mlflow required: pip install mlflow")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExperimentConfig:
    experiment_name: str
    tracking_uri: Optional[str] = None
    artifact_location: Optional[str] = None

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'ExperimentConfig':
        return cls(**config)


class MLflowTracker:
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.client = None

        self._setup_mlflow()
        self._create_experiment()

    def _setup_mlflow(self):
        if self.config.tracking_uri:
            mlflow.set_tracking_uri(self.config.tracking_uri)
            logger.info(f"MLflow tracking URI: {self.config.tracking_uri}")

        self.client = MlflowClient(
            tracking_uri=self.config.tracking_uri
        )

    def _create_experiment(self):
        try:
            experiment = self.client.get_experiment_by_name(self.config.experiment_name)

            if experiment:
                mlflow.set_experiment(self.config.experiment_name)
                logger.info(f"Using existing experiment: {self.config.experiment_name}")
            else:
                experiment_id = self.client.create_experiment(
                    name=self.config.experiment_name,
                    artifact_location=self.config.artifact_location
                )
                mlflow.set_experiment(self.config.experiment_name)
                logger.info(f"Created experiment: {self.config.experiment_name} (ID: {experiment_id})")

        except Exception as e:
            logger.error(f"Error creating experiment: {e}")
            raise

    def start_run(
        self,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ):
        run = mlflow.start_run(run_name=run_name)

        if tags:
            mlflow.set_tags(tags)

        logger.info(f"Started run: {run.info.run_id}")
        return run.info.run_id

    def log_params(self, params: Dict[str, Any]):
        for key, value in params.items():
            mlflow.log_param(key, value)
        logger.info(f"Logged {len(params)} parameters")

    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        for key, value in metrics.items():
            mlflow.log_metric(key, value, step=step)
        logger.info(f"Logged {len(metrics)} metrics")

    def log_model(
        self,
        model: Any,
        model_name: str,
        model_type: str = "sklearn",
        input_example: Optional[Any] = None,
        signature: Optional[Any] = None
    ):
        if model_type == "sklearn":
            mlflow.sklearn.log_model(
                model,
                artifact_path=model_name,
                input_example=input_example
            )
        elif model_type == "pytorch":
            mlflow.pytorch.log_model(
                model,
                artifact_path=model_name
            )
        elif model_type == "tensorflow":
            mlflow.tensorflow.log_model(
                model,
                artifact_path=model_name
            )
        else:
            mlflow.log_model(model, artifact_path=model_name)

        logger.info(f"Logged model: {model_name}")

    def log_artifact(self, artifact_path: Union[str, Path], artifact_path_in_repo: Optional[str] = None):
        mlflow.log_artifact(str(artifact_path), artifact_path_in_repo)
        logger.info(f"Logged artifact: {artifact_path}")

    def log_artifacts(self, artifact_dir: Union[str, Path]):
        mlflow.log_artifacts(str(artifact_dir))
        logger.info(f"Logged artifacts from: {artifact_dir}")

    def end_run(self, status: str = "FINISHED"):
        mlflow.end_run()
        logger.info(f"Run ended with status: {status}")

    def get_best_runs(
        self,
        metric_name: str,
        n: int = 5,
        order: str = "DESC"
    ) -> List[Dict[str, Any]]:
        experiment = self.client.get_experiment_by_name(self.config.experiment_name)

        runs = self.client.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=[f"metrics.{metric_name} {order}"],
            max_results=n,
            run_view_type=ViewType.ACTIVE_ONLY
        )

        return [
            {
                'run_id': run.info.run_id,
                'status': run.info.status,
                'start_time': run.info.start_time,
                'metrics': run.data.metrics,
                'params': run.data.params
            }
            for run in runs
        ]

    def get_run_history(self, run_id: str, metric_name: str) -> List[Dict[str, Any]]:
        history = self.client.get_metric_history(run_id, metric_name)

        return [
            {
                'step': h.step,
                'value': h.value,
                'timestamp': h.timestamp
            }
            for h in history
        ]

    def compare_runs(self, run_ids: List[str]) -> Dict[str, Any]:
        comparison = {}

        for run_id in run_ids:
            run = self.client.get_run(run_id)
            comparison[run_id] = {
                'metrics': run.data.metrics,
                'params': run.data.params
            }

        return comparison

    def delete_run(self, run_id: str):
        self.client.delete_run(run_id)
        logger.info(f"Deleted run: {run_id}")

    def restore_run(self, run_id: str):
        self.client.restore_run(run_id)
        logger.info(f"Restored run: {run_id}")


class MLflowModelRegistry:
    def __init__(self, tracking_uri: Optional[str] = None):
        self.client = MlflowClient(tracking_uri=tracking_uri)

    def register_model(
        self,
        run_id: str,
        model_name: str,
        model_type: str = "sklearn"
    ):
        model_uri = f"runs:/{run_id}/model"

        model_version = mlflow.register_model(
            model_uri=model_uri,
            name=model_name
        )

        logger.info(f"Registered model: {model_name} v{model_version.version}")
        return model_version

    def stage_model_transition(
        self,
        model_name: str,
        version: str,
        stage: str  # "Staging", "Production", "Archived"
    ):
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )

        logger.info(f"Transitioned {model_name} v{version} to {stage}")

    def get_latest_version(self, model_name: str, stage: Optional[str] = None) -> Dict[str, Any]:
        versions = self.client.get_latest_versions(
            model_name,
            stages=[stage] if stage else None
        )

        if versions:
            version = versions[0]
            return {
                'name': version.name,
                'version': version.version,
                'stage': version.current_stage,
                'run_id': version.run_id,
                'source': version.source
            }

        return {}

    def load_model(self, model_name: str, version: Optional[str] = None, stage: Optional[str] = None):
        if version:
            model_uri = f"models:/{model_name}/{version}"
        elif stage:
            model_uri = f"models:/{model_name}/{stage}"
        else:
            model_uri = f"models:/{model_name}/Production"

        return mlflow.pyfunc.load_model(model_uri)


def main():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score

    # Setup MLflow
    config = ExperimentConfig(
        experiment_name="test_experiment",
        tracking_uri="./mlruns"
    )

    tracker = MLflowTracker(config)

    # Create sample data
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Start run
    run_id = tracker.start_run(run_name="rf_test", tags={"framework": "sklearn"})

    # Log parameters
    params = {
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 2,
        'random_state': 42
    }
    tracker.log_params(params)

    # Train model
    model = RandomForestClassifier(**params)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    # Log metrics
    metrics = {'accuracy': accuracy, 'n_features': X.shape[1]}
    tracker.log_metrics(metrics)

    # Log model
    tracker.log_model(model, "random_forest_model", model_type="sklearn")

    # End run
    tracker.end_run()

    # Get best runs
    best_runs = tracker.get_best_runs('accuracy', n=3)
    print(f"Best runs: {best_runs}")


if __name__ == "__main__":
    main()
