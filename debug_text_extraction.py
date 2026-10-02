"""
Debug text extraction to check actual content
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import LoaderFactory, DataNormalizer

files = [
    'data/sample/test_txt_problematic.txt',
    'data/sample/test_pdf_problematic.pdf',
    'data/sample/test_pdf_clean.pdf'
]

for filepath in files:
    print(f"\n{'='*60}")
    print(f"File: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    try:
        asset = LoaderFactory.load_file(filepath)
        normalized = DataNormalizer.normalize(asset)
        
        if normalized.is_text():
            text = normalized.text_data
            print(f"Text length: {len(text)} characters")
            print(f"Word count: {len(text.split())}")
            print(f"Line count: {len(text.split(chr(10)))}")
            print(f"First 200 chars: {text[:200]}")
        else:
            print("Not text data")
    except Exception as e:
        print(f"ERROR: {str(e)}")
