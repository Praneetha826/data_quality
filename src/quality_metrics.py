"""
Quality Metrics Module
Performs comprehensive quality assessment for all data formats
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class QualitySeverity(Enum):
    """Severity levels for quality issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityIssue:
    """Represents a single quality issue"""
    issue_type: str
    severity: QualitySeverity
    description: str
    location: str  # Column name, row index, or general location
    count: int = 1
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityReport:
    """Comprehensive quality report for a dataset"""
    total_issues: int = 0
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues_by_type: Dict[str, int] = field(default_factory=dict)
    issues: List[QualityIssue] = field(default_factory=list)
    quality_score: float = 0.0
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    overall_assessment: str = ""
    # Flag to indicate if component scores are applicable (tabular data)
    component_scores_applicable: bool = True


class QualityMetrics:
    """
    Performs quality metrics detection for both tabular and text data
    Uses deterministic Python/Pandas calculations
    """

    def __init__(self):
        self.report: Optional[QualityReport] = None

    def assess_quality(self, data_asset) -> QualityReport:
        """
        Main entry point for quality assessment

        Args:
            data_asset: DataAsset from the ingestion layer

        Returns:
            QualityReport with comprehensive quality metrics
        """
        self.report = QualityReport()

        if data_asset.is_tabular():
            self.report.component_scores_applicable = True
            self._assess_tabular_quality(data_asset.tabular_data)
        elif data_asset.is_text():
            self.report.component_scores_applicable = False
            self._assess_text_quality(data_asset.text_data)
        else:
            self.report.component_scores_applicable = False
            self._add_issue(
                "no_data",
                QualitySeverity.CRITICAL,
                "No data available for quality assessment",
                "general"
            )

        self._calculate_overall_score()
        self._generate_assessment()

        return self.report

    def _assess_tabular_quality(self, df: pd.DataFrame):
        """Assess quality of tabular data"""
        if df.empty:
            self._add_issue(
                "empty_dataset",
                QualitySeverity.CRITICAL,
                "Dataset is empty",
                "general"
            )
            return

        # Check for missing values
        self._check_missing_values(df)

        # Check for duplicates
        self._check_duplicates(df)

        # Check for outliers in numerical columns
        self._check_outliers(df)

        # Check data types
        self._check_data_types(df)

        # Check for invalid values
        self._check_invalid_values(df)

        # Check column consistency
        self._check_column_consistency(df)

    def _assess_text_quality(self, text: str):
        """Assess quality of text data"""
        if not text or not text.strip():
            self._add_issue(
                "empty_text",
                QualitySeverity.CRITICAL,
                "Text is empty or contains only whitespace",
                "general"
            )
            return

        # Check for encoding issues
        self._check_text_encoding(text)

        # Check for very short text (less than 50 characters after normalization)
        if len(text) < 50:
            self._add_issue(
                "very_short_text",
                QualitySeverity.LOW,
                f"Text is very short ({len(text)} characters)",
                "general"
            )

        # Check for repetitive content
        self._check_repetitive_content(text)

        # Check for special characters
        self._check_special_characters(text)

    def _check_missing_values(self, df: pd.DataFrame):
        """Check for missing values in each column"""
        missing_counts = df.isnull().sum()
        total_cells = len(df) * len(df.columns)

        for col, count in missing_counts.items():
            if count > 0:
                percentage = (count / len(df)) * 100

                if percentage > 50:
                    severity = QualitySeverity.CRITICAL
                elif percentage > 20:
                    severity = QualitySeverity.HIGH
                elif percentage > 10:
                    severity = QualitySeverity.MEDIUM
                else:
                    severity = QualitySeverity.LOW

                self._add_issue(
                    "missing_values",
                    severity,
                    f"Column '{col}' has {count} missing values ({percentage:.1f}%)",
                    col,
                    count,
                    {"percentage": percentage, "total_rows": len(df)}
                )

    def _check_duplicates(self, df: pd.DataFrame):
        """Check for duplicate rows"""
        exact_duplicates = df.duplicated().sum()

        if exact_duplicates > 0:
            percentage = (exact_duplicates / len(df)) * 100

            if percentage > 20:
                severity = QualitySeverity.HIGH
            elif percentage > 5:
                severity = QualitySeverity.MEDIUM
            else:
                severity = QualitySeverity.LOW

            self._add_issue(
                "duplicate_rows",
                severity,
                f"Found {exact_duplicates} duplicate rows ({percentage:.1f}%)",
                "general",
                exact_duplicates,
                {"percentage": percentage, "total_rows": len(df)}
            )

        # Check for partial duplicates (same key columns)
        if len(df.columns) > 0:
            # Use first column as key for partial duplicate check
            key_col = df.columns[0]
            key_duplicates = df[key_col].duplicated().sum()

            if key_duplicates > 0 and key_duplicates != exact_duplicates:
                self._add_issue(
                    "partial_duplicates",
                    QualitySeverity.LOW,
                    f"Found {key_duplicates} rows with duplicate values in column '{key_col}'",
                    key_col,
                    key_duplicates
                )

    def _check_outliers(self, df: pd.DataFrame):
        """Check for outliers in numerical columns using IQR method"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns

        for col in numerical_cols:
            if df[col].dropna().empty:
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            if IQR == 0:
                continue

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]

            if len(outliers) > 0:
                percentage = (len(outliers) / len(df)) * 100

                if percentage > 10:
                    severity = QualitySeverity.HIGH
                elif percentage > 5:
                    severity = QualitySeverity.MEDIUM
                else:
                    severity = QualitySeverity.LOW

                self._add_issue(
                    "outliers",
                    severity,
                    f"Column '{col}' has {len(outliers)} outliers ({percentage:.1f}%) using IQR method",
                    col,
                    len(outliers),
                    {
                        "percentage": percentage,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "outlier_values": outliers.tolist()[:10]  # First 10 outliers
                    }
                )

    def _check_data_types(self, df: pd.DataFrame):
        """Check for potential data type issues"""
        for col in df.columns:
            # Check for mixed types in object columns
            if df[col].dtype == 'object':
                # Check if column contains numbers stored as strings
                try:
                    numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                    if numeric_conversion.notna().sum() > len(df) * 0.8:
                        self._add_issue(
                            "inconsistent_type",
                            QualitySeverity.MEDIUM,
                            f"Column '{col}' appears to contain numeric data stored as strings",
                            col,
                            details={"suggested_type": "numeric"}
                        )
                except:
                    pass

            # Check for date columns stored as strings
            if df[col].dtype == 'object':
                try:
                    import warnings
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        date_conversion = pd.to_datetime(df[col], errors='coerce')
                    if date_conversion.notna().sum() > len(df) * 0.8:
                        self._add_issue(
                            "date_as_string",
                            QualitySeverity.LOW,
                            f"Column '{col}' appears to contain date data stored as strings",
                            col,
                            details={"suggested_type": "datetime"}
                        )
                except:
                    pass

    def _check_invalid_values(self, df: pd.DataFrame):
        """Check for invalid or suspicious values"""
        for col in df.columns:
            # Check for negative values in columns that shouldn't have them
            if df[col].dtype in [np.int64, np.float64]:
                if 'age' in col.lower() or 'count' in col.lower() or 'amount' in col.lower():
                    negative_count = (df[col] < 0).sum()
                    if negative_count > 0:
                        self._add_issue(
                            "negative_values",
                            QualitySeverity.MEDIUM,
                            f"Column '{col}' has {negative_count} negative values (may be invalid)",
                            col,
                            negative_count
                        )

            # Check for unreasonably large values
            if df[col].dtype in [np.int64, np.float64]:
                max_val = df[col].max()
                if max_val > 1e9:  # Values over 1 billion
                    self._add_issue(
                        "suspicious_large_values",
                        QualitySeverity.MEDIUM,
                        f"Column '{col}' has suspiciously large values (max: {max_val})",
                        col,
                        details={"max_value": max_val}
                    )

            # Check for zero values in critical columns
            if 'id' in col.lower() and df[col].dtype in [np.int64, np.float64]:
                zero_count = (df[col] == 0).sum()
                if zero_count > 0:
                    self._add_issue(
                        "zero_ids",
                        QualitySeverity.HIGH,
                        f"Column '{col}' has {zero_count} zero values (may be invalid for ID column)",
                        col,
                        zero_count
                    )

    def _check_column_consistency(self, df: pd.DataFrame):
        """Check for column consistency issues"""
        # Check for columns with all same values
        for col in df.columns:
            unique_count = df[col].nunique()
            if unique_count == 1:
                self._add_issue(
                    "constant_column",
                    QualitySeverity.LOW,
                    f"Column '{col}' has only one unique value (constant)",
                    col,
                    details={"unique_value": str(df[col].iloc[0])}
                )

        # Check for high cardinality in columns that might be categorical
        for col in df.select_dtypes(include=['object']).columns:
            unique_count = df[col].nunique()
            if unique_count == len(df) and len(df) > 10:
                self._add_issue(
                    "high_cardinality",
                    QualitySeverity.INFO,
                    f"Column '{col}' has high cardinality ({unique_count} unique values)",
                    col,
                    details={"unique_count": unique_count, "total_rows": len(df)}
                )

    def _check_text_encoding(self, text: str):
        """Check for text encoding issues"""
        # Check for replacement characters (encoding issues)
        replacement_char = '\ufffd'
        if replacement_char in text:
            count = text.count(replacement_char)
            if count > len(text) * 0.05:  # More than 5% replacement characters
                self._add_issue(
                    "encoding_issues",
                    QualitySeverity.MEDIUM,
                    f"Text contains many replacement characters ({count}), indicating possible encoding issues",
                    "general",
                    count
                )
            elif count > 0:
                self._add_issue(
                    "encoding_issues",
                    QualitySeverity.LOW,
                    f"Text contains some replacement characters ({count}), indicating possible encoding issues",
                    "general",
                    count
                )

        # Check for control characters
        control_chars = sum(1 for char in text if ord(char) < 32 and char not in '\n\r\t')
        if control_chars > len(text) * 0.01:  # More than 1% control characters
            self._add_issue(
                "control_characters",
                QualitySeverity.LOW,
                f"Text contains unusual control characters ({control_chars} found)",
                "general",
                control_chars
            )

    def _check_repetitive_content(self, text: str):
        """Check for repetitive content patterns"""
        # Check for repeated lines
        lines = text.split('\n')
        if len(lines) > 1:
            line_counts = {}
            for line in lines:
                line_stripped = line.strip()
                if line_stripped:
                    line_counts[line_stripped] = line_counts.get(line_stripped, 0) + 1

            max_repeat = max(line_counts.values()) if line_counts else 0
            if max_repeat > len(lines) * 0.1:  # If a line appears more than 10% of the time
                self._add_issue(
                    "repetitive_content",
                    QualitySeverity.LOW,
                    f"Text contains repetitive content (most frequent line appears {max_repeat} times)",
                    "general",
                    details={"max_repeat_count": max_repeat}
                )
        else:
            # For single-line text, check for repeated phrases
            words = text.split()
            if len(words) > 5:
                word_counts = {}
                for word in words:
                    word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1

                max_repeat = max(word_counts.values())
                if max_repeat > len(words) * 0.2:  # If a word appears more than 20% of the time
                    self._add_issue(
                        "repetitive_content",
                        QualitySeverity.LOW,
                        f"Text contains repetitive content (most frequent word appears {max_repeat} times)",
                        "general",
                        details={"max_repeat_count": max_repeat}
                    )

    def _check_special_characters(self, text: str):
        """Check for unusual special characters"""
        # Check for excessive special characters
        special_chars = sum(1 for char in text if not char.isalnum() and char not in ' \n\r\t.,!?;:\'"-()[]{}')
        if special_chars > len(text) * 0.05:  # Lower threshold from 10% to 5%
            self._add_issue(
                "many_special_characters",
                QualitySeverity.INFO,
                f"Text contains many special characters ({special_chars} found)",
                "general",
                special_chars
            )

    def _add_issue(self, issue_type: str, severity: QualitySeverity, description: str, location: str, count: int = 1, details: Dict[str, Any] = None):
        """Add a quality issue to the report"""
        issue = QualityIssue(
            issue_type=issue_type,
            severity=severity,
            description=description,
            location=location,
            count=count,
            details=details or {}
        )

        self.report.issues.append(issue)
        self.report.total_issues += 1

        # Update severity counts
        severity_name = severity.value
        self.report.issues_by_severity[severity_name] = self.report.issues_by_severity.get(severity_name, 0) + 1

        # Update type counts
        self.report.issues_by_type[issue_type] = self.report.issues_by_type.get(issue_type, 0) + 1

    def _calculate_overall_score(self):
        """Calculate overall quality score (0-100)"""
        if not self.report.issues:
            self.report.quality_score = 100.0
            self.report.completeness_score = 100.0
            self.report.consistency_score = 100.0
            self.report.validity_score = 100.0
            return

        # Calculate score based on severity weights
        severity_weights = {
            QualitySeverity.CRITICAL.value: 50,
            QualitySeverity.HIGH.value: 20,
            QualitySeverity.MEDIUM.value: 10,
            QualitySeverity.LOW.value: 5,
            QualitySeverity.INFO.value: 1
        }

        total_penalty = 0
        for issue in self.report.issues:
            weight = severity_weights.get(issue.severity.value, 5)
            total_penalty += weight * issue.count

        # Calculate score (max penalty of 100 points)
        self.report.quality_score = max(0, 100 - min(100, total_penalty))

        # Calculate component scores
        self._calculate_completeness_score()
        self._calculate_consistency_score()
        self._calculate_validity_score()

    def _calculate_completeness_score(self):
        """Calculate completeness score based on missing value issues"""
        missing_issues = [i for i in self.report.issues if i.issue_type == "missing_values"]
        if not missing_issues:
            self.report.completeness_score = 100.0
            return

        total_missing = sum(i.count for i in missing_issues)
        # Simple penalty: 10 points per missing value issue, max 50 points
        penalty = min(50, len(missing_issues) * 10)
        self.report.completeness_score = max(0, 100 - penalty)

    def _calculate_consistency_score(self):
        """Calculate consistency score based on duplicate and type issues"""
        consistency_issues = [i for i in self.report.issues if i.issue_type in ["duplicate_rows", "partial_duplicates", "inconsistent_type"]]
        if not consistency_issues:
            self.report.consistency_score = 100.0
            return

        # Simple penalty: 15 points per consistency issue, max 50 points
        penalty = min(50, len(consistency_issues) * 15)
        self.report.consistency_score = max(0, 100 - penalty)

    def _calculate_validity_score(self):
        """Calculate validity score based on invalid value issues"""
        validity_issues = [i for i in self.report.issues if i.issue_type in ["outliers", "invalid_values", "negative_values", "zero_ids"]]
        if not validity_issues:
            self.report.validity_score = 100.0
            return

        # Simple penalty: 10 points per validity issue, max 50 points
        penalty = min(50, len(validity_issues) * 10)
        self.report.validity_score = max(0, 100 - penalty)

    def _generate_assessment(self):
        """Generate overall quality assessment text"""
        score = self.report.quality_score

        if score >= 90:
            self.report.overall_assessment = "Excellent - Data quality is very high with minimal issues"
        elif score >= 75:
            self.report.overall_assessment = "Good - Data quality is acceptable with some minor issues"
        elif score >= 60:
            self.report.overall_assessment = "Fair - Data quality requires attention for several issues"
        elif score >= 40:
            self.report.overall_assessment = "Poor - Data quality has significant issues that should be addressed"
        else:
            self.report.overall_assessment = "Critical - Data quality is severely compromised"

    def get_summary(self) -> str:
        """Get a formatted summary of the quality report"""
        if not self.report:
            return "No quality assessment performed"

        lines = []
        lines.append("=" * 60)
        lines.append("QUALITY ASSESSMENT REPORT")
        lines.append("=" * 60)

        lines.append(f"\nOverall Quality Score: {self.report.quality_score:.1f}/100")
        lines.append(f"Assessment: {self.report.overall_assessment}")

        lines.append(f"\nComponent Scores:")
        lines.append(f"  Completeness: {self.report.completeness_score:.1f}/100")
        lines.append(f"  Consistency: {self.report.consistency_score:.1f}/100")
        lines.append(f"  Validity: {self.report.validity_score:.1f}/100")

        lines.append(f"\nTotal Issues: {self.report.total_issues}")

        if self.report.issues_by_severity:
            lines.append(f"\nIssues by Severity:")
            for severity, count in sorted(self.report.issues_by_severity.items(), reverse=True):
                lines.append(f"  {severity.upper()}: {count}")

        if self.report.issues_by_type:
            lines.append(f"\nIssues by Type:")
            for issue_type, count in sorted(self.report.issues_by_type.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"  {issue_type}: {count}")

        if self.report.issues:
            lines.append(f"\nDetailed Issues:")
            for i, issue in enumerate(self.report.issues, 1):
                lines.append(f"\n{i}. [{issue.severity.value.upper()}] {issue.description}")
                lines.append(f"   Location: {issue.location}")
                if issue.count > 1:
                    lines.append(f"   Count: {issue.count}")
                if issue.details:
                    lines.append(f"   Details: {issue.details}")

        lines.append("=" * 60)

        return "\n".join(lines)
