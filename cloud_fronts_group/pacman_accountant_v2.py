import pypdf
import pandas as pd
import re
import os
import glob

# Configuration
SOURCE_DIR = "/Volumes/USB_Storage/Shared/cloud_fronts_group"
OUTPUT_DIR = "/Volumes/USB_Storage/Shared/cloud_fronts_group/pacman_probabilistic"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

FILENAME_PATTERN = re.compile(r"([a-z]+)_(\d{4,5})\.pdf", re.IGNORECASE)

def parse_amount(amount_str):
    try:
        clean_amount = amount_str.replace('+', '').replace('-', '').replace('$', '').replace(',', '')
        return float(clean_amount)
    except:
        return 0.0

def parse_pdf(file_path):
    print(f"Processing {file_path}...")
    income_lines = []
    expense_lines = []
    
    summary_money_in = 0.0
    summary_money_out = 0.0
    
    try:
        reader = pypdf.PdfReader(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return [], [], 0.0, 0.0

    # Parse Summary from Page 1
    page1_text = reader.pages[0].extract_text()
    if page1_text:
        # Look for "Money In + $X,XXX.XX"
        # Look for "Money Out - $X,XXX.XX"
        # Regex for summary
        in_match = re.search(r"Money In \+ \$([\d,]+\.\d{2})", page1_text)
        out_match = re.search(r"Money Out - \$([\d,]+\.\d{2})", page1_text)
        
        if in_match:
            summary_money_in = parse_amount(in_match.group(1))
        if out_match:
            summary_money_out = parse_amount(out_match.group(1))

    # Parse Transactions
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            # Regex for transaction line:
            # Starts with Date (Jan 1)
            # Ends with Amount ($X.XX or + $X.XX)
            # Optional Fee column before Amount ($0.00)
            
            # Heuristic: Line must contain a date-like start and a dollar amount at end
            if not re.match(r"^[A-Z][a-z]{2} \d{1,2} ", line):
                continue
            
            # Split by spaces
            parts = line.split()
            if len(parts) < 4:
                continue
                
            # Check last part for amount
            last_part = parts[-1]
            second_last = parts[-2]
            
            is_income = False
            amount_str = ""
            description_end_idx = -1
            
            # Case 1: Income with "+ $X.XX" (space between + and $)
            if second_last == "+" and last_part.startswith("$"):
                is_income = True
                amount_str = second_last + last_part
                # Fee is likely at parts[-3]
                description_end_idx = -3
                
            # Case 2: Income with "+$X.XX" (no space)
            elif last_part.startswith("+$"):
                is_income = True
                amount_str = last_part
                # Fee is likely at parts[-2]
                description_end_idx = -2
                
            # Case 3: Expense with "$X.XX" (no plus)
            elif last_part.startswith("$") and not last_part.startswith("+$"):
                is_income = False
                amount_str = last_part
                # Fee is likely at parts[-2]
                description_end_idx = -2
            
            else:
                continue
                
            amount_val = parse_amount(amount_str)
            
            # Extract Date and Description
            date_str = parts[0] + " " + parts[1]
            
            # Description is everything between Date and Fee/Amount
            # parts[2] to description_end_idx
            if description_end_idx < 0:
                desc_parts = parts[2:description_end_idx]
            else:
                # Should not happen based on logic above
                desc_parts = parts[2:]
            
            description = " ".join(desc_parts)
            
            # Identify "Fee" if present
            # If description_end_idx is -2, Fee is -2? No, Fee is BEFORE amount.
            # In Case 3 (Expense): parts = [Date, Date, Desc..., Fee, Amount] -> Fee is parts[-2]
            # Verify Fee starts with $
            if parts[description_end_idx].startswith("$"):
                # It's a fee column, remove it from description if we accidentally included it?
                # Actually, slice above excludes it.
                pass
            else:
                # Maybe Description included the fee part? Or Fee is missing?
                # Let's verify.
                pass
                
            item = {
                "Date": date_str,
                "Description": description,
                "Amount": amount_val,
                "Original_Amount_Str": amount_str,
                "Source_File": os.path.basename(file_path)
            }
            
            if is_income:
                income_lines.append(item)
            else:
                expense_lines.append(item)

    return income_lines, expense_lines, summary_money_in, summary_money_out

def main():
    pdf_files = glob.glob(os.path.join(SOURCE_DIR, "*_202*.pdf"))
    
    months = {
        "jan": 1, "feb": 2, "march": 3, "april": 4, "may": 5, "june": 6,
        "july": 7, "aug": 8, "sept": 9, "oct": 10, "nov": 11, "dec": 12
    }
    
    files_to_process = []
    for f in pdf_files:
        name = os.path.basename(f)
        match = FILENAME_PATTERN.search(name)
        if match:
            month_str = match.group(1).lower()
            year_str = match.group(2)
            if month_str in months:
                files_to_process.append((months[month_str], year_str, f))
    
    files_to_process.sort()
    
    for month_idx, year, file_path in files_to_process:
        month_name = [k for k, v in months.items() if v == month_idx][0]
        print(f"--- {month_name} {year} ---")
        
        income, expenses, sum_in, sum_out = parse_pdf(file_path)
        
        # Calculate calculated sums
        calc_in = sum(i['Amount'] for i in income)
        calc_out = sum(e['Amount'] for e in expenses)
        
        print(f"Money In: Summary={sum_in:.2f}, Calculated={calc_in:.2f}, Diff={sum_in - calc_in:.2f}")
        print(f"Money Out: Summary={sum_out:.2f}, Calculated={calc_out:.2f}, Diff={sum_out - calc_out:.2f}")
        
        # Warn if diff
        if abs(sum_in - calc_in) > 0.01:
            print(f"WARNING: Income mismatch in {month_name}!")
        if abs(sum_out - calc_out) > 0.01:
            print(f"WARNING: Expense mismatch in {month_name}!")
            
        # Save CSVs
        if income:
            df_in = pd.DataFrame(income)
            # Add summary row at top
            summary_row = pd.DataFrame([{"Date": "Summary Money In", "Amount": sum_in}])
            df_in = pd.concat([summary_row, df_in], ignore_index=True)
            out_in = os.path.join(OUTPUT_DIR, f"income_{month_name}_{year}.csv")
            df_in.to_csv(out_in, index=False)
            print(f"Saved Income CSV: {out_in}")
            
        if expenses:
            df_out = pd.DataFrame(expenses)
            summary_row = pd.DataFrame([{"Date": "Summary Money Out", "Amount": sum_out}])
            df_out = pd.concat([summary_row, df_out], ignore_index=True)
            out_out = os.path.join(OUTPUT_DIR, f"expenses_{month_name}_{year}.csv")
            df_out.to_csv(out_out, index=False)
            print(f"Saved Expense CSV: {out_out}")

if __name__ == "__main__":
    main()
