"""
Data Quality Assessment System
Retrieval-Augmented Data Quality Assessment for Enterprise Data Lakes using Large Language Models
"""

__version__ = "1.0.0"
__author__ = "B.Tech Final Year Student"

# Export key modules
from .ingestion import (
    BaseLoader, DataAsset, CSVLoader, ExcelLoader, JSONLoader,
    XMLLoader, TXTLoader, PDFLoader, LoaderFactory, DataNormalizer
)
from .profiling import DataProfiler
from .quality_metrics import QualityMetrics, QualityReport, QualityIssue, QualitySeverity
from .metadata_generator import MetadataGenerator, DatasetMetadata
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .rag_pipeline import RAGPipeline, RAGContext, RAGResponse
from .llm_client import LLMClient
from .database import DatabaseManager, DatasetRecord, QualityIssueRecord, RAGQueryRecord

__all__ = [
    # Ingestion
    'BaseLoader', 'DataAsset', 'CSVLoader', 'ExcelLoader', 'JSONLoader',
    'XMLLoader', 'TXTLoader', 'PDFLoader', 'LoaderFactory', 'DataNormalizer',
    # Profiling
    'DataProfiler',
    # Quality Metrics
    'QualityMetrics', 'QualityReport', 'QualityIssue', 'QualitySeverity',
    # Metadata & Embeddings
    'MetadataGenerator', 'DatasetMetadata',
    'EmbeddingGenerator',
    'VectorStore',
    # RAG Pipeline
    'RAGPipeline', 'RAGContext', 'RAGResponse',
    # LLM Client
    'LLMClient',
    # Database
    'DatabaseManager', 'DatasetRecord', 'QualityIssueRecord', 'RAGQueryRecord'
]
