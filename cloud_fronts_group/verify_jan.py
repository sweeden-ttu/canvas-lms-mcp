import pandas as pd

try:
    df = pd.read_csv("/Volumes/USB_Storage/Shared/cloud_fronts_group/pacman_probabilistic/income_jan_2025.csv")
    # Filter out the "Money In" summary line
    transactions = df[df['Date'] != 'Money In']
    summary_line = df[df['Date'] == 'Money In']
    
    total_transactions = transactions['Amount'].sum()
    summary_total = summary_line['Amount'].sum() if not summary_line.empty else 0
    
    print(f"Total Transactions Sum: {total_transactions:.2f}")
    print(f"Summary Line Total: {summary_total:.2f}")
    print(f"Difference: {summary_total - total_transactions:.2f}")
    
except Exception as e:
    print(f"Error: {e}")
