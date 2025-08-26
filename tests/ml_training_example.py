import fckprint
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import time

# Generate synthetic dataset
@fckprint.snoop(watch=('n_samples', 'n_features', 'n_classes'))
def create_dataset():
    print("🎯 Creating synthetic dataset...")
    n_samples = 1000
    n_features = 20
    n_classes = 3
    
    X, y = make_classification(
        n_samples=n_samples,
        n_features=n_features,
        n_classes=n_classes,
        n_informative=15,
        n_redundant=5,
        random_state=42
    )
    
    return X, y

# Data preprocessing with detailed monitoring
@fckprint.snoop(watch_explode=('data_stats',))
def preprocess_data(X, y):
    print("🔧 Preprocessing data...")
    
    data_stats = {
        'original_shape': X.shape,
        'missing_values': np.isnan(X).sum(),
        'class_distribution': np.bincount(y),
        'feature_means': X.mean(axis=0)[:5],  # First 5 features only for brevity
        'feature_stds': X.std(axis=0)[:5]
    }
    
    # Normalize features
    X_normalized = (X - X.mean(axis=0)) / X.std(axis=0)
    
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(
        X_normalized, y, test_size=0.2, random_state=42, stratify=y
    )
    
    data_stats['train_shape'] = X_train.shape
    data_stats['test_shape'] = X_test.shape
    
    return X_train, X_test, y_train, y_test, data_stats

# Model training with performance monitoring
@fckprint.snoop(watch=('model_type', 'training_time', 'train_accuracy', 'test_accuracy'))
def train_model(X_train, X_test, y_train, y_test, model_type='logistic'):
    print(f"🤖 Training {model_type} model...")
    
    start_time = time.time()
    
    if model_type == 'logistic':
        model = LogisticRegression(random_state=42, max_iter=1000)
    elif model_type == 'random_forest':
        model = RandomForestClassifier(n_estimators=100, random_state=42)
    else:
        raise ValueError(f"Unknown model type: {model_type}")
    
    # Train the model
    model.fit(X_train, y_train)
    
    training_time = time.time() - start_time
    
    # Make predictions
    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)
    
    # Calculate accuracies
    train_accuracy = accuracy_score(y_train, train_predictions)
    test_accuracy = accuracy_score(y_test, test_predictions)
    
    return model, train_predictions, test_predictions, {
        'training_time': training_time,
        'train_accuracy': train_accuracy,
        'test_accuracy': test_accuracy
    }

# Feature importance analysis
@fckprint.snoop(watch_explode=('feature_importance',))
def analyze_feature_importance(model, model_type):
    print("📊 Analyzing feature importance...")
    
    if model_type == 'logistic':
        # For logistic regression, use coefficient magnitudes
        feature_importance = np.abs(model.coef_).mean(axis=0)
    elif model_type == 'random_forest':
        # For random forest, use built-in feature importance
        feature_importance = model.feature_importances_
    
    # Get top 5 most important features
    top_features = np.argsort(feature_importance)[-5:][::-1]
    
    feature_analysis = {
        'top_5_features': top_features.tolist(),
        'top_5_importance': feature_importance[top_features].tolist(),
        'mean_importance': feature_importance.mean(),
        'std_importance': feature_importance.std()
    }
    
    return feature_analysis

# Model comparison with detailed logging
@fckprint.snoop(watch=('best_model', 'performance_diff'))
def compare_models(X_train, X_test, y_train, y_test):
    print("🔄 Comparing different models...")
    
    models_to_test = ['logistic', 'random_forest']
    results = {}
    
    for model_type in models_to_test:
        print(f"\n--- Testing {model_type} ---")
        
        model, train_pred, test_pred, metrics = train_model(
            X_train, X_test, y_train, y_test, model_type
        )
        
        feature_analysis = analyze_feature_importance(model, model_type)
        
        results[model_type] = {
            'model': model,
            'metrics': metrics,
            'feature_analysis': feature_analysis
        }
    
    # Determine best model
    best_model = max(results.keys(), key=lambda k: results[k]['metrics']['test_accuracy'])
    performance_diff = (
        results[best_model]['metrics']['test_accuracy'] - 
        min(results[k]['metrics']['test_accuracy'] for k in results.keys())
    )
    
    return results, best_model

# Hyperparameter tuning simulation
@fckprint.snoop(watch=('current_params', 'current_score', 'best_params', 'best_score'))
def hyperparameter_tuning_simulation(X_train, X_test, y_train, y_test):
    print("🎛️  Simulating hyperparameter tuning...")
    
    # Simulate different hyperparameters for Random Forest
    param_grid = [
        {'n_estimators': 50, 'max_depth': 5},
        {'n_estimators': 100, 'max_depth': 10},
        {'n_estimators': 150, 'max_depth': 15},
        {'n_estimators': 200, 'max_depth': None}
    ]
    
    best_score = 0
    best_params = None
    
    for current_params in param_grid:
        model = RandomForestClassifier(
            n_estimators=current_params['n_estimators'],
            max_depth=current_params['max_depth'],
            random_state=42
        )
        
        model.fit(X_train, y_train)
        current_score = model.score(X_test, y_test)
        
        if current_score > best_score:
            best_score = current_score
            best_params = current_params.copy()
    
    return best_params, best_score

# Main training pipeline
@fckprint.snoop(prefix='PIPELINE: ')
def ml_training_pipeline():
    print("🚀 Starting ML Training Pipeline with fckprint debugging!")
    print("=" * 60)
    
    # Step 1: Create dataset
    X, y = create_dataset()
    
    # Step 2: Preprocess data
    X_train, X_test, y_train, y_test, data_stats = preprocess_data(X, y)
    
    # Step 3: Compare models
    results, best_model = compare_models(X_train, X_test, y_train, y_test)
    
    # Step 4: Hyperparameter tuning
    best_params, best_score = hyperparameter_tuning_simulation(X_train, X_test, y_train, y_test)
    
    print("\n" + "=" * 60)
    print("🎉 Pipeline completed!")
    print(f"Best model: {best_model}")
    print(f"Best hyperparameters: {best_params}")
    print(f"Best score: {best_score:.4f}")
    
    return results, best_params, best_score

if __name__ == "__main__":
    # Run the complete ML pipeline with fckprint monitoring
    results, best_params, best_score = ml_training_pipeline() 