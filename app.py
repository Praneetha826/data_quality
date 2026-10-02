"""
Streamlit Web Interface for Data Quality Assessment
RAG-Based Data Quality Assessment for Enterprise Data Lakes
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# CRITICAL: Remove GOOGLE_API_KEY BEFORE loading .env
# to prevent it from overriding GEMINI_API_KEY
if "GOOGLE_API_KEY" in os.environ:
    del os.environ["GOOGLE_API_KEY"]

# Load environment variables from .env file
load_dotenv(override=True)  # override=True ensures .env values take precedence

# Check DEBUG_MODE for verbose logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

if DEBUG_MODE:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        if DEBUG_MODE:
                print(f"DEBUG: GEMINI_API_KEY loaded (length={len(gemini_key)}, prefix={gemini_key[:10]}...)")
else:
    if DEBUG_MODE:
        print("DEBUG: GEMINI_API_KEY NOT loaded")

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion import LoaderFactory, DataNormalizer
from src.profiling import DataProfiler
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline
from src.llm_client import LLMClient
from src.database import DatabaseManager


# Custom CSS for professional styling
st.markdown("""
<style>
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
    }
    .status-dot {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-green { background-color: #4CAF50; }
    .status-red { background-color: #F44336; }
    .status-orange { background-color: #FF9800; }
    .card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 1rem;
        text-align: center;
    }
    .section-title {
        font-size: 1.4rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    .pipeline-step {
        background-color: #f0f4f8;
        border-left: 3px solid #3498db;
        padding: 0.75rem 1rem;
        margin: 0.25rem 0;
        border-radius: 4px;
    }
    .response-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .recommendation-item {
        background-color: #e8f5e9;
        border-left: 3px solid #4CAF50;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar(db_manager, llm_model):
    """Render compact professional sidebar"""
    
    with st.sidebar:
        st.markdown("### System Status")
        
        # Database status
        if db_manager:
            st.markdown('<span class="status-dot status-green"></span>Database Connected', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-dot status-red"></span>Database Not Available', unsafe_allow_html=True)
        
        # Vector store status
        vs_status = st.session_state.get('vector_store_status', 'Ready')
        vs_color = 'status-green' if vs_status == 'Ready' else 'status-red'
        st.markdown(f'<span class="status-dot {vs_color}"></span>Vector Store: {vs_status}', unsafe_allow_html=True)
        
        # LLM status
        model_display = llm_model.split('/')[-1] if '/' in llm_model else llm_model
        st.markdown(f'<span class="status-dot status-green"></span>LLM: {model_display}', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Configuration
        with st.expander("Configuration", expanded=False):
            st.markdown("#### Database")
            db_connection_string = st.text_input(
                "Connection String",
                value="sqlite:///data_quality.db",
                help="PostgreSQL: postgresql://user:password@host:port/database\nSQLite: sqlite:///database.db"
            )
            
            st.markdown("#### LLM Model")
            llm_model_input = st.text_input(
                "Model Name",
                value=llm_model,
                help="Available models:\n- gemini-3.5-flash (Gemini API)\n- meta-llama/Meta-Llama-3-8B-Instruct (local)\n- Qwen/Qwen2.5-3B-Instruct (local)"
            )
        
        # Advanced Settings
        with st.expander("Advanced Settings", expanded=False):
            st.markdown("#### System Configuration")
            st.info("Advanced configuration options for debugging and development.")
        
        return db_connection_string, llm_model_input


def render_header(db_manager, llm_model):
    """Render professional header with status indicators"""
    
    model_display = llm_model.split('/')[-1] if '/' in llm_model else llm_model
    
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <h1 style="font-size: 2rem; font-weight: 700; color: #2c3e50; margin-bottom: 0.5rem;">
            RAG-Based Data Quality Assessment
        </h1>
        <p style="font-size: 1rem; color: #7f8c8d; margin-bottom: 1rem;">
            Enterprise Data Lake Quality Analysis using Retrieval-Augmented Generation
        </p>
        <div style="display: flex; gap: 2rem; font-size: 0.9rem; color: #555;">
            <span><span class="status-dot status-green"></span>Database Connected</span>
            <span><span class="status-dot status-green"></span>FAISS Ready</span>
            <span><span class="status-dot status-green"></span>LLM: """ + model_display + """</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_section_header(number, title):
    """Render section header"""
    st.markdown(f'<div class="section-title">{number:02d} — {title}</div>', unsafe_allow_html=True)


def render_dataset_overview(normalized_asset):
    """Render compact dataset overview card"""
    
    file_size_mb = normalized_asset.metadata.get('file_size', 0) / (1024 * 1024)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Dataset Overview")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"**File:** {Path(normalized_asset.metadata.get('file_name', 'Unknown')).name}")
        st.markdown(f"**Format:** {normalized_asset.source_format}")
    with col2:
        st.markdown(f"**Category:** {normalized_asset.data_category}")
        st.markdown(f"**Size:** {file_size_mb:.2f} MB")
    with col3:
        if normalized_asset.is_tabular():
            st.markdown(f"**Rows:** {len(normalized_asset.tabular_data)}")
            st.markdown(f"**Columns:** {len(normalized_asset.tabular_data.columns)}")
        else:
            st.markdown(f"**Characters:** {len(normalized_asset.text_data)}")
            st.markdown(f"**Words:** {len(normalized_asset.text_data.split())}")
    
    st.markdown('<span class="status-dot status-green"></span>Status: Processed', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


def render_quality_scores(quality_report, is_tabular=True):
    """Render quality score cards"""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Quality Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "#4CAF50" if quality_report.quality_score >= 80 else "#FF9800" if quality_report.quality_score >= 60 else "#F44336"
        st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {score_color};">
            <div style="font-size: 2rem; font-weight: 700; color: {score_color};">{quality_report.quality_score:.0f}/100</div>
            <div style="font-size: 0.85rem; color: #666;">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    if is_tabular:
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600;">{quality_report.completeness_score:.0f}/100</div>
                <div style="font-size: 0.85rem; color: #666;">Completeness</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600;">{quality_report.consistency_score:.0f}/100</div>
                <div style="font-size: 0.85rem; color: #666;">Consistency</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600;">{quality_report.validity_score:.0f}/100</div>
                <div style="font-size: 0.85rem; color: #666;">Validity</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600; color: #999;">N/A</div>
                <div style="font-size: 0.85rem; color: #666;">Tabular Completeness</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600; color: #999;">N/A</div>
                <div style="font-size: 0.85rem; color: #666;">Tabular Consistency</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 1.5rem; font-weight: 600; color: #999;">N/A</div>
                <div style="font-size: 0.85rem; color: #666;">Tabular Validity</div>
            </div>
            """, unsafe_allow_html=True)
    
    issue_count = len(quality_report.issues)
    st.markdown(f"**Detected Issues:** {issue_count}")
    
    if not is_tabular:
        st.caption("Note: Tabular component scores are not applicable to unstructured text data.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_issues_table(quality_report):
    """Render detected issues in professional table"""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Detected Issues")
    
    if quality_report.issues:
        issues_data = []
        for issue in quality_report.issues:
            issues_data.append({
                "Type": issue.issue_type,
                "Severity": issue.severity.value.upper(),
                "Location": issue.location,
                "Description": issue.description
            })
        issues_df = pd.DataFrame(issues_data)
        st.dataframe(issues_df, use_container_width=True, hide_index=True)
    else:
        st.info("No quality issues detected under the current assessment rules.")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_metadata_grouped(metadata, quality_report, is_tabular=True):
    """Render metadata in grouped expandable cards"""

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Metadata")

    with st.expander("Dataset Information", expanded=False):
        st.markdown(f"**Source:** {metadata.source_file}")
        st.markdown(f"**Format:** {metadata.source_format}")
        st.markdown(f"**Category:** {metadata.data_category}")
        st.markdown(f"**Timestamp:** {metadata.timestamp}")

    if is_tabular:
        with st.expander("Structure", expanded=False):
            st.markdown(f"**Total Rows:** {metadata.total_rows}")
            st.markdown(f"**Total Columns:** {metadata.total_columns}")
            st.markdown(f"**Memory Usage:** {metadata.memory_usage_mb:.2f} MB")
    else:
        with st.expander("Text Information", expanded=False):
            st.markdown(f"**Character Count:** {metadata.character_count}")
            st.markdown(f"**Word Count:** {metadata.word_count}")
            st.markdown(f"**Line Count:** {metadata.line_count}")

    with st.expander("Quality Information", expanded=False):
        st.markdown(f"**Quality Score:** {metadata.quality_score:.1f}/100")
        if quality_report.component_scores_applicable:
            st.markdown(f"**Completeness:** {metadata.completeness_score:.1f}/100")
            st.markdown(f"**Consistency:** {metadata.consistency_score:.1f}/100")
            st.markdown(f"**Validity:** {metadata.validity_score:.1f}/100")
        else:
            st.markdown("**Completeness:** N/A (not applicable for unstructured data)")
            st.markdown("**Consistency:** N/A (not applicable for unstructured data)")
            st.markdown("**Validity:** N/A (not applicable for unstructured data)")

    with st.expander("File Information", expanded=False):
        st.markdown(f"**File Size:** {metadata.memory_usage_mb:.2f} MB")
        st.markdown(f"**Data Type:** {metadata.data_category}")

    st.markdown('</div>', unsafe_allow_html=True)


def render_semantic_retrieval(embed_gen, vector_store):
    """Render semantic retrieval section"""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Semantic Retrieval")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Embedding Model**")
        st.caption("all-MiniLM-L6-v2")
    with col2:
        st.markdown("**Embedding Dimension**")
        st.caption(f"{embed_gen.get_embedding_dimension()}")
    with col3:
        st.markdown("**Vector Store**")
        st.caption("FAISS ✓")
    
    # Debug: Show vector store size
    vs_size = vector_store.get_size()
    if DEBUG_MODE:
        st.caption(f"Debug: Vectors indexed: {vs_size}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_rag_pipeline_visualization(llm_client):
    """Render compact RAG pipeline visualization"""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### RAG Pipeline Flow")
    
    # Get actual model name
    if llm_client and llm_client.is_available():
        model_info = llm_client.get_model_info()
        actual_model = model_info.get("model_name", "LLM")
        # Display friendly name
        if "gemini" in actual_model.lower():
            model_display = actual_model.replace("-", " ").replace(".", " ").title()
        elif "/" in actual_model:
            model_display = actual_model.split("/")[-1]
        else:
            model_display = actual_model
    else:
        model_display = "LLM"
    
    steps = [
        "User Query",
        "FAISS Retrieval",
        "Retrieved Context",
        "RAG Prompt",
        model_display,
        "Explanation & Recommendations"
    ]
    
    for i, step in enumerate(steps):
        st.markdown(f'<div class="pipeline-step">{step}</div>', unsafe_allow_html=True)
        if i < len(steps) - 1:
            st.markdown('<div style="text-align: center; color: #999;">↓</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_rag_assistant(vector_store, embed_gen, metadata, db_manager, llm_model, is_tabular=True):
    """Render polished RAG Assistant section"""
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### RAG Assistant")

    # Debug: Check session state
    if DEBUG_MODE:
        st.caption(f"DEBUG 0: rag_response in session: {st.session_state.rag_response is not None}")
    
    # LLM Status
    llm_client = None
    llm_available = False
    actual_model_used = None
    actual_provider = None
    
    # Check provider from environment before initializing
    provider = os.getenv("LLM_PROVIDER", "local").lower()
    
    try:
        # For Gemini, don't pass model_name - let it read from GEMINI_MODEL env var
        if provider == "gemini":
            llm_client = LLMClient(device="cpu")
        else:
            llm_client = LLMClient(model_name=llm_model, device="cpu")
        llm_available = llm_client.is_available()
        model_info = llm_client.get_model_info()
        actual_provider = model_info.get("provider", "local")
        
        if llm_available:
            if actual_provider == "gemini":
                model_display = model_info.get("model_name", "gemini-3.5-flash")
                # Display friendly name
                model_display_friendly = model_display.replace("-", " ").replace(".", " ").title()
                st.markdown(f'<span class="status-dot status-green"></span>LLM Status: Gemini API connected ({model_display_friendly})', unsafe_allow_html=True)
                actual_model_used = model_display
            else:
                model_display = llm_model.split('/')[-1] if '/' in llm_model else llm_model
                st.markdown(f'<span class="status-dot status-green"></span>LLM Status: {model_display} loaded', unsafe_allow_html=True)
                actual_model_used = llm_model
        else:
            st.markdown('<span class="status-dot status-orange"></span>LLM Status: Not available (fallback mode)', unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f'<span class="status-dot status-red"></span>LLM Status: Initialization failed', unsafe_allow_html=True)
        st.error(f"LLM Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
    
    if not vector_store or not embed_gen:
        st.warning("RAG not available - vector store initialization failed")
        st.markdown('</div>', unsafe_allow_html=True)
        return
    
    rag = RAGPipeline(vector_store, embed_gen, llm_client=llm_client)
    
    # Question input
    default_query = "What are the main quality issues?" if is_tabular else "How can I improve the document quality?"
    user_query = st.text_input("Ask about the detected data quality issues...", value=default_query, key="rag_query")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        use_llm = False
        if llm_available:
            use_llm = st.checkbox("Use LLM", value=False, help="Enable LLM-based explanations", key="use_llm_checkbox")
    with col2:
        analyze_button = st.button("Get Analysis", type="primary", use_container_width=True, key="get_analysis_button")
    
    # Display cached response if available
    if st.session_state.rag_response is not None:
        response = st.session_state.rag_response
        
        st.markdown("---")
        st.markdown("##### RAG Analysis")
        st.info(response.explanation)
        
        # Recommendations
        if response.recommendations:
            st.markdown("##### Recommended Actions")
            for rec in response.recommendations:
                st.markdown(f'<div class="recommendation-item">{rec}</div>', unsafe_allow_html=True)
        
        # Quality Assessment
        st.markdown("##### Quality Assessment")
        st.success(response.quality_assessment)
        
        # Model and source info
        st.markdown("---")
        if response.used_llm:
            model_display = response.model_name.split('/')[-1] if '/' in response.model_name else response.model_name
            st.markdown(f"**Model:** {model_display}")
            # Check if it's a cloud API
            if actual_provider == "gemini":
                st.markdown("**Response Source:** Gemini API")
                # Show inference time
                model_info = llm_client.get_model_info()
                inference_time = model_info.get("inference_time", 0.0)
                if inference_time > 0:
                    st.markdown(f"**Gemini inference time:** {inference_time:.2f}s")
            else:
                st.markdown("**Response Source:** LLM")
        else:
            st.markdown("**Response Source:** Rule-based fallback")
        
        # Save to database (only if not already saved)
        if db_manager and not st.session_state.get('rag_saved', False):
            try:
                rag_response_dict = {
                    'query': response.query,
                    'context': {
                        'retrieved_documents': response.context.retrieved_documents,
                        'similarities': response.context.similarities
                    },
                    'explanation': response.explanation,
                    'recommendations': response.recommendations,
                    'quality_assessment': response.quality_assessment,
                    'used_llm': response.used_llm,
                    'model_name': response.model_name,
                    'sources': response.sources
                }
                
                query_id = db_manager.save_rag_query(metadata.source_file, rag_response_dict)
                if query_id:
                    st.caption(f"Query saved to database (ID: {query_id})")
                    st.session_state.rag_saved = True
            except Exception as e:
                st.caption(f"Failed to save query: {str(e)}")
    
    if analyze_button:
        import time
        start_time = time.time()
        
        if DEBUG_MODE:
                st.caption("DEBUG 1: Get Analysis button clicked")
        
        try:
            if DEBUG_MODE:
                        st.caption(f"DEBUG 2: Query received: '{user_query[:50]}...'")
            
            # Step 1: Query embedding
            if DEBUG_MODE:
                        st.caption("DEBUG 3: Query embedding started")
            query_embedding_start = time.time()
            query_embedding = embed_gen.generate_embedding(user_query)
            query_embedding_time = time.time() - query_embedding_start
            if DEBUG_MODE:
                        st.caption(f"DEBUG 4: Query embedding completed ({query_embedding_time:.2f}s)")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 4a: Query embedding shape={query_embedding.shape}, dtype={query_embedding.dtype}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 4b: Query embedding min={query_embedding.min():.4f}, max={query_embedding.max():.4f}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 4c: Query embedding finite: {np.all(np.isfinite(query_embedding))}")
            
            # Step 2: FAISS retrieval
            if DEBUG_MODE:
                        st.caption("DEBUG 5: Vector store exists: True")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 5a: FAISS index.ntotal={vector_store.index.ntotal}")
            if DEBUG_MODE:
                        st.caption("DEBUG 6: FAISS retrieval started")
            retrieval_start = time.time()
            
            # Debug: Show k values
            requested_k = 2
            actual_count = vector_store.index.ntotal
            effective_k = min(requested_k, actual_count)
            if DEBUG_MODE:
                        st.caption(f"DEBUG: Retrieval requested_k={requested_k}, index.ntotal={actual_count}, effective_k={effective_k}")
            
            retrieved_docs = vector_store.search(query_embedding, k=requested_k)
            retrieval_time = time.time() - retrieval_start
            if DEBUG_MODE:
                        st.caption(f"DEBUG 7: FAISS retrieval completed ({retrieval_time:.2f}s)")
            
            # Debug retrieval results
            if retrieved_docs:
                if DEBUG_MODE:
                    st.caption(f"DEBUG 8: Number of retrieved documents: {len(retrieved_docs)}")
                if DEBUG_MODE:
                    st.caption(f"DEBUG 8a: FAISS index.ntotal: {vector_store.index.ntotal}")
                if DEBUG_MODE:
                    st.caption(f"DEBUG 8b: Document metadata count: {len(vector_store.documents)}")
                for i, (dist, doc) in enumerate(retrieved_docs):
                    if DEBUG_MODE:
                        st.caption(f"DEBUG 9: Doc {i+1} - Distance: {dist:.4f}, Source: {doc.get('source_file', 'Unknown')}")
                    if DEBUG_MODE:
                        st.caption(f"DEBUG 9a: Doc {i+1} - Index ID: {i}, Distance finite: {np.isfinite(dist)}")
            else:
                if DEBUG_MODE:
                    st.caption("DEBUG 8: Number of retrieved documents: 0")
                if DEBUG_MODE:
                    st.caption("DEBUG 9: Retrieved context length: 0")
            
            # Step 3: RAG query through pipeline
            if DEBUG_MODE:
                        st.caption("DEBUG 10: RAG pipeline query started")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 10a: use_llm checkbox value: {use_llm}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 10b: llm_available: {llm_available}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 10c: llm_client.is_available(): {llm_client.is_available() if llm_client else 'None'}")
            pipeline_start = time.time()
            
            with st.spinner(f"Generating analysis with {llm_model.split('/')[-1]}..."):
                response = rag.query(user_query, metadata, k=2, use_llm=use_llm)
            
            pipeline_time = time.time() - pipeline_start
            if DEBUG_MODE:
                        st.caption(f"DEBUG 11: RAG pipeline query completed ({pipeline_time:.2f}s)")
            
            # Debug response
            if DEBUG_MODE:
                        st.caption(f"DEBUG 12: Response object created")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 13: used_llm={response.used_llm}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 14: model={response.model_name}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 15: Explanation length={len(response.explanation)}")
            if DEBUG_MODE:
                        st.caption(f"DEBUG 16: Recommendations count={len(response.recommendations)}")
            
            # If Gemini was expected but not used, show user-friendly message
            if use_llm and not response.used_llm and actual_provider == "gemini":
                st.warning("Gemini is currently unavailable. A rule-based response has been provided instead.")
                if DEBUG_MODE:
                    st.caption("Check terminal output for DEBUG GEMINI ERROR TYPE and DEBUG GEMINI ERROR MESSAGE")
            
            # Store in session state
            st.session_state.rag_response = response
            st.session_state.rag_saved = False
            
            if DEBUG_MODE:
                        st.caption("DEBUG 17: Response saved to session state")
            
            total_time = time.time() - start_time
            if DEBUG_MODE:
                        st.caption(f"DEBUG 18: Total RAG analysis time: {total_time:.2f}s")
            
            # Temporary: Render response immediately without rerun
            st.markdown("---")
            st.markdown("##### RAG Analysis (Generated)")
            st.info(response.explanation)
            
            if response.recommendations:
                st.markdown("##### Recommended Actions")
                for rec in response.recommendations:
                    st.markdown(f'<div class="recommendation-item">{rec}</div>', unsafe_allow_html=True)
            
            st.markdown("##### Quality Assessment")
            st.success(response.quality_assessment)
            
            st.markdown("---")
            if response.used_llm:
                model_display = response.model_name.split('/')[-1] if '/' in response.model_name else response.model_name
                st.markdown(f"**Model:** {model_display}")
                # Check if it's a cloud API
                if actual_provider == "gemini":
                    st.markdown("**Response Source:** Gemini API")
                    # Show inference time
                    model_info = llm_client.get_model_info()
                    inference_time = model_info.get("inference_time", 0.0)
                    if inference_time > 0:
                        st.markdown(f"**Gemini inference time:** {inference_time:.2f}s")
                else:
                    st.markdown("**Response Source:** LLM")
            else:
                st.markdown("**Response Source:** Rule-based fallback")
            
            st.success("✓ Response generated successfully")
            
        except Exception as e:
            st.error(f"ERROR at RAG execution: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
            total_time = time.time() - start_time
            st.caption(f"ERROR occurred after: {total_time:.2f}s")
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_database_actions(db_manager, metadata, quality_report):
    """Render compact database actions"""
    
    if not db_manager:
        return
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Database Actions")
    
    if st.button("Save Dataset to Database", type="secondary"):
        try:
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
            if dataset_id:
                st.success(f"Dataset saved (ID: {dataset_id})")
        except Exception as e:
            st.error(f"Save failed: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)


def process_data_workflow(normalized_asset, quality_report, db_manager, llm_model):
    """Process complete data workflow with professional UI"""

    metadata_gen = MetadataGenerator()
    metadata = metadata_gen.generate_metadata(normalized_asset, quality_report)
    textual_metadata = metadata_gen.generate_textual_metadata(metadata)
    is_tabular = normalized_asset.is_tabular()

    # Store metadata in session state
    st.session_state.metadata = metadata

    # Debug: Track workflow state
    if DEBUG_MODE:
        st.caption(f"Debug: Processing workflow, is_tabular={is_tabular}")

    # Initialize LLM client for use in RAG sections
    llm_client = None
    llm_available = False
    actual_provider = None
    provider = os.getenv("LLM_PROVIDER", "local").lower()

    try:
        if provider == "gemini":
            llm_client = LLMClient(device="cpu")
        else:
            llm_client = LLMClient(model_name=llm_model, device="cpu")
        llm_available = llm_client.is_available()
        model_info = llm_client.get_model_info()
        actual_provider = model_info.get("provider", "local")
    except Exception as e:
        llm_client = None
        llm_available = False
    
    # Section 01: Dataset Overview
    render_dataset_overview(normalized_asset)

    # Section 02: Quality Assessment
    render_section_header(2, "Data Quality Assessment")
    render_quality_scores(quality_report, is_tabular)

    # Section 03: Detected Issues
    render_section_header(3, "Detected Issues")
    render_issues_table(quality_report)

    # Section 04: Metadata
    render_section_header(4, "Metadata")
    render_metadata_grouped(metadata, quality_report, is_tabular)

    # Section 05: Semantic Retrieval
    render_section_header(5, "Semantic Retrieval")

    # Check if vector store already exists in session state
    if st.session_state.vector_store is None or st.session_state.embed_gen is None:
        vector_store = None
        embed_gen = None
        
        if DEBUG_MODE:
                st.caption("Debug: Creating new vector store...")
        
        try:
            embed_gen = EmbeddingGenerator()
            embedding = embed_gen.generate_embedding(textual_metadata)
            
            if DEBUG_MODE:
                        st.caption(f"Debug: Embedding generated, shape={embedding.shape}, dtype={embedding.dtype}")
            if DEBUG_MODE:
                        st.caption(f"Debug: Embedding min={embedding.min():.4f}, max={embedding.max():.4f}")
            if DEBUG_MODE:
                        st.caption(f"Debug: Embedding finite: {np.all(np.isfinite(embedding))}")
            
            dimension = embed_gen.get_embedding_dimension()
            vector_store = VectorStore(dimension=dimension, index_type="flat")
            
            document = {
                "source_file": metadata.source_file,
                "format": metadata.source_format,
                "quality_score": metadata.quality_score,
                "metadata": textual_metadata
            }
            
            vector_store.add_embeddings([embedding], [document])
            
            if DEBUG_MODE:
                        st.caption(f"Debug: Document added to vector store")
            if DEBUG_MODE:
                        st.caption(f"Debug: FAISS index.ntotal={vector_store.index.ntotal}")
            if DEBUG_MODE:
                        st.caption(f"Debug: Document metadata count={len(vector_store.documents)}")
            
            # Store in session state
            st.session_state.vector_store = vector_store
            st.session_state.embed_gen = embed_gen
            st.session_state.vector_store_status = "Ready"
            
            render_semantic_retrieval(embed_gen, vector_store)
            
        except Exception as e:
            st.error(f"Error in embedding/vector store: {str(e)}")
            st.session_state.vector_store_status = "Failed"
            st.info("Make sure sentence-transformers and faiss-cpu are installed")
            import traceback
            st.error(traceback.format_exc())
    else:
        # Use cached vector store
        vector_store = st.session_state.vector_store
        embed_gen = st.session_state.embed_gen
        if DEBUG_MODE:
                st.caption("Debug: Using cached vector store")
        if DEBUG_MODE:
                st.caption(f"Debug: FAISS index.ntotal={vector_store.index.ntotal}")
        if DEBUG_MODE:
                st.caption(f"Debug: Document metadata count={len(vector_store.documents)}")
        render_semantic_retrieval(embed_gen, vector_store)
    
    # Section 06: RAG Assistant
    render_section_header(6, "RAG Assistant")

    if vector_store and embed_gen:
        render_rag_pipeline_visualization(llm_client)
        render_rag_assistant(vector_store, embed_gen, metadata, db_manager, llm_model, is_tabular)
        render_database_actions(db_manager, metadata, quality_report)
    else:
        st.warning("RAG not available - vector store initialization failed")


def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="RAG Data Quality Assessment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Initialize session state
    if 'vector_store_status' not in st.session_state:
        st.session_state.vector_store_status = "Ready"
    if 'normalized_asset' not in st.session_state:
        st.session_state.normalized_asset = None
    if 'quality_report' not in st.session_state:
        st.session_state.quality_report = None
    if 'metadata' not in st.session_state:
        st.session_state.metadata = None
    if 'vector_store' not in st.session_state:
        st.session_state.vector_store = None
    if 'embed_gen' not in st.session_state:
        st.session_state.embed_gen = None
    if 'rag_response' not in st.session_state:
        st.session_state.rag_response = None
    if 'llm_model' not in st.session_state:
        st.session_state.llm_model = None
    
    # Get configured model from environment
    provider = os.getenv("LLM_PROVIDER", "local").lower()
    if provider == "gemini":
        default_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    else:
        default_model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    
    # Initialize database
    db_manager = None
    try:
        db_manager = DatabaseManager("sqlite:///data_quality.db")
        db_manager.create_tables()
    except Exception as e:
        pass
    
    # Render UI components
    render_header(db_manager, default_model)
    db_connection_string, llm_model = render_sidebar(db_manager, default_model)
    st.session_state.llm_model = llm_model
    
    # Section 01: Data Ingestion
    render_section_header(1, "Data Ingestion")
    
    uploaded_file = st.file_uploader(
        "Upload dataset",
        type=['csv', 'xlsx', 'xls', 'json', 'xml', 'txt', 'pdf'],
        help="Supported formats: CSV, Excel, JSON, XML, TXT, PDF"
    )
    
    # Check if we have data in session state or new upload
    if uploaded_file is not None:
        try:
            # Save uploaded file
            temp_path = Path("data/input") / uploaded_file.name
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load and process data
            asset = LoaderFactory.load_file(str(temp_path))
            normalized_asset = DataNormalizer.normalize(asset)
            
            # Quality assessment
            metrics = QualityMetrics()
            quality_report = metrics.assess_quality(normalized_asset)
            
            # Store in session state
            st.session_state.normalized_asset = normalized_asset
            st.session_state.quality_report = quality_report
            st.session_state.rag_response = None  # Reset RAG response on new upload
            
            # CRITICAL: Reset vector store and embeddings on new upload
            st.session_state.vector_store = None
            st.session_state.embed_gen = None
            
            # Process workflow
            process_data_workflow(normalized_asset, quality_report, db_manager, llm_model)
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
    
    elif st.session_state.normalized_asset is not None:
        # Display data from session state
        try:
            normalized_asset = st.session_state.normalized_asset
            quality_report = st.session_state.quality_report
            
            process_data_workflow(normalized_asset, quality_report, db_manager, llm_model)
            
        except Exception as e:
            st.error(f"Error displaying cached data: {str(e)}")
    
    else:
        st.info("Upload a file to begin data quality assessment")
        
        # Sample data section
        st.markdown("---")
        with st.expander("Demo / Sample Data", expanded=False):
            st.markdown("#### Sample Datasets")
            
            sample_files = {
                'CSV': 'data/sample/sample_dataset.csv',
                'Excel': 'data/sample/sample_dataset.xlsx',
                'JSON': 'data/sample/sample_dataset.json',
                'XML': 'data/sample/sample_dataset.xml',
                'TXT': 'data/sample/sample_document.txt',
                'PDF': 'data/sample/sample_document.pdf'
            }
            
            for format_name, file_path in sample_files.items():
                if st.button(f"Load Sample {format_name}"):
                    path = Path(file_path)
                    if path.exists():
                        try:
                            asset = LoaderFactory.load_file(str(path))
                            normalized_asset = DataNormalizer.normalize(asset)
                            
                            metrics = QualityMetrics()
                            quality_report = metrics.assess_quality(normalized_asset)
                            
                            # Store in session state
                            st.session_state.normalized_asset = normalized_asset
                            st.session_state.quality_report = quality_report
                            st.session_state.rag_response = None
                            
                            # CRITICAL: Reset vector store and embeddings on new upload
                            st.session_state.vector_store = None
                            st.session_state.embed_gen = None
                            
                            process_data_workflow(normalized_asset, quality_report, db_manager, llm_model)
                        except Exception as e:
                            st.error(f"Error loading sample: {str(e)}")
                    else:
                        st.error(f"Sample file not found: {file_path}")


if __name__ == "__main__":
    main()
