"""
Bayesian Bank Statement Reader with Q-Learning

A probabilistic income extraction system that:
- Uses Bayesian reasoning to classify income items
- Uses Q-learning to optimize extraction and avoid missed income
- Has "ghost hunting" mode (4 uses) for large deposit analysis
- Exports income to CSV organized by month/year
"""

import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
import uuid

import pdfplumber
import numpy as np
from dataclasses import dataclass, field

from agents.bayesian.schemas import BayesianBelief, Evidence, EvidenceType


@dataclass
class IncomeItem:
    """Represents a single income transaction."""
    date: str
    description: str
    amount: float
    transaction_type: str  # "credit", "deposit", "transfer_in", etc.
    confidence: float  # Bayesian confidence (0-1)
    line_number: int
    page_number: int
    raw_text: str
    item_id: str = field(default_factory=lambda: f"inc-{uuid.uuid4().hex[:8]}")


@dataclass
class QLearningConfig:
    """Configuration for Q-learning agent."""
    learning_rate: float = 0.1
    discount_factor: float = 0.9
    epsilon: float = 0.15  # Exploration rate
    large_deposit_threshold: float = 10000.0  # Threshold for "ghost hunting"
    ghost_hunt_uses: int = 4  # Number of ghost hunting opportunities


class BayesianIncomeClassifier:
    """
    Bayesian classifier for identifying income items from bank statements.
    
    Uses probabilistic reasoning to classify transactions as income based on:
    - Transaction patterns
    - Amount characteristics
    - Description keywords
    - Historical patterns
    """
    
    def __init__(self):
        # Income indicators (prior probabilities)
        self.income_keywords = {
            "deposit": 0.85,
            "credit": 0.80,
            "payment": 0.70,
            "transfer": 0.60,
            "refund": 0.75,
            "income": 0.90,
            "salary": 0.95,
            "wage": 0.95,
            "commission": 0.85,
            "fee": 0.40,  # Lower - could be expense
            "charge": 0.20,  # Lower - likely expense
        }
        
        # Non-income indicators (negative evidence)
        self.expense_keywords = {
            "debit": 0.10,
            "withdrawal": 0.15,
            "purchase": 0.20,
            "fee": 0.30,
            "charge": 0.25,
            "payment": 0.40,  # Ambiguous
        }
        
        # Amount-based priors
        self.amount_patterns = {
            "regular": 0.70,  # Regular amounts suggest income
            "irregular": 0.50,
            "large": 0.60,  # Large amounts might be income
            "small": 0.40,
        }
    
    def classify_transaction(
        self,
        description: str,
        amount: float,
        transaction_type: str,
    ) -> Tuple[bool, float]:
        """
        Classify a transaction as income using Bayesian reasoning.
        
        Returns:
            (is_income: bool, confidence: float)
        """
        desc_lower = description.lower()
        
        # Start with base prior based on transaction type
        if transaction_type.lower() in ["credit", "deposit", "transfer_in"]:
            prior = 0.70
        elif transaction_type.lower() in ["debit", "withdrawal", "transfer_out"]:
            prior = 0.20
        else:
            prior = 0.50  # Neutral
        
        # Update belief with keyword evidence
        belief = BayesianBelief(prior=prior)
        
        # Check for income keywords
        income_evidence_found = False
        for keyword, likelihood in self.income_keywords.items():
            if keyword in desc_lower:
                income_evidence_found = True
                # Update belief: P(income | keyword) = high
                belief = belief.update(evidence_supports=True, strength=likelihood)
        
        # Check for expense keywords (negative evidence)
        expense_evidence_found = False
        for keyword, likelihood in self.expense_keywords.items():
            if keyword in desc_lower:
                expense_evidence_found = True
                # Update belief: P(income | expense_keyword) = low
                belief = belief.update(evidence_supports=False, strength=1.0 - likelihood)
        
        # Amount-based evidence
        if amount > 0:
            # Regular amounts (multiples of 100, 1000) suggest income
            if amount % 100 == 0 or amount % 1000 == 0:
                belief = belief.update(evidence_supports=True, strength=0.65)
            
            # Very large amounts might be income
            if amount >= 5000:
                belief = belief.update(evidence_supports=True, strength=0.60)
        
        # Final posterior probability
        posterior = belief.posterior or belief.prior
        
        # Classify as income if posterior > 0.5
        is_income = posterior > 0.5
        
        return is_income, posterior
    
    def refine_classification(
        self,
        item: IncomeItem,
        additional_context: Dict[str, Any],
    ) -> Tuple[bool, float]:
        """
        Refine classification with additional context (ghost hunting mode).
        
        Args:
            item: The income item to refine
            additional_context: Additional context (e.g., large deposit patterns)
        
        Returns:
            (is_income: bool, refined_confidence: float)
        """
        is_income, base_confidence = self.classify_transaction(
            item.description,
            item.amount,
            item.transaction_type,
        )
        
        # If it's a large deposit, increase confidence
        if additional_context.get("is_large_deposit", False):
            # Large deposits are more likely to be income
            refined_confidence = min(1.0, base_confidence + 0.15)
            is_income = refined_confidence > 0.5
            return is_income, refined_confidence
        
        return is_income, base_confidence


class QLearningIncomeExtractor:
    """
    Q-learning agent that optimizes income extraction to avoid missing items.
    
    States: (page_number, items_found_count, confidence_level)
    Actions: ["extract_normal", "extract_careful", "ghost_hunt", "skip"]
    Rewards: 
        - Positive: Found income item
        - Negative: Missed income item (ghost found it)
        - Penalty: Used ghost hunt unnecessarily
    """
    
    def __init__(self, config: QLearningConfig):
        self.config = config
        self.q_table: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.action_history: List[Tuple[str, str, float]] = []  # (state, action, reward)
        self.ghost_hunt_uses_remaining = config.ghost_hunt_uses
        self.missed_items: List[IncomeItem] = []
    
    def get_state(
        self,
        page_num: int,
        items_found: int,
        avg_confidence: float,
    ) -> str:
        """Encode state as string for Q-table lookup."""
        confidence_level = "high" if avg_confidence > 0.7 else "medium" if avg_confidence > 0.5 else "low"
        return f"p{page_num}_i{items_found}_c{confidence_level}"
    
    def get_available_actions(self, state: str) -> List[str]:
        """Get available actions for current state."""
        actions = ["extract_normal", "extract_careful"]
        
        # Ghost hunt only available if uses remaining
        if self.ghost_hunt_uses_remaining > 0:
            actions.append("ghost_hunt")
        
        return actions
    
    def choose_action(self, state: str, available_actions: List[str]) -> str:
        """Epsilon-greedy action selection."""
        if not available_actions:
            return "extract_normal"
        
        # Epsilon-greedy: explore with probability epsilon
        if np.random.random() < self.config.epsilon:
            return np.random.choice(available_actions)
        
        # Exploit: choose action with highest Q-value
        q_values = {a: self.q_table[state][a] for a in available_actions}
        return max(q_values, key=q_values.get)
    
    def update_q_value(
        self,
        state: str,
        action: str,
        reward: float,
        next_state: str,
        next_actions: List[str],
    ) -> None:
        """Update Q-value using Q-learning algorithm."""
        current_q = self.q_table[state][action]
        
        # Max Q-value for next state
        max_next_q = (
            max(self.q_table[next_state][a] for a in next_actions)
            if next_actions and next_state in self.q_table
            else 0.0
        )
        
        # Q-learning update: Q(s,a) = Q(s,a) + α[r + γ*max(Q(s',a')) - Q(s,a)]
        new_q = current_q + self.config.learning_rate * (
            reward + self.config.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def calculate_reward(
        self,
        action: str,
        items_found: int,
        items_missed: int,
        used_ghost_hunt: bool,
    ) -> float:
        """
        Calculate reward for an action.
        
        Rewards:
        - +10 per income item found
        - -20 per income item missed (ghost found it)
        - -5 for unnecessary ghost hunt use
        """
        reward = items_found * 10.0
        
        # Heavy penalty for missed items (ghosts found them)
        reward -= items_missed * 20.0
        
        # Penalty for unnecessary ghost hunt
        if used_ghost_hunt and items_found == 0:
            reward -= 5.0
        
        return reward
    
    def use_ghost_hunt(self) -> bool:
        """Use a ghost hunt opportunity. Returns True if successful."""
        if self.ghost_hunt_uses_remaining > 0:
            self.ghost_hunt_uses_remaining -= 1
            return True
        return False


class BankStatementReader:
    """
    Main bank statement reader that combines Bayesian classification
    and Q-learning optimization.
    """
    
    def __init__(self, config: Optional[QLearningConfig] = None):
        self.config = config or QLearningConfig()
        self.classifier = BayesianIncomeClassifier()
        self.q_agent = QLearningIncomeExtractor(self.config)
        self.income_items: List[IncomeItem] = []
        self.extraction_history: List[Dict] = []
    
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Dict]:
        """
        Extract text and tables from PDF bank statement.
        
        Returns:
            List of page data with text and tables
        """
        pages_data = []
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                tables = page.extract_tables()
                
                pages_data.append({
                    "page_number": page_num,
                    "text": text or "",
                    "tables": tables or [],
                })
        
        return pages_data
    
    def parse_transaction_line(self, line: str, page_num: int, line_num: int) -> Optional[IncomeItem]:
        """
        Parse a single transaction line from bank statement.
        
        Common formats:
        - "01/15/2025 DEPOSIT 1,234.56"
        - "01/15/2025 CHECK DEPOSIT 1,234.56"
        - "01/15/2025 ACH CREDIT 1,234.56"
        """
        # Pattern for date at start: MM/DD/YYYY or M/D/YYYY
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        date_match = re.search(date_pattern, line)
        
        if not date_match:
            return None
        
        date_str = date_match.group(1)
        
        # Extract amount (look for numbers with decimal points, possibly with commas)
        amount_pattern = r'([\d,]+\.\d{2})'
        amount_matches = re.findall(amount_pattern, line)
        
        if not amount_matches:
            return None
        
        # Take the last amount (usually the balance or transaction amount)
        amount_str = amount_matches[-1].replace(',', '')
        try:
            amount = float(amount_str)
        except ValueError:
            return None
        
        # Extract description (everything between date and amount)
        date_end = date_match.end()
        amount_start = line.rfind(amount_matches[-1])
        description = line[date_end:amount_start].strip()
        
        # Determine transaction type from description
        desc_lower = description.lower()
        if any(kw in desc_lower for kw in ["deposit", "credit", "ach credit"]):
            trans_type = "credit"
        elif any(kw in desc_lower for kw in ["transfer", "wire"]):
            trans_type = "transfer_in" if amount > 0 else "transfer_out"
        else:
            trans_type = "unknown"
        
        # Classify as income
        is_income, confidence = self.classifier.classify_transaction(
            description,
            amount,
            trans_type,
        )
        
        if not is_income:
            return None
        
        return IncomeItem(
            date=date_str,
            description=description,
            amount=amount,
            transaction_type=trans_type,
            confidence=confidence,
            line_number=line_num,
            page_number=page_num,
            raw_text=line,
        )
    
    def extract_income_from_page(
        self,
        page_data: Dict,
        use_ghost_hunt: bool = False,
    ) -> List[IncomeItem]:
        """
        Extract income items from a single page.
        
        Args:
            page_data: Page data with text and tables
            use_ghost_hunt: Whether to use ghost hunting mode (careful extraction)
        
        Returns:
            List of income items found
        """
        page_num = page_data["page_number"]
        text = page_data["text"]
        tables = page_data["tables"]
        
        income_items = []
        
        # Extract from text lines
        if text:
            lines = text.split('\n')
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                item = self.parse_transaction_line(line, page_num, line_num)
                if item:
                    # If ghost hunting, refine classification
                    if use_ghost_hunt:
                        is_income, refined_conf = self.classifier.refine_classification(
                            item,
                            {"is_large_deposit": item.amount >= self.config.large_deposit_threshold},
                        )
                        item.confidence = refined_conf
                        if is_income:
                            income_items.append(item)
                    else:
                        income_items.append(item)
        
        # Extract from tables
        for table in tables:
            if not table:
                continue
            
            # Look for transaction rows in table
            for row_idx, row in enumerate(table):
                if not row:
                    continue
                
                # Join row cells into a line
                row_text = " ".join(str(cell) if cell else "" for cell in row)
                
                item = self.parse_transaction_line(row_text, page_num, row_idx)
                if item:
                    if use_ghost_hunt:
                        is_income, refined_conf = self.classifier.refine_classification(
                            item,
                            {"is_large_deposit": item.amount >= self.config.large_deposit_threshold},
                        )
                        item.confidence = refined_conf
                        if is_income:
                            income_items.append(item)
                    else:
                        income_items.append(item)
        
        return income_items
    
    def process_pdf(self, pdf_path: Path) -> List[IncomeItem]:
        """
        Process entire PDF using Q-learning to optimize extraction.
        
        Returns:
            List of all income items found
        """
        pages_data = self.extract_text_from_pdf(pdf_path)
        all_income_items = []
        
        items_found_so_far = 0
        
        for page_data in pages_data:
            page_num = page_data["page_number"]
            
            # Calculate average confidence so far
            avg_confidence = (
                np.mean([item.confidence for item in all_income_items])
                if all_income_items
                else 0.5
            )
            
            # Get current state
            state = self.q_agent.get_state(page_num, items_found_so_far, avg_confidence)
            available_actions = self.q_agent.get_available_actions(state)
            
            # Choose action using Q-learning
            action = self.q_agent.choose_action(state, available_actions)
            
            # Execute action
            use_ghost_hunt = False
            if action == "ghost_hunt":
                use_ghost_hunt = self.q_agent.use_ghost_hunt()
            
            # Extract income from page
            page_income = self.extract_income_from_page(
                page_data,
                use_ghost_hunt=use_ghost_hunt,
            )
            
            items_found = len(page_income)
            items_missed = 0  # Would be detected by comparing with other models
            
            # Calculate reward
            reward = self.q_agent.calculate_reward(
                action,
                items_found,
                items_missed,
                use_ghost_hunt,
            )
            
            # Update Q-value
            next_state = self.q_agent.get_state(
                page_num + 1,
                items_found_so_far + items_found,
                avg_confidence,
            )
            next_actions = self.q_agent.get_available_actions(next_state)
            
            self.q_agent.update_q_value(state, action, reward, next_state, next_actions)
            
            # Record action
            self.q_agent.action_history.append((state, action, reward))
            
            # Add to results
            all_income_items.extend(page_income)
            items_found_so_far += items_found
            
            # Record extraction step
            self.extraction_history.append({
                "page": page_num,
                "action": action,
                "items_found": items_found,
                "reward": reward,
                "ghost_hunt_used": use_ghost_hunt,
            })
        
        self.income_items = all_income_items
        return all_income_items
    
    def export_to_csv(
        self,
        output_path: Path,
        group_by_month: bool = True,
    ) -> Path:
        """
        Export income items to CSV, optionally grouped by month/year.
        
        Args:
            output_path: Output CSV file path
            group_by_month: If True, create separate CSV files per month/year
        
        Returns:
            Path to created CSV file(s)
        """
        if not self.income_items:
            raise ValueError("No income items to export")
        
        if group_by_month:
            # Group by month/year
            grouped = defaultdict(list)
            
            for item in self.income_items:
                # Parse date to get month/year
                try:
                    # Try MM/DD/YYYY format
                    date_parts = item.date.split('/')
                    if len(date_parts) == 3:
                        month = date_parts[0].zfill(2)
                        year = date_parts[2] if len(date_parts[2]) == 4 else f"20{date_parts[2]}"
                        key = f"{year}_{month}"
                    else:
                        key = "unknown"
                except:
                    key = "unknown"
                
                grouped[key].append(item)
            
            # Create CSV for each month/year
            created_files = []
            for month_year, items in grouped.items():
                csv_path = output_path.parent / f"{output_path.stem}_{month_year}.csv"
                
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "Date",
                        "Description",
                        "Amount",
                        "Transaction Type",
                        "Confidence",
                        "Page Number",
                        "Line Number",
                        "Item ID",
                    ])
                    
                    for item in sorted(items, key=lambda x: x.date):
                        writer.writerow([
                            item.date,
                            item.description,
                            f"{item.amount:.2f}",
                            item.transaction_type,
                            f"{item.confidence:.3f}",
                            item.page_number,
                            item.line_number,
                            item.item_id,
                        ])
                
                created_files.append(csv_path)
            
            return created_files[0] if created_files else output_path
        else:
            # Single CSV file
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Date",
                    "Description",
                    "Amount",
                    "Transaction Type",
                    "Confidence",
                    "Page Number",
                    "Line Number",
                    "Item ID",
                ])
                
                for item in sorted(self.income_items, key=lambda x: x.date):
                    writer.writerow([
                        item.date,
                        item.description,
                        f"{item.amount:.2f}",
                        item.transaction_type,
                        f"{item.confidence:.3f}",
                        item.page_number,
                        item.line_number,
                        item.item_id,
                    ])
            
            return output_path
    
    def save_q_table(self, path: Path) -> None:
        """Save Q-table to JSON for future use."""
        with open(path, 'w') as f:
            json.dump(
                {k: dict(v) for k, v in self.q_agent.q_table.items()},
                f,
                indent=2,
            )
    
    def load_q_table(self, path: Path) -> None:
        """Load Q-table from JSON."""
        if path.exists():
            with open(path) as f:
                self.q_agent.q_table = defaultdict(
                    lambda: defaultdict(float),
                    {k: defaultdict(float, v) for k, v in json.load(f).items()},
                )


def main():
    """Main entry point for processing bank statements."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python bank_statement_reader.py <pdf_path> [output_dir]")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("income_extraction")
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create reader
    config = QLearningConfig()
    reader = BankStatementReader(config)
    
    print(f"Processing bank statement: {pdf_path}")
    print(f"Ghost hunt uses available: {config.ghost_hunt_uses}")
    
    # Process PDF
    income_items = reader.process_pdf(pdf_path)
    
    print(f"\nExtracted {len(income_items)} income items")
    print(f"Ghost hunt uses remaining: {reader.q_agent.ghost_hunt_uses_remaining}")
    
    # Export to CSV
    csv_path = output_dir / f"income_{pdf_path.stem}.csv"
    created_csv = reader.export_to_csv(csv_path, group_by_month=True)
    
    print(f"\nExported income items to: {created_csv}")
    
    # Save Q-table for future use
    q_table_path = output_dir / "q_table.json"
    reader.save_q_table(q_table_path)
    print(f"Saved Q-table to: {q_table_path}")
    
    # Print summary
    total_amount = sum(item.amount for item in income_items)
    avg_confidence = np.mean([item.confidence for item in income_items])
    
    print(f"\nSummary:")
    print(f"  Total income items: {len(income_items)}")
    print(f"  Total amount: ${total_amount:,.2f}")
    print(f"  Average confidence: {avg_confidence:.3f}")
    print(f"  Ghost hunt uses remaining: {reader.q_agent.ghost_hunt_uses_remaining}")


if __name__ == "__main__":
    main()
