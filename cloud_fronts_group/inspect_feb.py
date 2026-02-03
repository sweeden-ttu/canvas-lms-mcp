import pypdf
import os

pdf_path = "/Volumes/USB_Storage/Shared/cloud_fronts_group/feb_2025.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    print(reader.pages[0].extract_text())
except Exception as e:
    print(f"Error reading PDF: {e}")
