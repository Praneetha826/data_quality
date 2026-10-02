"""
Excel Loader Module
Handles loading and validation of Excel files (.xlsx, .xls)
"""

import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
from .base_loader import BaseLoader, DataAsset


class ExcelLoader(BaseLoader):
    """Loader for Excel files (.xlsx, .xls)"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.xlsx', '.xls']

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid Excel file

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid Excel, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to read the file to validate it's actually an Excel file
            pd.ExcelFile(file_path)
            return True

        except Exception:
            return False

    def load(self, file_path: str, sheet_name: Optional[str] = None) -> DataAsset:
        """
        Load an Excel file and return a DataAsset

        Args:
            file_path: Path to the Excel file
            sheet_name: Specific sheet to load (None for first sheet)

        Returns:
            DataAsset containing the loaded Excel data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not a valid Excel file or is empty
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be an Excel file (.xlsx or .xls). Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'Excel', 'structured')

        try:
            # Open the Excel file
            excel_file = pd.ExcelFile(file_path)

            # Get sheet names
            sheet_names = excel_file.sheet_names
            asset.metadata['available_sheets'] = sheet_names
            asset.metadata['total_sheets'] = len(sheet_names)

            # Determine which sheet to load
            if sheet_name is None:
                sheet_name = sheet_names[0] if sheet_names else None
                asset.warnings.append(f"Loading first sheet: {sheet_name}")
            elif sheet_name not in sheet_names:
                raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {sheet_names}")

            # Load the specified sheet
            data = pd.read_excel(file_path, sheet_name=sheet_name)

            # Check if DataFrame is empty
            if data.empty:
                asset.warnings.append(f"Sheet '{sheet_name}' is empty")

            # Set tabular data
            asset.tabular_data = data

            # Add Excel-specific metadata
            asset.metadata.update({
                'loaded_sheet': sheet_name,
                'rows': len(data),
                'columns': len(data.columns),
                'column_names': list(data.columns),
                'column_types': {col: str(dtype) for col, dtype in data.dtypes.items()},
                'missing_values': data.isnull().sum().to_dict()
            })

            # Add quality info
            total_cells = len(data) * len(data.columns) if len(data.columns) > 0 else 0
            asset.quality_info = {
                'total_missing': int(data.isnull().sum().sum()),
                'total_cells': int(total_cells),
                'completeness': 1.0 - (data.isnull().sum().sum() / total_cells) if total_cells > 0 else 0.0
            }

        except ValueError as e:
            asset.extraction_errors.append(str(e))
            raise
        except Exception as e:
            asset.extraction_errors.append(f"Excel loading error: {str(e)}")
            raise ValueError(f"Error loading Excel file: {str(e)}")

        return asset

    def load_all_sheets(self, file_path: str) -> Dict[str, DataAsset]:
        """
        Load all sheets from an Excel file

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary mapping sheet names to DataAssets
        """
        self._check_file_exists(file_path)

        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be an Excel file (.xlsx or .xls). Got: {path.suffix}")

        try:
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names

            assets = {}
            for sheet_name in sheet_names:
                try:
                    asset = self.load(file_path, sheet_name=sheet_name)
                    assets[sheet_name] = asset
                except Exception as e:
                    # Create error asset for failed sheet
                    base_asset = self._create_base_asset(file_path, 'Excel', 'structured')
                    base_asset.metadata['loaded_sheet'] = sheet_name
                    base_asset.extraction_errors.append(f"Failed to load sheet '{sheet_name}': {str(e)}")
                    assets[sheet_name] = base_asset

            return assets

        except Exception as e:
            raise ValueError(f"Error loading Excel sheets: {str(e)}")
