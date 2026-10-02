"""
Simplified Performance Measurement Script
Measures execution time for each pipeline component
"""

import sys
import os
import json
import time
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline


def measure_performance(dataset_path):
    """Measure performance for complete pipeline"""
    print(f"\n{'='*60}")
    print(f"Measuring Performance: {os.path.basename(dataset_path)}")
    print(f"{'='*60}")

    timings = {}

    # 1. File Loading
    start = time.time()
    asset = LoaderFactory.load_file(dataset_path)
    normalized = DataNormalizer.normalize(asset)
    timings['file_loading'] = time.time() - start
    print(f"File Loading: {timings['file_loading']:.4f}s")

    # 2. Quality Assessment
    start = time.time()
    metrics = QualityMetrics()
    quality_report = metrics.assess_quality(normalized)
    timings['quality_assessment'] = time.time() - start
    print(f"Quality Assessment: {timings['quality_assessment']:.4f}s")

    # 3. Metadata Generation
    start = time.time()
    metadata_gen = MetadataGenerator()
    metadata = metadata_gen.generate_metadata(normalized, quality_report)
    textual_metadata = metadata_gen.generate_textual_metadata(metadata)
    timings['metadata_generation'] = time.time() - start
    print(f"Metadata Generation: {timings['metadata_generation']:.4f}s")

    # 4. Embedding Generation
    start = time.time()
    embed_gen = EmbeddingGenerator()
    embedding = embed_gen.generate_embedding(textual_metadata)
    timings['embedding_generation'] = time.time() - start
    print(f"Embedding Generation: {timings['embedding_generation']:.4f}s")

    # 5. FAISS Indexing
    start = time.time()
    vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
    document = {
        "source_file": metadata.source_file,
        "format": metadata.source_format,
        "quality_score": metadata.quality_score,
        "metadata": textual_metadata
    }
    vector_store.add_embeddings([embedding], [document])
    timings['faiss_indexing'] = time.time() - start
    print(f"FAISS Indexing: {timings['faiss_indexing']:.4f}s")

    # 6. FAISS Retrieval
    start = time.time()
    query_embedding = embed_gen.generate_embedding("data quality metrics")
    results = vector_store.search(query_embedding, k=3)
    timings['faiss_retrieval'] = time.time() - start
    print(f"FAISS Retrieval: {timings['faiss_retrieval']:.4f}s")

    # 7. RAG Pipeline Setup
    start = time.time()
    rag = RAGPipeline(vector_store, embed_gen, llm_client=None)
    timings['rag_setup'] = time.time() - start
    print(f"RAG Setup: {timings['rag_setup']:.4f}s")

    # 8. RAG Query (Rule-Based)
    start = time.time()
    response = rag.query("What are the main quality issues?", metadata, k=1, use_llm=False)
    timings['rag_query'] = time.time() - start
    print(f"RAG Query: {timings['rag_query']:.4f}s")

    # 9. Database Save (SQLite)
    start = time.time()
    from src.database import DatabaseManager
    db_manager = DatabaseManager("sqlite:///performance_test.db")
    db_manager.create_tables()

    metadata_dict = {
        'source_file': metadata.source_file,
        'source_format': metadata.source_format,
        'data_category': metadata.data_category,
        'rows': len(normalized.tabular_data) if normalized.is_tabular() else None,
        'columns': len(normalized.tabular_data.columns) if normalized.is_tabular() else None,
        'memory_usage_mb': metadata.memory_usage_mb,
        'timestamp': str(metadata.timestamp)
    }

    quality_dict = {
        'quality_score': quality_report.quality_score,
        'completeness_score': quality_report.completeness_score,
        'consistency_score': quality_report.consistency_score,
        'validity_score': quality_report.validity_score,
        'assessment': quality_report.overall_assessment,
        'issues': [
            {
                'issue_type': issue.issue_type,
                'severity': issue.severity.value,
                'description': issue.description,
                'column_name': issue.column_name,
                'row_indices': issue.row_indices
            }
            for issue in quality_report.issues
        ]
    }

    dataset_id = db_manager.save_dataset(metadata_dict, quality_dict)
    timings['database_save'] = time.time() - start
    print(f"Database Save: {timings['database_save']:.4f}s")

    # 10. Database Retrieve
    start = time.time()
    retrieved = db_manager.get_dataset(metadata.source_file)
    timings['database_retrieve'] = time.time() - start
    print(f"Database Retrieve: {timings['database_retrieve']:.4f}s")

    # Total Pipeline
    timings['total_pipeline'] = sum(timings.values())
    print(f"\nTotal Pipeline: {timings['total_pipeline']:.4f}s")

    result = {
        "dataset": os.path.basename(dataset_path),
        "quality_score": float(quality_report.quality_score),
        "timings": {k: round(v, 4) for k, v in timings.items()},
        "measurement_timestamp": datetime.utcnow().isoformat()
    }

    return result


def main():
    """Run performance measurements"""
    print("="*60)
    print("PERFORMANCE MEASUREMENT")
    print("="*60)

    datasets = [
        "evaluation/structured/clean_dataset.csv",
        "evaluation/structured/missing_values.csv",
        "evaluation/structured/mixed_quality_dataset.csv",
    ]

    results = []
    for dataset_path in datasets:
        try:
            result = measure_performance(dataset_path)
            results.append(result)
        except Exception as e:
            print(f"ERROR measuring {dataset_path}: {e}")
            import traceback
            traceback.print_exc()

    # Save results
    output_file = "evaluation/reports/performance_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Performance results saved to: {output_file}")
    print(f"{'='*60}")

    # Generate markdown report
    generate_performance_markdown_report(results)

    return results


def generate_performance_markdown_report(results):
    """Generate performance markdown report"""
    output_file = "evaluation/reports/performance_results.md"

    with open(output_file, 'w') as f:
        f.write("# Performance Measurement Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().isoformat()}\n\n")
        f.write(f"**Total Datasets Measured:** {len(results)}\n\n")

        # Average performance
        f.write("## Average Performance (by operation)\n\n")
        f.write("| Operation | Avg Time (s) |\n")
        f.write("|-----------|--------------|\n")

        operations = ['file_loading', 'quality_assessment', 'metadata_generation',
                     'embedding_generation', 'faiss_indexing', 'faiss_retrieval',
                     'rag_setup', 'rag_query', 'database_save', 'database_retrieve',
                     'total_pipeline']

        for op in operations:
            avg_time = sum(r['timings'].get(op, 0) for r in results) / len(results) if results else 0
            f.write(f"| {op.replace('_', ' ').title()} | {avg_time:.4f} |\n")

        f.write("\n## Detailed Results\n\n")
        for result in results:
            f.write(f"### {result['dataset']}\n\n")
            f.write(f"- **Quality Score:** {result['quality_score']}/100\n\n")
            f.write("**Timings:**\n")
            for op, time_val in result['timings'].items():
                f.write(f"- {op.replace('_', ' ').title()}: {time_val}s\n")
            f.write("\n---\n\n")

    print(f"Markdown report saved to: {output_file}")


if __name__ == "__main__":
    main()
