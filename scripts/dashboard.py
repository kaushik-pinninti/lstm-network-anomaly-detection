"""
Web Dashboard for Real-Time Monitoring
Flask-based dashboard for visualizing detection results
"""

from flask import Flask, render_template, jsonify, Response
import json
import time
from datetime import datetime
from threading import Thread, Lock
import config
from realtime_detector import RealtimeAnomalyDetector


app = Flask(__name__)
app.config['SECRET_KEY'] = 'network-anomaly-detection-system'

# Global detector instance
detector = None
detector_lock = Lock()
detection_thread = None
is_running = False

# Statistics
stats = {
    'total': 0,
    'normal': 0,
    'anomaly': 0,
    'recent_alerts': [],
    'start_time': None
}


def background_detection():
    """Background thread for detection"""
    global detector, is_running, stats
    
    print("Starting background detection thread...")
    
    def packet_callback(packet_features):
        """Callback for each packet"""
        if detector:
            result = detector.process_packet(packet_features)
            
            if result:
                with detector_lock:
                    stats['total'] += 1
                    
                    if result['prediction'] == 'ANOMALY':
                        stats['anomaly'] += 1
                        # Keep only last 20 alerts
                        stats['recent_alerts'].insert(0, result)
                        stats['recent_alerts'] = stats['recent_alerts'][:20]
                    else:
                        stats['normal'] += 1
    
    # Start capture
    detector.traffic_capture.start_capture(callback=packet_callback)
    
    # Keep thread alive
    while is_running:
        time.sleep(1)
    
    detector.traffic_capture.stop_capture()


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/start', methods=['POST'])
def start_detection():
    """Start detection"""
    global detector, detection_thread, is_running, stats
    
    if is_running:
        return jsonify({'status': 'already_running'})
    
    try:
        # Initialize detector
        detector = RealtimeAnomalyDetector()
        
        # Reset stats
        stats = {
            'total': 0,
            'normal': 0,
            'anomaly': 0,
            'recent_alerts': [],
            'start_time': datetime.now().isoformat()
        }
        
        # Start background thread
        is_running = True
        detection_thread = Thread(target=background_detection, daemon=True)
        detection_thread.start()
        
        return jsonify({'status': 'started'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
def stop_detection():
    """Stop detection"""
    global is_running, detector
    
    if not is_running:
        return jsonify({'status': 'not_running'})
    
    is_running = False
    
    if detector:
        detector.stop_detection()
    
    return jsonify({'status': 'stopped'})


@app.route('/api/stats')
def get_stats():
    """Get current statistics"""
    with detector_lock:
        current_stats = stats.copy()
    
    # Calculate percentages
    total = current_stats['total']
    if total > 0:
        current_stats['anomaly_percent'] = (current_stats['anomaly'] / total) * 100
        current_stats['normal_percent'] = (current_stats['normal'] / total) * 100
    else:
        current_stats['anomaly_percent'] = 0
        current_stats['normal_percent'] = 0
    
    current_stats['is_running'] = is_running
    
    return jsonify(current_stats)


@app.route('/api/alerts')
def get_alerts():
    """Get recent alerts"""
    try:
        with open(config.ALERT_LOG, 'r') as f:
            alerts = json.load(f)
        return jsonify(alerts[-50:])  # Last 50 alerts
    except (FileNotFoundError, json.JSONDecodeError):
        return jsonify([])


@app.route('/stream')
def stream():
    """Server-Sent Events stream for real-time updates"""
    def event_stream():
        last_total = 0
        while True:
            with detector_lock:
                if stats['total'] != last_total:
                    last_total = stats['total']
                    yield f"data: {json.dumps(stats)}\n\n"
            time.sleep(0.5)
    
    return Response(event_stream(), mimetype='text/event-stream')


# HTML Template
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Anomaly Detection Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .controls {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-start {
            background: #10b981;
            color: white;
        }
        
        .btn-start:hover {
            background: #059669;
        }
        
        .btn-stop {
            background: #ef4444;
            color: white;
        }
        
        .btn-stop:hover {
            background: #dc2626;
        }
        
        .status {
            text-align: center;
            color: white;
            font-size: 1.2rem;
            margin-bottom: 30px;
        }
        
        .status.running {
            color: #10b981;
        }
        
        .status.stopped {
            color: #fbbf24;
        }
        
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .card h3 {
            font-size: 1.1rem;
            color: #6b7280;
            margin-bottom: 10px;
        }
        
        .card .value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #111827;
        }
        
        .card .percent {
            font-size: 1rem;
            color: #6b7280;
            margin-top: 5px;
        }
        
        .card.anomaly .value {
            color: #ef4444;
        }
        
        .card.normal .value {
            color: #10b981;
        }
        
        .alerts-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        .alerts-section h2 {
            margin-bottom: 20px;
            color: #111827;
        }
        
        .alert-item {
            padding: 15px;
            border-left: 4px solid #ef4444;
            background: #fef2f2;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        
        .alert-item .alert-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        
        .alert-item .timestamp {
            color: #6b7280;
            font-size: 0.9rem;
        }
        
        .alert-item .confidence {
            font-weight: bold;
            color: #ef4444;
        }
        
        .alert-item .details {
            display: flex;
            gap: 20px;
            font-size: 0.9rem;
            color: #4b5563;
        }
        
        .no-alerts {
            text-align: center;
            color: #9ca3af;
            padding: 40px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Network Anomaly Detection System</h1>
            <p>Real-Time LSTM-Based Intrusion Detection</p>
        </div>
        
        <div class="controls">
            <button class="btn btn-start" onclick="startDetection()">Start Detection</button>
            <button class="btn btn-stop" onclick="stopDetection()">Stop Detection</button>
        </div>
        
        <div class="status" id="status">System Ready</div>
        
        <div class="dashboard">
            <div class="card">
                <h3>Total Analyzed</h3>
                <div class="value" id="total">0</div>
            </div>
            
            <div class="card normal">
                <h3>Normal Traffic</h3>
                <div class="value" id="normal">0</div>
                <div class="percent" id="normal-percent">0%</div>
            </div>
            
            <div class="card anomaly">
                <h3>Anomalies Detected</h3>
                <div class="value" id="anomaly">0</div>
                <div class="percent" id="anomaly-percent">0%</div>
            </div>
        </div>
        
        <div class="alerts-section">
            <h2>🚨 Recent Alerts</h2>
            <div id="alerts">
                <div class="no-alerts">No anomalies detected yet</div>
            </div>
        </div>
    </div>
    
    <script>
        async function startDetection() {
            const response = await fetch('/api/start', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'started') {
                document.getElementById('status').textContent = 'Detection Running';
                document.getElementById('status').className = 'status running';
            }
        }
        
        async function stopDetection() {
            const response = await fetch('/api/stop', { method: 'POST' });
            const data = await response.json();
            if (data.status === 'stopped') {
                document.getElementById('status').textContent = 'Detection Stopped';
                document.getElementById('status').className = 'status stopped';
            }
        }
        
        function updateStats() {
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total').textContent = data.total.toLocaleString();
                    document.getElementById('normal').textContent = data.normal.toLocaleString();
                    document.getElementById('anomaly').textContent = data.anomaly.toLocaleString();
                    document.getElementById('normal-percent').textContent = data.normal_percent.toFixed(1) + '%';
                    document.getElementById('anomaly-percent').textContent = data.anomaly_percent.toFixed(1) + '%';
                    
                    if (data.is_running) {
                        document.getElementById('status').textContent = 'Detection Running';
                        document.getElementById('status').className = 'status running';
                    }
                    
                    // Update alerts
                    if (data.recent_alerts && data.recent_alerts.length > 0) {
                        const alertsHtml = data.recent_alerts.map(alert => `
                            <div class="alert-item">
                                <div class="alert-header">
                                    <span class="timestamp">${new Date(alert.timestamp).toLocaleString()}</span>
                                    <span class="confidence">Confidence: ${(alert.confidence * 100).toFixed(1)}%</span>
                                </div>
                                <div class="details">
                                    <span>Protocol: ${alert.packet_info.protocol}</span>
                                    <span>Size: ${alert.packet_info.size} bytes</span>
                                    <span>Ports: ${alert.packet_info.src_port} → ${alert.packet_info.dst_port}</span>
                                </div>
                            </div>
                        `).join('');
                        document.getElementById('alerts').innerHTML = alertsHtml;
                    }
                });
        }
        
        // Update stats every 2 seconds
        setInterval(updateStats, 2000);
        updateStats();
    </script>
</body>
</html>
'''


# Create templates directory and save HTML
import os
templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
os.makedirs(templates_dir, exist_ok=True)

with open(os.path.join(templates_dir, 'index.html'), 'w') as f:
    f.write(HTML_TEMPLATE)


if __name__ == '__main__':
    print("\n" + "="*70)
    print(" NETWORK ANOMALY DETECTION DASHBOARD")
    print("="*70)
    print(f"\nStarting server on http://{config.API_HOST}:{config.API_PORT}")
    print("\nOpen your browser and navigate to the URL above")
    print("="*70 + "\n")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=config.DEBUG_MODE,
        threaded=True
    )
