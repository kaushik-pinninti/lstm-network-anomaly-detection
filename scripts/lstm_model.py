"""
LSTM Model Architecture
Implements the neural network for anomaly detection
"""

import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models, callbacks
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
import config
import os


class LSTMAnomalyDetector:
    """LSTM-based Network Traffic Anomaly Detector"""
    
    def __init__(self, input_shape: tuple):
        """
        Initialize the LSTM model
        
        Args:
            input_shape: (sequence_length, n_features)
        """
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build the LSTM architecture"""
        print("\n" + "="*50)
        print("BUILDING LSTM MODEL")
        print("="*50)
        
        model = models.Sequential([
            # Input layer
            layers.Input(shape=self.input_shape),
            
            # First LSTM layer with dropout
            layers.LSTM(
                units=config.LSTM_UNITS[0],
                return_sequences=True,
                activation='tanh',
                recurrent_dropout=0.2
            ),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Second LSTM layer
            layers.LSTM(
                units=config.LSTM_UNITS[1],
                return_sequences=False,
                activation='tanh',
                recurrent_dropout=0.2
            ),
            layers.Dropout(config.DROPOUT_RATE),
            
            # Dense layers
            layers.Dense(config.DENSE_UNITS, activation='relu'),
            layers.Dropout(config.DROPOUT_RATE / 2),
            
            # Output layer (binary classification)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=config.LEARNING_RATE),
            loss='binary_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        self.model = model
        
        print("\nModel Architecture:")
        print(model.summary())
        print(f"\nTotal parameters: {model.count_params():,}")
        
        return model
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None):
        """
        Train the LSTM model
        
        Args:
            X_train: Training sequences
            y_train: Training labels
            X_val: Validation sequences (optional)
            y_val: Validation labels (optional)
        """
        print("\n" + "="*50)
        print("TRAINING MODEL")
        print("="*50)
        
        if self.model is None:
            raise ValueError("Model not built. Call build_model() first.")
        
        # Callbacks
        callback_list = [
            callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            callbacks.ModelCheckpoint(
                filepath=config.MODEL_PATH,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Prepare validation data
        if X_val is None:
            validation_data = None
            validation_split = config.VALIDATION_SPLIT
        else:
            validation_data = (X_val, y_val)
            validation_split = 0.0
        
        # Train the model
        print(f"\nTraining for up to {config.EPOCHS} epochs...")
        print(f"Batch size: {config.BATCH_SIZE}")
        
        self.history = self.model.fit(
            X_train, y_train,
            batch_size=config.BATCH_SIZE,
            epochs=config.EPOCHS,
            validation_split=validation_split,
            validation_data=validation_data,
            callbacks=callback_list,
            verbose=1
        )
        
        print("\nTraining completed!")
        
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray):
        """Evaluate the model and print metrics"""
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        
        # Predictions
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        
        # Metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary'
        )
        
        print(f"\nTest Set Performance:")
        print(f"{'='*40}")
        print(f"Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
        print(f"Precision: {precision:.4f}")
        print(f"Recall:    {recall:.4f}")
        print(f"F1-Score:  {f1:.4f}")
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        print(f"\nConfusion Matrix:")
        print(f"{'='*40}")
        print(f"                Predicted")
        print(f"              Normal  Anomaly")
        print(f"Actual Normal   {cm[0][0]:5d}   {cm[0][1]:5d}")
        print(f"      Anomaly   {cm[1][0]:5d}   {cm[1][1]:5d}")
        
        # Classification Report
        print(f"\nDetailed Classification Report:")
        print(f"{'='*40}")
        print(classification_report(
            y_test, y_pred, 
            target_names=['Normal', 'Anomaly']
        ))
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist()
        }
    
    def plot_training_history(self, save_path: str = None):
        """Plot training history"""
        if self.history is None:
            print("No training history available")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train')
        if 'val_accuracy' in self.history.history:
            axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train')
        if 'val_loss' in self.history.history:
            axes[0, 1].plot(self.history.history['val_loss'], label='Validation')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Train')
        if 'val_precision' in self.history.history:
            axes[1, 0].plot(self.history.history['val_precision'], label='Validation')
        axes[1, 0].set_title('Model Precision')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Train')
        if 'val_recall' in self.history.history:
            axes[1, 1].plot(self.history.history['val_recall'], label='Validation')
        axes[1, 1].set_title('Model Recall')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"\nTraining history plot saved to {save_path}")
        
        plt.show()
    
    def save_model(self, filepath: str = None):
        """Save the trained model"""
        if filepath is None:
            filepath = config.MODEL_PATH
        
        self.model.save(filepath)
        print(f"\nModel saved to {filepath}")
    
    def load_model(self, filepath: str = None):
        """Load a trained model"""
        if filepath is None:
            filepath = config.MODEL_PATH
        
        self.model = keras.models.load_model(filepath)
        print(f"\nModel loaded from {filepath}")
    
    def predict(self, X: np.ndarray, threshold: float = None) -> tuple:
        """
        Make predictions on new data
        
        Returns:
            predictions (0 or 1), probabilities
        """
        if threshold is None:
            threshold = 0.5
        
        probabilities = self.model.predict(X, verbose=0)
        predictions = (probabilities > threshold).astype(int).flatten()
        
        return predictions, probabilities.flatten()


if __name__ == "__main__":
    print("LSTM Model module loaded successfully")
    print("Use train_model.py to train the model")
