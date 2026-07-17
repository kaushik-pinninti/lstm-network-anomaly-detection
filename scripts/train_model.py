"""
Training Script
Trains the LSTM model on network traffic data
"""

import sys
import numpy as np
from data_preprocessing import DataPreprocessor
from lstm_model import LSTMAnomalyDetector
import config


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print(" NETWORK TRAFFIC ANOMALY DETECTION - TRAINING PIPELINE")
    print("="*60)
    
    # Step 1: Load and preprocess data
    print("\n[STEP 1/4] Loading and preprocessing data...")
    preprocessor = DataPreprocessor()
    
    # Load dataset
    df = preprocessor.load_dataset()
    
    # Prepare training data
    X_train, X_test, y_train, y_test = preprocessor.prepare_training_data(df)
    
    # Save preprocessors
    preprocessor.save_preprocessors()
    
    # Step 2: Build model
    print("\n[STEP 2/4] Building LSTM model...")
    input_shape = (X_train.shape[1], X_train.shape[2])
    detector = LSTMAnomalyDetector(input_shape=input_shape)
    detector.build_model()
    
    # Step 3: Train model
    print("\n[STEP 3/4] Training model...")
    detector.train(X_train, y_train, X_test, y_test)
    
    # Step 4: Evaluate model
    print("\n[STEP 4/4] Evaluating model...")
    metrics = detector.evaluate(X_test, y_test)
    
    # Save model
    detector.save_model()
    
    # Plot training history
    plot_path = config.LOG_DIR + '/training_history.png'
    detector.plot_training_history(save_path=plot_path)
    
    # Summary
    print("\n" + "="*60)
    print(" TRAINING COMPLETE")
    print("="*60)
    print(f"\nModel saved to: {config.MODEL_PATH}")
    print(f"Scaler saved to: {config.SCALER_PATH}")
    print(f"Encoder saved to: {config.ENCODER_PATH}")
    print(f"\nFinal Test Accuracy: {metrics['accuracy']*100:.2f}%")
    print(f"Final Test F1-Score: {metrics['f1_score']:.4f}")
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
