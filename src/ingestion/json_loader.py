"""
JSON Loader Module
Handles loading and validation of JSON files
"""

import json
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from .base_loader import BaseLoader, DataAsset


class JSONLoader(BaseLoader):
    """Loader for JSON files"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.json']

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid JSON file

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid JSON, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to parse the file to validate it's actually JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True

        except Exception:
            return False

    def load(self, file_path: str) -> DataAsset:
        """
        Load a JSON file and return a DataAsset

        Args:
            file_path: Path to the JSON file

        Returns:
            DataAsset containing the loaded JSON data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not valid JSON
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be a JSON file. Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'JSON', 'semi-structured')

        try:
            # Read and parse JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Analyze JSON structure
            structure_info = self._analyze_structure(json_data)
            asset.metadata.update(structure_info)

            # Try to convert to tabular format if possible
            if structure_info['is_array_of_records']:
                # Convert array of records to DataFrame
                df = pd.DataFrame(json_data)
                asset.tabular_data = df
                asset.metadata.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'missing_values': df.isnull().sum().to_dict()
                })
                asset.quality_info = {
                    'total_missing': int(df.isnull().sum().sum()),
                    'total_cells': int(len(df) * len(df.columns)),
                    'completeness': 1.0 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
                }
            elif structure_info['is_single_record']:
                # Convert single record to DataFrame
                df = pd.DataFrame([json_data])
                asset.tabular_data = df
                asset.metadata.update({
                    'rows': 1,
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'missing_values': df.isnull().sum().to_dict()
                })
                asset.quality_info = {
                    'total_missing': int(df.isnull().sum().sum()),
                    'total_cells': int(len(df.columns)),
                    'completeness': 1.0 - (df.isnull().sum().sum() / len(df.columns))
                }
            else:
                # Complex nested structure - store as text for now
                asset.text_data = json.dumps(json_data, indent=2)
                asset.warnings.append("JSON has complex nested structure, stored as text")
                asset.metadata['tabular_conversion'] = 'not_possible'

        except json.JSONDecodeError as e:
            asset.extraction_errors.append(f"JSON parsing error: {str(e)}")
            raise ValueError(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            asset.extraction_errors.append(f"JSON loading error: {str(e)}")
            raise ValueError(f"Error loading JSON file: {str(e)}")

        return asset

    def _analyze_structure(self, json_data: Any) -> Dict[str, Any]:
        """
        Analyze the structure of JSON data

        Args:
            json_data: Parsed JSON data

        Returns:
            Dictionary with structure information
        """
        info = {
            'data_type': type(json_data).__name__,
            'is_array_of_records': False,
            'is_single_record': False,
            'has_nested_structure': False,
            'total_keys': 0,
            'max_depth': 0
        }

        if isinstance(json_data, list):
            if len(json_data) > 0 and all(isinstance(item, dict) for item in json_data):
                info['is_array_of_records'] = True
                info['total_keys'] = len(json_data[0].keys()) if json_data else 0
            else:
                info['has_nested_structure'] = True
            info['max_depth'] = self._calculate_depth(json_data)

        elif isinstance(json_data, dict):
            info['is_single_record'] = True
            info['total_keys'] = len(json_data.keys())
            info['max_depth'] = self._calculate_depth(json_data)
            info['has_nested_structure'] = any(
                isinstance(v, (dict, list)) for v in json_data.values()
            )

        return info

    def _calculate_depth(self, obj: Any, current_depth: int = 0) -> int:
        """Calculate the maximum nesting depth of a JSON structure"""
        if not isinstance(obj, (dict, list)):
            return current_depth

        max_child_depth = current_depth
        if isinstance(obj, dict):
            for value in obj.values():
                child_depth = self._calculate_depth(value, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        elif isinstance(obj, list):
            for item in obj:
                child_depth = self._calculate_depth(item, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)

        return max_child_depth
