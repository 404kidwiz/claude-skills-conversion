# Scikit-Learn Guide

## Overview

Scikit-learn is the most popular Python library for machine learning, providing simple and efficient tools for predictive data analysis.

## Installation

```bash
pip install scikit-learn pandas numpy matplotlib
```

## Quick Start

### Basic Workflow

```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Load data
X, y = load_your_data()

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Predict
y_pred = model.predict(X_test_scaled)

# Evaluate
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {accuracy:.2%}")
```

## Model Selection Guide

### Classification Models

**Random Forest**
- **When**: Most classification tasks, good starting point
- **Pros**: Handles non-linear data, robust to overfitting
- **Cons**: Can be slow on large datasets

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42
)
```

**Gradient Boosting**
- **When**: High accuracy required, structured data
- **Pros**: Best performance on many tasks
- **Cons**: Longer training time, sensitive to overfitting

```python
from sklearn.ensemble import GradientBoostingClassifier

model = GradientBoostingClassifier(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=5
)
```

**Logistic Regression**
- **When**: Binary classification, interpretable results
- **Pros**: Fast, interpretable, good baseline

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    penalty='l2',
    C=1.0,
    random_state=42
)
```

**SVM**
- **When**: Small to medium datasets, clear margin separation
- **Pros**: Effective in high dimensions
- **Cons**: Slow on large datasets

```python
from sklearn.svm import SVC

model = SVC(
    kernel='rbf',
    C=1.0,
    gamma='scale'
)
```

### Regression Models

**Linear Regression**
- **When**: Simple linear relationships, interpretable
- **Pros**: Fast, interpretable

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
```

**Random Forest Regressor**
- **When**: Non-linear relationships, robust model needed
- **Pros**: Handles complex patterns

```python
from sklearn.ensemble import RandomForestRegressor

model = RandomForestRegressor(n_estimators=100)
```

**Gradient Boosting Regressor**
- **When**: High accuracy required
- **Pros**: State-of-the-art for tabular data

```python
from sklearn.ensemble import GradientBoostingRegressor

model = GradientBoostingRegressor(n_estimators=100)
```

## Preprocessing Pipeline

### Complete Pipeline

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Numeric preprocessing
numeric_features = ['age', 'income']
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())
])

# Categorical preprocessing
categorical_features = ['city', 'gender']
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='most_frequent')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))
])

# Combine transformers
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])

# Full pipeline
model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier())
])

model.fit(X_train, y_train)
```

### Feature Scaling

```python
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

# StandardScaler (z-score normalization)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# MinMaxScaler (0-1 range)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# RobustScaler (handles outliers)
scaler = RobustScaler()
X_scaled = scaler.fit_transform(X)
```

### Encoding Categorical Variables

```python
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# Label encoding for ordinal data
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# One-hot encoding for nominal data
ohe = OneHotEncoder(handle_unknown='ignore')
X_encoded = ohe.fit_transform(X_categorical)
```

## Cross-Validation

### K-Fold Cross-Validation

```python
from sklearn.model_selection import cross_val_score

model = RandomForestClassifier(n_estimators=100)
scores = cross_val_score(model, X, y, cv=5)

print(f"CV Scores: {scores}")
print(f"Mean Score: {scores.mean():.2%} (+/- {scores.std() * 2:.2%})")
```

### Stratified K-Fold (for classification)

```python
from sklearn.model_selection import StratifiedKFold, cross_val_score

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf)
```

### Grid Search CV

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(),
    param_grid,
    cv=5,
    scoring='accuracy',
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(f"Best params: {grid_search.best_params_}")
print(f"Best score: {grid_search.best_score_:.2%}")
```

## Feature Engineering

### Creating New Features

```python
import pandas as pd

# Interaction features
X['feature_product'] = X['feature1'] * X['feature2']

# Polynomial features
from sklearn.preprocessing import PolynomialFeatures
poly = PolynomialFeatures(degree=2)
X_poly = poly.fit_transform(X)

# Binning
X['age_bin'] = pd.cut(X['age'], bins=[0, 18, 35, 50, 100], labels=['child', 'young', 'middle', 'senior'])
```

### Feature Selection

```python
from sklearn.feature_selection import SelectKBest, f_classif

# Select top k features
selector = SelectKBest(f_classif, k=10)
X_selected = selector.fit_transform(X, y)

# Get selected feature names
selected_features = [X.columns[i] for i in selector.get_support(indices=True)]
```

## Model Evaluation

### Classification Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report,
    roc_auc_score, roc_curve
)

# Basic metrics
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, average='weighted')
recall = recall_score(y_test, y_pred, average='weighted')
f1 = f1_score(y_test, y_pred, average='weighted')

# Confusion matrix
cm = confusion_matrix(y_test, y_pred)

# Classification report
report = classification_report(y_test, y_pred)

# ROC AUC
from sklearn.preprocessing import label_binarize
y_bin = label_binarize(y_test, classes=[0, 1, 2])
roc_auc = roc_auc_score(y_bin, y_pred_proba, multi_class='ovr')
```

### Regression Metrics

```python
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
```

## Model Persistence

### Save and Load Models

```python
import joblib

# Save model
joblib.dump(model, 'model.pkl')
joblib.dump(scaler, 'scaler.pkl')

# Load model
loaded_model = joblib.load('model.pkl')
loaded_scaler = joblib.load('scaler.pkl')

# Make predictions
y_pred = loaded_model.predict(loaded_scaler.transform(X_test))
```

## Best Practices

1. **Always scale features**: Required for many models
2. **Use cross-validation**: More reliable than single train/test split
3. **Handle class imbalance**: Use class weights or resampling
4. **Start simple**: Begin with Random Forest, then try complex models
5. **Validate on hold-out set**: Don't use test data for tuning
6. **Save preprocessing**: Store scalers/encoders with model
7. **Monitor feature importance**: Understand what drives predictions
8. **Check for overfitting**: Compare train and validation scores

## Common Issues

### Overfitting
- **Symptoms**: High train accuracy, low test accuracy
- **Solutions**:
  - Reduce model complexity
  - Add regularization
  - Increase training data
  - Use cross-validation

### Underfitting
- **Symptoms**: Low accuracy on both train and test
- **Solutions**:
  - Increase model complexity
  - Add more features
  - Reduce regularization
  - Train longer

### Class Imbalance
- **Symptoms**: Poor performance on minority class
- **Solutions**:
  - Use class_weight parameter
  - Resample data (SMOTE, random undersampling)
  - Use appropriate metrics (F1, AUC)

## Resources

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [User Guide](https://scikit-learn.org/stable/user_guide.html)
- [API Reference](https://scikit-learn.org/stable/modules/classes.html)
