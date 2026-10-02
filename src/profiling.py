"""
Data Profiling Module
Performs statistical analysis and profiling on datasets
"""

import pandas as pd
from typing import Dict, Any


class DataProfiler:
    """Handles data profiling and statistical analysis"""

    def __init__(self, data: pd.DataFrame):
        """
        Initialize the profiler with a DataFrame

        Args:
            data: Pandas DataFrame to profile
        """
        self.data = data
        self.profile: Dict[str, Any] = {}

    def generate_profile(self) -> Dict[str, Any]:
        """
        Generate a comprehensive profile of the dataset

        Returns:
            Dictionary containing profiling information
        """
        self.profile = {
            'basic_info': self._get_basic_info(),
            'column_info': self._get_column_info(),
            'data_types': self._get_data_types(),
            'missing_values': self._get_missing_values(),
            'numerical_stats': self._get_numerical_stats()
        }

        return self.profile

    def _get_basic_info(self) -> Dict[str, Any]:
        """Get basic dataset information"""
        return {
            'num_rows': len(self.data),
            'num_columns': len(self.data.columns),
            'memory_usage_mb': self.data.memory_usage(deep=True).sum() / (1024 * 1024)
        }

    def _get_column_info(self) -> Dict[str, Any]:
        """Get column names and basic information"""
        return {
            'column_names': list(self.data.columns),
            'num_columns': len(self.data.columns)
        }

    def _get_data_types(self) -> Dict[str, str]:
        """Get data types for each column"""
        return {col: str(dtype) for col, dtype in self.data.dtypes.items()}

    def _get_missing_values(self) -> Dict[str, int]:
        """Get count of missing values for each column"""
        return self.data.isnull().sum().to_dict()

    def _get_numerical_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistical summary for numerical columns"""
        numerical_cols = self.data.select_dtypes(include=['number']).columns

        if len(numerical_cols) == 0:
            return {}

        stats = {}
        for col in numerical_cols:
            col_stats = {
                'count': int(self.data[col].count()),
                'mean': float(self.data[col].mean()) if not self.data[col].empty else None,
                'std': float(self.data[col].std()) if not self.data[col].empty else None,
                'min': float(self.data[col].min()) if not self.data[col].empty else None,
                'max': float(self.data[col].max()) if not self.data[col].empty else None,
                'median': float(self.data[col].median()) if not self.data[col].empty else None,
                'quartiles': {
                    '25%': float(self.data[col].quantile(0.25)) if not self.data[col].empty else None,
                    '50%': float(self.data[col].quantile(0.50)) if not self.data[col].empty else None,
                    '75%': float(self.data[col].quantile(0.75)) if not self.data[col].empty else None
                }
            }
            stats[col] = col_stats

        return stats

    def get_profile_summary(self) -> str:
        """
        Get a human-readable summary of the profile

        Returns:
            Formatted string summary
        """
        if not self.profile:
            self.generate_profile()

        summary = []
        summary.append("=" * 50)
        summary.append("DATA PROFILE SUMMARY")
        summary.append("=" * 50)

        # Basic info
        basic = self.profile['basic_info']
        summary.append(f"\nRows: {basic['num_rows']}")
        summary.append(f"Columns: {basic['num_columns']}")
        summary.append(f"Memory Usage: {basic['memory_usage_mb']:.2f} MB")

        # Data types
        summary.append("\nColumn Data Types:")
        for col, dtype in self.profile['data_types'].items():
            summary.append(f"  {col}: {dtype}")

        # Missing values
        summary.append("\nMissing Values:")
        missing = self.profile['missing_values']
        total_missing = sum(missing.values())
        if total_missing > 0:
            for col, count in missing.items():
                if count > 0:
                    summary.append(f"  {col}: {count} missing")
        else:
            summary.append("  No missing values")

        # Numerical stats
        if self.profile['numerical_stats']:
            summary.append("\nNumerical Statistics:")
            for col, stats in self.profile['numerical_stats'].items():
                summary.append(f"\n  {col}:")
                summary.append(f"    Count: {stats['count']}")
                summary.append(f"    Mean: {stats['mean']:.2f}" if stats['mean'] else "    Mean: N/A")
                summary.append(f"    Std: {stats['std']:.2f}" if stats['std'] else "    Std: N/A")
                summary.append(f"    Min: {stats['min']:.2f}" if stats['min'] is not None else "    Min: N/A")
                summary.append(f"    Max: {stats['max']:.2f}" if stats['max'] is not None else "    Max: N/A")
                summary.append(f"    Median: {stats['median']:.2f}" if stats['median'] else "    Median: N/A")

        return "\n".join(summary)
