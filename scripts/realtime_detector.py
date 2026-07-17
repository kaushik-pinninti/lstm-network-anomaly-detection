"""
Real-Time Anomaly Detection Engine
Performs live inference on captured traffic
"""

import numpy as np
import time
import json
from datetime import datetime
from collections import deque
from typing import Dict, List
import tensorflow as tf
from traffic_capture import TrafficCapture
from data_preprocessing import DataPreprocessor
from lstm_model import LSTMAnomalyDetector
import config


class RealtimeAnomalyDetector:
    """Real-time network traffic anomaly detection system"""
    
    def __init__(self):
        """Initialize the real-time detector"""
        print("Initializing Real-Time Anomaly Detector...")
        
        # Load model
        print("Loading trained model...")
        self.model = LSTMAnomalyDetector(input_shape=(config.SEQUENCE_LENGTH, len(config.FEATURES)))
        self.model.load_model()
        
        # Load preprocessors
        print("Loading preprocessors...")
        self.preprocessor = DataPreprocessor()
        self.preprocessor.load_preprocessors()
        
        # Initialize traffic capture
        print("Initializing traffic capture...")
        self.traffic_capture = TrafficCapture()
        
        # Sequence buffer for LSTM input
        self.sequence_buffer = deque(maxlen=config.SEQUENCE_LENGTH)
        
        # Detection results
        self.anomaly_count = 0
        self.normal_count = 0
        self.alerts = []
        
        # Statistics
        self.start_time = None
        self.total_predictions = 0
        
        print("Initialization complete!\n")
    
    def process_packet(self, packet_features: Dict):
        """
        Process a single packet and detect anomalies
        
        Args:
            packet_features: Dictionary of packet features
        """
        # Add to sequence buffer
        self.sequence_buffer.append(packet_features)
        
        # Need full sequence for prediction
        if len(self.sequence_buffer) < config.SEQUENCE_LENGTH:
            return None
        
        # Prepare features for prediction
        features_list = list(self.sequence_buffer)
        
        try:
            # Preprocess
            X = self.preprocessor.preprocess_live_data(features_list)
            
            # Reshape for LSTM: (1, sequence_length, n_features)
            X_seq = X.reshape(1, config.SEQUENCE_LENGTH, -1)
            
            # Predict
            prediction, probability = self.model.predict(X_seq, threshold=config.ANOMALY_THRESHOLD)
            
            # Update statistics
            self.total_predictions += 1
            
            result = {
                'timestamp': packet_features['timestamp'],
                'prediction': 'ANOMALY' if prediction[0] == 1 else 'NORMAL',
                'confidence': float(probability[0]),
                'packet_info': {
                    'protocol': packet_features['protocol'],
                    'size': packet_features['packet_size'],
                    'src_port': packet_features['src_port'],
                    'dst_port': packet_features['dst_port']
                }
            }
            
            # Count and handle alerts
            if prediction[0] == 1:
                self.anomaly_count += 1
                self.handle_anomaly(result)
            else:
                self.normal_count += 1
            
            return result
            
        except Exception as e:
            print(f"Error processing packet: {e}")
            return None
    
    def handle_anomaly(self, result: Dict):
        """Handle detected anomaly"""
        # Add to alerts
        self.alerts.append(result)
        
        # Log alert
        self.log_alert(result)
        
        # Print alert to console
        self.print_alert(result)
    
    def print_alert(self, result: Dict):
        """Print anomaly alert to console"""
        print(f"\n{'='*70}")
        print(f"🚨 ANOMALY DETECTED!")
        print(f"{'='*70}")
        print(f"Timestamp:   {result['timestamp']}")
        print(f"Confidence:  {result['confidence']*100:.2f}%")
        print(f"Protocol:    {result['packet_info']['protocol']}")
        print(f"Packet Size: {result['packet_info']['size']} bytes")
        print(f"Ports:       {result['packet_info']['src_port']} -> {result['packet_info']['dst_port']}")
        print(f"{'='*70}\n")
    
    def log_alert(self, result: Dict):
        """Log anomaly to file"""
        try:
            # Read existing alerts
            try:
                with open(config.ALERT_LOG, 'r') as f:
                    alerts = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                alerts = []
            
            # Add new alert
            alerts.append(result)
            
            # Save
            with open(config.ALERT_LOG, 'w') as f:
                json.dump(alerts, f, indent=2)
                
        except Exception as e:
            print(f"Error logging alert: {e}")
    
    def print_statistics(self):
        """Print detection statistics"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            rate = self.total_predictions / elapsed if elapsed > 0 else 0
        else:
            elapsed = 0
            rate = 0
        
        total = self.anomaly_count + self.normal_count
        anomaly_percent = (self.anomaly_count / total * 100) if total > 0 else 0
        
        print(f"\n{'─'*70}")
        print(f"📊 Detection Statistics")
        print(f"{'─'*70}")
        print(f"Runtime:         {elapsed:.1f} seconds")
        print(f"Total Analyzed:  {total:,}")
        print(f"Normal Traffic:  {self.normal_count:,} ({100-anomaly_percent:.1f}%)")
        print(f"Anomalies:       {self.anomaly_count:,} ({anomaly_percent:.1f}%)")
        print(f"Detection Rate:  {rate:.1f} predictions/sec")
        print(f"{'─'*70}\n")
    
    def start_detection(self, duration: int = None):
        """
        Start real-time detection
        
        Args:
            duration: Detection duration in seconds (None for infinite)
        """
        print("\n" + "="*70)
        print(" STARTING REAL-TIME NETWORK TRAFFIC ANOMALY DETECTION")
        print("="*70)
        print(f"Model:           {config.MODEL_PATH}")
        print(f"Threshold:       {config.ANOMALY_THRESHOLD}")
        print(f"Sequence Length: {config.SEQUENCE_LENGTH}")
        print(f"Window Size:     {config.WINDOW_SIZE}")
        
        if duration:
            print(f"Duration:        {duration} seconds")
        else:
            print("Duration:        Infinite (Ctrl+C to stop)")
        
        print("="*70 + "\n")
        
        self.start_time = time.time()
        
        # Start traffic capture
        self.traffic_capture.start_capture(callback=self.process_packet)
        
        try:
            if duration:
                # Run for specified duration
                end_time = time.time() + duration
                while time.time() < end_time:
                    time.sleep(1)
                    if int(time.time() - self.start_time) % 10 == 0:
                        self.print_statistics()
            else:
                # Run indefinitely
                print("Press Ctrl+C to stop detection...\n")
                while True:
                    time.sleep(5)
                    self.print_statistics()
                    
        except KeyboardInterrupt:
            print("\n\nStopping detection...")
        finally:
            self.stop_detection()
    
    def stop_detection(self):
        """Stop detection and print final statistics"""
        self.traffic_capture.stop_capture()
        
        print("\n" + "="*70)
        print(" DETECTION STOPPED")
        print("="*70)
        
        self.print_statistics()
        
        if self.anomaly_count > 0:
            print(f"Alerts saved to: {config.ALERT_LOG}")
        
        print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    # Parse arguments
    duration = None
    if len(sys.argv) > 1:
        try:
            duration = int(sys.argv[1])
        except ValueError:
            print(f"Invalid duration: {sys.argv[1]}")
            sys.exit(1)
    
    # Create detector
    detector = RealtimeAnomalyDetector()
    
    # Start detection
    try:
        detector.start_detection(duration=duration)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
