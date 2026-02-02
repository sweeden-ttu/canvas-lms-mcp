---
name: adaptive-course-learner
description: Build adaptive knowledge systems that learn from Canvas course and module content using reinforcement learning and perceptrons. Use when processing course materials, building iterative learning models, extracting knowledge from Canvas modules, creating adaptive context builders, or implementing RL-based content understanding systems. Iteratively improves understanding through reward-based learning and neural network pattern recognition.
---

# Adaptive Course Learner

Build reinforcement learning systems that iteratively learn from Canvas course and module content using perceptrons and RL techniques.

## Quick Start

**Setup:**
```bash
mkdir adaptive-learner && cd adaptive-learner
uv init --name adaptive-learner --python 3.10+
uv add numpy scikit-learn torch transformers
```

**Project structure:**
```
adaptive-learner/
├── knowledge_base/         # Learned knowledge storage
│   ├── course_{id}/       # Per-course folders
│   │   └── module_{id}/   # Per-module folders
├── models/                 # Trained models
│   ├── perceptron.pkl     # Perceptron model
│   └── rl_agent.json      # RL agent Q-table
├── learner.py              # Main system
├── perceptron_model.py     # Perceptron implementation
├── rl_agent.py             # RL agent
└── canvas_fetcher.py        # Content fetcher
```

## Architecture

Three-component system:
1. **Content Fetcher** - Retrieves Canvas course/module data via API/MCP
2. **Perceptron Network** - Extracts features and patterns using MLP
3. **RL Agent** - Learns optimal context building strategies via Q-learning

## Implementation Pattern

### Step 1: Content Fetcher

**canvas_fetcher.py:**
```python
import httpx
import json
from pathlib import Path
from config import load_env_config, get_api_headers

class CanvasContentFetcher:
    def __init__(self):
        self.config = load_env_config()
    
    async def fetch_course_content(self, course_id: int) -> dict:
        async with httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=get_api_headers(self.config.api_token)
        ) as client:
            modules = (await client.get(f"/api/v1/courses/{course_id}/modules")).json()
            for module in modules:
                module["items"] = (await client.get(
                    f"/api/v1/courses/{course_id}/modules/{module['id']}/items"
                )).json()
            return {"course_id": course_id, "modules": modules}
    
    def save_to_folder(self, content: dict, base_path: Path):
        course_path = base_path / f"course_{content['course_id']}"
        course_path.mkdir(exist_ok=True)
        for module in content["modules"]:
            module_path = course_path / f"module_{module['id']}"
            module_path.mkdir(exist_ok=True)
            (module_path / "items.json").write_text(json.dumps(module["items"], indent=2))
```

### Step 2: Perceptron Feature Extractor

**perceptron_model.py:**
```python
import numpy as np
from sklearn.neural_network import MLPClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle

class PerceptronFeatureExtractor:
    def __init__(self, hidden_layers=(100, 50)):
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.perceptron = MLPClassifier(
            hidden_layer_sizes=hidden_layers,
            activation='relu',
            solver='adam',
            max_iter=500
        )
        self.is_fitted = False
    
    def extract_features(self, content: dict) -> np.ndarray:
        texts = [m.get("name", "") for m in content.get("modules", [])]
        for m in content.get("modules", []):
            texts.extend([i.get("title", "") for i in m.get("items", [])])
        
        if not self.is_fitted:
            features = self.vectorizer.fit_transform(texts)
            self.is_fitted = True
        else:
            features = self.vectorizer.transform(texts)
        
        return np.mean(features.toarray(), axis=0)
    
    def learn_patterns(self, course_contents: list, labels: np.ndarray = None):
        if labels is None:
            labels = np.array([i % 3 for i in range(len(course_contents))])
        features = np.array([self.extract_features(c) for c in course_contents])
        self.perceptron.fit(features, labels)
        return self.perceptron
    
    def predict_importance(self, content: dict) -> float:
        features = self.extract_features(content).reshape(1, -1)
        return float(self.perceptron.decision_function(features)[0])
```

### Step 3: Reinforcement Learning Agent

**rl_agent.py:**
```python
import numpy as np
from collections import defaultdict
import json

class RLContextBuilder:
    def __init__(self, learning_rate=0.1, discount_factor=0.9, epsilon=0.1):
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon
        self.q_table = defaultdict(lambda: defaultdict(float))
    
    def get_state(self, course_content: dict, context: list) -> str:
        module_count = len(course_content.get("modules", []))
        item_count = sum(len(m.get("items", [])) for m in course_content.get("modules", []))
        return f"{module_count}_{item_count}_{len(context)}"
    
    def choose_action(self, state: str, actions: list) -> str:
        if np.random.random() < self.epsilon:
            return np.random.choice(actions)
        q_values = {a: self.q_table[state][a] for a in actions}
        return max(q_values, key=q_values.get)
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str, next_actions: list):
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state][a] for a in next_actions) if next_actions else 0
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * max_next_q - current_q)
        self.q_table[state][action] = new_q
    
    def calculate_reward(self, action: str, context_quality: float, user_feedback: float = 0.5) -> float:
        base_reward = context_quality
        feedback_reward = (user_feedback + 1) / 2
        reward = 0.7 * base_reward + 0.3 * feedback_reward
        return reward * (0.8 if action in self.action_history[-5:] else 1.0)
    
    def build_context_iteratively(self, course_content: dict, perceptron, max_iterations: int = 10) -> list:
        context = []
        state = self.get_state(course_content, context)
        
        for _ in range(max_iterations):
            actions = [f"add_module_{m['id']}" for m in course_content.get("modules", []) 
                      if f"module_{m['id']}" not in " ".join(context)]
            if not actions:
                break
            
            action = self.choose_action(state, actions)
            item, quality = self._execute_action(action, course_content, perceptron)
            
            reward = self.calculate_reward(action, quality)
            context.append(item)
            next_state = self.get_state(course_content, context)
            next_actions = [f"add_module_{m['id']}" for m in course_content.get("modules", [])]
            
            self.update_q_value(state, action, reward, next_state, next_actions)
            state = next_state
        
        return context
    
    def _execute_action(self, action: str, course_content: dict, perceptron) -> tuple:
        if action.startswith("add_module_"):
            module_id = int(action.split("_")[-1])
            module = next(m for m in course_content["modules"] if m["id"] == module_id)
            text = f"Module {module.get('name', '')}: " + "; ".join(
                [i.get("title", "") for i in module.get("items", [])[:5]]
            )
            importance = perceptron.predict_importance({"modules": [module]})
            return text, float(importance)
        return "", 0.0
```

### Step 4: Integrated System

**learner.py:**
```python
from pathlib import Path
from canvas_fetcher import CanvasContentFetcher
from perceptron_model import PerceptronFeatureExtractor
from rl_agent import RLContextBuilder
import asyncio
import json

class AdaptiveCourseLearner:
    def __init__(self, knowledge_base_path: Path = Path("knowledge_base")):
        self.knowledge_base = knowledge_base_path
        self.knowledge_base.mkdir(exist_ok=True)
        self.fetcher = CanvasContentFetcher()
        self.perceptron = PerceptronFeatureExtractor()
        self.rl_agent = RLContextBuilder()
        self._load_models()
    
    async def learn_from_course(self, course_id: int, iterations: int = 5):
        course_content = await self.fetcher.fetch_course_content(course_id)
        self.fetcher.save_to_folder(course_content, self.knowledge_base)
        self.perceptron.learn_patterns([course_content])
        context = self.rl_agent.build_context_iteratively(
            course_content, self.perceptron, max_iterations=iterations
        )
        (self.knowledge_base / f"course_{course_id}_context.json").write_text(
            json.dumps({"course_id": course_id, "context": context}, indent=2)
        )
        self._save_models()
        return context
    
    def _save_models(self):
        Path("models").mkdir(exist_ok=True)
        import pickle
        with open("models/perceptron.pkl", "wb") as f:
            pickle.dump({"vectorizer": self.perceptron.vectorizer, 
                        "perceptron": self.perceptron.perceptron}, f)
        with open("models/rl_agent.json", "w") as f:
            json.dump({k: dict(v) for k, v in self.rl_agent.q_table.items()}, f)
    
    def _load_models(self):
        # Load if exists
        pass

# Usage
async def main():
    learner = AdaptiveCourseLearner()
    for course_id in [58606, 53482, 51243]:
        context = await learner.learn_from_course(course_id, iterations=10)
        print(f"Course {course_id}: {len(context)} items")

if __name__ == "__main__":
    asyncio.run(main())
```

## Training Workflow

**1. Initial training:**
```bash
uv run python learner.py --course-id 58606 --iterations 5
```

**2. Incremental learning:**
```python
learner = AdaptiveCourseLearner()
await learner.learn_from_course(53482, iterations=10)
await learner.learn_from_course(51243, iterations=10)
```

**3. Build context for new course:**
```python
course_content = await fetcher.fetch_course_content(new_course_id)
context = rl_agent.build_context_iteratively(course_content, perceptron, max_iterations=15)
```

## Reward Function

**Metrics:**
- Coverage: Content inclusion percentage
- Relevance: Perceptron importance scores
- Coherence: Logical flow of context
- User feedback: Explicit feedback (-1 to 1)

**Reward formula:**
```python
reward = 0.7 * context_quality + 0.3 * ((user_feedback + 1) / 2)
if redundant: reward *= 0.8
```

## Best Practices

- [ ] Start with 1-2 courses, iterate gradually
- [ ] Monitor reward history to assess progress
- [ ] Balance exploration (epsilon) vs exploitation
- [ ] Tune perceptron architecture (hidden_layers) for content
- [ ] Cache built contexts to avoid recomputation
- [ ] Update models incrementally as courses added
- [ ] Validate context quality with sample queries
- [ ] Persist models and Q-table after each session

## Advanced Techniques

**Deeper perceptron:**
```python
perceptron = PerceptronFeatureExtractor(hidden_layers=(200, 100, 50))
```

**Epsilon decay:**
```python
rl_agent.epsilon = max(0.01, rl_agent.epsilon * 0.95)
```

**Context pruning:**
```python
context = [item for item in context if importance(item) > threshold]
```

## Integration with Canvas MCP

**Use MCP tools instead of direct API:**
```python
from mcp import Client

async def fetch_via_mcp(course_id: int):
    client = Client("canvas_mcp")
    modules = await client.call_tool("canvas_get_modules", {"course_id": course_id})
    module_items = await client.call_tool("canvas_list_module_items", 
                                         {"course_id": course_id, "module_id": module["id"]})
```
