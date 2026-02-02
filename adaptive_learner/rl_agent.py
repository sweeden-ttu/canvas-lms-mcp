"""
RL Context Builder - Q-learning agent for optimal context construction.
"""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np


class RLContextBuilder:
    """Q-learning agent that builds optimal context from course content."""

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        epsilon: float = 0.1,
    ):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.action_history: list[str] = []

    def get_state(self, course_content: dict, context: list) -> str:
        """Encode state as string for Q-table lookup."""
        module_count = len(course_content.get("modules", []))
        item_count = sum(
            len(m.get("items", [])) for m in course_content.get("modules", [])
        )
        return f"{module_count}_{item_count}_{len(context)}"

    def choose_action(self, state: str, actions: list[str]) -> str:
        """Epsilon-greedy action selection."""
        if not actions:
            return ""
        if np.random.random() < self.epsilon:
            return np.random.choice(actions)
        q_values = {a: self.q_table[state][a] for a in actions}
        return max(q_values, key=q_values.get)

    def update_q_value(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        next_actions: list[str],
    ) -> None:
        """Q-learning update."""
        current_q = self.q_table[state][action]
        max_next_q = (
            max(self.q_table[next_state][a] for a in next_actions)
            if next_actions
            else 0.0
        )
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        self.q_table[state][action] = new_q

    def calculate_reward(
        self,
        action: str,
        context_quality: float,
        user_feedback: float = 0.5,
    ) -> float:
        """Compute reward for an action."""
        base_reward = context_quality
        feedback_reward = (user_feedback + 1) / 2
        reward = 0.7 * base_reward + 0.3 * feedback_reward
        # Penalize recent redundancy
        if action in self.action_history[-5:]:
            reward *= 0.8
        return reward

    def _execute_action(
        self,
        action: str,
        course_content: dict,
        perceptron,
    ) -> tuple[str, float]:
        """Execute add_module action and return (text, quality)."""
        if action.startswith("add_module_"):
            module_id = int(action.split("_")[-1])
            module = next(
                (m for m in course_content["modules"] if m["id"] == module_id),
                None,
            )
            if not module:
                return "", 0.0
            text = f"Module {module.get('name', '')}: " + "; ".join(
                [i.get("title", "") for i in module.get("items", [])[:5]]
            )
            importance = perceptron.predict_importance({"modules": [module]})
            return text, float(importance)
        return "", 0.0

    def build_context_iteratively(
        self,
        course_content: dict,
        perceptron,
        max_iterations: int = 10,
    ) -> list[str]:
        """Build context by iteratively adding modules via RL."""
        context: list[str] = []
        state = self.get_state(course_content, context)

        added_module_ids: set[int] = set()
        for _ in range(max_iterations):
            actions = [
                f"add_module_{m['id']}"
                for m in course_content.get("modules", [])
                if m["id"] not in added_module_ids
            ]
            if not actions:
                break

            action = self.choose_action(state, actions)
            item, quality = self._execute_action(action, course_content, perceptron)

            reward = self.calculate_reward(action, quality)
            context.append(item)
            self.action_history.append(action)
            if action.startswith("add_module_"):
                added_module_ids.add(int(action.split("_")[-1]))

            next_state = self.get_state(course_content, context)
            next_actions = [
                f"add_module_{m['id']}"
                for m in course_content.get("modules", [])
                if m["id"] not in added_module_ids
            ]

            self.update_q_value(state, action, reward, next_state, next_actions)
            state = next_state

        return context

    def save(self, path: Path) -> None:
        """Save Q-table to JSON."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(
                {k: dict(v) for k, v in self.q_table.items()},
                f,
                indent=2,
            )

    def load(self, path: Path) -> "RLContextBuilder":
        """Load Q-table from JSON."""
        if path.exists():
            with open(path) as f:
                self.q_table = defaultdict(
                    lambda: defaultdict(float),
                    {k: defaultdict(float, v) for k, v in json.load(f).items()},
                )
        return self
