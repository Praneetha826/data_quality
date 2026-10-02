"""
Normalizer Module
Provides common normalization layer for all data formats
"""

from typing import Dict, Any, Optional
import pandas as pd
from .base_loader import DataAsset


class DataNormalizer:
    """
    Normalizes DataAssets from different formats into a consistent representation
    """

    @staticmethod
    def normalize(asset: DataAsset) -> DataAsset:
        """
        Normalize a DataAsset to ensure consistent representation

        Args:
            asset: DataAsset to normalize

        Returns:
            Normalized DataAsset
        """
        # Ensure metadata consistency
        asset.metadata = DataNormalizer._normalize_metadata(asset.metadata)

        # Ensure quality info consistency
        asset.quality_info = DataNormalizer._normalize_quality_info(asset.quality_info)

        # Normalize tabular data if present
        if asset.is_tabular():
            asset.tabular_data = DataNormalizer._normalize_dataframe(asset.tabular_data)

        # Normalize text data if present
        if asset.is_text():
            asset.text_data = DataNormalizer._normalize_text(asset.text_data)

        return asset

    @staticmethod
    def _normalize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize metadata dictionary"""
        normalized = {}

        # Ensure standard fields exist
        standard_fields = ['file_name', 'file_size', 'file_extension', 'source_format', 'data_category']
        for field in standard_fields:
            if field in metadata:
                normalized[field] = metadata[field]

        # Add any additional metadata
        for key, value in metadata.items():
            if key not in normalized:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_quality_info(quality_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize quality info dictionary"""
        normalized = {}

        # Ensure standard fields exist with proper types
        if 'completeness' in quality_info:
            normalized['completeness'] = float(quality_info['completeness'])
        else:
            normalized['completeness'] = 1.0  # Default to complete

        if 'total_missing' in quality_info:
            normalized['total_missing'] = int(quality_info['total_missing'])
        else:
            normalized['total_missing'] = 0

        # Add any additional quality info
        for key, value in quality_info.items():
            if key not in normalized:
                normalized[key] = value

        return normalized

    @staticmethod
    def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame"""
        # Make a copy to avoid modifying original
        normalized = df.copy()

        # Normalize column names (strip whitespace, lowercase)
        normalized.columns = [col.strip().lower() for col in normalized.columns]

        # Replace infinite values with NaN
        normalized.replace([float('inf'), -float('inf')], None, inplace=True)

        # Try to convert object columns to numeric where possible
        for col in normalized.select_dtypes(include=['object']).columns:
            # Try numeric conversion
            numeric_converted = pd.to_numeric(normalized[col], errors='coerce')
            # If conversion was successful for most values, use the numeric version
            if numeric_converted.notna().sum() > len(normalized) * 0.5:
                normalized[col] = numeric_converted
            else:
                # Keep as string but ensure consistent representation
                normalized[col] = normalized[col].astype(str)

        return normalized

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Normalize text content"""
        if not text:
            return ""

        # Normalize whitespace
        normalized = ' '.join(text.split())

        # Remove excessive newlines
        normalized = normalized.replace('\n\n\n', '\n\n')

        return normalized.strip()

    @staticmethod
    def get_summary(asset: DataAsset) -> str:
        """
        Get a standardized summary of a DataAsset

        Args:
            asset: DataAsset to summarize

        Returns:
            Formatted summary string
        """
        summary_lines = []
        summary_lines.append("=" * 60)
        summary_lines.append("DATA ASSET SUMMARY")
        summary_lines.append("=" * 60)

        # Basic information
        summary_lines.append(f"\nSource File: {asset.source_file}")
        summary_lines.append(f"Format: {asset.source_format}")
        summary_lines.append(f"Category: {asset.data_category}")

        # File metadata
        if 'file_name' in asset.metadata:
            summary_lines.append(f"File Name: {asset.metadata['file_name']}")
        if 'file_size' in asset.metadata:
            size_mb = asset.metadata['file_size'] / (1024 * 1024)
            summary_lines.append(f"File Size: {size_mb:.2f} MB")

        # Tabular data information
        if asset.is_tabular():
            df = asset.tabular_data
            summary_lines.append(f"\nTabular Data:")
            summary_lines.append(f"  Rows: {len(df)}")
            summary_lines.append(f"  Columns: {len(df.columns)}")
            summary_lines.append(f"  Column Names: {list(df.columns)}")

        # Text data information
        if asset.is_text():
            text = asset.text_data
            summary_lines.append(f"\nText Data:")
            summary_lines.append(f"  Characters: {len(text)}")
            summary_lines.append(f"  Words: {len(text.split())}")
            summary_lines.append(f"  Lines: {len(text.split(chr(10)))}")

        # Quality information
        if asset.quality_info:
            summary_lines.append(f"\nQuality Information:")
            for key, value in asset.quality_info.items():
                summary_lines.append(f"  {key}: {value}")

        # Errors and warnings
        if asset.extraction_errors:
            summary_lines.append(f"\nErrors ({len(asset.extraction_errors)}):")
            for error in asset.extraction_errors:
                summary_lines.append(f"  - {error}")

        if asset.warnings:
            summary_lines.append(f"\nWarnings ({len(asset.warnings)}):")
            for warning in asset.warnings:
                summary_lines.append(f"  - {warning}")

        summary_lines.append("=" * 60)

        return "\n".join(summary_lines)
