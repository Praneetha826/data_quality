"""
Base Loader Module
Defines the abstract base class and common data representation for all loaders
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path
import pandas as pd


@dataclass
class DataAsset:
    """
    Common data representation for all formats
    Supports both tabular and text/document data
    """
    source_file: str
    source_format: str
    data_category: str  # 'structured', 'semi-structured', 'unstructured'
    metadata: Dict[str, Any] = field(default_factory=dict)
    tabular_data: Optional[pd.DataFrame] = None
    text_data: Optional[str] = None
    quality_info: Dict[str, Any] = field(default_factory=dict)
    extraction_errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def is_tabular(self) -> bool:
        """Check if this asset contains tabular data"""
        return self.tabular_data is not None

    def is_text(self) -> bool:
        """Check if this asset contains text data"""
        return self.text_data is not None

    def get_summary(self) -> str:
        """Get a human-readable summary of the data asset"""
        summary = []
        summary.append(f"Source: {self.source_file}")
        summary.append(f"Format: {self.source_format}")
        summary.append(f"Category: {self.data_category}")

        if self.is_tabular():
            summary.append(f"Tabular Data: {len(self.tabular_data)} rows, {len(self.tabular_data.columns)} columns")
        if self.is_text():
            summary.append(f"Text Data: {len(self.text_data)} characters")

        if self.extraction_errors:
            summary.append(f"Errors: {len(self.extraction_errors)}")
        if self.warnings:
            summary.append(f"Warnings: {len(self.warnings)}")

        return "\n".join(summary)


class BaseLoader(ABC):
    """
    Abstract base class for all data loaders
    Defines the common interface that all format-specific loaders must implement
    """

    def __init__(self):
        self.supported_extensions = []

    @abstractmethod
    def load(self, file_path: str) -> DataAsset:
        """
        Load a file and return a DataAsset

        Args:
            file_path: Path to the file to load

        Returns:
            DataAsset containing the loaded data

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid or corrupted
        """
        pass

    @abstractmethod
    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file can be loaded by this loader

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid, False otherwise
        """
        pass

    def _check_file_exists(self, file_path: str) -> None:
        """Check if file exists, raise exception if not"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic file information"""
        path = Path(file_path)
        return {
            'file_name': path.name,
            'file_size': path.stat().st_size,
            'file_extension': path.suffix.lower()
        }

    def _create_base_asset(self, file_path: str, format_name: str, category: str) -> DataAsset:
        """Create a base DataAsset with common metadata"""
        file_info = self._get_file_info(file_path)

        return DataAsset(
            source_file=file_path,
            source_format=format_name,
            data_category=category,
            metadata={
                'file_name': file_info['file_name'],
                'file_size': file_info['file_size'],
                'file_extension': file_info['file_extension']
            }
        )
