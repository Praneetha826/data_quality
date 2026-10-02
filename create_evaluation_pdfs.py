"""
Create PDF evaluation documents
"""

import fitz  # PyMuPDF


def create_pdf(filename, text):
    """Create a simple PDF with the given text"""
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), text, fontsize=12)
    doc.save(filename)
    doc.close()


# Create clean document PDF
clean_text = """This is a clean document with proper formatting and consistent structure.

The document contains well-structured paragraphs with clear separation between ideas. There are no encoding issues, no excessive repetition, and no problematic characters.

The content is organized logically with proper punctuation and grammar. Each paragraph serves a distinct purpose and contributes to the overall coherence of the document.

This document demonstrates good text quality with:
- Proper encoding (UTF-8)
- No control characters
- Appropriate length
- Clear structure
- Good readability

No quality issues are present in this document."""

create_pdf("evaluation/unstructured/clean_document.pdf", clean_text)

# Create poor quality document PDF
poor_text = """This is a poor quality document with multiple issues.

It has encoding problems like this:  

This has excessive repetition repetition repetition repetition repetition repetition repetition repetition repetition.

This has many special characters: @#$%^&*()_+-=[]{}|;':",./<>?

This has control characters and unusual formatting.

This paragraph is very short.

This paragraph is also very short.

The document lacks proper structure and organization."""

create_pdf("evaluation/unstructured/poor_quality_document.pdf", poor_text)

print("PDF documents created successfully")
