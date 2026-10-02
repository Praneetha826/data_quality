"""
XML Loader Module
Handles loading and validation of XML files
"""

import xml.etree.ElementTree as ET
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any, List
from .base_loader import BaseLoader, DataAsset


class XMLLoader(BaseLoader):
    """Loader for XML files"""

    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.xml']

    def validate_file(self, file_path: str) -> bool:
        """
        Validate that the file is a valid XML file

        Args:
            file_path: Path to the file to validate

        Returns:
            True if file is valid XML, False otherwise
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
            if path.suffix.lower() not in self.supported_extensions:
                return False

            # Try to parse the file to validate it's actually XML
            ET.parse(file_path)
            return True

        except Exception:
            return False

    def load(self, file_path: str) -> DataAsset:
        """
        Load an XML file and return a DataAsset

        Args:
            file_path: Path to the XML file

        Returns:
            DataAsset containing the loaded XML data

        Raises:
            FileNotFoundError: If the file does not exist
            ValueError: If the file is not valid XML
        """
        self._check_file_exists(file_path)

        # Validate file extension
        path = Path(file_path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"File must be an XML file. Got: {path.suffix}")

        # Create base asset
        asset = self._create_base_asset(file_path, 'XML', 'semi-structured')

        try:
            # Parse XML
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Analyze XML structure
            structure_info = self._analyze_structure(root)
            asset.metadata.update(structure_info)

            # Try to extract records from XML
            records = self._extract_records(root)

            if records:
                # Convert to DataFrame
                df = pd.DataFrame(records)
                asset.tabular_data = df
                asset.metadata.update({
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': list(df.columns),
                    'column_types': {col: str(dtype) for col, dtype in df.dtypes.items()},
                    'missing_values': df.isnull().sum().to_dict(),
                    'records_extracted': True
                })
                asset.quality_info = {
                    'total_missing': int(df.isnull().sum().sum()),
                    'total_cells': int(len(df) * len(df.columns)),
                    'completeness': 1.0 - (df.isnull().sum().sum() / (len(df) * len(df.columns)))
                }
            else:
                # No structured records found - store as text
                asset.text_data = ET.tostring(root, encoding='unicode')
                asset.warnings.append("No structured records found, stored as text")
                asset.metadata['tabular_conversion'] = 'not_possible'

        except ET.ParseError as e:
            asset.extraction_errors.append(f"XML parsing error: {str(e)}")
            raise ValueError(f"Invalid XML file: {str(e)}")
        except Exception as e:
            asset.extraction_errors.append(f"XML loading error: {str(e)}")
            raise ValueError(f"Error loading XML file: {str(e)}")

        return asset

    def _analyze_structure(self, root: ET.Element) -> Dict[str, Any]:
        """
        Analyze the structure of XML data

        Args:
            root: Root XML element

        Returns:
            Dictionary with structure information
        """
        info = {
            'root_tag': root.tag,
            'root_attributes': dict(root.attrib),
            'total_elements': len(list(root)),
            'total_attributes': len(root.attrib),
            'has_namespaces': bool('}' in root.tag),
            'depth': self._calculate_depth(root)
        }

        # Get direct children tags
        children_tags = [child.tag for child in root]
        info['children_tags'] = children_tags
        info['unique_children_tags'] = list(set(children_tags))

        return info

    def _calculate_depth(self, element: ET.Element, current_depth: int = 0) -> int:
        """Calculate the maximum nesting depth of XML structure"""
        max_child_depth = current_depth
        for child in element:
            child_depth = self._calculate_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        return max_child_depth

    def _extract_records(self, root: ET.Element) -> List[Dict[str, Any]]:
        """
        Try to extract structured records from XML

        Args:
            root: Root XML element

        Returns:
            List of dictionaries representing records
        """
        records = []

        # Try to find repeating elements that look like records
        # Strategy: Find direct children with same tag
        children = list(root)
        if not children:
            return records

        # Group children by tag
        tag_groups = {}
        for child in children:
            tag = child.tag
            if tag not in tag_groups:
                tag_groups[tag] = []
            tag_groups[tag].append(child)

        # Find the most common tag (likely the record tag)
        if tag_groups:
            most_common_tag = max(tag_groups.keys(), key=lambda k: len(tag_groups[k]))

            # Extract records from the most common tag
            for element in tag_groups[most_common_tag]:
                record = self._element_to_dict(element)
                if record:
                    records.append(record)

        return records

    def _element_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """
        Convert an XML element to a dictionary

        Args:
            element: XML element

        Returns:
            Dictionary representation of the element
        """
        result = {}

        # Add attributes
        if element.attrib:
            result.update({f'@{k}': v for k, v in element.attrib.items()})

        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            else:
                result['#text'] = element.text.strip()

        # Add child elements
        children = list(element)
        if children:
            for child in children:
                child_data = self._element_to_dict(child)
                if child.tag in result:
                    # Handle multiple children with same tag
                    if not isinstance(result[child.tag], list):
                        result[child.tag] = [result[child.tag]]
                    result[child.tag].append(child_data)
                else:
                    result[child.tag] = child_data

        return result
