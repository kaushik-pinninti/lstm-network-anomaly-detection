"""
Configuration file for Network Traffic Anomaly Detection System
Contains all hyperparameters, paths, and system settings
"""

import os

# ==================== PATHS ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
for directory in [DATA_DIR, MODEL_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# ==================== MODEL PARAMETERS ====================
# LSTM Architecture
SEQUENCE_LENGTH = 10  # Number of time steps in each sequence
LSTM_UNITS = [128, 64]  # Number of units in each LSTM layer
DROPOUT_RATE = 0.3  # Dropout rate to prevent overfitting
DENSE_UNITS = 32  # Units in dense layer before output

# Training Parameters
BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 0.001
VALIDATION_SPLIT = 0.2

# ==================== FEATURE ENGINEERING ====================
# Network traffic features to extract
FEATURES = [
    'packet_size',
    'time_delta',
    'protocol',
    'src_port',
    'dst_port',
    'packet_count',
    'flow_duration',
    'bytes_per_second',
    'packets_per_second'
]

# Protocol mapping
PROTOCOL_MAP = {
    'TCP': 6,
    'UDP': 17,
    'ICMP': 1,
    'OTHER': 0
}

# ==================== DETECTION PARAMETERS ====================
ANOMALY_THRESHOLD = 0.7  # Confidence threshold for anomaly detection
WINDOW_SIZE = 100  # Number of packets to analyze in sliding window
CAPTURE_INTERFACE = 'eth0'  # Network interface to capture from (change as needed)
CAPTURE_TIMEOUT = 1  # Packet capture timeout in seconds

# ==================== DATASET PARAMETERS ====================
# For training - you can use CICIDS2017, NSL-KDD, or UNSW-NB15
DATASET_PATH = os.path.join(DATA_DIR, 'network_traffic.csv')
TEST_SIZE = 0.2
RANDOM_STATE = 42

# ==================== API/DASHBOARD SETTINGS ====================
API_HOST = '0.0.0.0'
API_PORT = 5000
DEBUG_MODE = True

# ==================== LOGGING ====================
LOG_FILE = os.path.join(LOG_DIR, 'anomaly_detection.log')
ALERT_LOG = os.path.join(LOG_DIR, 'alerts.json')

# ==================== MODEL PATHS ====================
MODEL_PATH = os.path.join(MODEL_DIR, 'lstm_anomaly_detector.h5')
SCALER_PATH = os.path.join(MODEL_DIR, 'feature_scaler.pkl')
ENCODER_PATH = os.path.join(MODEL_DIR, 'label_encoder.pkl')
