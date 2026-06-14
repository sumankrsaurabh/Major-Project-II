"""
Machine Learning Module
Classification, clustering, anomaly detection, recommendation
"""

import logging
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import silhouette_score
import pickle
import os

logger = logging.getLogger(__name__)


class TextClassifier:
    """Text classification using ML"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, max_depth=20)
        self.classes = ['positive', 'negative', 'neutral', 'technical', 'general']
        self.is_trained = False
    
    def train_classifier(self, X: np.ndarray, y: np.ndarray):
        """Train classifier"""
        try:
            self.model.fit(X, y)
            self.is_trained = True
            logger.info("Classifier trained successfully")
        except Exception as e:
            logger.error(f"Training error: {e}")
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict class labels and confidence"""
        if not self.is_trained:
            logger.warning("Classifier not trained")
            return np.array([]), np.array([])
        
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        confidence = np.max(probabilities, axis=1)
        
        return predictions, confidence
    
    def feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        if not self.is_trained:
            return {}
        
        importances = self.model.feature_importances_
        return {f'feature_{i}': float(imp) for i, imp in enumerate(importances)}


class DocumentClustering:
    """Cluster similar documents"""
    
    def __init__(self, n_clusters: int = 5):
        self.n_clusters = n_clusters
        self.scaler = StandardScaler()
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        self.is_fitted = False
    
    def fit(self, X: np.ndarray):
        """Fit clustering model"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.kmeans.fit(X_scaled)
            self.is_fitted = True
            logger.info(f"Clustering fitted with {self.n_clusters} clusters")
        except Exception as e:
            logger.error(f"Clustering fit error: {e}")
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict cluster assignments"""
        if not self.is_fitted:
            logger.warning("Clustering model not fitted")
            return np.array([]), np.array([])
        
        X_scaled = self.scaler.transform(X)
        clusters = self.kmeans.predict(X_scaled)
        distances = np.min(self.kmeans.transform(X_scaled), axis=1)
        
        return clusters, distances
    
    def get_cluster_info(self, X: np.ndarray) -> List[Dict]:
        """Get information about clusters"""
        if not self.is_fitted:
            return []
        
        clusters, distances = self.predict(X)
        cluster_info = []
        
        for i in range(self.n_clusters):
            mask = clusters == i
            cluster_info.append({
                'cluster_id': i,
                'size': int(np.sum(mask)),
                'center': self.kmeans.cluster_centers_[i].tolist() if hasattr(self, 'scaler') else [],
                'avg_distance': float(np.mean(distances[mask])) if np.sum(mask) > 0 else 0,
                'silhouette': self._calculate_silhouette(X, clusters)
            })
        
        return cluster_info
    
    def _calculate_silhouette(self, X: np.ndarray, clusters: np.ndarray) -> float:
        """Calculate silhouette score"""
        try:
            X_scaled = self.scaler.transform(X)
            return float(silhouette_score(X_scaled, clusters))
        except Exception as e:
            logger.error(f"Silhouette calculation error: {e}")
            return 0.0


class AnomalyDetector:
    """Detect anomalies in text/data"""
    
    def __init__(self, contamination: float = 0.1):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.is_fitted = False
    
    def fit(self, X: np.ndarray):
        """Fit anomaly detection model"""
        try:
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled)
            self.is_fitted = True
            logger.info("Anomaly detector fitted")
        except Exception as e:
            logger.error(f"Anomaly detector fit error: {e}")
    
    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies (-1 for anomaly, 1 for normal)"""
        if not self.is_fitted:
            return np.array([]), np.array([])
        
        X_scaled = self.scaler.transform(X)
        anomaly_labels = self.model.predict(X_scaled)
        anomaly_scores = -self.model.score_samples(X_scaled)  # Convert to positive scores
        
        return anomaly_labels, anomaly_scores
    
    def get_anomalies_with_scores(self, X: np.ndarray) -> List[Dict]:
        """Get anomalies with their scores"""
        anomalies, scores = self.predict(X)
        
        results = []
        for i, (label, score) in enumerate(zip(anomalies, scores)):
            if label == -1:  # Is anomaly
                results.append({
                    'index': i,
                    'anomaly_score': float(score),
                    'is_anomaly': True
                })
        
        results.sort(key=lambda x: x['anomaly_score'], reverse=True)
        return results


class RecommendationEngine:
    """Content-based recommendation system"""
    
    def __init__(self):
        self.user_profiles = {}
        self.content_vectors = {}
        self.interaction_history = {}
    
    def record_interaction(self, user_id: str, content_id: str, interaction_type: str, score: float):
        """Record user-content interaction"""
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
        
        self.interaction_history[user_id].append({
            'content_id': content_id,
            'type': interaction_type,  # 'view', 'like', 'share', 'click'
            'score': score
        })
    
    def update_user_profile(self, user_id: str, content_vectors: Dict[str, np.ndarray]):
        """Update user profile based on interactions"""
        if user_id not in self.interaction_history:
            return
        
        # Weight interactions
        weights = {'view': 1.0, 'like': 2.0, 'share': 3.0, 'click': 1.5}
        
        profile_vector = None
        total_weight = 0
        
        for interaction in self.interaction_history[user_id]:
            content_id = interaction['content_id']
            if content_id in content_vectors:
                weight = weights.get(interaction['type'], 1.0) * interaction['score']
                
                if profile_vector is None:
                    profile_vector = content_vectors[content_id] * weight
                else:
                    profile_vector += content_vectors[content_id] * weight
                
                total_weight += weight
        
        if profile_vector is not None and total_weight > 0:
            self.user_profiles[user_id] = profile_vector / total_weight
    
    def recommend_content(self, user_id: str, content_vectors: Dict[str, np.ndarray], 
                         top_k: int = 5) -> List[Tuple[str, float]]:
        """Recommend content for user"""
        if user_id not in self.user_profiles:
            logger.warning(f"User {user_id} not in profiles")
            return []
        
        user_vector = self.user_profiles[user_id]
        recommendations = []
        
        for content_id, content_vector in content_vectors.items():
            # Check if user already interacted
            if any(i['content_id'] == content_id for i in self.interaction_history.get(user_id, [])):
                continue
            
            # Cosine similarity
            similarity = self._cosine_similarity(user_vector, content_vector)
            recommendations.append((content_id, similarity))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_k]
    
    @staticmethod
    def _cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity"""
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (norm_v1 * norm_v2))


class DimensionalityReduction:
    """Reduce dimensionality of embeddings"""
    
    def __init__(self, n_components: int = 10):
        self.n_components = n_components
        self.pca = PCA(n_components=n_components)
        self.is_fitted = False
    
    def fit(self, X: np.ndarray):
        """Fit PCA model"""
        try:
            self.pca.fit(X)
            self.is_fitted = True
            logger.info(f"PCA fitted with {self.n_components} components")
        except Exception as e:
            logger.error(f"PCA fit error: {e}")
    
    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transform data to reduced dimensions"""
        if not self.is_fitted:
            logger.warning("PCA not fitted")
            return X
        
        return self.pca.transform(X)
    
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform data"""
        self.fit(X)
        return self.transform(X)
    
    def get_explained_variance(self) -> Dict[str, float]:
        """Get explained variance ratio"""
        if not self.is_fitted:
            return {}
        
        return {
            'total_variance': float(np.sum(self.pca.explained_variance_ratio_)),
            'variance_ratio': self.pca.explained_variance_ratio_.tolist(),
            'cumulative_variance': np.cumsum(self.pca.explained_variance_ratio_).tolist()
        }


class ModelPersistence:
    """Save and load ML models"""
    
    @staticmethod
    def save_model(model: object, filepath: str):
        """Save model to file"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Model save error: {e}")
    
    @staticmethod
    def load_model(filepath: str) -> Optional[object]:
        """Load model from file"""
        try:
            with open(filepath, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Model loaded from {filepath}")
            return model
        except Exception as e:
            logger.error(f"Model load error: {e}")
            return None
