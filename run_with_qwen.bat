@echo off
set LLM_MODEL=Qwen/Qwen2.5-3B-Instruct
python -m streamlit run app.py --server.port 8501
