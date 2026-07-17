"""
Live Network Traffic Capture Module
Captures and extracts features from live network traffic
"""

import time
import numpy as np
from collections import deque
from datetime import datetime
from typing import Dict, List
import threading
import config


class TrafficCapture:
    """Captures live network traffic and extracts features"""
    
    def __init__(self, interface: str = None):
        """
        Initialize traffic capture
        
        Args:
            interface: Network interface to capture from (e.g., 'eth0', 'wlan0')
        """
        self.interface = interface or config.CAPTURE_INTERFACE
        self.packet_buffer = deque(maxlen=config.WINDOW_SIZE)
        self.is_capturing = False
        self.capture_thread = None
        self.flow_tracker = {}
        
        # Try to import packet capture library
        try:
            from scapy.all import sniff, IP, TCP, UDP, ICMP
            self.sniff = sniff
            self.IP = IP
            self.TCP = TCP
            self.UDP = UDP
            self.ICMP = ICMP
            self.capture_available = True
        except ImportError:
            print("Warning: Scapy not available. Using simulated traffic capture.")
            self.capture_available = False
    
    def extract_features(self, packet) -> Dict:
        """
        Extract features from a network packet
        
        Returns dictionary with feature values
        """
        features = {
            'packet_size': 0,
            'time_delta': 0.0,
            'protocol': 'OTHER',
            'src_port': 0,
            'dst_port': 0,
            'packet_count': 1,
            'flow_duration': 0.0,
            'bytes_per_second': 0.0,
            'packets_per_second': 0.0,
            'timestamp': datetime.now().isoformat()
        }
        
        if not self.capture_available:
            # Generate simulated features
            return self._generate_simulated_packet()
        
        try:
            # Extract packet size
            features['packet_size'] = len(packet)
            
            # Extract protocol and ports
            if packet.haslayer(self.IP):
                ip_layer = packet[self.IP]
                
                if packet.haslayer(self.TCP):
                    features['protocol'] = 'TCP'
                    features['src_port'] = packet[self.TCP].sport
                    features['dst_port'] = packet[self.TCP].dport
                elif packet.haslayer(self.UDP):
                    features['protocol'] = 'UDP'
                    features['src_port'] = packet[self.UDP].sport
                    features['dst_port'] = packet[self.UDP].dport
                elif packet.haslayer(self.ICMP):
                    features['protocol'] = 'ICMP'
                
                # Track flow
                flow_key = (ip_layer.src, ip_layer.dst, features['protocol'])
                current_time = time.time()
                
                if flow_key in self.flow_tracker:
                    flow_data = self.flow_tracker[flow_key]
                    features['time_delta'] = current_time - flow_data['last_time']
                    features['flow_duration'] = current_time - flow_data['start_time']
                    features['packet_count'] = flow_data['packet_count'] + 1
                    
                    # Update flow tracker
                    flow_data['last_time'] = current_time
                    flow_data['packet_count'] += 1
                    flow_data['total_bytes'] += features['packet_size']
                else:
                    # New flow
                    self.flow_tracker[flow_key] = {
                        'start_time': current_time,
                        'last_time': current_time,
                        'packet_count': 1,
                        'total_bytes': features['packet_size']
                    }
                
                # Calculate rates
                if features['flow_duration'] > 0:
                    flow_data = self.flow_tracker[flow_key]
                    features['bytes_per_second'] = flow_data['total_bytes'] / features['flow_duration']
                    features['packets_per_second'] = flow_data['packet_count'] / features['flow_duration']
        
        except Exception as e:
            print(f"Error extracting features: {e}")
        
        return features
    
    def _generate_simulated_packet(self) -> Dict:
        """Generate simulated network traffic for testing"""
        # Simulate normal traffic 90% of the time, anomalies 10%
        is_anomaly = np.random.random() < 0.1
        
        if is_anomaly:
            # Simulated attack patterns
            packet_size = np.random.randint(1000, 1500)
            time_delta = np.random.exponential(0.0001)
            protocol = np.random.choice(['TCP', 'UDP', 'ICMP'], p=[0.4, 0.5, 0.1])
            src_port = np.random.randint(1, 65535)
            dst_port = np.random.randint(1, 65535)
            packet_count = np.random.randint(100, 500)
            flow_duration = np.random.exponential(0.1)
        else:
            # Normal traffic
            packet_size = np.random.randint(64, 800)
            time_delta = np.random.exponential(0.01)
            protocol = np.random.choice(['TCP', 'UDP', 'ICMP'], p=[0.7, 0.25, 0.05])
            src_port = np.random.randint(1024, 65535)
            dst_port = np.random.choice([80, 443, 22, 53, 21])
            packet_count = np.random.randint(1, 30)
            flow_duration = np.random.exponential(5.0)
        
        bytes_per_second = packet_size * packet_count / (flow_duration + 0.001)
        packets_per_second = packet_count / (flow_duration + 0.001)
        
        return {
            'packet_size': packet_size,
            'time_delta': time_delta,
            'protocol': protocol,
            'src_port': src_port,
            'dst_port': dst_port,
            'packet_count': packet_count,
            'flow_duration': flow_duration,
            'bytes_per_second': bytes_per_second,
            'packets_per_second': packets_per_second,
            'timestamp': datetime.now().isoformat()
        }
    
    def packet_handler(self, packet):
        """Handle captured packets"""
        features = self.extract_features(packet)
        self.packet_buffer.append(features)
    
    def start_capture(self, callback=None):
        """Start capturing network traffic"""
        if self.is_capturing:
            print("Already capturing traffic")
            return
        
        self.is_capturing = True
        
        if self.capture_available:
            print(f"Starting packet capture on interface {self.interface}...")
            self.capture_thread = threading.Thread(
                target=self._capture_loop,
                args=(callback,),
                daemon=True
            )
        else:
            print("Starting simulated traffic capture...")
            self.capture_thread = threading.Thread(
                target=self._simulated_capture_loop,
                args=(callback,),
                daemon=True
            )
        
        self.capture_thread.start()
    
    def _capture_loop(self, callback):
        """Real packet capture loop"""
        try:
            self.sniff(
                iface=self.interface,
                prn=lambda pkt: self._handle_packet(pkt, callback),
                stop_filter=lambda _: not self.is_capturing,
                store=False
            )
        except Exception as e:
            print(f"Capture error: {e}")
            self.is_capturing = False
    
    def _simulated_capture_loop(self, callback):
        """Simulated traffic capture loop"""
        while self.is_capturing:
            packet_features = self._generate_simulated_packet()
            self.packet_buffer.append(packet_features)
            
            if callback:
                callback(packet_features)
            
            # Simulate packet arrival rate
            time.sleep(0.01 + np.random.exponential(0.02))
    
    def _handle_packet(self, packet, callback):
        """Handle captured packet with callback"""
        features = self.extract_features(packet)
        if callback:
            callback(features)
    
    def stop_capture(self):
        """Stop capturing traffic"""
        print("Stopping traffic capture...")
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
    
    def get_buffer(self) -> List[Dict]:
        """Get current packet buffer"""
        return list(self.packet_buffer)
    
    def clear_buffer(self):
        """Clear the packet buffer"""
        self.packet_buffer.clear()


if __name__ == "__main__":
    # Test traffic capture
    print("Testing traffic capture...")
    
    capture = TrafficCapture()
    
    def print_packet(features):
        print(f"Captured: {features['protocol']} | "
              f"Size: {features['packet_size']} bytes | "
              f"Ports: {features['src_port']}->{features['dst_port']}")
    
    capture.start_capture(callback=print_packet)
    
    try:
        print("Capturing for 10 seconds...")
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        capture.stop_capture()
        print(f"\nCaptured {len(capture.get_buffer())} packets")
