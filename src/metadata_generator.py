"""
Metadata Generator Module
Generates comprehensive metadata from DataAssets and quality reports
"""

import pandas as pd
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DatasetMetadata:
    """
    Comprehensive metadata for a dataset
    Contains information for both tabular and text data
    """
    # Basic information
    source_file: str = ""
    source_format: str = ""
    data_category: str = ""
    timestamp: str = ""

    # Dataset statistics
    total_rows: int = 0
    total_columns: int = 0
    total_cells: int = 0
    memory_usage_mb: float = 0.0

    # Tabular-specific metadata
    column_names: List[str] = field(default_factory=list)
    column_types: Dict[str, str] = field(default_factory=dict)
    column_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Text-specific metadata
    character_count: int = 0
    word_count: int = 0
    line_count: int = 0
    encoding: str = ""

    # Quality information
    quality_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    overall_assessment: str = ""

    # Quality issues
    quality_issues: List[Dict[str, Any]] = field(default_factory=list)
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_type: Dict[str, int] = field(default_factory=dict)

    # Additional metadata
    custom_metadata: Dict[str, Any] = field(default_factory=dict)


class MetadataGenerator:
    """
    Generates comprehensive metadata from DataAssets and quality reports
    """

    def __init__(self):
        pass

    def generate_metadata(self, data_asset, quality_report) -> DatasetMetadata:
        """
        Generate comprehensive metadata from DataAsset and quality report

        Args:
            data_asset: DataAsset from ingestion layer
            quality_report: QualityReport from quality assessment

        Returns:
            DatasetMetadata with comprehensive information
        """
        metadata = DatasetMetadata()

        # Basic information
        metadata.source_file = data_asset.source_file
        metadata.source_format = data_asset.source_format
        metadata.data_category = data_asset.data_category
        metadata.timestamp = datetime.now().isoformat()

        # Copy metadata from DataAsset
        metadata.custom_metadata.update(data_asset.metadata)

        # Generate statistics based on data type
        if data_asset.is_tabular():
            self._generate_tabular_metadata(data_asset, metadata)
        elif data_asset.is_text():
            self._generate_text_metadata(data_asset, metadata)

        # Add quality information
        self._add_quality_metadata(quality_report, metadata)

        return metadata

    def _generate_tabular_metadata(self, data_asset, metadata):
        """Generate metadata for tabular data"""
        df = data_asset.tabular_data

        metadata.total_rows = len(df)
        metadata.total_columns = len(df.columns)
        metadata.total_cells = len(df) * len(df.columns)
        metadata.memory_usage_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)

        metadata.column_names = list(df.columns)
        metadata.column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}

        # Generate column statistics
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                metadata.column_stats[col] = {
                    'count': int(df[col].count()),
                    'mean': float(df[col].mean()) if not df[col].empty else None,
                    'std': float(df[col].std()) if not df[col].empty else None,
                    'min': float(df[col].min()) if not df[col].empty else None,
                    'max': float(df[col].max()) if not df[col].empty else None,
                    'median': float(df[col].median()) if not df[col].empty else None
                }
            else:
                metadata.column_stats[col] = {
                    'count': int(df[col].count()),
                    'unique_count': int(df[col].nunique()),
                    'most_common': str(df[col].mode()[0]) if not df[col].empty else None
                }

    def _generate_text_metadata(self, data_asset, metadata):
        """Generate metadata for text data"""
        text = data_asset.text_data

        metadata.character_count = len(text)
        metadata.word_count = len(text.split())
        metadata.line_count = len(text.split('\n'))
        metadata.encoding = data_asset.metadata.get('encoding', 'unknown')

    def _add_quality_metadata(self, quality_report, metadata):
        """Add quality information from quality report"""
        metadata.quality_score = quality_report.quality_score
        metadata.completeness_score = quality_report.completeness_score
        metadata.consistency_score = quality_report.consistency_score
        metadata.validity_score = quality_report.validity_score
        metadata.overall_assessment = quality_report.overall_assessment

        # Convert quality issues to dictionary format
        for issue in quality_report.issues:
            issue_dict = {
                'issue_type': issue.issue_type,
                'severity': issue.severity.value,
                'description': issue.description,
                'location': issue.location,
                'count': issue.count,
                'details': issue.details
            }
            metadata.quality_issues.append(issue_dict)

        metadata.total_issues = quality_report.total_issues
        metadata.issues_by_severity = quality_report.issues_by_severity
        metadata.issues_by_type = quality_report.issues_by_type

    def generate_textual_metadata(self, metadata: DatasetMetadata) -> str:
        """
        Generate textual representation of metadata for embedding
        This is the text that will be converted to embeddings

        Args:
            metadata: DatasetMetadata object

        Returns:
            Text string suitable for embedding generation
        """
        text_parts = []

        # Basic information
        text_parts.append(f"Dataset: {metadata.source_file}")
        text_parts.append(f"Format: {metadata.source_format}")
        text_parts.append(f"Category: {metadata.data_category}")
        text_parts.append(f"Timestamp: {metadata.timestamp}")

        # Statistics
        text_parts.append(f"Total rows: {metadata.total_rows}")
        text_parts.append(f"Total columns: {metadata.total_columns}")
        text_parts.append(f"Total cells: {metadata.total_cells}")
        text_parts.append(f"Memory usage: {metadata.memory_usage_mb:.2f} MB")

        # Column information for tabular data
        if metadata.column_names:
            text_parts.append(f"Columns: {', '.join(metadata.column_names)}")
            text_parts.append(f"Column types: {', '.join([f'{col}({dtype})' for col, dtype in metadata.column_types.items()])}")

        # Quality information
        text_parts.append(f"Quality score: {metadata.quality_score:.1f}/100")
        text_parts.append(f"Completeness: {metadata.completeness_score:.1f}/100")
        text_parts.append(f"Consistency: {metadata.consistency_score:.1f}/100")
        text_parts.append(f"Validity: {metadata.validity_score:.1f}/100")
        text_parts.append(f"Assessment: {metadata.overall_assessment}")

        # Quality issues
        if metadata.quality_issues:
            text_parts.append(f"Total quality issues: {metadata.total_issues}")
            text_parts.append(f"Issues by severity: {metadata.issues_by_severity}")
            text_parts.append(f"Issues by type: {metadata.issues_by_type}")

            for issue in metadata.quality_issues:
                text_parts.append(f"Issue: {issue['issue_type']} - {issue['severity']} - {issue['description']}")

        # Custom metadata
        if metadata.custom_metadata:
            text_parts.append("Additional metadata:")
            for key, value in metadata.custom_metadata.items():
                text_parts.append(f"{key}: {value}")

        return "\n".join(text_parts)

    def generate_chunked_metadata(self, metadata: DatasetMetadata, chunk_size: int = 500) -> List[str]:
        """
        Generate metadata in chunks for better embedding

        Args:
            metadata: DatasetMetadata object
            chunk_size: Maximum characters per chunk

        Returns:
            List of text chunks
        """
        full_text = self.generate_textual_metadata(metadata)

        if len(full_text) <= chunk_size:
            return [full_text]

        # Split into chunks by character count
        chunks = []
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i + chunk_size]
            chunks.append(chunk)

        return chunks
