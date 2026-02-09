#!/usr/bin/env python3
"""
LILITH Enhanced ML Anomaly Detection
=====================================
Advanced machine learning models for:
1. Behavioral anomaly detection
2. Network traffic analysis
3. Log analysis
4. Threat prediction
5. User behavior analytics (UBA)
6. Intrusion detection
"""

import os
import json
import pickle
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# ML imports
try:
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.cluster import DBSCAN, KMeans
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, confusion_matrix
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.svm import OneClassSVM
    import scipy.stats as stats
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False


class FeatureExtractor:
    """Extract features from various data sources"""
    
    @staticmethod
    def extract_network_features(packet_data: Dict) -> np.ndarray:
        """Extract features from network packet data"""
        features = [
            packet_data.get('packet_size', 0),
            packet_data.get('src_port', 0),
            packet_data.get('dst_port', 0),
            packet_data.get('protocol', 0),
            packet_data.get('flags', 0),
            packet_data.get('ttl', 64),
            packet_data.get('window_size', 0),
            packet_data.get('payload_entropy', 0),
            1 if packet_data.get('encrypted', False) else 0,
            packet_data.get('packet_rate', 0)
        ]
        return np.array(features)
    
    @staticmethod
    def extract_user_features(user_data: Dict) -> np.ndarray:
        """Extract features from user behavior data"""
        # Time features
        hour = user_data.get('hour', 12)
        day_of_week = user_data.get('day_of_week', 0)
        
        features = [
            hour,
            day_of_week,
            1 if 9 <= hour <= 17 else 0,  # Business hours
            1 if day_of_week < 5 else 0,   # Weekday
            user_data.get('login_count', 0),
            user_data.get('failed_logins', 0),
            user_data.get('data_downloaded', 0),
            user_data.get('data_uploaded', 0),
            user_data.get('unique_ips', 1),
            user_data.get('session_duration', 0),
            1 if user_data.get('new_device', False) else 0,
            1 if user_data.get('new_location', False) else 0,
            user_data.get('privilege_escalations', 0),
            user_data.get('sensitive_file_access', 0)
        ]
        return np.array(features)
    
    @staticmethod
    def extract_log_features(log_entry: Dict) -> np.ndarray:
        """Extract features from log entries"""
        features = [
            log_entry.get('severity_level', 0),
            log_entry.get('event_count', 1),
            log_entry.get('error_count', 0),
            log_entry.get('warning_count', 0),
            1 if 'fail' in str(log_entry.get('message', '')).lower() else 0,
            1 if 'error' in str(log_entry.get('message', '')).lower() else 0,
            1 if 'denied' in str(log_entry.get('message', '')).lower() else 0,
            1 if 'unauthorized' in str(log_entry.get('message', '')).lower() else 0,
            len(str(log_entry.get('message', ''))),
            log_entry.get('source_count', 1)
        ]
        return np.array(features)


class IsolationForestDetector:
    """Isolation Forest for anomaly detection"""
    
    def __init__(self, contamination: float = 0.1):
        self.contamination = contamination
        self.model = None
        self.scaler = StandardScaler()
        self.trained = False
    
    def train(self, data: np.ndarray) -> Dict:
        """Train the model on normal data"""
        if not ML_AVAILABLE:
            return {'success': False, 'error': 'scikit-learn not available'}
        
        try:
            # Scale data
            data_scaled = self.scaler.fit_transform(data)
            
            # Train model
            self.model = IsolationForest(
                contamination=self.contamination,
                random_state=42,
                n_estimators=100,
                max_samples='auto'
            )
            self.model.fit(data_scaled)
            self.trained = True
            
            return {
                'success': True,
                'samples_trained': len(data),
                'contamination': self.contamination
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def predict(self, data: np.ndarray) -> Dict:
        """Predict anomalies"""
        if not self.trained:
            return {'success': False, 'error': 'Model not trained'}
        
        try:
            data_scaled = self.scaler.transform(data)
            predictions = self.model.predict(data_scaled)
            scores = self.model.decision_function(data_scaled)
            
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:  # Anomaly
                    anomalies.append({
                        'index': i,
                        'score': float(score),
                        'severity': 'HIGH' if score < -0.3 else 'MEDIUM' if score < -0.1 else 'LOW'
                    })
            
            return {
                'success': True,
                'total_samples': len(data),
                'anomalies_detected': len(anomalies),
                'anomaly_rate': len(anomalies) / len(data) if len(data) > 0 else 0,
                'anomalies': anomalies[:50]  # Limit to 50
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class LOFDetector:
    """Local Outlier Factor for anomaly detection"""
    
    def __init__(self, n_neighbors: int = 20):
        self.n_neighbors = n_neighbors
        self.model = None
        self.scaler = StandardScaler()
        self.training_data = None
    
    def train(self, data: np.ndarray) -> Dict:
        """Store training data for LOF"""
        if not ML_AVAILABLE:
            return {'success': False, 'error': 'scikit-learn not available'}
        
        try:
            self.training_data = self.scaler.fit_transform(data)
            self.model = LocalOutlierFactor(
                n_neighbors=min(self.n_neighbors, len(data) - 1),
                novelty=True,
                contamination=0.1
            )
            self.model.fit(self.training_data)
            
            return {
                'success': True,
                'samples_trained': len(data),
                'n_neighbors': self.n_neighbors
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def predict(self, data: np.ndarray) -> Dict:
        """Predict using LOF"""
        if self.training_data is None:
            return {'success': False, 'error': 'Model not trained'}
        
        try:
            data_scaled = self.scaler.transform(data)
            predictions = self.model.predict(data_scaled)
            scores = self.model.decision_function(data_scaled)
            
            anomalies = []
            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    anomalies.append({
                        'index': i,
                        'lof_score': float(score),
                        'is_outlier': True
                    })
            
            return {
                'success': True,
                'total_samples': len(data),
                'outliers_detected': len(anomalies),
                'outliers': anomalies[:50]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ClusteringDetector:
    """Clustering-based anomaly detection"""
    
    def __init__(self, method: str = 'dbscan'):
        self.method = method
        self.model = None
        self.scaler = StandardScaler()
        self.cluster_centers = None
    
    def train(self, data: np.ndarray, **kwargs) -> Dict:
        """Train clustering model"""
        if not ML_AVAILABLE:
            return {'success': False, 'error': 'scikit-learn not available'}
        
        try:
            data_scaled = self.scaler.fit_transform(data)
            
            if self.method == 'dbscan':
                eps = kwargs.get('eps', 0.5)
                min_samples = kwargs.get('min_samples', 5)
                self.model = DBSCAN(eps=eps, min_samples=min_samples)
            else:  # kmeans
                n_clusters = kwargs.get('n_clusters', 3)
                self.model = KMeans(n_clusters=n_clusters, random_state=42)
            
            labels = self.model.fit_predict(data_scaled)
            
            if hasattr(self.model, 'cluster_centers_'):
                self.cluster_centers = self.model.cluster_centers_
            
            return {
                'success': True,
                'method': self.method,
                'n_clusters': len(set(labels)) - (1 if -1 in labels else 0),
                'noise_points': list(labels).count(-1) if self.method == 'dbscan' else 0
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_anomalies(self, data: np.ndarray) -> Dict:
        """Detect anomalies as points far from cluster centers or noise points"""
        if self.model is None:
            return {'success': False, 'error': 'Model not trained'}
        
        try:
            data_scaled = self.scaler.transform(data)
            labels = self.model.fit_predict(data_scaled)
            
            anomalies = []
            
            if self.method == 'dbscan':
                # Noise points are anomalies
                for i, label in enumerate(labels):
                    if label == -1:
                        anomalies.append({
                            'index': i,
                            'type': 'noise_point',
                            'cluster': -1
                        })
            else:
                # Points far from cluster centers
                if self.cluster_centers is not None:
                    for i, (point, label) in enumerate(zip(data_scaled, labels)):
                        center = self.cluster_centers[label]
                        distance = np.linalg.norm(point - center)
                        
                        # Threshold based on mean distance
                        if distance > np.mean([np.linalg.norm(data_scaled[j] - self.cluster_centers[labels[j]]) 
                                              for j in range(len(data_scaled))]) * 2:
                            anomalies.append({
                                'index': i,
                                'type': 'distant_point',
                                'cluster': int(label),
                                'distance': float(distance)
                            })
            
            return {
                'success': True,
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies[:50]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class StatisticalDetector:
    """Statistical methods for anomaly detection"""
    
    def __init__(self):
        self.baseline_stats = {}
    
    def compute_baseline(self, data: np.ndarray, feature_names: List[str] = None) -> Dict:
        """Compute baseline statistics"""
        try:
            n_features = data.shape[1] if len(data.shape) > 1 else 1
            
            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(n_features)]
            
            for i, name in enumerate(feature_names):
                feature_data = data[:, i] if len(data.shape) > 1 else data
                
                self.baseline_stats[name] = {
                    'mean': float(np.mean(feature_data)),
                    'std': float(np.std(feature_data)),
                    'median': float(np.median(feature_data)),
                    'q1': float(np.percentile(feature_data, 25)),
                    'q3': float(np.percentile(feature_data, 75)),
                    'min': float(np.min(feature_data)),
                    'max': float(np.max(feature_data))
                }
                
                # IQR for outlier detection
                iqr = self.baseline_stats[name]['q3'] - self.baseline_stats[name]['q1']
                self.baseline_stats[name]['lower_bound'] = self.baseline_stats[name]['q1'] - 1.5 * iqr
                self.baseline_stats[name]['upper_bound'] = self.baseline_stats[name]['q3'] + 1.5 * iqr
            
            return {
                'success': True,
                'features_analyzed': len(feature_names),
                'baseline': self.baseline_stats
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def detect_statistical_anomalies(self, data: np.ndarray, feature_names: List[str] = None, 
                                     z_threshold: float = 3.0) -> Dict:
        """Detect anomalies using statistical methods"""
        if not self.baseline_stats:
            return {'success': False, 'error': 'Baseline not computed'}
        
        try:
            n_features = data.shape[1] if len(data.shape) > 1 else 1
            
            if feature_names is None:
                feature_names = [f'feature_{i}' for i in range(n_features)]
            
            anomalies = []
            
            for sample_idx in range(len(data)):
                sample_anomalies = []
                
                for i, name in enumerate(feature_names):
                    if name not in self.baseline_stats:
                        continue
                    
                    value = data[sample_idx, i] if len(data.shape) > 1 else data[sample_idx]
                    stats = self.baseline_stats[name]
                    
                    # Z-score check
                    if stats['std'] > 0:
                        z_score = (value - stats['mean']) / stats['std']
                        if abs(z_score) > z_threshold:
                            sample_anomalies.append({
                                'feature': name,
                                'value': float(value),
                                'z_score': float(z_score),
                                'method': 'z_score'
                            })
                    
                    # IQR check
                    if value < stats['lower_bound'] or value > stats['upper_bound']:
                        sample_anomalies.append({
                            'feature': name,
                            'value': float(value),
                            'bounds': [stats['lower_bound'], stats['upper_bound']],
                            'method': 'iqr'
                        })
                
                if sample_anomalies:
                    anomalies.append({
                        'sample_index': sample_idx,
                        'anomalous_features': sample_anomalies,
                        'severity': 'HIGH' if len(sample_anomalies) > 3 else 'MEDIUM' if len(sample_anomalies) > 1 else 'LOW'
                    })
            
            return {
                'success': True,
                'total_samples': len(data),
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies[:50]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TimeSeriesDetector:
    """Time series anomaly detection"""
    
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.baseline = None
    
    def detect_anomalies(self, time_series: np.ndarray, timestamps: List = None) -> Dict:
        """Detect anomalies in time series data"""
        try:
            n = len(time_series)
            
            if n < self.window_size * 2:
                return {'success': False, 'error': 'Not enough data points'}
            
            anomalies = []
            
            # Rolling statistics
            for i in range(self.window_size, n):
                window = time_series[i-self.window_size:i]
                current = time_series[i]
                
                mean = np.mean(window)
                std = np.std(window)
                
                if std > 0:
                    z_score = (current - mean) / std
                    
                    if abs(z_score) > 3:
                        anomalies.append({
                            'index': i,
                            'timestamp': timestamps[i] if timestamps else i,
                            'value': float(current),
                            'expected_range': [float(mean - 2*std), float(mean + 2*std)],
                            'z_score': float(z_score),
                            'type': 'spike' if z_score > 0 else 'drop'
                        })
            
            # Detect sudden changes (derivatives)
            derivatives = np.diff(time_series)
            derivative_mean = np.mean(derivatives)
            derivative_std = np.std(derivatives)
            
            for i, deriv in enumerate(derivatives):
                if derivative_std > 0:
                    z = (deriv - derivative_mean) / derivative_std
                    if abs(z) > 4:
                        anomalies.append({
                            'index': i + 1,
                            'timestamp': timestamps[i+1] if timestamps else i+1,
                            'type': 'sudden_change',
                            'change_magnitude': float(deriv)
                        })
            
            return {
                'success': True,
                'total_points': n,
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies[:50]
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ThreatPredictor:
    """Predict potential threats using classification"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_importance = None
    
    def train(self, features: np.ndarray, labels: np.ndarray, feature_names: List[str] = None) -> Dict:
        """Train threat prediction model"""
        if not ML_AVAILABLE:
            return {'success': False, 'error': 'scikit-learn not available'}
        
        try:
            # Encode labels
            encoded_labels = self.label_encoder.fit_transform(labels)
            
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(
                features_scaled, encoded_labels, test_size=0.2, random_state=42
            )
            
            # Train Random Forest
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = self.model.predict(X_test)
            accuracy = (y_pred == y_test).mean()
            
            # Feature importance
            if feature_names:
                self.feature_importance = dict(zip(feature_names, self.model.feature_importances_))
            
            return {
                'success': True,
                'accuracy': float(accuracy),
                'classes': list(self.label_encoder.classes_),
                'feature_importance': self.feature_importance
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def predict(self, features: np.ndarray) -> Dict:
        """Predict threats"""
        if self.model is None:
            return {'success': False, 'error': 'Model not trained'}
        
        try:
            features_scaled = self.scaler.transform(features)
            predictions = self.model.predict(features_scaled)
            probabilities = self.model.predict_proba(features_scaled)
            
            results = []
            for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
                threat_class = self.label_encoder.inverse_transform([pred])[0]
                confidence = float(max(probs))
                
                results.append({
                    'sample_index': i,
                    'predicted_threat': threat_class,
                    'confidence': confidence,
                    'risk_level': 'CRITICAL' if confidence > 0.9 else 'HIGH' if confidence > 0.7 else 'MEDIUM' if confidence > 0.5 else 'LOW'
                })
            
            return {
                'success': True,
                'predictions': results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}


class EnhancedAnomalyDetector:
    """Master class combining all detection methods"""
    
    def __init__(self):
        self.isolation_forest = IsolationForestDetector()
        self.lof = LOFDetector()
        self.clustering = ClusteringDetector()
        self.statistical = StatisticalDetector()
        self.time_series = TimeSeriesDetector()
        self.threat_predictor = ThreatPredictor()
        self.feature_extractor = FeatureExtractor()
    
    def train_all_models(self, data: np.ndarray) -> Dict:
        """Train all anomaly detection models"""
        results = {}
        
        results['isolation_forest'] = self.isolation_forest.train(data)
        results['lof'] = self.lof.train(data)
        results['clustering'] = self.clustering.train(data)
        results['statistical'] = self.statistical.compute_baseline(data)
        
        return {
            'success': True,
            'models_trained': results
        }
    
    def detect_all(self, data: np.ndarray) -> Dict:
        """Run all detection methods and combine results"""
        results = {
            'isolation_forest': self.isolation_forest.predict(data),
            'lof': self.lof.predict(data),
            'clustering': self.clustering.detect_anomalies(data),
            'statistical': self.statistical.detect_statistical_anomalies(data)
        }
        
        # Combine anomalies from all methods
        all_anomaly_indices = set()
        method_votes = defaultdict(int)
        
        for method, result in results.items():
            if result.get('success') and 'anomalies' in result:
                for anomaly in result['anomalies']:
                    idx = anomaly.get('index', anomaly.get('sample_index', -1))
                    if idx >= 0:
                        all_anomaly_indices.add(idx)
                        method_votes[idx] += 1
        
        # Consensus anomalies (detected by multiple methods)
        consensus_anomalies = [
            {'index': idx, 'detection_methods': votes, 'confidence': votes / len(results)}
            for idx, votes in method_votes.items()
            if votes >= 2
        ]
        
        return {
            'success': True,
            'individual_results': results,
            'total_anomalies': len(all_anomaly_indices),
            'consensus_anomalies': sorted(consensus_anomalies, key=lambda x: -x['confidence']),
            'summary': {
                'samples_analyzed': len(data),
                'anomaly_rate': len(all_anomaly_indices) / len(data) if len(data) > 0 else 0,
                'high_confidence_anomalies': len([a for a in consensus_anomalies if a['confidence'] >= 0.5])
            }
        }
    
    def analyze_security_events(self, events: List[Dict]) -> Dict:
        """Analyze security events for anomalies"""
        if not events:
            return {'success': False, 'error': 'No events provided'}
        
        # Extract features
        features = np.array([
            self.feature_extractor.extract_user_features(event) 
            for event in events
        ])
        
        # Train and detect
        self.train_all_models(features)
        detection_results = self.detect_all(features)
        
        # Enrich results with event context
        anomalous_events = []
        for anomaly in detection_results.get('consensus_anomalies', []):
            idx = anomaly['index']
            if idx < len(events):
                anomalous_events.append({
                    **anomaly,
                    'event': events[idx]
                })
        
        return {
            'success': True,
            'events_analyzed': len(events),
            'detection_results': detection_results,
            'anomalous_events': anomalous_events,
            'recommendations': self._generate_recommendations(anomalous_events)
        }
    
    def _generate_recommendations(self, anomalies: List[Dict]) -> List[str]:
        """Generate security recommendations based on detected anomalies"""
        recommendations = []
        
        if not anomalies:
            return ['No anomalies detected - continue monitoring']
        
        # Analyze patterns
        has_after_hours = any(
            a.get('event', {}).get('hour', 12) < 6 or a.get('event', {}).get('hour', 12) > 22
            for a in anomalies
        )
        has_geo_anomaly = any(
            a.get('event', {}).get('new_location', False)
            for a in anomalies
        )
        has_privilege_escalation = any(
            a.get('event', {}).get('privilege_escalations', 0) > 0
            for a in anomalies
        )
        
        if has_after_hours:
            recommendations.append('ALERT: After-hours activity detected - review access policies')
        if has_geo_anomaly:
            recommendations.append('ALERT: Geographic anomaly detected - implement geo-fencing')
        if has_privilege_escalation:
            recommendations.append('CRITICAL: Privilege escalation detected - immediate review required')
        
        recommendations.extend([
            'Enable multi-factor authentication for all users',
            'Review and tighten access controls',
            'Implement user behavior analytics monitoring',
            'Set up real-time alerting for similar patterns'
        ])
        
        return recommendations


# Export functions
def get_enhanced_detector() -> EnhancedAnomalyDetector:
    return EnhancedAnomalyDetector()

def get_isolation_forest(contamination: float = 0.1) -> IsolationForestDetector:
    return IsolationForestDetector(contamination)

def get_lof_detector(n_neighbors: int = 20) -> LOFDetector:
    return LOFDetector(n_neighbors)

def get_clustering_detector(method: str = 'dbscan') -> ClusteringDetector:
    return ClusteringDetector(method)

def get_statistical_detector() -> StatisticalDetector:
    return StatisticalDetector()

def get_time_series_detector(window_size: int = 10) -> TimeSeriesDetector:
    return TimeSeriesDetector(window_size)

def get_threat_predictor() -> ThreatPredictor:
    return ThreatPredictor()
