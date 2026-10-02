"""
Verify all enterprise dataset files can be read
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from pathlib import Path

print("="*60)
print("ENTERPRISE DATASET FILE VERIFICATION")
print("="*60)

files = {
    "customers.csv": "CSV",
    "sales.xlsx": "Excel",
    "employee_records.json": "JSON",
    "application_logs.xml": "XML",
    "company_policy.txt": "TXT",
    "annual_report.pdf": "PDF"
}

dataset_dir = Path("enterprise_data_lake_sample")

for filename, file_type in files.items():
    filepath = dataset_dir / filename
    print(f"\n{filename} ({file_type})")
    print("-" * 60)
    
    try:
        if file_type == "CSV":
            df = pd.read_csv(filepath)
            print(f"[OK] Successfully read CSV")
            print(f"   Records: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            print(f"   Columns: {', '.join(df.columns.tolist())}")

        elif file_type == "Excel":
            df = pd.read_excel(filepath)
            print(f"[OK] Successfully read Excel")
            print(f"   Records: {len(df)}")
            print(f"   Columns: {len(df.columns)}")
            print(f"   Columns: {', '.join(df.columns.tolist())}")

        elif file_type == "JSON":
            with open(filepath, 'r') as f:
                data = json.load(f)
            print(f"[OK] Successfully read JSON")
            print(f"   Records: {len(data)}")
            if data:
                print(f"   Fields: {', '.join(data[0].keys())}")

        elif file_type == "XML":
            tree = ET.parse(filepath)
            root = tree.getroot()
            logs = root.findall('.//Log')
            print(f"[OK] Successfully read XML")
            print(f"   Root element: {root.tag}")
            print(f"   Log records: {len(logs)}")
            if logs:
                fields = [child.tag for child in logs[0]]
                print(f"   Fields: {', '.join(fields)}")

        elif file_type == "TXT":
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"[OK] Successfully read TXT")
            print(f"   Characters: {len(text)}")
            print(f"   Words: {len(text.split())}")
            print(f"   Lines: {len(text.split(chr(10)))}")
            print(f"   First 100 chars: {text[:100]}...")

        elif file_type == "PDF":
            try:
                import pymupdf as fitz
                doc = fitz.open(filepath)
                print(f"[OK] Successfully read PDF")
                print(f"   Pages: {doc.page_count}")
                # Extract text from first page
                page = doc[0]
                text = page.get_text()
                print(f"   First page chars: {len(text)}")
                print(f"   First 100 chars: {text[:100]}...")
                doc.close()
            except ImportError:
                print(f"[WARN] PyMuPDF not available, cannot verify PDF content")
                print(f"   File exists: {filepath.exists()}")
                print(f"   File size: {filepath.stat().st_size} bytes")

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("VERIFICATION COMPLETE")
print("="*60)
