"""
CSV Loader Module
Handles loading and validation of CSV files
"""

import pandas as pd
from pathlib import Path
from typing import Optional
from .base_loader import BaseLoader, DataAsset


class CSVLoader(BaseLoader):
    """Loader for CSV files"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.csv']

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid CSV

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid CSV, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to read the file to validate it's actually a CSV
            pd.read_csv(file_path, nrows=1)
            return True

        except Exception:
            return False

    def load(self, file_path: str) -> DataAsset:
        """
        Load a CSV file and return a DataAsset

        Args:
            file_path: Path to the CSV file

        Returns:
            DataAsset containing the loaded CSV data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid CSV or is empty
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be a CSV file. Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'CSV', 'structured')

        try:
            # Load the CSV file
            data = pd.read_csv(file_path)

            # Check if DataFrame is empty
            if data.empty:
                raise ValueError("CSV file is empty or contains no data")

            # Set tabular data
            asset.tabular_data = data

            # Add CSV-specific metadata
            asset.metadata.update({
                'rows': len(data),
                'columns': len(data.columns),
                'column_names': list(data.columns),
                'column_types': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'missing_values': data.isnull().sum().to_dict()
            })

            # Add quality info
            asset.quality_info = {
                'total_missing': int(data.isnull().sum().sum()),
                'total_cells': int(len(data) * len(data.columns)),
                'completeness': 1.0 - (data.isnull().sum().sum() / (len(data) * len(data.columns)))
            }

        except pd.errors.EmptyDataError:
            asset.extraction_errors.append("CSV file is empty")
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            asset.extraction_errors.append(f"CSV parsing error: {str(e)}")
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            asset.extraction_errors.append(f"Unexpected error: {str(e)}")
            raise ValueError(f"Unexpected error loading CSV: {str(e)}")

        return asset
