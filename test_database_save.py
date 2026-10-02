"""
Test database save and retrieve functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator
from src.database import DatabaseManager

# Load customers.csv
print("Loading customers.csv...")
asset = LoaderFactory.load_file("enterprise_data_lake_sample/customers.csv")
normalized = DataNormalizer.normalize(asset)

# Quality assessment
print("Running quality assessment...")
metrics = QualityMetrics()
quality_report = metrics.assess_quality(normalized)

# Metadata generation
print("Generating metadata...")
metadata_gen = MetadataGenerator()
metadata = metadata_gen.generate_metadata(normalized, quality_report)

# Database operations
print("Initializing database...")
db_manager = DatabaseManager("sqlite:///test_customers.db")
db_manager.create_tables()

# Save dataset
print("Saving dataset to database...")
metadata_dict = {
    'source_file': metadata.source_file,
    'source_format': metadata.source_format,
    'data_category': metadata.data_category,
    'rows': int(metadata.total_rows),
    'columns': int(metadata.total_columns),
    'memory_usage_mb': float(metadata.memory_usage_mb),
    'timestamp': metadata.timestamp
}

quality_dict = {
    'quality_score': float(quality_report.quality_score),
    'completeness_score': float(quality_report.completeness_score),
    'consistency_score': float(quality_report.consistency_score),
    'validity_score': float(quality_report.validity_score),
    'assessment': quality_report.overall_assessment,
    'issues': [
        {
            'issue_type': issue.issue_type,
            'severity': issue.severity.value,
            'description': issue.description,
            'location': issue.location,
            'count': int(issue.count)
        }
        for issue in quality_report.issues
    ]
}

dataset_id = db_manager.save_dataset(metadata_dict, quality_dict)
print(f"Dataset saved with ID: {dataset_id}")

# Retrieve dataset
print("Retrieving dataset from database...")
retrieved = db_manager.get_dataset(metadata.source_file)
print(f"Retrieved dataset: {retrieved}")

print("\nDatabase save/retrieve test completed successfully!")
