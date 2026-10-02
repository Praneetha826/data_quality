"""
Data Ingestion Module
Handles loading and validation of CSV datasets
"""

import pandas as pd
from pathlib import Path
from typing import Optional


class DataIngestion:
    """Handles data ingestion from CSV files"""

    def __init__(self):
        self.data: Optional[pd.DataFrame] = None
        self.file_path: Optional[str] = None

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load a CSV file into a Pandas DataFrame

        Args:
            file_path: Path to the CSV file

        Returns:
            Pandas DataFrame containing the loaded data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid CSV or is empty
        """
        # Check if file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check if file is a CSV
        if path.suffix.lower() != '.csv':
            raise ValueError(f"File must be a CSV file. Got: {path.suffix}")

        try:
            # Load the CSV file
            self.data = pd.read_csv(file_path)
            self.file_path = file_path

            # Check if DataFrame is empty
            if self.data.empty:
                raise ValueError("CSV file is empty or contains no data")

            return self.data

        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"Error parsing CSV file: {str(e)}")
        except Exception as e:
            raise ValueError(f"Unexpected error loading CSV: {str(e)}")

    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Get the currently loaded DataFrame

        Returns:
            Pandas DataFrame or None if no data is loaded
        """
        return self.data

    def get_file_info(self) -> dict:
        """
        Get information about the loaded file

        Returns:
            Dictionary containing file information
        """
        if self.data is None:
            return {}

        return {
            'file_path': self.file_path,
            'rows': len(self.data),
            'columns': len(self.data.columns),
            'column_names': list(self.data.columns),
            'file_size_mb': Path(self.file_path).stat().st_size / (1024 * 1024) if self.file_path else 0
        }
