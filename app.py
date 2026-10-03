"""
Streamlit Web Interface for Data Quality Assessment
RAG-Based Data Quality Assessment for Enterprise Data Lakes
"""

import streamlit as st
import pandas as pd
import numpy as np
import hashlib
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


APP_STYLES = """
<style>
    :root {
        --ink: #202b32;
        --muted: #68757c;
        --canvas: #f3f5f2;
        --panel: #ffffff;
        --line: #e1e7e3;
        --teal: #438f89;
        --blue: #5797b7;
        --plum: #9173a4;
        --rose: #c66e78;
    }
    .stApp { background: var(--canvas); color: var(--ink); }
    [data-testid="stSidebar"] { background: #e9ede9; border-right: 1px solid var(--line); }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 { color: var(--ink); }
    .block-container { max-width: 1500px; padding-top: 1.1rem; padding-bottom: 3rem; }
    .topbar {
        display: flex; align-items: center; justify-content: space-between;
        background: #27343a; color: #f7f8f6; border-radius: 8px;
        padding: 0.85rem 1.2rem; margin: 0 0 1.1rem;
    }
    .topbar-brand { font-size: 1.04rem; font-weight: 700; letter-spacing: .02em; }
    .topbar-status { color: #d0dad6; font-size: .8rem; }
    .page-title { color: var(--ink); font-size: 1.75rem; font-weight: 700; margin: 0; }
    .page-subtitle { color: var(--muted); margin: .2rem 0 1rem; font-size: .92rem; }
    .section-title {
        color: var(--ink); font-size: 1.08rem; font-weight: 650;
        margin: 1.1rem 0 .55rem;
    }
    [data-testid="stMetric"] {
        background: var(--panel); border: 1px solid var(--line);
        border-radius: 10px; padding: .8rem 1rem;
    }
    [data-testid="stMetricValue"] { color: var(--ink); }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        border: 1px solid var(--line); border-radius: 8px; overflow: hidden;
    }
    .status-dot {
        display: inline-block; width: 8px; height: 8px; border-radius: 50%;
        margin-right: 8px; vertical-align: middle;
    }
    .status-green { background-color: #4b9b70; }
    .status-red { background-color: #c75d63; }
    .status-orange { background-color: #d89a47; }
    .metric-card {
        background-color: #f8faf8; border: 1px solid var(--line);
        border-radius: 8px; padding: 1rem; text-align: center;
    }
    .pipeline-step {
        background-color: #f0f4f2; border-left: 3px solid var(--teal);
        padding: .75rem 1rem; margin: .25rem 0; border-radius: 4px;
    }
    .recommendation-item {
        background-color: #edf5ef; border-left: 3px solid #4b9b70;
        padding: .75rem 1rem; margin: .5rem 0; border-radius: 4px;
    }
    @media (max-width: 700px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .topbar { align-items: flex-start; gap: .5rem; flex-direction: column; }
    }
</style>
"""


def render_sidebar(db_manager, llm_model):
    """Render navigation, service status, and application settings."""
    
    with st.sidebar:
        st.markdown("### Data quality")
        st.caption("WORKSPACE")
        active_view = st.radio(
            "Workspace navigation",
            ["Overview", "Quality details", "AI assistant", "Dataset library"],
            label_visibility="collapsed",
            key="active_view",
        )
        st.markdown("---")
        st.markdown("#### System status")
        
        if db_manager:
            st.markdown('<span class="status-dot status-green"></span>Database Connected', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-dot status-red"></span>Database Not Available', unsafe_allow_html=True)
        
        vs_status = st.session_state.get('vector_store_status', 'Ready')
        vs_color = 'status-green' if vs_status == 'Ready' else 'status-orange' if vs_status == 'Not initialized' else 'status-red'
        st.markdown(f'<span class="status-dot {vs_color}"></span>Vector Store: {vs_status}', unsafe_allow_html=True)
        
        model_display = llm_model.split('/')[-1] if '/' in llm_model else llm_model
        st.markdown(f'<span class="status-dot status-orange"></span>LLM configured: {model_display}', unsafe_allow_html=True)
        
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
        
        with st.expander("Advanced Settings", expanded=False):
            st.markdown("#### System Configuration")
            st.info("Advanced configuration options for debugging and development.")
        
        return active_view, db_connection_string, llm_model_input


def render_header(db_manager, llm_model):
    """Render the dark application bar and page heading."""
    
    model_display = llm_model.split('/')[-1] if '/' in llm_model else llm_model
    db_label = "Database connected" if db_manager else "Database unavailable"
    st.markdown("""
    <div class="topbar">
        <span class="topbar-brand">DATA QUALITY • INSIGHTS</span>
        <span class="topbar-status">""" + db_label + " &nbsp; · &nbsp; " + model_display + """</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Data Quality Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Assess, explore, and improve the quality of your enterprise data.</p>',
        unsafe_allow_html=True,
    )


def render_section_header(number, title):
    """Render section header"""
    st.markdown(f'<div class="section-title">{number:02d} — {title}</div>', unsafe_allow_html=True)


def render_dashboard_overview(normalized_asset, quality_report, db_manager, is_tabular):
    """Show current quality indicators and persisted assessment history."""
    file_name = Path(normalized_asset.metadata.get('file_name', 'Dataset')).name
    file_size_mb = normalized_asset.metadata.get('file_size', 0) / (1024 * 1024)
    issue_count = len(quality_report.issues)

    st.markdown(f"### Latest assessment · {file_name}")
    st.caption(f"{normalized_asset.source_format} · {normalized_asset.data_category} · {file_size_mb:.2f} MB")

    metric_columns = st.columns(4)
    metrics = [
        ("Quality score", f"{quality_report.quality_score:.0f}/100"),
        ("Completeness", f"{quality_report.completeness_score:.0f}/100" if is_tabular else "N/A"),
        ("Consistency", f"{quality_report.consistency_score:.0f}/100" if is_tabular else "N/A"),
        ("Detected issues", str(issue_count)),
    ]
    for column, (label, value) in zip(metric_columns, metrics):
        with column:
            st.metric(label, value)

    chart_column, severity_column = st.columns([1.8, 1])
    with chart_column, st.container(border=True):
        st.markdown("#### Quality score history")
        saved_datasets = db_manager.list_datasets() if db_manager else []
        if saved_datasets:
            history = pd.DataFrame(saved_datasets)
            history["created_at"] = pd.to_datetime(history["created_at"], errors="coerce")
            history = history.dropna(subset=["created_at", "quality_score"]).sort_values("created_at")
            if not history.empty:
                history = history.tail(12).set_index("created_at")[["quality_score"]]
                st.line_chart(history, y="quality_score", color="#5797b7", height=220)
                st.caption("Latest saved assessments · save this dataset to add it to the history.")
            else:
                st.info("Saved assessment history is not available.")
        elif is_tabular:
            scores = pd.DataFrame({
                "Quality dimension": ["Completeness", "Consistency", "Validity"],
                "Score": [
                    quality_report.completeness_score,
                    quality_report.consistency_score,
                    quality_report.validity_score,
                ],
            }).set_index("Quality dimension")
            st.bar_chart(scores, y="Score", color="#5797b7", height=220)
            st.caption("Current dataset scores · save assessments to build a history.")
        else:
            st.info("Save an assessment to build a quality score history.")

    with severity_column, st.container(border=True):
        st.markdown("#### Issue profile")
        severity_data = {
            str(severity).replace("_", " ").title(): int(count)
            for severity, count in quality_report.issues_by_severity.items()
            if count
        }
        if severity_data:
            st.bar_chart(pd.Series(severity_data, name="Issues"), color="#c66e78", height=180)
        else:
            st.success("No issues detected")
        if is_tabular:
            st.caption(
                f"{len(normalized_asset.tabular_data):,} rows · "
                f"{len(normalized_asset.tabular_data.columns):,} columns"
            )
        else:
            st.caption(f"{len(normalized_asset.text_data):,} characters")

    overview_column, library_column = st.columns([1, 1.4])
    with overview_column, st.container(border=True):
        st.markdown("#### Dataset snapshot")
        st.write(f"**Format:** {normalized_asset.source_format}")
        st.write(f"**Category:** {normalized_asset.data_category}")
        if is_tabular:
            st.write(f"**Dimensions:** {len(normalized_asset.tabular_data):,} rows × {len(normalized_asset.tabular_data.columns):,} columns")
        st.write(f"**Assessment:** {quality_report.overall_assessment}")
        render_database_actions(
            db_manager,
            st.session_state.metadata,
            quality_report,
        )

    with library_column, st.container(border=True):
        st.markdown("#### Recent datasets")
        recent_datasets = db_manager.list_datasets()[:5] if db_manager else []
        if recent_datasets:
            recent_frame = pd.DataFrame(recent_datasets)
            recent_frame["Dataset"] = recent_frame["source_file"].map(lambda value: Path(value).name)
            recent_frame["Quality"] = recent_frame["quality_score"].map(lambda value: f"{value:.0f}/100")
            st.dataframe(
                recent_frame[["Dataset", "source_format", "Quality", "created_at"]],
                use_container_width=True,
                hide_index=True,
                column_config={"source_format": "Format", "created_at": "Assessed"},
            )
        else:
            st.caption("Saved assessments will appear here.")


def render_dataset_library(db_manager):
    """List assessments persisted by the database manager."""
    st.markdown("### Dataset library")
    st.caption("Previously saved quality assessments and their latest scores.")
    if not db_manager:
        st.warning("The database is unavailable, so saved datasets cannot be listed.")
        return

    datasets = db_manager.list_datasets()
    if not datasets:
        st.info("No saved assessments yet. Assess a dataset and save it from the Overview.")
        return

    frame = pd.DataFrame(datasets)
    frame["Dataset"] = frame["source_file"].map(lambda value: Path(value).name)
    frame["Quality score"] = frame["quality_score"].map(lambda value: f"{value:.0f}/100")
    frame["Assessed"] = pd.to_datetime(frame["created_at"], errors="coerce").dt.strftime("%Y-%m-%d %H:%M")
    st.dataframe(
        frame[["Dataset", "source_format", "data_category", "rows", "columns", "Quality score", "Assessed"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "source_format": "Format",
            "data_category": "Category",
            "rows": "Rows",
            "columns": "Columns",
        },
    )


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


def process_data_workflow(normalized_asset, quality_report, db_manager, llm_model, active_view="Overview"):
    """Render the selected dashboard view for the current dataset."""

    metadata_gen = MetadataGenerator()
    metadata = metadata_gen.generate_metadata(normalized_asset, quality_report)
    textual_metadata = metadata_gen.generate_textual_metadata(metadata)
    is_tabular = normalized_asset.is_tabular()

    # Store metadata in session state
    st.session_state.metadata = metadata

    # Debug: Track workflow state
    if DEBUG_MODE:
        st.caption(f"Debug: Processing workflow, is_tabular={is_tabular}")

    llm_client = None
    if active_view == "Overview":
        render_dashboard_overview(normalized_asset, quality_report, db_manager, is_tabular)
        return

    if active_view == "Quality details":
        render_section_header(1, "Dataset overview")
        render_dataset_overview(normalized_asset)
        render_section_header(2, "Quality assessment")
        render_quality_scores(quality_report, is_tabular)
        render_section_header(3, "Detected issues")
        render_issues_table(quality_report)
        render_section_header(4, "Metadata")
        render_metadata_grouped(metadata, quality_report, is_tabular)
        return

    if active_view != "AI assistant":
        return

    provider = os.getenv("LLM_PROVIDER", "local").lower()
    try:
        if provider == "gemini":
            llm_client = LLMClient(device="cpu")
        else:
            llm_client = LLMClient(model_name=llm_model, device="cpu")
    except Exception as e:
        st.error(f"Unable to initialize the configured language model: {e}")

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
    
    render_section_header(5, "AI quality assistant")

    if vector_store and embed_gen:
        render_rag_pipeline_visualization(llm_client)
        render_rag_assistant(vector_store, embed_gen, metadata, db_manager, llm_model, is_tabular)
    else:
        st.warning("RAG not available - vector store initialization failed")


def main():
    """Main Streamlit application"""
    
    st.set_page_config(
        page_title="RAG Data Quality Assessment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown(APP_STYLES, unsafe_allow_html=True)
    
    # Initialize session state
    if 'vector_store_status' not in st.session_state:
        st.session_state.vector_store_status = "Not initialized"
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
    if 'upload_signature' not in st.session_state:
        st.session_state.upload_signature = None
    if 'processed_upload_signature' not in st.session_state:
        st.session_state.processed_upload_signature = None
    
    # Get configured model from environment
    provider = os.getenv("LLM_PROVIDER", "local").lower()
    if provider == "gemini":
        default_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    else:
        default_model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    
    # Initialize database
    db_manager = None
    database_error = False
    try:
        db_manager = DatabaseManager("sqlite:///data_quality.db")
        db_manager.create_tables()
    except Exception as e:
        database_error = True
    
    render_header(db_manager, default_model)
    active_view, db_connection_string, llm_model = render_sidebar(db_manager, default_model)
    st.session_state.llm_model = llm_model
    if database_error:
        st.warning("Database initialization failed. Saved dataset and query history may be unavailable.")
    
    with st.container(border=True):
        upload_column, format_column = st.columns([1.5, 1])
        with upload_column:
            st.markdown("#### Assess a dataset")
            uploaded_file = st.file_uploader(
                "Upload a dataset",
                type=['csv', 'xlsx', 'xls', 'json', 'xml', 'txt', 'pdf'],
                help="Supported formats: CSV, Excel, JSON, XML, TXT, PDF",
                label_visibility="collapsed",
            )
        with format_column:
            st.markdown("#### Supported formats")
            st.caption("CSV · Excel · JSON · XML · TXT · PDF")

    process_current_dataset = False
    if uploaded_file is not None:
        upload_bytes = uploaded_file.getvalue()
        upload_signature = hashlib.sha256(upload_bytes).hexdigest()
        st.session_state.upload_signature = upload_signature
        try:
            if upload_signature != st.session_state.processed_upload_signature:
                temp_path = Path("data/input") / Path(uploaded_file.name).name
                temp_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path.write_bytes(upload_bytes)

                asset = LoaderFactory.load_file(str(temp_path))
                normalized_asset = DataNormalizer.normalize(asset)
                quality_report = QualityMetrics().assess_quality(normalized_asset)

                st.session_state.normalized_asset = normalized_asset
                st.session_state.quality_report = quality_report
                st.session_state.rag_response = None
                st.session_state.rag_saved = False
                st.session_state.vector_store = None
                st.session_state.embed_gen = None
                st.session_state.vector_store_status = "Not initialized"
                st.session_state.processed_upload_signature = upload_signature
            process_current_dataset = st.session_state.normalized_asset is not None
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

    if process_current_dataset or st.session_state.normalized_asset is not None:
        if active_view == "Dataset library":
            render_dataset_library(db_manager)
        else:
            try:
                process_data_workflow(
                    st.session_state.normalized_asset,
                    st.session_state.quality_report,
                    db_manager,
                    llm_model,
                    active_view,
                )
            except Exception as e:
                st.error(f"Error displaying the selected view: {e}")
    else:
        if active_view == "Dataset library":
            render_dataset_library(db_manager)
        else:
            st.info("Upload a dataset above or choose one of the samples to start an assessment.")

        sample_loaded = False
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
            sample_columns = st.columns(3)
            for index, (format_name, file_path) in enumerate(sample_files.items()):
                with sample_columns[index % len(sample_columns)]:
                    if st.button(f"Load {format_name} sample", key=f"load_sample_{format_name}"):
                        path = Path(file_path)
                        if path.exists():
                            try:
                                asset = LoaderFactory.load_file(str(path))
                                normalized_asset = DataNormalizer.normalize(asset)
                                quality_report = QualityMetrics().assess_quality(normalized_asset)

                                st.session_state.normalized_asset = normalized_asset
                                st.session_state.quality_report = quality_report
                                st.session_state.rag_response = None
                                st.session_state.rag_saved = False
                                st.session_state.vector_store = None
                                st.session_state.embed_gen = None
                                st.session_state.vector_store_status = "Not initialized"
                                st.session_state.upload_signature = None
                                st.session_state.processed_upload_signature = None
                                sample_loaded = True
                            except Exception as e:
                                st.error(f"Error loading sample: {str(e)}")
                        else:
                            st.error(f"Sample file not found: {file_path}")

        if sample_loaded:
            try:
                process_data_workflow(
                    st.session_state.normalized_asset,
                    st.session_state.quality_report,
                    db_manager,
                    llm_model,
                    active_view,
                )
            except Exception as e:
                st.error(f"Error displaying the selected view: {e}")


if __name__ == "__main__":
    main()
