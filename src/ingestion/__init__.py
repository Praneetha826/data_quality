"""
Data Ingestion Module
Handles loading and normalization of multiple data formats
"""

from .base_loader import BaseLoader, DataAsset
from .csv_loader import CSVLoader
from .excel_loader import ExcelLoader
from .json_loader import JSONLoader
from .xml_loader import XMLLoader
from .txt_loader import TXTLoader
from .pdf_loader import PDFLoader
from .loader_factory import LoaderFactory
from .normalizer import DataNormalizer

__all__ = [
    'BaseLoader',
    'DataAsset',
    'CSVLoader',
    'ExcelLoader',
    'JSONLoader',
    'XMLLoader',
    'TXTLoader',
    'PDFLoader',
    'LoaderFactory',
    'DataNormalizer'
]
