# Network Anomaly Detection Dashboard Guide

## Overview

This enhanced system includes a professional Next.js dashboard with real-time monitoring capabilities, an improved LSTM model with attention mechanism, and comprehensive packet analysis tools.

## Quick Start

### 1. Train the Enhanced Model

```bash
cd scripts
python enhanced_train.py
```

This will:
- Generate 55,000 synthetic training samples
- Build an enhanced LSTM with attention mechanism
- Train with advanced callbacks and class weighting
- Save the model and training artifacts

### 2. Launch the Web Dashboard

```bash
# From the project root
npm install
npm run dev
```

Visit `http://localhost:3000` to see the dashboard.

## Dashboard Features

### Real-Time Monitoring
- **Live Statistics**: Packets processed, anomalies detected, throughput, and model accuracy
- **Traffic Charts**: Real-time network traffic visualization with 60-second history
- **Anomaly Scores**: LSTM prediction confidence with threshold indicator

### Anomaly Detection Feed
- Real-time threat detection events
- Severity classification (high, medium, low)
- Detailed anomaly descriptions and scores
- Color-coded alerts for quick triage

### Packet Inspector
- Live packet capture display
- Deep packet analysis with metadata
- Protocol, IP addresses, flags, and payload information
- Click to inspect individual packets

## Enhanced Model Features

### Architecture Improvements
- **Bidirectional LSTM**: 128 → 64 units with dropout
- **Attention Mechanism**: Custom attention layer for feature focusing
- **Batch Normalization**: Improved training stability
- **Residual Connections**: Better gradient flow

### Training Enhancements
- **Class Weighting**: Handles imbalanced datasets
- **Advanced Callbacks**: Early stopping, learning rate reduction
- **Multiple Metrics**: Accuracy, precision, recall, AUC
- **Model Checkpointing**: Saves best performing model

### Performance Metrics
- Total Parameters: ~550K (vs 122K in basic model)
- Expected AUC: >0.95
- Training Time: ~10-15 minutes on CPU

## API Endpoints

The dashboard uses these Next.js API routes:

- `GET /api/stats` - Real-time system statistics
- `GET /api/charts` - Traffic and anomaly chart data
- `GET /api/anomalies` - Recent anomaly detections
- `GET /api/packets` - Live packet stream

## Integration with Python Backend

To connect the dashboard with actual network monitoring:

1. **Run Traffic Capture**:
```bash
sudo python scripts/traffic_capture.py
```

2. **Run Real-Time Detection**:
```bash
python scripts/realtime_detector.py --model models/enhanced_lstm_model.keras
```

3. **Bridge Data** (create a simple API bridge):
- Read detection results from Python
- Expose via Next.js API routes
- Use WebSockets for real-time updates

## Customization

### Adjust Detection Threshold
Edit `components/traffic-charts.tsx`:
```tsx
threshold: 0.5  // Change to 0.3 for more sensitive detection
```

### Modify Update Intervals
Edit component `useEffect` hooks:
```tsx
const interval = setInterval(fetchData, 3000)  // 3 seconds
```

### Add Custom Metrics
1. Update `app/api/stats/route.ts`
2. Add new stat card to `components/stats-grid.tsx`
3. Style with design tokens in `globals.css`

## Troubleshooting

**Dashboard shows no data:**
- Check API routes are responding
- Verify Python backend is running
- Check browser console for errors

**Model not loading:**
- Ensure `enhanced_train.py` completed successfully
- Check `models/` directory contains `.keras` file
- Verify TensorFlow is installed correctly

**High false positive rate:**
- Retrain with more diverse data
- Adjust anomaly threshold
- Review training metrics

## Next Steps

1. **Add Authentication**: Implement user login
2. **Database Integration**: Store alerts in Supabase/Neon
3. **Email Notifications**: Alert on critical anomalies
4. **Historical Analysis**: View past detection events
5. **Export Reports**: Generate PDF/CSV reports

## Support

For issues or questions, refer to the main README.md or check the training logs in `models/`.
