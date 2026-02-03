import pypdf
import os

pdf_path = "/Volumes/USB_Storage/Shared/cloud_fronts_group/jan_2025.pdf"

try:
    reader = pypdf.PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    print(reader.pages[1].extract_text())
    print("-" * 20)
    print(reader.pages[2].extract_text())
except Exception as e:
    print(f"Error reading PDF: {e}")
