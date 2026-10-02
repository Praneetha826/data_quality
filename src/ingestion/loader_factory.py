"""
Loader Factory Module
Provides automatic loader selection based on file extension
"""

from pathlib import Path
from typing import Optional
from .base_loader import BaseLoader, DataAsset
from .csv_loader import CSVLoader
from .excel_loader import ExcelLoader
from .json_loader import JSONLoader
from .xml_loader import XMLLoader
from .txt_loader import TXTLoader
from .pdf_loader import PDFLoader


class LoaderFactory:
    """
    Factory class for creating appropriate loaders based on file extension
    """

    # Mapping of file extensions to loader classes
    LOADERS = {
        '.csv': CSVLoader,
        '.xlsx': ExcelLoader,
        '.xls': ExcelLoader,
        '.json': JSONLoader,
        '.xml': XMLLoader,
        '.txt': TXTLoader,
        '.pdf': PDFLoader
    }

    @classmethod
    def get_loader(cls, file_path: str) -> BaseLoader:
        """
        Get the appropriate loader for a file based on its extension

        Args:
            file_path: Path to the file

        Returns:
            Instance of the appropriate loader

        Raises:
            ValueError: If file format is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in cls.LOADERS:
            supported_formats = ', '.join(cls.LOADERS.keys())
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {supported_formats}"
            )

        loader_class = cls.LOADERS[extension]
        return loader_class()

    @classmethod
    def load_file(cls, file_path: str, **kwargs) -> DataAsset:
        """
        Load a file using the appropriate loader

        Args:
            file_path: Path to the file
            **kwargs: Additional arguments to pass to the loader

        Returns:
            DataAsset containing the loaded data

        Raises:
            ValueError: If file format is not supported
            FileNotFoundError: If file doesn't exist
        """
        loader = cls.get_loader(file_path)
        return loader.load(file_path, **kwargs)

    @classmethod
    def get_supported_formats(cls) -> list:
        """
        Get list of supported file formats

        Returns:
            List of supported file extensions
        """
        return list(cls.LOADERS.keys())

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """
        Check if a file format is supported

        Args:
            file_path: Path to the file

        Returns:
            True if format is supported, False otherwise
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        return extension in cls.LOADERS

    @classmethod
    def get_format_category(cls, file_path: str) -> Optional[str]:
        """
        Get the data category for a file format

        Args:
            file_path: Path to the file

        Returns:
            Category string ('structured', 'semi-structured', 'unstructured') or None
        """
        loader = cls.get_loader(file_path)

        # Create a temporary asset to get the category
        # This is a bit inefficient but ensures consistency
        try:
            asset = loader.load(file_path)
            return asset.data_category
        except Exception:
            # If loading fails, infer from loader type
            if isinstance(loader, (CSVLoader, ExcelLoader)):
                return 'structured'
            elif isinstance(loader, (JSONLoader, XMLLoader)):
                return 'semi-structured'
            elif isinstance(loader, (TXTLoader, PDFLoader)):
                return 'unstructured'
            return None
