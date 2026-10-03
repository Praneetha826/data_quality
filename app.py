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


import html
import math


THEME_CSS = """
<style>
:root{
  --bg:#efede8; --panel:#f8f7f3; --card:#ffffff; --ink:#3d4147; --muted:#8e939a;
  --line:#e0ddd5; --bar:#2f3032; --red:#e05a5a; --blue:#4a9fd8; --green:#5bb98b;
  --purple:#8a5fbf; --amber:#e8a34a;
}
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"], [data-testid="stSidebarHeader"]{display:none !important;}
.stApp{background:var(--bg);color:var(--ink);font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;}
.block-container{padding:76px 2.2rem 2.5rem 2.2rem !important;max-width:1280px;}

.topbar{position:fixed;top:0;left:0;right:0;height:56px;background:var(--bar);z-index:999991;
  display:flex;align-items:center;justify-content:space-between;box-shadow:0 2px 6px rgba(0,0,0,.25);}
.topbar .brand{width:230px;height:100%;display:flex;align-items:center;padding-left:22px;
  color:#fff;font-size:19px;font-weight:300;background:#262628;border-right:1px solid #1d1d1f;box-sizing:border-box;}
.topbar .brand b{font-weight:700;color:var(--red);margin-left:2px;}
.topbar .right{display:flex;align-items:center;height:100%;}
.topbar .pill{display:flex;align-items:center;height:100%;padding:0 18px;color:#c9ccd1;font-size:10.5px;
  font-weight:600;letter-spacing:.09em;text-transform:uppercase;border-left:1px solid #3b3c3f;}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;}
.dot.green,.status-green{background:#4caf7d;} .dot.red,.status-red{background:#e05a5a;}
.dot.amber,.status-orange{background:#e8a34a;} .dot.grey{background:#8e939a;}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:8px;}

section[data-testid="stSidebar"]{top:56px;height:calc(100vh - 56px);background:var(--panel);
  border-right:1px solid var(--line);width:230px !important;min-width:230px !important;}
section[data-testid="stSidebar"] > div{padding-top:0 !important;}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:0;}
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:0;width:100%;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label{width:100%;margin:0;padding:16px 18px;
  border-bottom:1px solid var(--line);border-left:4px solid var(--accent,#ccc);border-radius:0;cursor:pointer;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-child{display:none;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label p{font-size:11px;font-weight:600;
  letter-spacing:.09em;text-transform:uppercase;color:#6b7078;margin:0;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover{background:#f0eee8;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked){background:var(--red);border-left-color:var(--red);}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:has(input:checked) p{color:#fff;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(1){--accent:#e05a5a;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(2){--accent:#4a9fd8;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(3){--accent:#5bb98b;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(4){--accent:#8a5fbf;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(5){--accent:#e8a34a;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(6){--accent:#4a9fd8;}
section[data-testid="stSidebar"] div[role="radiogroup"] > label:nth-of-type(7){--accent:#8e939a;}

.titlebar{display:flex;align-items:center;gap:12px;padding:0 0 14px 0;border-bottom:1px solid var(--line);margin-bottom:22px;}
.titlebar .ic{font-size:18px;color:#7b8087;} .titlebar .tt{font-size:15px;color:var(--ink);}
.titlebar .tag{margin-left:auto;font-size:10.5px;letter-spacing:.1em;color:#b9bcc1;text-transform:uppercase;}
.sec-title{font-size:15px;color:var(--ink);margin:0 0 8px 0;}
.cap{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-top:4px;}

.bignum{display:flex;align-items:center;gap:16px;}
.bignum .n{font-size:46px;font-weight:700;color:var(--red);line-height:1;}
.ticks{display:flex;align-items:flex-end;flex-wrap:wrap;max-width:210px;}
.ticks i{display:inline-block;width:4px;height:24px;margin:0 3px 3px 0;border-radius:1px;}
.donutrow{display:flex;align-items:center;gap:18px;margin-top:18px;}
.legend div{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#7a7f86;margin:5px 0;}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:8px;}

.stat{text-align:center;} .stat .lbl{font-size:13px;color:#555a61;margin-bottom:10px;}
.stat svg{display:block;margin:0 auto;}

.panel{background:var(--card);border:1px solid var(--line);border-radius:3px;margin-bottom:8px;}
.panel .head{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;
  border-bottom:1px solid var(--line);font-size:13.5px;color:var(--ink);}
.panel .head .btn{font-size:10px;letter-spacing:.08em;text-transform:uppercase;border:1px solid var(--line);
  padding:5px 9px;color:#777;background:#faf9f6;}
.panel .body{padding:18px;min-height:96px;}
.panel .body h4{margin:0 0 4px 0;font-size:17px;font-weight:600;color:var(--ink);}
.panel .body p{margin:2px 0;font-size:12.5px;color:var(--muted);}
.panel.accent-green{border-right:5px solid var(--green);}
.panel.accent-blue{border-right:5px solid var(--blue);}

.stButton>button{background:#faf9f6;border:1px solid var(--line);color:#6a6f76;border-radius:3px;
  font-size:11px;font-weight:600;letter-spacing:.07em;text-transform:uppercase;padding:.3rem .9rem;}
.stButton>button:hover{border-color:var(--red);color:var(--red);background:#fff;}
.stButton>button[kind="primary"]{background:var(--red);border-color:var(--red);color:#fff;}

.card{height:0;margin:0;}
.metric-card{background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:1rem;text-align:center;}
.pipeline-step{background:#f0f4f8;border-left:3px solid var(--blue);padding:.6rem 1rem;margin:.25rem 0;border-radius:3px;font-size:13px;}
.recommendation-item{background:#e8f5e9;border-left:3px solid var(--green);padding:.75rem 1rem;margin:.5rem 0;border-radius:3px;}
.response-box{background:#f8f9fa;border:1px solid #dee2e6;border-radius:6px;padding:1.2rem;margin:1rem 0;}
</style>
"""

PAGES = [
    ("Dashboard", "▦"),
    ("Ingestion", "⇪"),
    ("Issues", "⚠"),
    ("Metadata", "☰"),
    ("RAG Assistant", "✦"),
    ("Database", "▤"),
    ("Settings", "⚙"),
]
PAGE_ICON = dict(PAGES)

SEVERITY_ORDER = ["critical", "high", "medium", "low", "info"]
SEVERITY_COLOR = {
    "critical": "#e05a5a",
    "high": "#e8a34a",
    "medium": "#4a9fd8",
    "low": "#5bb98b",
    "info": "#8a5fbf",
}


def _h(markup):
    return "".join(line.strip() for line in markup.splitlines())


def severity_counts(quality_report):
    counts = {s: 0 for s in SEVERITY_ORDER}
    for issue in quality_report.issues:
        key = str(issue.severity.value).lower()
        counts[key] = counts.get(key, 0) + 1
    return counts


def chart_series(asset, quality_report):
    if asset.is_tabular():
        df = asset.tabular_data
        missing = (df.isna().mean() * 100).round(1)
        worst = missing.sort_values(ascending=False).head(8).index
        cols = [c for c in df.columns if c in worst]
        return "Missing Values by Column (%)", [str(c) for c in cols], [float(missing[c]) for c in cols]
    counts = severity_counts(quality_report)
    keys = [k for k in SEVERITY_ORDER]
    return "Issues by Severity", [k.title() for k in keys], [counts.get(k, 0) for k in keys]


def svg_area_chart(labels, values, color="#e05a5a", width=640, height=220):
    if not values:
        return '<p class="cap">No data to chart</p>'
    pad_l, pad_r, pad_t, pad_b = 34, 14, 12, 30
    plot_w, plot_h = width - pad_l - pad_r, height - pad_t - pad_b
    top = max(10, int(math.ceil(max(values) / 10.0) * 10))
    n = len(values)

    def x(i):
        return pad_l + (plot_w / 2 if n == 1 else i * plot_w / (n - 1))

    def y(v):
        return pad_t + plot_h - (v / top) * plot_h

    grid = ""
    for t in (0, top / 2, top):
        gy = y(t)
        grid += (
            f'<line x1="{pad_l}" y1="{gy:.1f}" x2="{width - pad_r}" y2="{gy:.1f}" stroke="#e6e3dc" stroke-width="1"/>'
            f'<text x="{pad_l - 8}" y="{gy + 3:.1f}" font-size="10" fill="#9a9fa6" text-anchor="end" font-family="Helvetica,Arial,sans-serif">{t:g}</text>'
        )
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(values))
    area = f"{x(0):.1f},{y(0):.1f} {pts} {x(n - 1):.1f},{y(0):.1f}"
    dots = "".join(
        f'<circle cx="{x(i):.1f}" cy="{y(v):.1f}" r="3.5" fill="#fff" stroke="{color}" stroke-width="2"/>'
        for i, v in enumerate(values)
    )
    xl = "".join(
        f'<text x="{x(i):.1f}" y="{height - 10}" font-size="10" fill="#9a9fa6" text-anchor="middle" font-family="Helvetica,Arial,sans-serif">{html.escape(lab[:9] + ("…" if len(lab) > 9 else ""))}</text>'
        for i, lab in enumerate(labels)
    )
    return (
        f'<svg viewBox="0 0 {width} {height}" width="100%" xmlns="http://www.w3.org/2000/svg">'
        f'{grid}<polygon points="{area}" fill="{color}" fill-opacity="0.10"/>'
        f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2"/>{dots}{xl}</svg>'
    )


def svg_donut(parts, size=118, thickness=15):
    r = (size - thickness) / 2
    c = 2 * math.pi * r
    cx = cy = size / 2
    total = sum(v for _, v, _ in parts)
    out = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e6e3dc" stroke-width="{thickness}"/>'
    offset = 0.0
    if total > 0:
        for _, v, col in parts:
            if v <= 0:
                continue
            seg = c * v / total
            out += (
                f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{thickness}" '
                f'stroke-dasharray="{seg:.2f} {c - seg:.2f}" stroke-dashoffset="{-offset:.2f}" '
                f'transform="rotate(-90 {cx} {cy})"/>'
            )
            offset += seg
    return f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">{out}</svg>'


def svg_ring(value, color, size=116, stroke=5, applicable=True):
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    cx = cy = size / 2
    if not applicable:
        color, label, pct = "#c9ccd1", "N/A", 0.0
        fs = 22
    else:
        pct = max(0.0, min(1.0, float(value) / 100.0))
        label, fs = f"{float(value):.0f}", 36
    arc = c * pct
    return (
        f'<svg viewBox="0 0 {size} {size}" width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e6e3dc" stroke-width="{stroke}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-dasharray="{arc:.2f} {c - arc:.2f}" transform="rotate(-90 {cx} {cy})"/>'
        f'<text x="{cx}" y="{cy + fs * 0.34:.1f}" font-size="{fs}" font-weight="300" fill="{color}" '
        f'text-anchor="middle" font-family="Helvetica,Arial,sans-serif">{label}</text></svg>'
    )


def score_color(score):
    return "#5bb98b" if score >= 80 else "#e8a34a" if score >= 60 else "#e05a5a"

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


def go(page):
    st.session_state.goto = page


def persist(widget_key, store_key):
    st.session_state[store_key] = st.session_state[widget_key]


@st.cache_resource(show_spinner=False)
def get_db_manager(url):
    try:
        db = DatabaseManager(url)
        db.create_tables()
        return db
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def get_embedder():
    return EmbeddingGenerator()


@st.cache_resource(show_spinner=False)
def get_llm_client(provider, model_name):
    try:
        if provider == "gemini":
            return LLMClient(device="cpu")
        return LLMClient(model_name=model_name, device="cpu")
    except Exception:
        return None


def init_state(default_model):
    defaults = {
        "nav": "Dashboard",
        "normalized_asset": None,
        "quality_report": None,
        "metadata": None,
        "vector_store": None,
        "embed_gen": None,
        "rag_response": None,
        "rag_saved": False,
        "vector_store_status": "Idle",
        "vector_error": None,
        "file_sig": None,
        "db_url": "sqlite:///data_quality.db",
        "llm_model": default_model,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def prepare_retrieval(normalized_asset, quality_report):
    generator = MetadataGenerator()
    metadata = generator.generate_metadata(normalized_asset, quality_report)
    textual = generator.generate_textual_metadata(metadata)
    st.session_state.metadata = metadata
    st.session_state.vector_error = None
    try:
        embed_gen = get_embedder()
        embedding = embed_gen.generate_embedding(textual)
        store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
        store.add_embeddings([embedding], [{
            "source_file": metadata.source_file,
            "format": metadata.source_format,
            "quality_score": metadata.quality_score,
            "metadata": textual,
        }])
        st.session_state.vector_store = store
        st.session_state.embed_gen = embed_gen
        st.session_state.vector_store_status = "Ready"
    except Exception as exc:
        st.session_state.vector_store = None
        st.session_state.embed_gen = None
        st.session_state.vector_store_status = "Failed"
        st.session_state.vector_error = str(exc)


def ingest(path):
    asset = LoaderFactory.load_file(str(path))
    normalized_asset = DataNormalizer.normalize(asset)
    quality_report = QualityMetrics().assess_quality(normalized_asset)
    st.session_state.normalized_asset = normalized_asset
    st.session_state.quality_report = quality_report
    st.session_state.rag_response = None
    st.session_state.rag_saved = False
    prepare_retrieval(normalized_asset, quality_report)


def render_topbar(db_ok, llm_label, llm_ok):
    status = st.session_state.vector_store_status
    vs_dot = {"Ready": "green", "Failed": "red"}.get(status, "grey")
    st.markdown(_h(f"""
        <div class="topbar">
          <div class="brand">DataQuality<b>RAG</b></div>
          <div class="right">
            <div class="pill"><span class="dot {'green' if db_ok else 'red'}"></span>Database</div>
            <div class="pill"><span class="dot {vs_dot}"></span>FAISS {html.escape(status)}</div>
            <div class="pill"><span class="dot {'green' if llm_ok else 'amber'}"></span>{html.escape(llm_label)}</div>
          </div>
        </div>
    """), unsafe_allow_html=True)


def render_titlebar(title_html, icon, tag):
    st.markdown(_h(f"""
        <div class="titlebar"><span class="ic">{icon}</span>
        <span class="tt">{title_html}</span><span class="tag">{tag}</span></div>
    """), unsafe_allow_html=True)


def require_data():
    if st.session_state.normalized_asset is None:
        render_titlebar("No dataset loaded", PAGE_ICON["Ingestion"], "EMPTY")
        st.markdown(_h("""
            <div class="panel"><div class="body"><h4>Nothing to show yet</h4>
            <p>Upload a file or load a sample to generate a quality report.</p></div></div>
        """), unsafe_allow_html=True)
        st.button("Go to Ingestion", type="primary", on_click=go, args=("Ingestion",), key="empty_go")
        return False
    return True


def page_dashboard():
    if not require_data():
        return
    asset = st.session_state.normalized_asset
    report = st.session_state.quality_report
    is_tabular = asset.is_tabular()
    file_name = Path(asset.metadata.get("file_name", "Unknown")).name
    render_titlebar(f"Quality Report for <b>{html.escape(file_name)}</b>", PAGE_ICON["Dashboard"], "DASHBOARD")

    chart_title, labels, values = chart_series(asset, report)
    counts = severity_counts(report)
    total_issues = len(report.issues)
    tick_colors = [SEVERITY_COLOR.get(sev, "#8e939a") for sev in SEVERITY_ORDER for _ in range(counts.get(sev, 0))][:24]
    ticks = "".join(f'<i style="background:{c}"></i>' for c in tick_colors)
    parts = [(s, counts.get(s, 0), SEVERITY_COLOR[s]) for s in SEVERITY_ORDER]
    legend = "".join(
        f'<div><i style="background:{col}"></i>{name} · {val}</div>' for name, val, col in parts
    )

    left, right = st.columns([3, 2], gap="large")
    with left:
        st.markdown(_h(f'<div class="sec-title">{html.escape(chart_title)}</div>') + svg_area_chart(labels, values), unsafe_allow_html=True)
    with right:
        st.markdown(_h(f"""
            <div class="bignum"><div class="n">{total_issues}</div><div class="ticks">{ticks}</div></div>
            <div class="cap">Detected issues</div>
            <div class="donutrow">{svg_donut(parts)}<div class="legend">{legend}</div></div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    rings = [
        ("Overall Score", report.quality_score, score_color(report.quality_score), True),
        ("Completeness", report.completeness_score, "#4a9fd8", is_tabular),
        ("Consistency", report.consistency_score, "#5bb98b", is_tabular),
        ("Validity", report.validity_score, "#8a5fbf", is_tabular),
    ]
    for col, (label, value, color, applicable) in zip(st.columns(4), rings):
        with col:
            st.markdown(_h(f'<div class="stat"><div class="lbl">{label}</div>') + svg_ring(value, color, applicable=applicable) + "</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    size_mb = asset.metadata.get("file_size", 0) / (1024 * 1024)
    shape = (
        f"{len(asset.tabular_data)} rows × {len(asset.tabular_data.columns)} columns"
        if is_tabular else f"{len(asset.text_data.split())} words"
    )
    with c1:
        st.markdown(_h(f"""
            <div class="panel accent-green"><div class="head"><span>Dataset</span><span class="btn">{html.escape(str(asset.source_format))}</span></div>
            <div class="body"><h4>{html.escape(file_name)}</h4>
            <p>{html.escape(str(asset.data_category))} · {shape} · {size_mb:.2f} MB</p>
            <p>{html.escape(str(report.overall_assessment))}</p></div></div>
        """), unsafe_allow_html=True)
        st.button("View metadata", on_click=go, args=("Metadata",), key="dash_meta")
    with c2:
        response = st.session_state.rag_response
        if response is not None:
            snippet = html.escape(response.explanation[:230] + ("…" if len(response.explanation) > 230 else ""))
            source = "LLM" if response.used_llm else "Rule-based"
            body = f"<h4>{html.escape(response.query)}</h4><p>{snippet}</p><p>Source: {source}</p>"
        else:
            body = "<h4>No analysis yet</h4><p>Ask the assistant why the issues were flagged and how to fix them.</p>"
        st.markdown(_h(f"""
            <div class="panel accent-blue"><div class="head"><span>Latest RAG Analysis</span><span class="btn">Assistant</span></div>
            <div class="body">{body}</div></div>
        """), unsafe_allow_html=True)
        st.button("Open assistant", on_click=go, args=("RAG Assistant",), key="dash_rag")


def page_ingestion():
    render_titlebar("Data Ingestion", PAGE_ICON["Ingestion"], "INGESTION")
    with st.container(border=True):
        uploaded = st.file_uploader(
            "Upload dataset",
            type=["csv", "xlsx", "xls", "json", "xml", "txt", "pdf"],
            help="Supported formats: CSV, Excel, JSON, XML, TXT, PDF",
        )
        if uploaded is not None:
            signature = (uploaded.name, uploaded.size)
            if st.session_state.file_sig != signature:
                try:
                    path = Path("data/input") / uploaded.name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(uploaded.getbuffer())
                    with st.spinner("Analysing dataset..."):
                        ingest(path)
                    st.session_state.file_sig = signature
                    st.session_state.goto = "Dashboard"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Error processing file: {exc}")
    with st.expander("Demo / Sample Data", expanded=st.session_state.normalized_asset is None):
        samples = {
            "CSV": "data/sample/sample_dataset.csv",
            "Excel": "data/sample/sample_dataset.xlsx",
            "JSON": "data/sample/sample_dataset.json",
            "XML": "data/sample/sample_dataset.xml",
            "TXT": "data/sample/sample_document.txt",
            "PDF": "data/sample/sample_document.pdf",
        }
        for fmt, file_path in samples.items():
            if st.button(f"Load Sample {fmt}", key=f"sample_{fmt}"):
                if not Path(file_path).exists():
                    st.error(f"Sample file not found: {file_path}")
                else:
                    try:
                        ingest(file_path)
                        st.session_state.file_sig = None
                        st.session_state.goto = "Dashboard"
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Error loading sample: {exc}")
    if st.session_state.normalized_asset is not None:
        render_dataset_overview(st.session_state.normalized_asset)


def page_issues():
    if not require_data():
        return
    render_titlebar("Detected Issues", PAGE_ICON["Issues"], "ISSUES")
    with st.container(border=True):
        render_issues_table(st.session_state.quality_report)


def page_metadata():
    if not require_data():
        return
    render_titlebar("Dataset Metadata", PAGE_ICON["Metadata"], "METADATA")
    with st.container(border=True):
        render_metadata_grouped(
            st.session_state.metadata,
            st.session_state.quality_report,
            st.session_state.normalized_asset.is_tabular(),
        )


def page_assistant(db_manager):
    if not require_data():
        return
    render_titlebar("RAG Assistant", PAGE_ICON["RAG Assistant"], "ASSISTANT")
    store, embed_gen = st.session_state.vector_store, st.session_state.embed_gen
    if not store or not embed_gen:
        st.warning("RAG not available - vector store initialization failed")
        if st.session_state.vector_error:
            st.caption(st.session_state.vector_error)
        return
    provider = os.getenv("LLM_PROVIDER", "local").lower()
    llm_model = st.session_state.llm_model
    left, right = st.columns([2, 3], gap="large")
    with left:
        with st.container(border=True):
            render_rag_pipeline_visualization(get_llm_client(provider, llm_model))
        with st.container(border=True):
            render_semantic_retrieval(embed_gen, store)
    with right:
        with st.container(border=True):
            render_rag_assistant(
                store, embed_gen, st.session_state.metadata, db_manager, llm_model,
                st.session_state.normalized_asset.is_tabular(),
            )


def page_database(db_manager):
    render_titlebar("Database", PAGE_ICON["Database"], "DATABASE")
    if not db_manager:
        st.error("Database not available. Check the connection string in Settings.")
        return
    st.caption(f"Connected: {st.session_state.db_url}")
    if not require_data():
        return
    with st.container(border=True):
        render_database_actions(db_manager, st.session_state.metadata, st.session_state.quality_report)


def page_settings():
    render_titlebar("Settings", PAGE_ICON["Settings"], "SETTINGS")
    with st.container(border=True):
        st.markdown("##### Database")
        st.text_input(
            "Connection string", value=st.session_state.db_url, key="w_db_url",
            on_change=persist, args=("w_db_url", "db_url"),
            help="PostgreSQL: postgresql://user:password@host:port/database\nSQLite: sqlite:///database.db",
        )
        st.markdown("##### LLM")
        st.text_input(
            "Model name", value=st.session_state.llm_model, key="w_llm_model",
            on_change=persist, args=("w_llm_model", "llm_model"),
            help="gemini-3.5-flash (Gemini API), meta-llama/Meta-Llama-3-8B-Instruct or Qwen/Qwen2.5-3B-Instruct (local)",
        )
    with st.expander("Advanced", expanded=False):
        st.write(f"Provider: {os.getenv('LLM_PROVIDER', 'local')}")
        st.write(f"Debug mode: {DEBUG_MODE}")


def main():
    st.set_page_config(
        page_title="RAG Data Quality Assessment",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(THEME_CSS, unsafe_allow_html=True)

    provider = os.getenv("LLM_PROVIDER", "local").lower()
    if provider == "gemini":
        default_model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")
    else:
        default_model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct")
    init_state(default_model)

    db_manager = get_db_manager(st.session_state.db_url)
    model = st.session_state.llm_model
    llm_ok = provider == "gemini" and bool(os.getenv("GEMINI_API_KEY"))
    render_topbar(db_manager is not None, model.split("/")[-1], llm_ok)

    if st.session_state.get("goto"):
        st.session_state.nav = st.session_state.pop("goto")
    with st.sidebar:
        page = st.radio(
            "Navigation", [name for name, _ in PAGES], key="nav",
            format_func=lambda n: f"{PAGE_ICON[n]}   {n}", label_visibility="collapsed",
        )

    if page == "Dashboard":
        page_dashboard()
    elif page == "Ingestion":
        page_ingestion()
    elif page == "Issues":
        page_issues()
    elif page == "Metadata":
        page_metadata()
    elif page == "RAG Assistant":
        page_assistant(db_manager)
    elif page == "Database":
        page_database(db_manager)
    else:
        page_settings()


if __name__ == "__main__":
    main()