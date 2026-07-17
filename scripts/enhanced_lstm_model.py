"""
Enhanced LSTM Model with Attention Mechanism and Improved Architecture
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import json
from pathlib import Path

class AttentionLayer(layers.Layer):
    """Custom attention layer for LSTM"""
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)
    
    def build(self, input_shape):
        self.W = self.add_weight(
            name='attention_weight',
            shape=(input_shape[-1], input_shape[-1]),
            initializer='glorot_uniform',
            trainable=True
        )
        self.b = self.add_weight(
            name='attention_bias',
            shape=(input_shape[-1],),
            initializer='zeros',
            trainable=True
        )
        super(AttentionLayer, self).build(input_shape)
    
    def call(self, inputs):
        # Compute attention scores
        score = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        attention_weights = tf.nn.softmax(score, axis=1)
        context_vector = attention_weights * inputs
        context_vector = tf.reduce_sum(context_vector, axis=1)
        return context_vector

class EnhancedLSTMModel:
    """Enhanced LSTM model with attention mechanism for anomaly detection"""
    
    def __init__(self, input_shape, config_path='scripts/config.py'):
        self.input_shape = input_shape
        self.model = None
        self.history = None
        
    def build_model(self):
        """Build enhanced LSTM architecture with attention"""
        inputs = keras.Input(shape=self.input_shape)
        
        # First LSTM layer with return sequences
        x = layers.Bidirectional(
            layers.LSTM(128, return_sequences=True, dropout=0.3, recurrent_dropout=0.2)
        )(inputs)
        x = layers.BatchNormalization()(x)
        
        # Second LSTM layer with return sequences for attention
        x = layers.Bidirectional(
            layers.LSTM(64, return_sequences=True, dropout=0.3, recurrent_dropout=0.2)
        )(x)
        x = layers.BatchNormalization()(x)
        
        # Attention mechanism
        attention_output = AttentionLayer()(x)
        
        # Dense layers with residual connection
        dense1 = layers.Dense(64, activation='relu')(attention_output)
        dense1 = layers.Dropout(0.4)(dense1)
        dense1 = layers.BatchNormalization()(dense1)
        
        dense2 = layers.Dense(32, activation='relu')(dense1)
        dense2 = layers.Dropout(0.3)(dense2)
        dense2 = layers.BatchNormalization()(dense2)
        
        # Output layer
        outputs = layers.Dense(1, activation='sigmoid')(dense2)
        
        self.model = Model(inputs=inputs, outputs=outputs)
        
        # Compile with advanced optimizer
        optimizer = keras.optimizers.Adam(learning_rate=0.001)
        self.model.compile(
            optimizer=optimizer,
            loss='binary_crossentropy',
            metrics=[
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        )
        
        print("\n=== Enhanced LSTM Model Architecture ===")
        self.model.summary()
        print(f"Total parameters: {self.model.count_params():,}")
        
        return self.model
    
    def train(self, X_train, y_train, X_val, y_val, epochs=100, batch_size=64):
        """Train the model with advanced callbacks"""
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                'models/best_model.keras',
                monitor='val_auc',
                mode='max',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Calculate class weights for imbalanced data
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        total = len(y_train)
        
        class_weight = {
            0: (1 / neg_count) * (total / 2.0),
            1: (1 / pos_count) * (total / 2.0)
        }
        
        print(f"\nClass weights: {class_weight}")
        print(f"Training samples: {len(X_train)}")
        print(f"Validation samples: {len(X_val)}")
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            class_weight=class_weight,
            verbose=1
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        results = self.model.evaluate(X_test, y_test, verbose=0)
        metrics = dict(zip(self.model.metrics_names, results))
        
        # Calculate additional metrics
        y_pred_proba = self.model.predict(X_test, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int)
        
        from sklearn.metrics import confusion_matrix, classification_report
        cm = confusion_matrix(y_test, y_pred)
        
        print("\n=== Model Evaluation ===")
        print(f"Loss: {metrics['loss']:.4f}")
        print(f"Accuracy: {metrics['accuracy']:.4f}")
        print(f"Precision: {metrics['precision']:.4f}")
        print(f"Recall: {metrics['recall']:.4f}")
        print(f"AUC: {metrics['auc']:.4f}")
        print("\nConfusion Matrix:")
        print(cm)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Normal', 'Anomaly']))
        
        return metrics
    
    def save_model(self, path='models/enhanced_lstm_model.keras'):
        """Save the trained model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.model.save(path)
        print(f"Model saved to {path}")
        
        # Save training history
        history_path = path.replace('.keras', '_history.json')
        with open(history_path, 'w') as f:
            json.dump({k: [float(v) for v in vals] for k, vals in self.history.history.items()}, f)
        print(f"Training history saved to {history_path}")
    
    def load_model(self, path='models/enhanced_lstm_model.keras'):
        """Load a trained model"""
        self.model = keras.models.load_model(
            path,
            custom_objects={'AttentionLayer': AttentionLayer}
        )
        print(f"Model loaded from {path}")
        return self.model

if __name__ == "__main__":
    # Test model creation
    print("Creating enhanced LSTM model...")
    model = EnhancedLSTMModel(input_shape=(10, 8))
    model.build_model()
    print("\nModel created successfully!")
