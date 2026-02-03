import pypdf
import pandas as pd
import re
import os
import glob

# Configuration
SOURCE_DIR = "/Volumes/USB_Storage/Shared/cloud_fronts_group"
OUTPUT_DIR = "/Volumes/USB_Storage/Shared/cloud_fronts_group/pacman_probabilistic"
GHOST_LIVES = 6
GHOST_HUNTER_CHARGES = 4

# Patterns
# Filename pattern to identify month and year
FILENAME_PATTERN = re.compile(r"([a-z]+)_(\d{4,5})\.pdf", re.IGNORECASE)

# Line pattern: Date Description Details Fee Amount
# Amount must start with +
# Example: Jan 3 From Tracy Myers Cash App payment $0.00 + $8.00
# Example: Jan 9 DoorDash, Inc. San Francisco CA Cash App Card $0.00 + $42.81
# We look for lines ending in: $X.XX + $Y.YY or similar.
# Actually the "Fee" column is usually $0.00.
# The Amount column has + for income.

def parse_pdf(file_path):
    print(f"Processing {file_path}...")
    income_lines = []
    
    try:
        reader = pypdf.PdfReader(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # We are looking for lines that end with an amount starting with +
            # format: ... $0.00 + $8.00
            # Regex to find amount at end
            # It seems there is a Fee column before Amount.
            
            # Look for " + $" or "+$" near the end
            if "+ $" in line or "+$" in line:
                # It is likely income.
                # Let's try to extract the components.
                
                # Simple extraction: Split by spaces, but description can have spaces.
                # We know the last two items are likely Fee and Amount (if Fee exists).
                # Wait, "Fee Amount" header suggests Fee is separate.
                # " $0.00 + $8.00" -> Fee: $0.00, Amount: + $8.00
                
                parts = line.split()
                if len(parts) < 4:
                    continue
                
                # Check if the last part or second to last starts with +
                # Case 1: "+ $8.00" -> parts[-2] is "+", parts[-1] is "$8.00"
                # Case 2: "+$8.00" -> parts[-1] is "+$8.00"
                
                amount_str = ""
                fee_str = ""
                remainder = []
                
                if parts[-2] == "+" and parts[-1].startswith("$"):
                    amount_str = parts[-2] + parts[-1] # "+$8.00"
                    if parts[-3].startswith("$"):
                        fee_str = parts[-3]
                        remainder = parts[:-3]
                    else:
                        # Maybe no fee?
                        remainder = parts[:-2]
                elif parts[-1].startswith("+$"):
                    amount_str = parts[-1]
                    if parts[-2].startswith("$"):
                        fee_str = parts[-2]
                        remainder = parts[:-2]
                    else:
                        remainder = parts[:-1]
                else:
                    # Not a clear income line format we expected
                    continue
                
                # Parse Date: First 2 tokens usually "Jan 3"
                if len(remainder) >= 2:
                    date_str = remainder[0] + " " + remainder[1]
                    description_details = " ".join(remainder[2:])
                else:
                    date_str = "Unknown"
                    description_details = " ".join(remainder)
                
                # Parse numeric amount
                try:
                    clean_amount = amount_str.replace('+', '').replace('$', '').replace(',', '')
                    amount_val = float(clean_amount)
                except:
                    amount_val = 0.0
                
                income_lines.append({
                    "Date": date_str,
                    "Description": description_details,
                    "Amount": amount_val,
                    "Original_Amount_Str": amount_str,
                    "Source_File": os.path.basename(file_path)
                })
                
    return income_lines

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    pdf_files = glob.glob(os.path.join(SOURCE_DIR, "*_202*.pdf")) # Matches 2025, 20225
    
    # Sort files to process in order (Jan to Dec) if possible
    # We can rely on filename parsing for sorting
    
    files_to_process = []
    months = {
        "jan": 1, "feb": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "aug": 8, "sept": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    for f in pdf_files:
        name = os.path.basename(f)
        match = FILENAME_PATTERN.search(name)
        if match:
            month_str = match.group(1).lower()
            year_str = match.group(2)
            if month_str in months:
                files_to_process.append((months[month_str], year_str, f))
    
    files_to_process.sort() # Sorts by month index
    
    ghost_hunter_charges = GHOST_HUNTER_CHARGES
    
    for month_idx, year, file_path in files_to_process:
        print(f"Analyzing {os.path.basename(file_path)}...")
        income_data = parse_pdf(file_path)
        
        if not income_data:
            print(f"No income found in {file_path}")
            continue
            
        df = pd.DataFrame(income_data)
        
        # Ghost Hunter Logic
        # Identify "Large Deposits"
        # Let's say large is > $500 for this context? Or maybe relative?
        # Let's sort by amount desc
        df_sorted = df.sort_values(by="Amount", ascending=False)
        
        # Mark suspicious/large items
        # Note: In a real scenario, we'd use more complex logic.
        # Here we just output all of them as requested.
        
        month_name = [k for k, v in months.items() if v == month_idx][0]
        output_csv = os.path.join(OUTPUT_DIR, f"income_{month_name}_{year}.csv")
        
        df.to_csv(output_csv, index=False)
        print(f"Saved {len(df)} lines to {output_csv}")

if __name__ == "__main__":
    main()
