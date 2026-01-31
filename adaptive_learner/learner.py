"""
Adaptive Course Learner - Integrated system for learning from Canvas courses.
"""

import json
import pickle
from pathlib import Path

from adaptive_learner.canvas_fetcher import CanvasContentFetcher
from adaptive_learner.perceptron_model import PerceptronFeatureExtractor
from adaptive_learner.rl_agent import RLContextBuilder


class AdaptiveCourseLearner:
    """Orchestrates content fetching, perceptron learning, and RL context building."""

    def __init__(self, knowledge_base_path: Path | None = None):
        self.knowledge_base = knowledge_base_path or Path("knowledge_base")
        self.knowledge_base.mkdir(parents=True, exist_ok=True)
        self.models_path = self.knowledge_base / "models"
        self.models_path.mkdir(exist_ok=True)
        self.fetcher = CanvasContentFetcher()
        self.perceptron = PerceptronFeatureExtractor()
        self.rl_agent = RLContextBuilder()
        self._load_models()

    def learn_from_course(
        self,
        course_id: int,
        iterations: int = 5,
    ) -> list[str]:
        """
        Fetch course content, learn patterns, and build optimal context.

        Args:
            course_id: Canvas course ID
            iterations: Max RL iterations for context building

        Returns:
            List of context strings (module summaries)
        """
        course_content = self.fetcher.fetch_course_content(course_id)
        self.fetcher.save_to_folder(course_content, self.knowledge_base)
        self.perceptron.learn_patterns([course_content])
        context = self.rl_agent.build_context_iteratively(
            course_content, self.perceptron, max_iterations=iterations
        )
        context_path = self.knowledge_base / f"course_{course_id}_context.json"
        context_path.write_text(
            json.dumps({"course_id": course_id, "context": context}, indent=2)
        )
        self._save_models()
        return context

    def get_course_content(self, course_id: int) -> dict:
        """Fetch and return raw course content (no learning)."""
        return self.fetcher.fetch_course_content(course_id)

    def _save_models(self) -> None:
        """Persist perceptron and RL agent."""
        self.perceptron.save(self.models_path / "perceptron.pkl")
        self.rl_agent.save(self.models_path / "rl_agent.json")

    def _load_models(self) -> None:
        """Load persisted models if they exist."""
        pkl = self.models_path / "perceptron.pkl"
        if pkl.exists():
            self.perceptron.load(pkl)
        rl = self.models_path / "rl_agent.json"
        if rl.exists():
            self.rl_agent.load(rl)
