import fckprint
import numpy as np
import time

# 1. Deep Learning Training Loop Debugging
@fckprint.snoop(watch=('epoch', 'loss', 'learning_rate', 'batch_accuracy'))
def training_step_simulation(model_weights, data_batch, learning_rate=0.01):
    """Simulate a deep learning training step with fckprint monitoring"""
    epoch = 1
    batch_size = 32
    
    # Simulate forward pass
    predictions = np.random.random(batch_size)
    targets = np.random.randint(0, 2, batch_size)
    
    # Calculate loss (simulated)
    loss = np.mean((predictions - targets) ** 2)
    
    # Calculate batch accuracy
    batch_accuracy = np.mean((predictions > 0.5) == targets)
    
    # Simulate gradient computation and weight update
    gradients = np.random.normal(0, 0.1, model_weights.shape)
    model_weights = model_weights - learning_rate * gradients
    
    return model_weights, loss, batch_accuracy

# 2. Data Pipeline Debugging
@fckprint.snoop(watch_explode=('batch_stats', 'preprocessing_time'))
def data_preprocessing_pipeline(raw_data):
    """Monitor data preprocessing with detailed statistics"""
    start_time = time.time()
    
    batch_stats = {
        'original_shape': raw_data.shape,
        'missing_values': np.isnan(raw_data).sum(),
        'outliers_detected': 0,
        'normalization_applied': False
    }
    
    # Step 1: Handle missing values
    if batch_stats['missing_values'] > 0:
        raw_data = np.nan_to_num(raw_data)
        batch_stats['missing_handling'] = 'replaced_with_zero'
    
    # Step 2: Outlier detection
    z_scores = np.abs((raw_data - np.mean(raw_data)) / np.std(raw_data))
    outliers = z_scores > 3
    batch_stats['outliers_detected'] = np.sum(outliers)
    
    # Step 3: Normalization
    normalized_data = (raw_data - np.mean(raw_data)) / np.std(raw_data)
    batch_stats['normalization_applied'] = True
    batch_stats['final_shape'] = normalized_data.shape
    
    preprocessing_time = time.time() - start_time
    
    return normalized_data, batch_stats

# 3. Model Evaluation with Cross-Validation
@fckprint.snoop(watch=('fold', 'train_score', 'val_score', 'score_variance'))
def cross_validation_debugging(X, y, n_folds=5):
    """Debug cross-validation with fold-by-fold monitoring"""
    fold_size = len(X) // n_folds
    train_scores = []
    val_scores = []
    
    for fold in range(n_folds):
        # Create train/val splits
        val_start = fold * fold_size
        val_end = (fold + 1) * fold_size
        
        X_val = X[val_start:val_end]
        y_val = y[val_start:val_end]
        
        X_train = np.concatenate([X[:val_start], X[val_end:]])
        y_train = np.concatenate([y[:val_start], y[val_end:]])
        
        # Simulate model training and evaluation
        train_score = np.random.uniform(0.7, 0.95)  # Simulated training score
        val_score = np.random.uniform(0.6, 0.85)    # Simulated validation score
        
        train_scores.append(train_score)
        val_scores.append(val_score)
        
        # Calculate running variance
        if len(val_scores) > 1:
            score_variance = np.var(val_scores)
        else:
            score_variance = 0.0
    
    return {
        'mean_train_score': np.mean(train_scores),
        'mean_val_score': np.mean(val_scores),
        'score_variance': np.var(val_scores)
    }

# 4. Feature Selection with Performance Tracking
@fckprint.snoop(watch=('n_features', 'current_feature', 'feature_importance', 'cumulative_score'))
def feature_selection_debugging(X, y):
    """Debug feature selection process"""
    n_features = X.shape[1]
    selected_features = []
    cumulative_score = 0.0
    
    # Simulate feature importance scores
    feature_importances = np.random.random(n_features)
    sorted_features = np.argsort(feature_importances)[::-1]
    
    for i, current_feature in enumerate(sorted_features[:10]):  # Select top 10
        feature_importance = feature_importances[current_feature]
        selected_features.append(current_feature)
        
        # Simulate model performance with current feature set
        cumulative_score = min(0.95, cumulative_score + feature_importance * 0.1)
        
        # Early stopping if improvement is minimal
        if i > 0 and cumulative_score - prev_score < 0.01:
            break
            
        prev_score = cumulative_score
    
    return selected_features, cumulative_score

# 5. Learning Curve Analysis
@fckprint.snoop(watch=('sample_size', 'train_error', 'val_error', 'overfitting_gap'))
def learning_curve_analysis(X, y):
    """Analyze learning curves with overfitting detection"""
    sample_sizes = [100, 200, 400, 600, 800]
    results = []
    
    for sample_size in sample_sizes:
        if sample_size > len(X):
            break
            
        # Use subset of data
        X_subset = X[:sample_size]
        y_subset = y[:sample_size]
        
        # Simulate training and validation errors
        train_error = max(0.05, 0.3 - sample_size * 0.0003)  # Decreasing with more data
        val_error = max(0.1, 0.4 - sample_size * 0.0002)     # Decreasing slower
        
        overfitting_gap = val_error - train_error
        
        results.append({
            'sample_size': sample_size,
            'train_error': train_error,
            'val_error': val_error,
            'overfitting_gap': overfitting_gap
        })
    
    return results

# 6. Main ML Debugging Demo
def run_ml_debugging_examples():
    """Run all ML debugging examples"""
    print("🧠 Advanced ML Debugging with fckprint")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    X = np.random.randn(1000, 20)
    y = np.random.randint(0, 2, 1000)
    
    print("\n1️⃣ Training Step Simulation:")
    model_weights = np.random.randn(100)
    for i in range(3):
        model_weights, loss, acc = training_step_simulation(model_weights, X[:32])
        print(f"Step {i+1}: Loss={loss:.4f}, Accuracy={acc:.4f}")
    
    print("\n2️⃣ Data Preprocessing Pipeline:")
    # Add some NaN values for testing
    X_with_nans = X.copy()
    X_with_nans[0, 0] = np.nan
    processed_data, stats = data_preprocessing_pipeline(X_with_nans)
    
    print("\n3️⃣ Cross-Validation Analysis:")
    cv_results = cross_validation_debugging(X, y)
    print(f"CV Results: {cv_results}")
    
    print("\n4️⃣ Feature Selection:")
    selected_features, final_score = feature_selection_debugging(X, y)
    print(f"Selected {len(selected_features)} features, Final Score: {final_score:.4f}")
    
    print("\n5️⃣ Learning Curve Analysis:")
    learning_results = learning_curve_analysis(X, y)
    print(f"Analyzed {len(learning_results)} sample sizes")
    
    print("\n🎉 All ML debugging examples completed!")

if __name__ == "__main__":
    run_ml_debugging_examples() 