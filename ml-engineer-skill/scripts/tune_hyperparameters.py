"""
Hyperparameter Tuning with Optuna
Automated hyperparameter optimization
"""

import logging
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import joblib
import numpy as np

try:
    import optuna
    from optuna.pruners import MedianPruner
    from optuna.samplers import TPESampler
    import optuna.visualization as vis
except ImportError:
    raise ImportError("optuna required: pip install optuna")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TuningConfig:
    n_trials: int = 100
    timeout: Optional[int] = None
    direction: str = "maximize"
    metric_name: str = "accuracy"
    study_name: str = "optimization"

    # Pruning
    enable_pruning: bool = True
    n_startup_trials: int = 10

    # Sampler
    sampler_type: str = "tpe"  # "tpe", "random", "grid"

    @classmethod
    def from_dict(cls, config: Dict[str, Any]) -> 'TuningConfig':
        return cls(**config)


class HyperparameterTuner:
    def __init__(self, config: TuningConfig):
        self.config = config
        self.study = None
        self.best_params = None
        self.best_value = None

    def create_study(self, objective: Callable, storage_path: Optional[str] = None):
        logger.info(f"Creating study: {self.config.study_name}")

        sampler = self._get_sampler()

        pruner = None
        if self.config.enable_pruning:
            pruner = MedianPruner(
                n_startup_trials=self.config.n_startup_trials,
                n_warmup_steps=5
            )

        self.study = optuna.create_study(
            study_name=self.config.study_name,
            direction=self.config.direction,
            sampler=sampler,
            pruner=pruner,
            storage=f"sqlite:///{storage_path}" if storage_path else None,
            load_if_exists=True
        )

    def _get_sampler(self):
        if self.config.sampler_type == "tpe":
            return TPESampler(seed=42)
        elif self.config.sampler_type == "random":
            return optuna.samplers.RandomSampler(seed=42)
        else:
            return optuna.samplers.GridSampler()

    def optimize(self, objective: Callable):
        logger.info(
            f"Starting optimization: {self.config.n_trials} trials, "
            f"direction={self.config.direction}"
        )

        self.study.optimize(
            objective,
            n_trials=self.config.n_trials,
            timeout=self.config.timeout,
            show_progress_bar=True
        )

        self.best_params = self.study.best_params
        self.best_value = self.study.best_value

        logger.info(f"Best value: {self.best_value}")
        logger.info(f"Best params: {self.best_params}")

    def suggest_hyperparameters(self, trial: optuna.Trial, param_space: Dict[str, Any]) -> Dict[str, Any]:
        params = {}

        for param_name, param_config in param_space.items():
            param_type = param_config['type']

            if param_type == 'float':
                if param_config.get('log', False):
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_config['low'],
                        param_config['high'],
                        log=True
                    )
                else:
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_config['low'],
                        param_config['high']
                    )

            elif param_type == 'int':
                if param_config.get('log', False):
                    params[param_name] = trial.suggest_int(
                        param_name,
                        param_config['low'],
                        param_config['high'],
                        log=True
                    )
                else:
                    params[param_name] = trial.suggest_int(
                        param_name,
                        param_config['low'],
                        param_config['high']
                    )

            elif param_type == 'categorical':
                params[param_name] = trial.suggest_categorical(
                    param_name,
                    param_config['choices']
                )

            elif param_type == 'discrete_uniform':
                params[param_name] = trial.suggest_discrete_uniform(
                    param_name,
                    param_config['low'],
                    param_config['high'],
                    param_config['q']
                )

        return params

    def get_best_trial(self) -> optuna.trial.FrozenTrial:
        return self.study.best_trial

    def get_trials_dataframe(self):
        return self.study.trials_dataframe()

    def plot_optimization_history(self, save_path: Optional[str] = None):
        fig = vis.plot_optimization_history(self.study)
        if save_path:
            fig.write_html(save_path)
        return fig

    def plot_param_importances(self, save_path: Optional[str] = None):
        fig = vis.plot_param_importances(self.study)
        if save_path:
            fig.write_html(save_path)
        return fig

    def plot_parallel_coordinate(self, save_path: Optional[str] = None):
        fig = vis.plot_parallel_coordinate(self.study)
        if save_path:
            fig.write_html(save_path)
        return fig

    def save_study(self, filepath: str):
        joblib.dump(self.study, filepath)
        logger.info(f"Study saved to {filepath}")

    def load_study(self, filepath: str):
        self.study = joblib.load(filepath)
        self.best_params = self.study.best_params
        self.best_value = self.study.best_value
        logger.info(f"Study loaded from {filepath}")


def create_rf_param_space() -> Dict[str, Any]:
    return {
        'n_estimators': {
            'type': 'int',
            'low': 10,
            'high': 500
        },
        'max_depth': {
            'type': 'int',
            'low': 5,
            'high': 50
        },
        'min_samples_split': {
            'type': 'int',
            'low': 2,
            'high': 20
        },
        'min_samples_leaf': {
            'type': 'int',
            'low': 1,
            'high': 10
        },
        'max_features': {
            'type': 'categorical',
            'choices': ['sqrt', 'log2', None]
        }
    }


def create_gb_param_space() -> Dict[str, Any]:
    return {
        'n_estimators': {
            'type': 'int',
            'low': 50,
            'high': 500
        },
        'learning_rate': {
            'type': 'float',
            'low': 0.01,
            'high': 0.3,
            'log': True
        },
        'max_depth': {
            'type': 'int',
            'low': 3,
            'high': 20
        },
        'subsample': {
            'type': 'float',
            'low': 0.5,
            'high': 1.0
        }
    }


def main():
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.datasets import make_classification
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import train_test_split

    # Create sample data
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=15,
        n_classes=2,
        random_state=42
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Define objective function
    def objective(trial):
        tuner = HyperparameterTuner(TuningConfig())
        params = tuner.suggest_hyperparameters(trial, create_rf_param_space())

        model = RandomForestClassifier(**params, random_state=42)

        scores = cross_val_score(model, X_train, y_train, cv=5, scoring='accuracy')
        return scores.mean()

    # Run optimization
    config = TuningConfig(n_trials=50, study_name="rf_optimization")
    tuner = HyperparameterTuner(config)
    tuner.create_study(objective)
    tuner.optimize(objective)

    print(f"\nBest parameters: {tuner.best_params}")
    print(f"Best accuracy: {tuner.best_value:.2%}")

    # Visualizations
    tuner.plot_optimization_history("optimization_history.html")
    tuner.plot_param_importances("param_importances.html")

    # Train final model with best params
    best_model = RandomForestClassifier(**tuner.best_params, random_state=42)
    best_model.fit(X_train, y_train)

    test_accuracy = best_model.score(X_test, y_test)
    print(f"Test accuracy: {test_accuracy:.2%}")


if __name__ == "__main__":
    main()
