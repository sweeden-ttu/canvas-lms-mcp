import pypdf

pdf_path = "/Volumes/USB_Storage/Shared/cloud_fronts_group/sept_20225.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    # Search for "Crowne Plaza"
    found = False
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if "Crowne Plaza" in text:
            print(f"--- Page {i+1} ---")
            print(text)
            found = True
            break
    if not found:
        print("Crowne Plaza not found")
except Exception as e:
    print(f"Error: {e}")
