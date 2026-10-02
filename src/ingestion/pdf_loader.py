"""
PDF Loader Module
Handles loading and validation of PDF files with text extraction
"""

from pathlib import Path
from typing import Optional, Dict, Any
from .base_loader import BaseLoader, DataAsset

# Try to import PyMuPDF with fallback to legacy fitz
try:
    import pymupdf  # PyMuPDF
    fitz = pymupdf
    PDF_AVAILABLE = True
except ImportError:
    try:
        import fitz  # Legacy PyMuPDF import
        PDF_AVAILABLE = True
    except ImportError:
        PDF_AVAILABLE = False


class PDFLoader(BaseLoader):
    """Loader for PDF files"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.pdf']

        if not PDF_AVAILABLE:
            raise ImportError(
                "PyMuPDF is required for PDF loading. "
                "Install it with: pip install PyMuPDF"
            )

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid PDF file

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid PDF, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to open the file to validate it's actually a PDF
            doc = fitz.open(file_path)
            doc.close()
            return True

        except Exception:
            return False

    def load(self, file_path: str) -> DataAsset:
        """
        Load a PDF file and return a DataAsset

        Args:
            file_path: Path to the PDF file

        Returns:
            DataAsset containing the loaded PDF data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid PDF
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be a PDF file. Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'PDF', 'unstructured')

        try:
            # Open PDF document
            doc = fitz.open(file_path)

            # Store page count before closing
            page_count = doc.page_count
            is_encrypted = doc.is_encrypted

            # Extract metadata
            pdf_metadata = {
                'page_count': page_count,
                'metadata': doc.metadata,
                'is_encrypted': is_encrypted,
                'is_pdf': True
            }
            asset.metadata.update(pdf_metadata)

            # Extract text from all pages
            extracted_text = []
            total_chars = 0

            for page_num in range(page_count):
                page = doc[page_num]
                page_text = page.get_text()
                extracted_text.append(page_text)
                total_chars += len(page_text)

            doc.close()

            # Combine text from all pages
            full_text = "\n\n".join(extracted_text)
            asset.text_data = full_text

            # Add text-specific metadata
            asset.metadata.update({
                'total_characters': total_chars,
                'characters_per_page': total_chars / page_count if page_count > 0 else 0,
                'pages_with_text': len([t for t in extracted_text if t.strip()]),
                'pages_without_text': len([t for t in extracted_text if not t.strip()])
            })

            # Add quality info
            asset.quality_info = {
                'has_extractable_text': total_chars > 0,
                'text_extraction_success': True,
                'extraction_ratio': total_chars / (page_count * 1000) if page_count > 0 else 0
            }

            # Warnings for PDF quality
            if total_chars == 0:
                asset.warnings.append("No extractable text found in PDF")
            elif asset.metadata['pages_without_text'] > 0:
                asset.warnings.append(
                    f"{asset.metadata['pages_without_text']} pages have no extractable text"
                )

            if is_encrypted:
                asset.warnings.append("PDF is encrypted - some content may not be accessible")

        except Exception as e:
            asset.extraction_errors.append(f"PDF loading error: {str(e)}")
            raise ValueError(f"Error loading PDF file: {str(e)}")

        return asset
