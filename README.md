# Retrieval-Augmented Data Quality Assessment for Enterprise Data Lakes using Large Language Models

## Project Objective

Build an AI-powered data quality assessment system that combines traditional data profiling with Retrieval-Augmented Generation (RAG) to provide intelligent, context-aware explanations of data quality issues and actionable correction recommendations.

## Architecture Overview

The system follows a modular pipeline architecture with support for three categories of enterprise data:

```
Data Source (Structured/Semi-structured/Unstructured)
→ Format-Specific Ingestion (CSV/Excel/JSON/XML/TXT/PDF)
→ Common Normalization Layer
→ Preprocessing
→ Data Profiling
→ Quality Metrics
→ Metadata Generation
→ Text Chunking
→ Embeddings
→ FAISS Vector Store
→ Retriever
→ RAG Pipeline
→ Llama 3
→ Explanation + Recommendations
→ Quality Report
```

### Data Categories Supported

1. **Structured Data**:
   - CSV (Completed - Milestone 1)
   - Excel (Milestone 2)
   - Relational/tabular data

2. **Semi-structured Data**:
   - JSON (Milestone 3)
   - XML (Milestone 3)

3. **Unstructured Data**:
   - TXT (Milestone 4)
   - PDF (Milestone 4)
   - Other text-based documents

### Key Components

1. **Format-Specific Ingestion**: Separate loaders for each data format (CSV, Excel, JSON, XML, TXT, PDF)
2. **Common Normalization Layer**: Converts all formats into a unified internal representation
3. **Preprocessing**: Basic data cleaning and normalization
4. **Data Profiling**: Statistical analysis and schema validation
5. **Quality Metrics**: Detection of missing values, duplicates, outliers, type mismatches
6. **Metadata Generation**: Extracts dataset metadata and quality information
7. **Embeddings**: Converts metadata into vector representations
8. **FAISS Vector Store**: Stores embeddings for semantic search
9. **Retriever**: Performs semantic similarity search
10. **RAG Pipeline**: Orchestrates retrieval and LLM inference
11. **LLM Handler**: Integrates with Llama 3 for explanations
12. **Quality Scorer**: Calculates numerical quality scores
13. **Report Generator**: Creates comprehensive quality reports
14. **Database**: PostgreSQL for persistent storage of metadata and reports
15. **Streamlit Interface**: User-friendly web application

## Technology Stack

### Core Libraries
- **Python 3.10+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Scikit-learn**: Machine learning utilities

### Data Format Support
- **OpenPyXL**: Excel file processing
- **xlrd**: Excel file reading (legacy support)
- **json**: JSON processing (built-in)
- **xml.etree.ElementTree**: XML processing (built-in)
- **PyPDF2** or **pdfplumber**: PDF text extraction
- **python-docx**: Word document processing (optional)

### RAG & AI Components
- **Sentence Transformers**: Text embedding generation
- **FAISS**: Vector similarity search
- **LangChain**: RAG pipeline orchestration
- **Llama 3**: Large Language Model for explanations

### Storage & Interface
- **PostgreSQL**: Structured data storage
- **Streamlit**: Web interface

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip package manager
- PostgreSQL (for later milestones)

### Installation

1. Clone or navigate to the project directory:
```bash
cd C:\Users\FALCON JNP\Data_quality
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root with the following variables (for later milestones):

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=data_quality
DB_USER=your_username
DB_PASSWORD=your_password

# LLM Configuration (for later milestones)
LLM_API_KEY=your_api_key
LLM_MODEL=llama3
```

## How to Run the Project

### Run the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Dashboard navigation

The dashboard groups the workflow into **Overview**, **Quality details**, **AI assistant**, and **Dataset library** in the left navigation. Upload CSV, Excel, JSON, XML, TXT, or PDF files from the assessment panel, or load a sample dataset. The Overview summarizes quality scores and saved assessment history; detailed issue and metadata views, semantic retrieval and RAG recommendations, and saved dataset records are available in their corresponding sections. Database and language-model settings remain in the sidebar.

### Run Tests

```bash
python -m pytest tests/
```

Or run individual test files:
```bash
python tests/test_milestone1.py
```

## Project Structure

```
data_quality_assessment/
├── data/                           # Dataset storage
│   ├── input/                      # User-uploaded datasets
│   └── sample/                     # Sample datasets for testing
│       ├── sample_dataset.csv      # CSV sample (Milestone 1)
│       ├── sample_dataset.xlsx     # Excel sample (Milestone 2)
│       ├── sample_dataset.json     # JSON sample (Milestone 3)
│       ├── sample_dataset.xml      # XML sample (Milestone 3)
│       ├── sample_document.txt     # TXT sample (Milestone 4)
│       └── sample_document.pdf     # PDF sample (Milestone 4)
├── src/                            # Source code
│   ├── __init__.py
│   ├── ingestion/                  # Data ingestion module
│   │   ├── __init__.py
│   │   ├── base_loader.py          # Abstract base loader
│   │   ├── csv_loader.py           # CSV format loader (Milestone 1)
│   │   ├── excel_loader.py        # Excel format loader (Milestone 2)
│   │   ├── json_loader.py         # JSON format loader (Milestone 3)
│   │   ├── xml_loader.py          # XML format loader (Milestone 3)
│   │   ├── txt_loader.py          # TXT format loader (Milestone 4)
│   │   ├── pdf_loader.py          # PDF format loader (Milestone 4)
│   │   └── normalizer.py          # Common normalization layer
│   ├── preprocessing.py            # Data cleaning & normalization
│   ├── profiling.py                # Data profiling & statistics
│   ├── quality_metrics.py          # Quality issue detection
│   ├── metadata_generator.py       # Metadata extraction
│   ├── embeddings.py               # Text chunking & embedding generation
│   ├── vector_store.py             # FAISS operations
│   ├── retriever.py                # Semantic search
│   ├── rag_pipeline.py             # RAG orchestration
│   ├── llm_handler.py              # Llama 3 integration
│   ├── quality_scorer.py           # Score calculation
│   ├── report_generator.py         # Report generation
│   └── database.py                 # PostgreSQL operations
├── models/                         # Saved models (FAISS indices, etc.)
├── config/                         # Configuration files
│   └── config.yaml
├── tests/                          # Unit tests
│   ├── test_milestone1.py         # Milestone 1 tests
│   ├── test_milestone2.py         # Milestone 2 tests
│   ├── test_milestone3.py         # Milestone 3 tests
│   └── test_milestone4.py         # Milestone 4 tests
├── app.py                          # Streamlit web interface
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── README.md                       # Project documentation
└── .env.example                    # Environment variables template
```

## Implementation Milestones

### Phase 1: Data Ingestion Foundation

**Milestone 1**: Structured CSV Foundation ✅ Completed
- CSV data ingestion
- Basic data profiling
- Streamlit interface for dataset upload and visualization
- Common normalization layer foundation

**Milestone 2**: Structured Data Extension (Excel)
- Excel format loader (.xlsx, .xls)
- Improved common ingestion interface
- Enhanced normalization layer for structured data
- Testing with Excel samples
- Updated Streamlit interface for Excel support

**Milestone 3**: Semi-structured Data Support (JSON & XML)
- JSON format loader
- XML format loader
- Extended normalization layer for semi-structured data
- Schema inference for JSON/XML
- Testing with JSON/XML samples
- Updated Streamlit interface for JSON/XML support

**Milestone 4**: Unstructured Data Support (TXT & PDF)
- TXT format loader
- PDF format loader with text extraction
- Text preprocessing for unstructured data
- Extended normalization layer for unstructured data
- Testing with TXT/PDF samples
- Updated Streamlit interface for TXT/PDF support

### Phase 2: Quality Assessment Pipeline

**Milestone 5**: Quality Metrics Detection
- Missing value detection
- Duplicate detection
- Outlier detection using statistical methods
- Data-type/schema validation
- Format-specific quality checks
- Quality metrics calculation

**Milestone 6**: Metadata Generation & Embeddings
- Metadata extraction for all data formats
- Text chunking strategies
- Embedding generation using Sentence Transformers
- FAISS vector store setup
- Semantic search testing

**Milestone 7**: RAG Pipeline with LLM
- RAG pipeline orchestration
- Llama 3 integration
- Context-aware explanation generation
- Correction recommendations
- Prompt engineering for quality explanations

**Milestone 8**: Quality Scoring & Reporting
- Numerical quality score calculation
- Comprehensive quality report generation
- Format-specific reporting
- Visual quality dashboards

### Phase 3: Storage & Interface

**Milestone 9**: Database Integration
- PostgreSQL schema design
- Metadata storage
- Quality metrics persistence
- Report storage and retrieval
- Database connection management

**Milestone 10**: Enhanced Streamlit Interface
- Multi-format upload support
- Unified quality assessment workflow
- Interactive quality dashboards
- Report generation and download
- User management (optional)

## Current Status

**Milestone 1**: ✅ Completed
- CSV data ingestion
- Basic data profiling
- Streamlit interface for dataset upload and visualization
- Foundation for multi-format support

**Milestone 2**: ✅ Completed
- Complete data ingestion layer for all six formats
- Structured data: CSV, Excel (.xlsx, .xls)
- Semi-structured data: JSON, XML
- Unstructured data: TXT, PDF
- Common DataAsset representation
- Format-agnostic architecture
- Enhanced Streamlit interface with multi-format support
- Full backward compatibility with Milestone 1

**Milestone 3**: ✅ Completed
- Comprehensive quality metrics detection
- Quality scoring system (0-100 scale)
- Issue detection with severity levels (CRITICAL, HIGH, MEDIUM, LOW, INFO)
- Format-specific quality checks (tabular and text data)
- Component scoring (completeness, consistency, validity)
- Enhanced Streamlit interface with quality assessment display
- Full backward compatibility with Milestones 1 and 2

**Milestone 4**: ✅ Completed
- Comprehensive metadata generation
- Textual metadata for embedding
- Embedding generation using Sentence Transformers (all-MiniLM-L6-v2)
- FAISS vector store implementation
- Semantic similarity search
- Vector store persistence
- Enhanced Streamlit interface with metadata, embeddings, and vector store features
- Full backward compatibility with Milestones 1, 2, and 3

**Milestone 5**: ✅ Completed
- RAG pipeline implementation (rule-based explanations)
- Context retrieval from vector store
- Prompt construction for LLM (ready for future integration)
- Rule-based response generation with quality-aware explanations
- Actionable recommendations based on detected issues
- Quality assessment with score-based categorization
- Enhanced Streamlit interface with RAG query and explanation features
- Full backward compatibility with Milestones 1, 2, 3, and 4

**Next**: Milestone 6 - PostgreSQL Integration

## Academic Project Notes

This project is designed as a B.Tech final-year academic project with emphasis on:
- **Correctness**: Deterministic quality calculations using Python/Pandas
- **Explainability**: RAG provides context-aware explanations
- **Reproducibility**: Modular, well-documented code
- **Simplicity**: Clean architecture, no over-engineering
- **Demonstration**: Easy to explain and demonstrate during viva

## License

This is an academic project for educational purposes.
