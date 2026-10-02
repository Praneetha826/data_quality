# PDF Sample File Instructions

To test the PDF loader functionality, you need to create a sample PDF file.

## Options:

1. **Convert the sample_document.txt to PDF:**
   - Open `sample_document.txt` in any text editor
   - Use "Print to PDF" or "Save as PDF" functionality
   - Save as `sample_document.pdf` in this directory

2. **Use any existing PDF file:**
   - Place any PDF file in this directory
   - Rename it to `sample_document.pdf`

3. **Create a simple PDF with Python:**
   ```python
   from reportlab.lib.pagesizes import letter
   from reportlab.pdfgen import canvas

   def create_sample_pdf():
       c = canvas.Canvas("sample_document.pdf", pagesize=letter)
       c.drawString(100, 750, "Data Quality Assessment Sample PDF")
       c.drawString(100, 730, "This is a sample PDF for testing PDF loader functionality.")
       c.drawString(100, 710, "The PDF loader should extract this text successfully.")
       c.save()

   create_sample_pdf()
   ```

## Note:
The PDF loader requires PyMuPDF (fitz) to be installed. If you encounter import errors, install it with:
```bash
pip install PyMuPDF
```

For testing purposes, the PDF loader includes graceful handling of missing or corrupt PDF files.
