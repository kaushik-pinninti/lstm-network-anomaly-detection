"""
Data Preprocessing Module
Handles data loading, cleaning, normalization, and sequence creation
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
from typing import Tuple, List
import config


class DataPreprocessor:
    """Preprocesses network traffic data for LSTM training"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_columns = []
        
    def load_dataset(self, filepath: str = None) -> pd.DataFrame:
        """
        Load network traffic dataset
        Supports CICIDS2017, NSL-KDD, UNSW-NB15 formats
        """
        if filepath is None:
            filepath = config.DATASET_PATH
            
        print(f"Loading dataset from {filepath}...")
        
        try:
            # Try to load the dataset
            df = pd.read_csv(filepath)
            print(f"Dataset loaded successfully. Shape: {df.shape}")
            return df
        except FileNotFoundError:
            print(f"Dataset not found at {filepath}")
            print("Generating synthetic dataset for demonstration...")
            return self._generate_synthetic_dataset()
    
    def _generate_synthetic_dataset(self, n_samples: int = 10000) -> pd.DataFrame:
        """
        Generate synthetic network traffic data for demonstration
        In production, replace this with real dataset loading
        """
        np.random.seed(config.RANDOM_STATE)
        
        # Generate normal traffic (80% of data)
        n_normal = int(n_samples * 0.8)
        normal_data = {
            'packet_size': np.random.normal(500, 100, n_normal).clip(64, 1500),
            'time_delta': np.random.exponential(0.01, n_normal),
            'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], n_normal, p=[0.7, 0.25, 0.05]),
            'src_port': np.random.randint(1024, 65535, n_normal),
            'dst_port': np.random.choice([80, 443, 22, 21, 53], n_normal),
            'packet_count': np.random.randint(1, 50, n_normal),
            'flow_duration': np.random.exponential(5, n_normal),
            'label': ['Normal'] * n_normal
        }
        
        # Generate anomalous traffic (20% of data)
        n_anomaly = n_samples - n_normal
        anomaly_data = {
            'packet_size': np.random.normal(1200, 300, n_anomaly).clip(64, 1500),
            'time_delta': np.random.exponential(0.001, n_anomaly),
            'protocol': np.random.choice(['TCP', 'UDP', 'ICMP'], n_anomaly, p=[0.5, 0.4, 0.1]),
            'src_port': np.random.randint(1, 65535, n_anomaly),
            'dst_port': np.random.randint(1, 65535, n_anomaly),
            'packet_count': np.random.randint(50, 500, n_anomaly),
            'flow_duration': np.random.exponential(0.5, n_anomaly),
            'label': ['Anomaly'] * n_anomaly
        }
        
        # Combine and shuffle
        df_normal = pd.DataFrame(normal_data)
        df_anomaly = pd.DataFrame(anomaly_data)
        df = pd.concat([df_normal, df_anomaly], ignore_index=True)
        df = df.sample(frac=1, random_state=config.RANDOM_STATE).reset_index(drop=True)
        
        # Add derived features
        df['bytes_per_second'] = df['packet_size'] * df['packet_count'] / (df['flow_duration'] + 0.001)
        df['packets_per_second'] = df['packet_count'] / (df['flow_duration'] + 0.001)
        
        print(f"Generated synthetic dataset with {len(df)} samples")
        print(f"Normal: {len(df[df['label'] == 'Normal'])}, Anomaly: {len(df[df['label'] == 'Anomaly'])}")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare the dataset"""
        print("Cleaning data...")
        
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        
        # Remove duplicates
        initial_len = len(df)
        df = df.drop_duplicates()
        print(f"Removed {initial_len - len(df)} duplicate rows")
        
        # Ensure required columns exist
        required_cols = ['packet_size', 'time_delta', 'protocol', 'label']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        return df
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        print("Encoding categorical features...")
        
        # Encode protocol
        if 'protocol' in df.columns:
            df['protocol'] = df['protocol'].map(
                lambda x: config.PROTOCOL_MAP.get(x.upper(), config.PROTOCOL_MAP['OTHER'])
                if isinstance(x, str) else config.PROTOCOL_MAP['OTHER']
            )
        
        return df
    
    def normalize_features(self, df: pd.DataFrame, fit: bool = True) -> pd.DataFrame:
        """Normalize numerical features"""
        print("Normalizing features...")
        
        # Select feature columns (exclude label)
        self.feature_columns = [col for col in config.FEATURES if col in df.columns]
        
        if fit:
            df[self.feature_columns] = self.scaler.fit_transform(df[self.feature_columns])
        else:
            df[self.feature_columns] = self.scaler.transform(df[self.feature_columns])
        
        return df
    
    def create_sequences(self, X: np.ndarray, y: np.ndarray, 
                        sequence_length: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert data into sequences for LSTM
        Each sequence contains 'sequence_length' time steps
        """
        if sequence_length is None:
            sequence_length = config.SEQUENCE_LENGTH
        
        print(f"Creating sequences with length {sequence_length}...")
        
        X_sequences = []
        y_sequences = []
        
        for i in range(len(X) - sequence_length + 1):
            X_sequences.append(X[i:i + sequence_length])
            y_sequences.append(y[i + sequence_length - 1])
        
        X_sequences = np.array(X_sequences)
        y_sequences = np.array(y_sequences)
        
        print(f"Created {len(X_sequences)} sequences")
        print(f"Sequence shape: {X_sequences.shape}")
        
        return X_sequences, y_sequences
    
    def prepare_training_data(self, df: pd.DataFrame) -> Tuple:
        """
        Complete preprocessing pipeline for training
        Returns X_train, X_test, y_train, y_test as sequences
        """
        print("\n" + "="*50)
        print("PREPROCESSING PIPELINE")
        print("="*50)
        
        # Clean data
        df = self.clean_data(df)
        
        # Encode categorical features
        df = self.encode_categorical(df)
        
        # Encode labels
        y = self.label_encoder.fit_transform(df['label'])
        
        # Normalize features
        df = self.normalize_features(df, fit=True)
        
        # Extract feature matrix
        X = df[self.feature_columns].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE, stratify=y
        )
        
        print(f"\nTrain set size: {len(X_train)}")
        print(f"Test set size: {len(X_test)}")
        
        # Create sequences
        X_train_seq, y_train_seq = self.create_sequences(X_train, y_train)
        X_test_seq, y_test_seq = self.create_sequences(X_test, y_test)
        
        print(f"\nFinal training sequences: {X_train_seq.shape}")
        print(f"Final testing sequences: {X_test_seq.shape}")
        
        return X_train_seq, X_test_seq, y_train_seq, y_test_seq
    
    def save_preprocessors(self):
        """Save scaler and encoder for later use"""
        print(f"\nSaving preprocessors...")
        with open(config.SCALER_PATH, 'wb') as f:
            pickle.dump(self.scaler, f)
        with open(config.ENCODER_PATH, 'wb') as f:
            pickle.dump(self.label_encoder, f)
        print(f"Saved scaler to {config.SCALER_PATH}")
        print(f"Saved encoder to {config.ENCODER_PATH}")
    
    def load_preprocessors(self):
        """Load saved scaler and encoder"""
        with open(config.SCALER_PATH, 'rb') as f:
            self.scaler = pickle.load(f)
        with open(config.ENCODER_PATH, 'rb') as f:
            self.label_encoder = pickle.load(f)
        print("Loaded preprocessors successfully")
    
    def preprocess_live_data(self, traffic_data: List[dict]) -> np.ndarray:
        """
        Preprocess live traffic data for real-time prediction
        """
        df = pd.DataFrame(traffic_data)
        
        # Encode categorical
        df = self.encode_categorical(df)
        
        # Normalize
        df = self.normalize_features(df, fit=False)
        
        # Extract features
        X = df[self.feature_columns].values
        
        return X


if __name__ == "__main__":
    # Test preprocessing
    preprocessor = DataPreprocessor()
    df = preprocessor.load_dataset()
    X_train, X_test, y_train, y_test = preprocessor.prepare_training_data(df)
    preprocessor.save_preprocessors()
    
    print("\n" + "="*50)
    print("PREPROCESSING COMPLETE")
    print("="*50)
