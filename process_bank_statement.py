#!/usr/bin/env python3
"""
Script to process bank statement PDFs and extract income items.

Usage:
    python process_bank_statement.py <pdf_path> [output_dir]
"""

import sys
from pathlib import Path
from bank_statement_reader import BankStatementReader, QLearningConfig


def main():
    """Process bank statement PDF."""
    if len(sys.argv) < 2:
        print("Usage: python process_bank_statement.py <pdf_path> [output_dir]")
        print("\nExample:")
        print("  python process_bank_statement.py jan_2025.pdf income_extraction/")
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("income_extraction")
    
    if not pdf_path.exists():
        print(f"Error: PDF file not found: {pdf_path}")
        print(f"\nPlease provide the path to your bank statement PDF.")
        print(f"Looking for: {pdf_path.absolute()}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create reader with Q-learning configuration
    config = QLearningConfig(
        learning_rate=0.1,
        discount_factor=0.9,
        epsilon=0.15,
        large_deposit_threshold=10000.0,
        ghost_hunt_uses=4,  # 4 ghost hunting opportunities
    )
    reader = BankStatementReader(config)
    
    print("=" * 70)
    print("Bayesian Bank Statement Reader - Income Extraction System")
    print("=" * 70)
    print(f"\nProcessing: {pdf_path.name}")
    print(f"Ghost hunt uses available: {config.ghost_hunt_uses}")
    print(f"Large deposit threshold: ${config.large_deposit_threshold:,.2f}")
    print("\nExtracting income items using:")
    print("  - Bayesian probabilistic classification")
    print("  - Q-learning optimization")
    print("  - Ghost hunting mode for large deposits")
    print("-" * 70)
    
    try:
        # Process PDF
        income_items = reader.process_pdf(pdf_path)
        
        print(f"\n✓ Extraction complete!")
        print(f"  Items found: {len(income_items)}")
        print(f"  Ghost hunt uses remaining: {reader.q_agent.ghost_hunt_uses_remaining}")
        
        if not income_items:
            print("\n⚠ Warning: No income items found in the statement.")
            print("  This could mean:")
            print("    - The statement format is different than expected")
            print("    - All transactions are expenses")
            print("    - The PDF needs OCR or different parsing")
            return
        
        # Export to CSV
        csv_path = output_dir / f"income_{pdf_path.stem}.csv"
        created_csvs = reader.export_to_csv(csv_path, group_by_month=True)
        
        # Handle both single file and multiple files
        if isinstance(created_csvs, list):
            print(f"\n✓ Exported {len(created_csvs)} CSV file(s) by month/year:")
            for csv_file in created_csvs:
                print(f"    - {csv_file}")
        else:
            print(f"\n✓ Exported income items to: {created_csvs}")
        
        # Save Q-table for future use
        q_table_path = output_dir / "q_table.json"
        reader.save_q_table(q_table_path)
        print(f"✓ Saved Q-table to: {q_table_path}")
        
        # Print summary statistics
        total_amount = sum(item.amount for item in income_items)
        avg_confidence = sum(item.confidence for item in income_items) / len(income_items)
        min_confidence = min(item.confidence for item in income_items)
        max_confidence = max(item.confidence for item in income_items)
        
        print("\n" + "=" * 70)
        print("EXTRACTION SUMMARY")
        print("=" * 70)
        print(f"  Total income items: {len(income_items)}")
        print(f"  Total amount: ${total_amount:,.2f}")
        print(f"  Average confidence: {avg_confidence:.3f}")
        print(f"  Confidence range: {min_confidence:.3f} - {max_confidence:.3f}")
        print(f"  Ghost hunt uses remaining: {reader.q_agent.ghost_hunt_uses_remaining}")
        
        # Show extraction actions taken
        print("\n" + "-" * 70)
        print("EXTRACTION ACTIONS")
        print("-" * 70)
        ghost_hunts_used = sum(1 for h in reader.extraction_history if h.get("ghost_hunt_used"))
        normal_extractions = len(reader.extraction_history) - ghost_hunts_used
        
        print(f"  Normal extractions: {normal_extractions}")
        print(f"  Ghost hunts used: {ghost_hunts_used}")
        
        # Show top income items by amount
        print("\n" + "-" * 70)
        print("TOP 10 INCOME ITEMS BY AMOUNT")
        print("-" * 70)
        top_items = sorted(income_items, key=lambda x: x.amount, reverse=True)[:10]
        for i, item in enumerate(top_items, 1):
            print(f"  {i:2d}. ${item.amount:>12,.2f} | {item.date} | {item.description[:50]}")
        
        print("\n" + "=" * 70)
        print("Processing complete! CSV files are ready for CPA review.")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error processing PDF: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
