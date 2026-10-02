"""
Database Module
Handles PostgreSQL integration for persistent storage
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError


Base = declarative_base()


class DatasetRecord(Base):
    """
    Dataset record in database
    """
    __tablename__ = 'datasets'

    id = Column(Integer, primary_key=True)
    source_file = Column(String(500), nullable=False, unique=True)
    source_format = Column(String(50), nullable=False)
    data_category = Column(String(50), nullable=False)
    rows = Column(Integer)
    columns = Column(Integer)
    memory_usage = Column(Float)
    quality_score = Column(Float, nullable=False)
    completeness_score = Column(Float)
    consistency_score = Column(Float)
    validity_score = Column(Float)
    overall_assessment = Column(Text)
    metadata_json = Column(Text)  # Store full metadata as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    quality_issues = relationship("QualityIssueRecord", back_populates="dataset", cascade="all, delete-orphan")
    rag_queries = relationship("RAGQueryRecord", back_populates="dataset", cascade="all, delete-orphan")


class QualityIssueRecord(Base):
    """
    Quality issue record in database
    """
    __tablename__ = 'quality_issues'

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    issue_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    column_name = Column(String(100))  # Stores location (column name, row index, or general)
    row_indices = Column(Text)  # JSON array, stores count as single-element array
    metadata_json = Column(Text)  # Additional issue metadata as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("DatasetRecord", back_populates="quality_issues")


class RAGQueryRecord(Base):
    """
    RAG query history record in database
    """
    __tablename__ = 'rag_queries'

    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey('datasets.id'), nullable=False)
    user_query = Column(Text, nullable=False)
    retrieved_context = Column(Text)  # JSON string of retrieved documents
    explanation = Column(Text)
    recommendations = Column(Text)  # JSON array of recommendations
    quality_assessment = Column(Text)
    used_llm = Column(Boolean, default=False)
    model_name = Column(String(200), default="rule-based")  # Track which model generated the response
    sources = Column(Text)  # JSON array of sources
    response_json = Column(Text)  # Full response as JSON
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    dataset = relationship("DatasetRecord", back_populates="rag_queries")


class DatabaseManager:
    """
    Database manager for PostgreSQL operations
    """

    def __init__(self, connection_string: str):
        """
        Initialize database manager

        Args:
            connection_string: PostgreSQL connection string
                Format: postgresql://user:password@host:port/database
        """
        self.connection_string = connection_string
        self.engine = None
        self.Session = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize database engine and session"""
        try:
            self.engine = create_engine(self.connection_string, echo=False)
            self.Session = sessionmaker(bind=self.engine)
            print(f"Database engine initialized successfully")
        except Exception as e:
            print(f"Error initializing database engine: {e}")
            raise

    def create_tables(self):
        """Create all tables in database"""
        try:
            Base.metadata.create_all(self.engine)
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            raise

    def drop_tables(self):
        """Drop all tables from database"""
        try:
            Base.metadata.drop_all(self.engine)
            print("Database tables dropped successfully")
        except Exception as e:
            print(f"Error dropping tables: {e}")
            raise

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def save_dataset(self, metadata: Dict[str, Any], quality_report: Dict[str, Any]) -> Optional[int]:
        """
        Save dataset metadata and quality report to database

        Args:
            metadata: Dataset metadata dictionary
            quality_report: Quality report dictionary

        Returns:
            Dataset ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            # Check if dataset already exists
            existing = session.query(DatasetRecord).filter_by(source_file=metadata['source_file']).first()

            if existing:
                # Update existing record
                existing.source_format = metadata['source_format']
                existing.data_category = metadata['data_category']
                existing.rows = metadata.get('rows')
                existing.columns = metadata.get('columns')
                existing.memory_usage = metadata.get('memory_usage_mb')
                existing.quality_score = quality_report['quality_score']
                existing.completeness_score = quality_report['completeness_score']
                existing.consistency_score = quality_report['consistency_score']
                existing.validity_score = quality_report['validity_score']
                existing.overall_assessment = quality_report['assessment']
                existing.metadata_json = json.dumps(metadata)
                existing.updated_at = datetime.utcnow()

                # Delete old quality issues
                session.query(QualityIssueRecord).filter_by(dataset_id=existing.id).delete()

                dataset_id = existing.id
            else:
                # Create new record
                dataset = DatasetRecord(
                    source_file=metadata['source_file'],
                    source_format=metadata['source_format'],
                    data_category=metadata['data_category'],
                    rows=metadata.get('rows'),
                    columns=metadata.get('columns'),
                    memory_usage=metadata.get('memory_usage_mb'),
                    quality_score=quality_report['quality_score'],
                    completeness_score=quality_report['completeness_score'],
                    consistency_score=quality_report['consistency_score'],
                    validity_score=quality_report['validity_score'],
                    overall_assessment=quality_report['assessment'],
                    metadata_json=json.dumps(metadata)
                )
                session.add(dataset)
                session.flush()
                dataset_id = dataset.id

            # Save quality issues
            for issue in quality_report['issues']:
                issue_record = QualityIssueRecord(
                    dataset_id=dataset_id,
                    issue_type=issue['issue_type'],
                    severity=issue['severity'],
                    description=issue['description'],
                    column_name=issue.get('location'),
                    row_indices=json.dumps([issue.get('count', 1)]),
                    metadata_json=json.dumps(issue)
                )
                session.add(issue_record)

            session.commit()
            print(f"Dataset saved successfully (ID: {dataset_id})")
            return dataset_id

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error saving dataset: {e}")
            return None
        finally:
            session.close()

    def get_dataset(self, source_file: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve dataset metadata from database

        Args:
            source_file: Source file path

        Returns:
            Dataset metadata dictionary if found, None otherwise
        """
        session = self.get_session()
        try:
            dataset = session.query(DatasetRecord).filter_by(source_file=source_file).first()

            if dataset:
                # Get quality issues
                issues = []
                for issue in dataset.quality_issues:
                    # Parse count from row_indices JSON array
                    count = 1
                    if issue.row_indices:
                        try:
                            count_list = json.loads(issue.row_indices)
                            if count_list and len(count_list) > 0:
                                count = count_list[0]
                        except:
                            pass

                    issue_dict = {
                        'issue_type': issue.issue_type,
                        'severity': issue.severity,
                        'description': issue.description,
                        'location': issue.column_name,  # column_name field stores location
                        'count': count
                    }
                    issues.append(issue_dict)

                # Build metadata dictionary
                metadata = json.loads(dataset.metadata_json)
                metadata['quality_score'] = dataset.quality_score
                metadata['completeness_score'] = dataset.completeness_score
                metadata['consistency_score'] = dataset.consistency_score
                metadata['validity_score'] = dataset.validity_score
                metadata['quality_issues'] = issues

                return metadata

            return None

        except SQLAlchemyError as e:
            print(f"Error retrieving dataset: {e}")
            return None
        finally:
            session.close()

    def save_rag_query(self, source_file: str, rag_response: Dict[str, Any]) -> Optional[int]:
        """
        Save RAG query and response to database

        Args:
            source_file: Source file path
            rag_response: RAG response dictionary

        Returns:
            Query ID if successful, None otherwise
        """
        session = self.get_session()
        try:
            # Get dataset
            dataset = session.query(DatasetRecord).filter_by(source_file=source_file).first()

            if not dataset:
                print(f"Dataset not found: {source_file}")
                return None

            # Create query record
            query_record = RAGQueryRecord(
                dataset_id=dataset.id,
                user_query=rag_response['query'],
                retrieved_context=json.dumps(rag_response.get('context', {})),
                explanation=rag_response['explanation'],
                recommendations=json.dumps(rag_response['recommendations']),
                quality_assessment=rag_response['quality_assessment'],
                used_llm=rag_response.get('used_llm', False),
                model_name=rag_response.get('model_name', 'rule-based'),
                sources=json.dumps(rag_response.get('sources', [])),
                response_json=json.dumps(rag_response)
            )

            session.add(query_record)
            session.commit()

            print(f"RAG query saved successfully (ID: {query_record.id})")
            return query_record.id

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error saving RAG query: {e}")
            return None
        finally:
            session.close()

    def get_rag_query_history(self, source_file: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve RAG query history for a dataset

        Args:
            source_file: Source file path
            limit: Maximum number of queries to retrieve

        Returns:
            List of RAG query dictionaries
        """
        session = self.get_session()
        try:
            dataset = session.query(DatasetRecord).filter_by(source_file=source_file).first()

            if not dataset:
                return []

            queries = session.query(RAGQueryRecord).filter_by(
                dataset_id=dataset.id
            ).order_by(RAGQueryRecord.created_at.desc()).limit(limit).all()

            query_list = []
            for query in queries:
                query_dict = {
                    'id': query.id,
                    'user_query': query.user_query,
                    'explanation': query.explanation,
                    'recommendations': json.loads(query.recommendations) if query.recommendations else [],
                    'quality_assessment': query.quality_assessment,
                    'used_llm': query.used_llm,
                    'sources': json.loads(query.sources) if query.sources else [],
                    'created_at': query.created_at.isoformat()
                }
                query_list.append(query_dict)

            return query_list

        except SQLAlchemyError as e:
            print(f"Error retrieving RAG query history: {e}")
            return []
        finally:
            session.close()

    def list_datasets(self) -> List[Dict[str, Any]]:
        """
        List all datasets in database

        Returns:
            List of dataset summary dictionaries
        """
        session = self.get_session()
        try:
            datasets = session.query(DatasetRecord).order_by(DatasetRecord.created_at.desc()).all()

            dataset_list = []
            for dataset in datasets:
                dataset_dict = {
                    'id': dataset.id,
                    'source_file': dataset.source_file,
                    'source_format': dataset.source_format,
                    'data_category': dataset.data_category,
                    'rows': dataset.rows,
                    'columns': dataset.columns,
                    'quality_score': dataset.quality_score,
                    'overall_assessment': dataset.overall_assessment,
                    'created_at': dataset.created_at.isoformat(),
                    'updated_at': dataset.updated_at.isoformat()
                }
                dataset_list.append(dataset_dict)

            return dataset_list

        except SQLAlchemyError as e:
            print(f"Error listing datasets: {e}")
            return []
        finally:
            session.close()

    def delete_dataset(self, source_file: str) -> bool:
        """
        Delete a dataset and all related records from database

        Args:
            source_file: Source file path

        Returns:
            True if successful, False otherwise
        """
        session = self.get_session()
        try:
            dataset = session.query(DatasetRecord).filter_by(source_file=source_file).first()

            if dataset:
                session.delete(dataset)
                session.commit()
                print(f"Dataset deleted successfully: {source_file}")
                return True

            print(f"Dataset not found: {source_file}")
            return False

        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting dataset: {e}")
            return False
        finally:
            session.close()

    def test_connection(self) -> bool:
        """
        Test database connection

        Returns:
            True if connection successful, False otherwise
        """
        session = self.get_session()
        try:
            session.execute(text("SELECT 1"))
            print("Database connection test successful")
            return True
        except Exception as e:
            print(f"Database connection test failed: {e}")
            return False
        finally:
            session.close()
