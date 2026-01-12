"""
Scikit-learn Training Pipeline
Production-ready ML pipeline with scikit-learn
"""

import logging
import joblib
import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict

try:
    import numpy as np
    import pandas as pd
    from sklearn.model_selection import train_test_split, cross_val_score
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score,
        f1_score, classification_report, confusion_matrix
    )
except ImportError:
    raise ImportError("scikit-learn required: pip install scikit-learn")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    model_type: str = "random_forest"
    test_size: float = 0.2
    random_state: int = 42
    scaling: bool = True
    encoding: bool = True

    # Model hyperparameters
    n_estimators: int = 100
    max_depth: Optional[int] = None
    min_samples_split: int = 2
    learning_rate: float = 0.1

    @classmethod
    def from_yaml(cls, path: Union[str, Path]) -> 'ModelConfig':
        with open(path, 'r') as f:
            config = yaml.safe_load(f)
        return cls(**config)


class MLModelTrainer:
    def __init__(self, config: ModelConfig):
        self.config = config
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.feature_names = None

    def load_data(
        self,
        filepath: Union[str, Path],
        target_column: str,
        feature_columns: Optional[List[str]] = None
    ) -> tuple:
        logger.info(f"Loading data from {filepath}")

        if filepath.suffix == '.csv':
            data = pd.read_csv(filepath)
        elif filepath.suffix in ['.xlsx', '.xls']:
            data = pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

        if feature_columns is None:
            feature_columns = [col for col in data.columns if col != target_column]

        X = data[feature_columns]
        y = data[target_column]

        logger.info(f"Features: {X.shape}, Target: {y.shape}")
        return X, y

    def preprocess_features(self, X_train: pd.DataFrame, X_test: Optional[pd.DataFrame] = None) -> tuple:
        X_train_processed = X_train.copy()
        X_test_processed = X_test.copy() if X_test is not None else None

        self.feature_names = X_train.columns.tolist()

        # Encode categorical features
        if self.config.encoding:
            X_train_processed = self._encode_features(X_train_processed, fit=True)
            if X_test_processed is not None:
                X_test_processed = self._encode_features(X_test_processed, fit=False)

        # Scale features
        if self.config.scaling:
            X_train_processed, X_test_processed = self._scale_features(
                X_train_processed, X_test_processed
            )

        return X_train_processed, X_test_processed

    def _encode_features(self, X: pd.DataFrame, fit: bool) -> pd.DataFrame:
        cat_columns = X.select_dtypes(include=['object']).columns.tolist()

        if not cat_columns:
            return X

        X_encoded = X.copy()

        for col in cat_columns:
            if fit:
                encoder = LabelEncoder()
                X_encoded[col] = encoder.fit_transform(X[col].astype(str))
                if not hasattr(self, 'encoders'):
                    self.encoders = {}
                self.encoders[col] = encoder
            else:
                if col in self.encoders:
                    X_encoded[col] = self.encoders[col].transform(X[col].astype(str))

        return X_encoded

    def _scale_features(
        self,
        X_train: pd.DataFrame,
        X_test: Optional[pd.DataFrame]
    ) -> tuple:
        if self.scaler is None:
            self.scaler = StandardScaler()

        X_train_scaled = pd.DataFrame(
            self.scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index
        )

        X_test_scaled = None
        if X_test is not None:
            X_test_scaled = pd.DataFrame(
                self.scaler.transform(X_test),
                columns=X_test.columns,
                index=X_test.index
            )

        return X_train_scaled, X_test_scaled

    def preprocess_target(self, y_train: pd.Series, y_test: Optional[pd.Series] = None) -> tuple:
        if y_train.dtype == 'object':
            if self.label_encoder is None:
                self.label_encoder = LabelEncoder()
                y_train_encoded = self.label_encoder.fit_transform(y_train)
            else:
                y_train_encoded = self.label_encoder.transform(y_train)

            y_test_encoded = None
            if y_test is not None:
                y_test_encoded = self.label_encoder.transform(y_test)

            return y_train_encoded, y_test_encoded

        return y_train, y_test

    def train_model(self, X_train: pd.DataFrame, y_train: pd.Series):
        logger.info(f"Training {self.config.model_type} model")

        if self.config.model_type == "random_forest":
            self.model = RandomForestClassifier(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                min_samples_split=self.config.min_samples_split,
                random_state=self.config.random_state
            )
        elif self.config.model_type == "gradient_boosting":
            self.model = GradientBoostingClassifier(
                n_estimators=self.config.n_estimators,
                learning_rate=self.config.learning_rate,
                max_depth=self.config.max_depth,
                random_state=self.config.random_state
            )
        else:
            raise ValueError(f"Unknown model type: {self.config.model_type}")

        self.model.fit(X_train, y_train)
        logger.info("Model training completed")

    def evaluate_model(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict[str, Any]:
        logger.info("Evaluating model")

        y_pred = self.model.predict(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=0),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=0),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=0)
        }

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_test, y_test, cv=5)
        metrics['cv_mean'] = cv_scores.mean()
        metrics['cv_std'] = cv_scores.std()

        # Classification report
        metrics['classification_report'] = classification_report(y_test, y_pred)

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics['confusion_matrix'] = cm.tolist()

        logger.info(f"Accuracy: {metrics['accuracy']:.2%}")
        return metrics

    def save_model(self, filepath: Union[str, Path]):
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'config': asdict(self.config)
        }

        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")

    def load_model(self, filepath: Union[str, Path]):
        model_data = joblib.load(filepath)

        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.config = ModelConfig(**model_data['config'])

        logger.info(f"Model loaded from {filepath}")

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = self._encode_features(X.copy(), fit=False)
        if self.scaler:
            X_processed = pd.DataFrame(
                self.scaler.transform(X_processed),
                columns=X_processed.columns,
                index=X_processed.index
            )

        return self.model.predict(X_processed)

    def get_feature_importance(self) -> Dict[str, float]:
        if not hasattr(self.model, 'feature_importances_'):
            return {}

        importance = self.model.feature_importances_
        return dict(zip(self.feature_names, importance))


def main():
    config = ModelConfig(model_type="random_forest", n_estimators=50)

    trainer = MLModelTrainer(config)

    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    X = pd.DataFrame({
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.randn(n_samples),
        'feature4': np.random.randn(n_samples)
    })
    y = pd.Series(np.random.randint(0, 2, n_samples), name='target')

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Preprocess
    X_train_processed, X_test_processed = trainer.preprocess_features(X_train, X_test)

    # Train
    trainer.train_model(X_train_processed, y_train)

    # Evaluate
    metrics = trainer.evaluate_model(X_test_processed, y_test)
    print("Metrics:", json.dumps({k: v for k, v in metrics.items() if k != 'classification_report'}, indent=2))

    # Feature importance
    importance = trainer.get_feature_importance()
    print("\nFeature Importance:", importance)


if __name__ == "__main__":
    main()
