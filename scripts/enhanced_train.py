"""
Enhanced Training Script with Advanced Features
"""
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from enhanced_lstm_model import EnhancedLSTMModel
from data_preprocessing import DataPreprocessor

def plot_training_history(history, save_path='models/training_history.png'):
    """Plot and save training history"""
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Enhanced LSTM Training History', fontsize=16)
    
    # Loss
    axes[0, 0].plot(history.history['loss'], label='Training Loss')
    axes[0, 0].plot(history.history['val_loss'], label='Validation Loss')
    axes[0, 0].set_title('Model Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Accuracy
    axes[0, 1].plot(history.history['accuracy'], label='Training Accuracy')
    axes[0, 1].plot(history.history['val_accuracy'], label='Validation Accuracy')
    axes[0, 1].set_title('Model Accuracy')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # AUC
    axes[1, 0].plot(history.history['auc'], label='Training AUC')
    axes[1, 0].plot(history.history['val_auc'], label='Validation AUC')
    axes[1, 0].set_title('Model AUC')
    axes[1, 0].set_xlabel('Epoch')
    axes[1, 0].set_ylabel('AUC')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Precision and Recall
    axes[1, 1].plot(history.history['precision'], label='Training Precision')
    axes[1, 1].plot(history.history['recall'], label='Training Recall')
    axes[1, 1].plot(history.history['val_precision'], label='Val Precision')
    axes[1, 1].plot(history.history['val_recall'], label='Val Recall')
    axes[1, 1].set_title('Precision & Recall')
    axes[1, 1].set_xlabel('Epoch')
    axes[1, 1].set_ylabel('Score')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Training history plot saved to {save_path}")

def main():
    print("=" * 60)
    print("ENHANCED NETWORK TRAFFIC ANOMALY DETECTION - TRAINING")
    print("=" * 60)
    
    # Create directories
    Path('data').mkdir(exist_ok=True)
    Path('models').mkdir(exist_ok=True)
    
    # Initialize preprocessor
    print("\n[1/5] Initializing data preprocessor...")
    preprocessor = DataPreprocessor()
    
    # Generate synthetic data
    print("\n[2/5] Generating synthetic training data...")
    print("Generating 50,000 normal samples...")
    print("Generating 5,000 anomaly samples...")
    X_normal, y_normal = preprocessor.generate_synthetic_data(n_samples=50000, anomaly=False)
    X_anomaly, y_anomaly = preprocessor.generate_synthetic_data(n_samples=5000, anomaly=True)
    
    # Combine and shuffle
    X = np.concatenate([X_normal, X_anomaly])
    y = np.concatenate([y_normal, y_anomaly])
    
    indices = np.random.permutation(len(X))
    X, y = X[indices], y[indices]
    
    print(f"Total dataset size: {len(X)} samples")
    print(f"Normal samples: {np.sum(y == 0)} ({np.sum(y == 0) / len(y) * 100:.1f}%)")
    print(f"Anomaly samples: {np.sum(y == 1)} ({np.sum(y == 1) / len(y) * 100:.1f}%)")
    
    # Preprocess data
    print("\n[3/5] Preprocessing data...")
    X_train, X_val, X_test, y_train, y_val, y_test = preprocessor.prepare_sequences(
        X, y, sequence_length=10, test_size=0.2, val_size=0.1
    )
    
    print(f"Training set: {X_train.shape}")
    print(f"Validation set: {X_val.shape}")
    print(f"Test set: {X_test.shape}")
    
    # Build and train model
    print("\n[4/5] Building enhanced LSTM model...")
    model = EnhancedLSTMModel(input_shape=(X_train.shape[1], X_train.shape[2]))
    model.build_model()
    
    print("\n[5/5] Training model...")
    print("This may take several minutes...")
    history = model.train(
        X_train, y_train,
        X_val, y_val,
        epochs=100,
        batch_size=64
    )
    
    # Evaluate model
    print("\n" + "=" * 60)
    print("EVALUATING MODEL ON TEST SET")
    print("=" * 60)
    metrics = model.evaluate(X_test, y_test)
    
    # Save model and artifacts
    print("\n" + "=" * 60)
    print("SAVING MODEL AND ARTIFACTS")
    print("=" * 60)
    model.save_model('models/enhanced_lstm_model.keras')
    preprocessor.save_scaler('models/scaler.pkl')
    plot_training_history(history)
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Model saved to: models/enhanced_lstm_model.keras")
    print(f"Scaler saved to: models/scaler.pkl")
    print(f"Training plot saved to: models/training_history.png")
    print("\nYou can now use this model for real-time anomaly detection!")

if __name__ == "__main__":
    main()
