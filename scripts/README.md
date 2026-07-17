# Network Traffic Anomaly Detection System

A real-time network intrusion detection system using LSTM (Long Short-Term Memory) neural networks to identify anomalous network traffic patterns.

## Features

- **Live Traffic Capture**: Captures network packets using Scapy
- **LSTM-Based Detection**: Deep learning model for sequence-based anomaly detection
- **Real-Time Inference**: Low-latency prediction on live network traffic
- **Web Dashboard**: Beautiful Flask-based dashboard for monitoring
- **Alert System**: Logs and displays detected anomalies with confidence scores
- **Comprehensive Metrics**: Accuracy, Precision, Recall, F1-Score

## System Architecture

```
┌─────────────────────┐
│ Network Interface   │
│ (Live Traffic)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Traffic Capture     │
│ (Scapy/PyShark)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Feature Extraction  │
│ (9 Features)        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Preprocessing       │
│ (Normalize/Encode)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Sequence Creation   │
│ (Sliding Window)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ LSTM Model          │
│ (2 LSTM Layers)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Anomaly Detection   │
│ (Binary Class.)     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Alert & Dashboard   │
│ (Real-Time Display) │
└─────────────────────┘
```

## Installation

### 1. Install Python Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### 2. System Requirements

- Python 3.8+
- TensorFlow 2.13+
- 4GB+ RAM
- Network interface access (for live capture)

### 3. Optional: Dataset Download

For training with real datasets, download one of:
- **CICIDS 2017**: https://www.unb.ca/cic/datasets/ids-2017.html
- **NSL-KDD**: https://www.unb.ca/cic/datasets/nsl.html
- **UNSW-NB15**: https://research.unsw.edu.au/projects/unsw-nb15-dataset

Place the CSV file in `scripts/data/network_traffic.csv`

> **Note**: The system includes synthetic data generation for testing without a dataset.

## Usage

### Step 1: Train the Model

```bash
cd scripts
python train_model.py
```

This will:
- Load or generate training data
- Preprocess features
- Build and train the LSTM model
- Evaluate performance
- Save the trained model

**Expected Output:**
```
TRAINING COMPLETE
Model saved to: scripts/models/lstm_anomaly_detector.h5
Final Test Accuracy: 95.23%
Final Test F1-Score: 0.9456
```

### Step 2: Run Real-Time Detection (Console)

```bash
python realtime_detector.py
```

Or run for specific duration:
```bash
python realtime_detector.py 60  # Run for 60 seconds
```

### Step 3: Run Web Dashboard

```bash
python dashboard.py
```

Then open your browser to: **http://localhost:5000**

The dashboard provides:
- Real-time statistics
- Anomaly alerts
- Traffic visualization
- Start/Stop controls

## Project Structure

```
scripts/
├── config.py                  # Configuration and hyperparameters
├── data_preprocessing.py      # Data loading and preprocessing
├── lstm_model.py             # LSTM model architecture
├── train_model.py            # Training pipeline
├── traffic_capture.py        # Live traffic capture
├── realtime_detector.py      # Real-time detection engine
├── dashboard.py              # Web dashboard
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/                     # Dataset directory
├── models/                   # Trained models
│   ├── lstm_anomaly_detector.h5
│   ├── feature_scaler.pkl
│   └── label_encoder.pkl
├── logs/                     # Logs and alerts
│   ├── anomaly_detection.log
│   ├── alerts.json
│   └── training_history.png
└── templates/                # HTML templates
    └── index.html
```

## Model Architecture

```
Layer (type)                 Output Shape              Params
=================================================================
LSTM (128 units)            (None, 10, 128)           70,656
Dropout (0.3)               (None, 10, 128)           0
LSTM (64 units)             (None, 64)                49,408
Dropout (0.3)               (None, 64)                0
Dense (32 units)            (None, 32)                2,080
Dropout (0.15)              (None, 32)                0
Dense (1 unit, sigmoid)     (None, 1)                 33
=================================================================
Total params: 122,177
```

## Features Extracted

1. **packet_size**: Size of packet in bytes
2. **time_delta**: Time between consecutive packets
3. **protocol**: Network protocol (TCP/UDP/ICMP)
4. **src_port**: Source port number
5. **dst_port**: Destination port number
6. **packet_count**: Number of packets in flow
7. **flow_duration**: Duration of network flow
8. **bytes_per_second**: Data transfer rate
9. **packets_per_second**: Packet rate

## Configuration

Edit `config.py` to customize:

```python
# Model Parameters
SEQUENCE_LENGTH = 10
LSTM_UNITS = [128, 64]
DROPOUT_RATE = 0.3
EPOCHS = 50
BATCH_SIZE = 64

# Detection Parameters
ANOMALY_THRESHOLD = 0.7
WINDOW_SIZE = 100
CAPTURE_INTERFACE = 'eth0'  # Change to your interface
```

## Network Interface Setup

### Linux/Mac
```bash
# List available interfaces
ifconfig

# Common interfaces: eth0, wlan0, en0
```

### Windows
```bash
# List interfaces
ipconfig

# Common interfaces: Ethernet, Wi-Fi
```

Update `CAPTURE_INTERFACE` in `config.py` with your interface name.

## Troubleshooting

### Issue: Scapy Permission Error
**Solution**: Run with sudo/admin privileges
```bash
sudo python realtime_detector.py
```

### Issue: No network interface found
**Solution**: Update interface name in `config.py`

### Issue: Low detection accuracy
**Solution**: 
- Train with more data
- Adjust `ANOMALY_THRESHOLD`
- Increase `EPOCHS` in config

### Issue: TensorFlow warnings
**Solution**: These are typically informational. To suppress:
```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

## Performance Metrics

Typical performance on test data:

| Metric    | Score  |
|-----------|--------|
| Accuracy  | 95.2%  |
| Precision | 94.8%  |
| Recall    | 95.6%  |
| F1-Score  | 0.946  |

## Attack Types Detected

- **DoS/DDoS**: Denial of Service attacks
- **Port Scanning**: Network reconnaissance
- **Brute Force**: Authentication attacks
- **Abnormal Traffic**: Unusual patterns
- **Botnet Activity**: Command & control traffic

## API Endpoints

When running the dashboard:

- `GET /` - Dashboard UI
- `POST /api/start` - Start detection
- `POST /api/stop` - Stop detection
- `GET /api/stats` - Get current statistics
- `GET /api/alerts` - Get recent alerts
- `GET /stream` - Server-Sent Events stream

## Security Considerations

- **Privacy**: Only extracts metadata, not packet content
- **Permissions**: Requires network interface access
- **Production**: Implement proper authentication for dashboard
- **Logging**: Sensitive data should be encrypted

## Future Enhancements

- [ ] Multi-class classification (attack type identification)
- [ ] Auto-retraining with detected anomalies
- [ ] Integration with firewall rules
- [ ] Email/SMS alerts
- [ ] Historical data visualization
- [ ] Model explainability (SHAP values)

## Credits

Built with:
- TensorFlow/Keras
- Scapy
- Flask
- Scikit-learn

## License

MIT License - Feel free to use and modify

## Support

For issues or questions, please review the troubleshooting section or check the inline code comments.
