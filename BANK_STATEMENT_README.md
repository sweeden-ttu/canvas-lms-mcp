# Bayesian Bank Statement Reader

A probabilistic income extraction system for bank statements that uses Bayesian reasoning and Q-learning to optimize extraction accuracy.

## Features

- **Bayesian Classification**: Uses probabilistic reasoning to classify transactions as income based on patterns, keywords, and amount characteristics
- **Q-Learning Optimization**: Learns optimal extraction strategies to minimize missed income items
- **Ghost Hunting Mode**: 4 special opportunities to carefully analyze large deposits (>$10,000)
- **CSV Export**: Exports income items organized by month/year for easy CPA review
- **Probabilistic Confidence**: Each income item includes a confidence score (0-1) based on Bayesian posterior probability

## Architecture

### Pacman Analogy
- **You (Pacman)**: The income extraction agent that "eats" (extracts) income lines
- **Ghosts**: Other models that find income you missed (competitors)
- **Ghost Hunting**: Special mode (4 uses) for analyzing large deposits carefully
- **Q-Learning**: Strategy to avoid ghosts (missed income) and optimize extraction

### Components

1. **BayesianIncomeClassifier**: Probabilistic classifier using Bayes' theorem
   - Updates beliefs based on transaction patterns
   - Considers keywords, amounts, and transaction types
   - Provides confidence scores for each classification

2. **QLearningIncomeExtractor**: Q-learning agent for optimization
   - States: (page_number, items_found_count, confidence_level)
   - Actions: extract_normal, extract_careful, ghost_hunt
   - Rewards: +10 per item found, -20 per missed item, -5 for unnecessary ghost hunt

3. **BankStatementReader**: Main orchestrator
   - Processes PDFs using pdfplumber
   - Coordinates classification and Q-learning
   - Exports results to CSV

## Installation

```bash
# Install dependencies (using uv as preferred)
uv pip install pdfplumber numpy pydantic

# Or using pip
pip install pdfplumber numpy pydantic
```

## Usage

### Basic Usage

```bash
python process_bank_statement.py jan_2025.pdf
```

### With Custom Output Directory

```bash
python process_bank_statement.py jan_2025.pdf income_extraction/
```

### Programmatic Usage

```python
from pathlib import Path
from bank_statement_reader import BankStatementReader, QLearningConfig

# Create reader
config = QLearningConfig(
    ghost_hunt_uses=4,
    large_deposit_threshold=10000.0,
)
reader = BankStatementReader(config)

# Process PDF
pdf_path = Path("jan_2025.pdf")
income_items = reader.process_pdf(pdf_path)

# Export to CSV
csv_path = reader.export_to_csv(Path("income_jan_2025.csv"), group_by_month=True)
```

## Output Format

The system generates CSV files with the following columns:

- **Date**: Transaction date (MM/DD/YYYY)
- **Description**: Transaction description
- **Amount**: Transaction amount
- **Transaction Type**: credit, deposit, transfer_in, etc.
- **Confidence**: Bayesian confidence score (0-1)
- **Page Number**: Page where transaction was found
- **Line Number**: Line number on the page
- **Item ID**: Unique identifier for the item

### Monthly Organization

When `group_by_month=True`, separate CSV files are created for each month/year:
- `income_jan_2025_2025_01.csv`
- `income_jan_2025_2025_02.csv`
- etc.

## Bayesian Reasoning

The classifier uses Bayes' theorem to update beliefs:

```
P(income | evidence) = P(evidence | income) * P(income) / P(evidence)
```

### Income Indicators (High Prior)
- Keywords: "deposit", "credit", "salary", "wage", "commission"
- Transaction types: credit, deposit, transfer_in
- Regular amounts (multiples of 100, 1000)

### Expense Indicators (Low Prior)
- Keywords: "debit", "withdrawal", "purchase", "fee", "charge"
- Transaction types: debit, withdrawal, transfer_out

## Q-Learning Strategy

The Q-learning agent learns optimal extraction strategies:

- **States**: Encoded as (page_number, items_found_count, confidence_level)
- **Actions**: 
  - `extract_normal`: Standard extraction
  - `extract_careful`: More careful extraction
  - `ghost_hunt`: Special mode for large deposits (4 uses only)
- **Rewards**:
  - +10: Found income item
  - -20: Missed income item (ghost found it)
  - -5: Unnecessary ghost hunt use

The Q-table is saved to `q_table.json` for future use, allowing the system to learn from previous extractions.

## Ghost Hunting Mode

Ghost hunting is a special extraction mode available 4 times per statement:

- Automatically triggered for large deposits (>$10,000 threshold)
- Uses refined Bayesian classification with higher confidence
- Helps catch income that might be missed in normal extraction
- Should be used strategically to maximize coverage

## Tax Context

This system is designed for tax preparation (Form 1065, Partnership tax):

- **Probabilistic Nature**: Tax rules allow probabilistic reasoning
- **CPA Review**: Final results reviewed by tax accountant
- **Accuracy Competition**: Results compared against 3 other models
- **Audit Avoidance**: Q-learning helps avoid missed income that could trigger audits

## Configuration

### QLearningConfig Parameters

- `learning_rate` (default: 0.1): Q-learning learning rate
- `discount_factor` (default: 0.9): Future reward discount
- `epsilon` (default: 0.15): Exploration rate (15% random actions)
- `large_deposit_threshold` (default: 10000.0): Threshold for ghost hunting
- `ghost_hunt_uses` (default: 4): Number of ghost hunting opportunities

## Example Output

```
======================================================================
Bayesian Bank Statement Reader - Income Extraction System
======================================================================

Processing: jan_2025.pdf
Ghost hunt uses available: 4
Large deposit threshold: $10,000.00

Extracting income items using:
  - Bayesian probabilistic classification
  - Q-learning optimization
  - Ghost hunting mode for large deposits
----------------------------------------------------------------------

✓ Extraction complete!
  Items found: 47
  Ghost hunt uses remaining: 2

✓ Exported 1 CSV file(s) by month/year:
    - income_extraction/income_jan_2025_2025_01.csv
✓ Saved Q-table to: income_extraction/q_table.json

======================================================================
EXTRACTION SUMMARY
======================================================================
  Total income items: 47
  Total amount: $125,430.50
  Average confidence: 0.782
  Confidence range: 0.521 - 0.945
  Ghost hunt uses remaining: 2

----------------------------------------------------------------------
TOP 10 INCOME ITEMS BY AMOUNT
----------------------------------------------------------------------
   1. $   15,000.00 | 01/15/2025 | ACH CREDIT - PAYROLL
   2. $   12,500.00 | 01/01/2025 | DEPOSIT - CLIENT PAYMENT
   3. $   10,250.00 | 01/20/2025 | WIRE TRANSFER IN
   ...
```

## Troubleshooting

### No Income Items Found

If no income items are found:
1. Check PDF format - the parser expects standard bank statement formats
2. Verify transaction patterns match expected formats
3. Consider adjusting keyword lists in `BayesianIncomeClassifier`
4. Check if PDF needs OCR (scanned documents)

### Low Confidence Scores

Low confidence scores indicate uncertain classifications:
- Review transaction descriptions
- Adjust Bayesian priors in classifier
- Consider manual review for low-confidence items

### Q-Learning Not Learning

If Q-learning doesn't seem to improve:
- Check that rewards are being calculated correctly
- Verify state encoding captures relevant information
- Review epsilon value (too high = too much exploration)

## Future Enhancements

- Support for multiple bank statement formats
- OCR integration for scanned statements
- Integration with tax software APIs
- Multi-model comparison and consensus
- Adaptive threshold tuning based on historical accuracy

## License

MIT License - See LICENSE file for details
