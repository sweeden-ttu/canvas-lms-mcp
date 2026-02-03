import pandas as pd
import os
import glob
import re

# Configuration
INPUT_DIR = "/Volumes/USB_Storage/Shared/cloud_fronts_group/pacman_probabilistic"
OUTPUT_FILE = "/Volumes/USB_Storage/Shared/cloud_fronts_group/pacman_probabilistic/form_1065_income_classification.csv"

def classify_transaction(row):
    desc = str(row['Description']).lower()
    amount = row['Amount']
    
    # Exclude Summary Lines
    if str(row['Date']) == "Money In":
        return "Excluded", "Summary Line"
    
    # Exclude Transfers (Ghost Hunter Logic: Avoid false positives)
    if "from savings transfer" in desc or "transfer from" in desc:
        return "Excluded", "Internal Transfer"

    # Line 1a: Gross Receipts (Business Income)
    # Gig Economy / Payroll / Client Payments
    if any(keyword in desc for keyword in [
        "uber", "doordash", "oasisbatch", "payroll", 
        "cash app payment", "direct deposit", "payment from",
        "stripe", "square", "client", "invoice"
    ]):
        return "Line 1a", "Gross receipts or sales"
        
    # Schedule K: Capital Gains (Crypto)
    if "bitcoin sale" in desc or "sale of btc" in desc:
        return "Schedule K", "Partners' Distributive Share Items (Capital Gains Proceeds)"
        
    # Line 7: Other Income
    if "refund" in desc or "reward" in desc or "interest" in desc:
        return "Line 7", "Other income"
        
    # Fallback: Assume Gross Receipts for unrecognized positive inflows 
    # (Better to report as income than miss it for the ghosts)
    return "Line 1a", "Gross receipts or sales (Uncategorized)"

def main():
    all_files = glob.glob(os.path.join(INPUT_DIR, "income_*.csv"))
    
    combined_data = []
    
    print(f"Found {len(all_files)} files to process.")
    
    for filename in all_files:
        # Skip the summary file if it exists from previous run
        if "form_1065" in filename:
            continue
            
        try:
            df = pd.read_csv(filename)
            for _, row in df.iterrows():
                line_id, line_desc = classify_transaction(row)
                
                # We only want "Income" lines (Amount > 0)
                # The CSVs from previous step were already filtered for Income, 
                # but let's be safe.
                try:
                    amt = float(row['Amount'])
                except:
                    amt = 0
                
                if amt > 0:
                    combined_data.append({
                        "Date": row['Date'],
                        "Description": row['Description'],
                        "Amount": amt,
                        "Source_File": os.path.basename(filename),
                        "Form_1065_Line": line_id,
                        "Line_Description": line_desc
                    })
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Create DataFrame
    final_df = pd.DataFrame(combined_data)
    
    # Filter out Excluded
    report_df = final_df[final_df['Form_1065_Line'] != "Excluded"]
    
    # Sort
    report_df = report_df.sort_values(by=['Form_1065_Line', 'Date'])
    
    # Save
    report_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Successfully classified {len(report_df)} transactions.")
    print(f"Report saved to: {OUTPUT_FILE}")
    
    # Print Summary
    summary = report_df.groupby(['Form_1065_Line', 'Line_Description'])['Amount'].sum()
    print("\n--- Form 1065 Income Summary ---")
    print(summary)

if __name__ == "__main__":
    main()
