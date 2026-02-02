"""
Adaptive Course Learner - Extracts and learns from Canvas course content.

Uses CANVAS_API_TOKEN from environment (.env) for authentication.
"""

from adaptive_learner.canvas_fetcher import CanvasContentFetcher
from adaptive_learner.perceptron_model import PerceptronFeatureExtractor
from adaptive_learner.rl_agent import RLContextBuilder
from adaptive_learner.learner import AdaptiveCourseLearner

__all__ = [
    "CanvasContentFetcher",
    "PerceptronFeatureExtractor",
    "RLContextBuilder",
    "AdaptiveCourseLearner",
]
