"""
TXT Loader Module
Handles loading and validation of text files
"""

from pathlib import Path
from typing import Optional, Dict, Any
from .base_loader import BaseLoader, DataAsset


class TXTLoader(BaseLoader):
    """Loader for text files"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.txt']

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid text file

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid text, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to read the file to validate it's readable as text
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return True

        except Exception:
            return False

    def load(self, file_path: str, encoding: str = 'utf-8') -> DataAsset:
        """
        Load a text file and return a DataAsset

        Args:
            file_path: Path to the text file
            encoding: File encoding (default: utf-8)

        Returns:
            DataAsset containing the loaded text data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file cannot be read as text
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be a text file (.txt). Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'TXT', 'unstructured')
        asset.metadata['encoding'] = encoding

        try:
            # Try to read with specified encoding
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
            except UnicodeDecodeError:
                # Fallback to common encodings
                encodings_to_try = ['latin-1', 'cp1252', 'iso-8859-1']
                text = None
                for enc in encodings_to_try:
                    try:
                        with open(file_path, 'r', encoding=enc) as f:
                            text = f.read()
                        asset.metadata['encoding'] = enc
                        asset.warnings.append(f"Used fallback encoding: {enc}")
                        break
                    except UnicodeDecodeError:
                        continue

                if text is None:
                    raise ValueError(f"Could not decode file with any common encoding")

            # Check if file is empty
            if not text.strip():
                asset.warnings.append("File is empty or contains only whitespace")

            # Set text data
            asset.text_data = text

            # Add text-specific metadata
            lines = text.split('\n')
            words = text.split()

            asset.metadata.update({
                'character_count': len(text),
                'line_count': len(lines),
                'word_count': len(words),
                'non_empty_lines': len([line for line in lines if line.strip()]),
                'average_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
            })

            # Add quality info
            asset.quality_info = {
                'is_empty': len(text.strip()) == 0,
                'has_content': len(text.strip()) > 0,
                'readability_score': self._calculate_readability_score(text)
            }

        except Exception as e:
            asset.extraction_errors.append(f"Text loading error: {str(e)}")
            raise ValueError(f"Error loading text file: {str(e)}")

        return asset

    def _calculate_readability_score(self, text: str) -> float:
        """
        Calculate a simple readability score

        Args:
            text: Text content

        Returns:
            Readability score (0-1, higher is more readable)
        """
        if not text.strip():
            return 0.0

        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        if not sentences:
            return 0.5  # Neutral score if no sentences

        avg_words_per_sentence = len(words) / len(sentences)

        # Simple scoring: prefer 10-20 words per sentence
        if 10 <= avg_words_per_sentence <= 20:
            return 1.0
        elif avg_words_per_sentence < 10:
            return 0.7  # Short sentences
        else:
            return max(0.3, 1.0 - (avg_words_per_sentence - 20) / 30)  # Long sentences
