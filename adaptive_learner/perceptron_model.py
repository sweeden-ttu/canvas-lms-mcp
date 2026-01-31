"""
Perceptron Feature Extractor - ML-based importance scoring for course content.
"""

import pickle
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier


class PerceptronFeatureExtractor:
    """Extracts features and predicts importance using MLP classifier."""

    def __init__(self, hidden_layers: tuple[int, ...] = (100, 50)):
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", max_df=0.95, min_df=1
        )
        self.perceptron = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation="relu",
            solver="adam",
            max_iter=500,
            random_state=42,
        )
        self.is_fitted = False

    def _collect_texts(self, content: dict) -> list[str]:
        """Extract text from course content for vectorization."""
        texts = []
        for m in content.get("modules", []):
            texts.append(m.get("name", ""))
            for item in m.get("items", []):
                texts.append(item.get("title", ""))
        return [t for t in texts if t]

    def extract_features(self, content: dict) -> np.ndarray:
        """Extract feature vector from course content."""
        texts = self._collect_texts(content)
        if not texts:
            return np.zeros(self.vectorizer.max_features)

        if not self.is_fitted:
            features = self.vectorizer.fit_transform(texts)
            self.is_fitted = True
        else:
            features = self.vectorizer.transform(texts)

        return np.mean(features.toarray(), axis=0)

    def learn_patterns(
        self,
        course_contents: list[dict],
        labels: np.ndarray | None = None,
    ) -> "PerceptronFeatureExtractor":
        """Fit the perceptron on course contents."""
        if labels is None:
            labels = np.array([i % 3 for i in range(len(course_contents))])
        features = np.array([self.extract_features(c) for c in course_contents])
        self.perceptron.fit(features, labels)
        return self

    def predict_importance(self, content: dict) -> float:
        """Predict importance score for content (higher = more important)."""
        features = self.extract_features(content).reshape(1, -1)
        if not self.is_fitted or features.shape[1] == 0:
            return 0.0
        try:
            return float(self.perceptron.decision_function(features)[0])
        except Exception:
            return 0.0

    def save(self, path: Path) -> None:
        """Save model to disk."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(
                {
                    "vectorizer": self.vectorizer,
                    "perceptron": self.perceptron,
                    "is_fitted": self.is_fitted,
                },
                f,
            )

    def load(self, path: Path) -> "PerceptronFeatureExtractor":
        """Load model from disk."""
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.vectorizer = data["vectorizer"]
        self.perceptron = data["perceptron"]
        self.is_fitted = data.get("is_fitted", True)
        return self
