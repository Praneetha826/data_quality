# Updated Development Plan - Multi-Format Data Quality Assessment

## Executive Summary

The development plan has been updated to support three categories of enterprise data while maintaining the existing CSV foundation. The architecture now includes a common normalization layer that allows downstream components to work consistently with different data formats.

## Revised Architecture

### Final Architecture Flow

```
Data Source (Structured/Semi-structured/Unstructured)
↓
Format-Specific Ingestion
├── CSV Loader (Milestone 1 - Completed)
├── Excel Loader (Milestone 2)
├── JSON Loader (Milestone 3)
├── XML Loader (Milestone 3)
├── TXT Loader (Milestone 4)
└── PDF Loader (Milestone 4)
↓
Common Normalization Layer
↓
Preprocessing
↓
Data Profiling
↓
Quality Metrics
↓
Metadata Generation
↓
Text Chunking
↓
Embeddings
↓
FAISS Vector Store
↓
Retriever
↓
RAG Pipeline
↓
Llama 3
↓
Explanation + Recommendations
↓
Quality Report
```

### Key Architectural Principles

1. **Format-Specific Loaders**: Each data format has its own parser/loader
2. **Common Normalization Layer**: All formats normalized into unified internal representation
3. **Format-Agnostic Downstream**: Quality assessment pipeline doesn't depend on specific formats
4. **Modular Design**: Each format can be developed and tested independently
5. **Backward Compatibility**: Existing CSV functionality remains intact

## Data Categories and Implementation Sequence

### Category 1: Structured Data

**Formats**: CSV, Excel, Relational/tabular data

**Implementation Sequence**:
- Milestone 1: CSV foundation (Completed)
- Milestone 2: Excel support

**Characteristics**:
- Well-defined schema
- Tabular structure
- Strong typing
- Easy to normalize

### Category 2: Semi-structured Data

**Formats**: JSON, XML

**Implementation Sequence**:
- Milestone 3: JSON and XML support

**Characteristics**:
- Flexible schema
- Nested structures
- Self-describing
- Requires schema inference

### Category 3: Unstructured Data

**Formats**: TXT, PDF, other text-based documents

**Implementation Sequence**:
- Milestone 4: TXT and PDF support

**Characteristics**:
- No predefined schema
- Free-form text
- Requires text extraction
- Needs preprocessing for analysis

## Updated Implementation Milestones

### Phase 1: Data Ingestion Foundation (Milestones 1-4)

#### Milestone 1: Structured CSV Foundation ✅ COMPLETED

**Status**: Complete and tested

**Implemented**:
- CSV data ingestion with validation
- Basic data profiling
- Streamlit interface for CSV upload
- Foundation for common normalization layer

**Files Created**:
- `src/data_ingestion.py` (to be refactored into `src/ingestion/csv_loader.py`)
- `src/profiling.py`
- `tests/test_milestone1.py`
- `app.py`

**Achievements**:
- All tests passed
- Working Streamlit interface
- Sample dataset with quality issues
- Documentation complete

#### Milestone 2: Structured Data Extension (Excel)

**Goal**: Add Excel format support while improving the common ingestion interface

**Components to Implement**:
- `src/ingestion/base_loader.py` - Abstract base class for all loaders
- `src/ingestion/csv_loader.py` - Refactor existing CSV loader
- `src/ingestion/excel_loader.py` - New Excel loader
- `src/ingestion/normalizer.py` - Common normalization layer
- `data/sample/sample_dataset.xlsx` - Excel sample with quality issues
- `tests/test_milestone2.py` - Excel loader tests
- Update `app.py` for Excel support

**Key Features**:
- Support for .xlsx and .xls formats
- Multi-sheet handling
- Data type preservation
- Error handling for corrupted Excel files
- Unified interface with CSV loader

**Testing Requirements**:
- Load valid Excel files
- Handle multi-sheet workbooks
- Validate data types
- Test error cases (corrupted files, invalid formats)
- Verify normalization consistency with CSV

**Deliverable**: Working Excel upload with same profiling capabilities as CSV

#### Milestone 3: Semi-structured Data Support (JSON & XML)

**Goal**: Add JSON and XML format support with schema inference

**Components to Implement**:
- `src/ingestion/json_loader.py` - JSON format loader
- `src/ingestion/xml_loader.py` - XML format loader
- Extended `src/ingestion/normalizer.py` for semi-structured data
- `data/sample/sample_dataset.json` - JSON sample
- `data/sample/sample_dataset.xml` - XML sample
- `tests/test_milestone3.py` - JSON/XML loader tests
- Update `app.py` for JSON/XML support

**Key Features**:
- JSON parsing with nested structure handling
- XML parsing with namespace support
- Schema inference from data
- Flattening of nested structures
- Data type detection from JSON/XML
- Error handling for malformed data

**Testing Requirements**:
- Load valid JSON/XML files
- Handle nested structures
- Infer schema correctly
- Test error cases (malformed JSON/XML)
- Verify normalization produces tabular format

**Deliverable**: Working JSON/XML upload with profiling capabilities

#### Milestone 4: Unstructured Data Support (TXT & PDF)

**Goal**: Add TXT and PDF format support with text extraction

**Components to Implement**:
- `src/ingestion/txt_loader.py` - TXT format loader
- `src/ingestion/pdf_loader.py` - PDF format loader with text extraction
- Extended `src/ingestion/normalizer.py` for unstructured data
- `data/sample/sample_document.txt` - TXT sample
- `data/sample/sample_document.pdf` - PDF sample
- `tests/test_milestone4.py` - TXT/PDF loader tests
- Update `app.py` for TXT/PDF support

**Key Features**:
- TXT file loading with encoding detection
- PDF text extraction using PyPDF2/pdfplumber
- Text preprocessing (tokenization, cleaning)
- Basic text statistics (word count, sentence count)
- Error handling for corrupted/unreadable files
- Encoding handling for international text

**Testing Requirements**:
- Load valid TXT files with various encodings
- Extract text from PDF files
- Handle different PDF formats
- Test error cases (corrupted PDFs, encoding issues)
- Verify text quality metrics

**Deliverable**: Working TXT/PDF upload with basic text profiling

### Phase 2: Quality Assessment Pipeline (Milestones 5-8)

#### Milestone 5: Quality Metrics Detection

**Goal**: Implement comprehensive quality metrics for all supported formats

**Components to Implement**:
- `src/quality_metrics.py` - Quality metrics detection
- Format-specific quality checks
- Statistical outlier detection
- Duplicate detection algorithms
- Schema validation
- `tests/test_milestone5.py` - Quality metrics tests

**Key Features**:
- Missing value analysis
- Duplicate detection (exact and fuzzy)
- Outlier detection (IQR, Z-score)
- Data type validation
- Format-specific checks
- Quality severity levels

#### Milestone 6: Metadata Generation & Embeddings

**Goal**: Generate metadata and create embeddings for RAG

**Components to Implement**:
- `src/metadata_generator.py` - Metadata extraction
- `src/embeddings.py` - Text chunking and embedding generation
- `src/vector_store.py` - FAISS operations
- `tests/test_milestone6.py` - Metadata and embeddings tests

**Key Features**:
- Dataset metadata extraction
- Quality issue metadata
- Text chunking strategies
- Embedding generation with Sentence Transformers
- FAISS index creation and management
- Semantic search testing

#### Milestone 7: RAG Pipeline with LLM

**Goal**: Implement RAG pipeline for context-aware explanations

**Components to Implement**:
- `src/retriever.py` - Semantic search
- `src/rag_pipeline.py` - RAG orchestration
- `src/llm_handler.py` - Llama 3 integration
- `tests/test_milestone7.py` - RAG pipeline tests

**Key Features**:
- Query embedding
- FAISS similarity search
- Context retrieval
- Prompt construction
- LLM integration (Llama 3)
- Explanation generation
- Correction recommendations

#### Milestone 8: Quality Scoring & Reporting

**Goal**: Calculate quality scores and generate comprehensive reports

**Components to Implement**:
- `src/quality_scorer.py` - Score calculation
- `src/report_generator.py` - Report generation
- `tests/test_milestone8.py` - Scoring and reporting tests

**Key Features**:
- Numerical quality score calculation
- Weighted quality metrics
- Format-specific scoring
- Comprehensive report generation
- Visual quality dashboards
- Exportable reports

### Phase 3: Storage & Interface (Milestones 9-10)

#### Milestone 9: Database Integration

**Goal**: Implement PostgreSQL for persistent storage

**Components to Implement**:
- `src/database.py` - PostgreSQL operations
- Database schema design
- `tests/test_milestone9.py` - Database tests

**Key Features**:
- Database connection management
- Schema creation and migration
- Metadata storage
- Quality metrics persistence
- Report storage and retrieval
- Query optimization

#### Milestone 10: Enhanced Streamlit Interface

**Goal**: Complete web interface with multi-format support

**Components to Implement**:
- Enhanced `app.py` with full functionality
- Multi-format upload support
- Unified quality assessment workflow
- Interactive quality dashboards
- Report generation and download
- User management (optional)

**Key Features**:
- Unified upload interface for all formats
- Real-time quality assessment
- Interactive visualizations
- Downloadable reports
- User preferences
- Session management

## Common Normalization Layer Design

### Purpose

The common normalization layer converts all data formats into a unified internal representation that downstream components can work with consistently.

### Internal Representation

All formats will be normalized into a common structure:

```python
{
    'data': pd.DataFrame,  # Normalized tabular data
    'metadata': {
        'source_format': str,        # Original format (csv, excel, json, etc.)
        'source_file': str,          # Original filename
        'schema': dict,              # Inferred or detected schema
        'encoding': str,              # Text encoding (if applicable)
        'structure': str,            # Data structure type (structured, semi-structured, unstructured)
        'extraction_metadata': dict   # Format-specific extraction metadata
    },
    'quality_info': {
        'extraction_errors': list,   # Errors during extraction
        'warnings': list,            # Warnings during extraction
        'completeness': float        # Data completeness score
    }
}
```

### Normalization Strategies

#### Structured Data (CSV, Excel)
- Direct conversion to DataFrame
- Type inference and validation
- Schema preservation
- Header detection

#### Semi-structured Data (JSON, XML)
- Flattening of nested structures
- Schema inference
- Type detection from values
- Array handling

#### Unstructured Data (TXT, PDF)
- Text extraction
- Tokenization
- Basic text statistics
- Structure inference (paragraphs, sections)

## Backward Compatibility

The existing CSV functionality will be preserved during refactoring:

1. **Current CSV Implementation**: Will be refactored into `src/ingestion/csv_loader.py`
2. **Interface Compatibility**: Existing API will be maintained where possible
3. **Test Preservation**: All existing tests will continue to pass
4. **Streamlit Interface**: Will be enhanced, not replaced

## Implementation Guidelines

### Do NOT Break Existing Functionality
- All Milestone 1 tests must continue to pass
- CSV loading must work exactly as before
- Profiling results must remain consistent

### Modular Development
- Each format loader developed independently
- Each milestone tested before proceeding
- Clear separation between format-specific and common code

### Beginner-Friendly Code
- Clear documentation for each component
- Simple, straightforward implementations
- Avoid over-engineering
- Focus on academic demonstration value

### Testing Strategy
- Each milestone has dedicated test file
- Sample datasets for each format
- Error case testing
- Integration testing with normalization layer

## Dependencies by Milestone

### Milestone 2 (Excel)
- `openpyxl>=3.1.0` (already in requirements.txt)
- `xlrd>=2.0.1` (already in requirements.txt)

### Milestone 3 (JSON/XML)
- Built-in `json` module
- Built-in `xml.etree.ElementTree`
- No additional dependencies

### Milestone 4 (TXT/PDF)
- `PyPDF2>=3.0.0` (already in requirements.txt)
- `pdfplumber>=0.9.0` (already in requirements.txt)
- Built-in file handling

### Milestones 5-10
- Dependencies already in requirements.txt
- Will be installed when needed

## Next Steps

**Current Status**: Milestone 1 complete and tested

**Recommended Next Action**: Implement Milestone 2 (Excel support)

**Milestone 2 Scope**:
1. Refactor existing CSV code into modular structure
2. Implement Excel loader
3. Create common normalization layer
4. Update Streamlit interface
5. Create Excel sample dataset
6. Write comprehensive tests
7. Verify backward compatibility

**Approval Required**: Please confirm approval to proceed with Milestone 2 implementation.

## Summary of Changes

### Architecture Changes
- Added format-specific ingestion layer
- Introduced common normalization layer
- Extended pipeline to support 3 data categories
- Maintained format-agnostic downstream components

### Milestone Changes
- Expanded from 8 to 10 milestones
- Reorganized into 3 phases
- Milestones 1-4: Data ingestion foundation
- Milestones 5-8: Quality assessment pipeline
- Milestones 9-10: Storage and interface

### Implementation Sequence
- Structured data first (CSV → Excel)
- Semi-structured data second (JSON → XML)
- Unstructured data third (TXT → PDF)
- Each format independently testable

### Code Structure Changes
- New `src/ingestion/` module
- Separate loader files for each format
- Common normalization layer
- Enhanced modularity

This updated plan provides a clear path to support all three categories of enterprise data while maintaining the solid CSV foundation established in Milestone 1.
