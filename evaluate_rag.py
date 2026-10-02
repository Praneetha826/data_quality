"""
RAG Evaluation Script
Evaluates RAG pipeline on evaluation datasets
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


def evaluate_rag(dataset_path, dataset_name):
    """Evaluate RAG pipeline on a single dataset"""
    print(f"\n{'='*60}")
    print(f"Evaluating RAG on: {dataset_name}")
    print(f"{'='*60}")

    # Load dataset
    start_time = time.time()
    asset = LoaderFactory.load_file(dataset_path)
    normalized = DataNormalizer.normalize(asset)
    load_time = time.time() - start_time

    # Quality assessment
    start_time = time.time()
    metrics = QualityMetrics()
    quality_report = metrics.assess_quality(normalized)
    quality_time = time.time() - start_time

    # Metadata generation
    start_time = time.time()
    metadata_gen = MetadataGenerator()
    metadata = metadata_gen.generate_metadata(normalized, quality_report)
    textual_metadata = metadata_gen.generate_textual_metadata(metadata)
    metadata_time = time.time() - start_time

    # Embedding generation
    start_time = time.time()
    embed_gen = EmbeddingGenerator()
    embedding = embed_gen.generate_embedding(textual_metadata)
    embedding_time = time.time() - start_time

    # Vector store setup
    start_time = time.time()
    vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
    document = {
        "source_file": metadata.source_file,
        "format": metadata.source_format,
        "quality_score": metadata.quality_score,
        "metadata": textual_metadata
    }
    vector_store.add_embeddings([embedding], [document])
    vector_time = time.time() - start_time

    # RAG pipeline
    start_time = time.time()
    rag = RAGPipeline(vector_store, embed_gen, llm_client=None)
    rag_time = time.time() - start_time

    # Evaluation questions
    questions = [
        "Why does this dataset have a low quality score?",
        "What are the major quality problems?",
        "Which columns contain missing values?",
        "What duplicate problems were detected?",
        "What outliers were detected?",
        "What corrective actions are recommended?",
        "What is the overall quality score?",
        "Which issues have the highest severity?"
    ]

    results = []
    for question in questions:
        q_start = time.time()
        response = rag.query(question, metadata, k=1, use_llm=False)
        q_time = time.time() - q_start

        result = {
            "question": question,
            "explanation": response.explanation,
            "recommendations": response.recommendations,
            "quality_assessment": response.quality_assessment,
            "used_llm": response.used_llm,
            "query_time": round(q_time, 3),
            "retrieved_context": {
                "document_count": len(response.context.retrieved_documents),
                "similarities": response.context.similarities
            }
        }
        results.append(result)

        print(f"\nQ: {question}")
        print(f"Response Source: {'LLM' if response.used_llm else 'Rule-Based'}")
        print(f"Query Time: {q_time:.3f}s")
        print(f"Explanation Length: {len(response.explanation)}")
        print(f"Recommendations: {len(response.recommendations)}")

    # Total performance
    total_time = load_time + quality_time + metadata_time + embedding_time + vector_time + rag_time

    summary = {
        "dataset": dataset_name,
        "source_file": metadata.source_file,
        "format": metadata.source_format,
        "quality_score": float(quality_report.quality_score),
        "total_issues": len(quality_report.issues),
        "performance": {
            "load_time": round(load_time, 3),
            "quality_time": round(quality_time, 3),
            "metadata_time": round(metadata_time, 3),
            "embedding_time": round(embedding_time, 3),
            "vector_time": round(vector_time, 3),
            "rag_time": round(rag_time, 3),
            "total_time": round(total_time, 3)
        },
        "rag_results": results,
        "evaluation_timestamp": datetime.utcnow().isoformat()
    }

    return summary


def main():
    """Run RAG evaluation on structured datasets"""
    print("="*60)
    print("RAG EVALUATION")
    print("="*60)

    # Define datasets to evaluate (structured only for meaningful RAG)
    datasets = [
        ("evaluation/structured/clean_dataset.csv", "clean_dataset.csv"),
        ("evaluation/structured/missing_values.csv", "missing_values.csv"),
        ("evaluation/structured/duplicate_records.csv", "duplicate_records.csv"),
        ("evaluation/structured/outlier_dataset.csv", "outlier_dataset.csv"),
        ("evaluation/structured/type_inconsistency.csv", "type_inconsistency.csv"),
        ("evaluation/structured/mixed_quality_dataset.csv", "mixed_quality_dataset.csv"),
    ]

    results = []
    for dataset_path, dataset_name in datasets:
        try:
            result = evaluate_rag(dataset_path, dataset_name)
            results.append(result)
        except Exception as e:
            print(f"ERROR evaluating RAG on {dataset_name}: {e}")
            import traceback
            traceback.print_exc()

    # Save results
    output_file = "evaluation/reports/rag_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"RAG results saved to: {output_file}")
    print(f"{'='*60}")

    # Generate markdown report
    generate_rag_markdown_report(results)

    return results


def generate_rag_markdown_report(results):
    """Generate human-readable RAG markdown report"""
    output_file = "evaluation/reports/rag_results.md"

    with open(output_file, 'w') as f:
        f.write("# RAG Evaluation Report\n\n")
        f.write(f"**Generated:** {datetime.utcnow().isoformat()}\n\n")
        f.write(f"**Total Datasets Evaluated:** {len(results)}\n\n")
        f.write("**Note:** RAG responses use rule-based fallback due to Llama 3 authentication requirements.\n\n")

        # Summary statistics
        f.write("## Summary Statistics\n\n")
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")

        total_queries = sum(len(r['rag_results']) for r in results)
        avg_query_time = sum(sum(q['query_time'] for q in r['rag_results']) for r in results) / total_queries if total_queries > 0 else 0

        f.write(f"| Total Queries | {total_queries} |\n")
        f.write(f"| Average Query Time | {avg_query_time:.3f}s |\n")
        f.write(f"| Response Source | Rule-Based Fallback (LLM requires authentication) |\n\n")

        # Detailed results
        f.write("## Detailed Results\n\n")
        for result in results:
            f.write(f"### {result['dataset']}\n\n")
            f.write(f"- **Quality Score:** {result['quality_score']}/100\n")
            f.write(f"- **Total Issues:** {result['total_issues']}\n")
            f.write(f"- **Format:** {result['format']}\n\n")

            f.write("**Performance:**\n")
            f.write(f"- Load Time: {result['performance']['load_time']}s\n")
            f.write(f"- Quality Time: {result['performance']['quality_time']}s\n")
            f.write(f"- Metadata Time: {result['performance']['metadata_time']}s\n")
            f.write(f"- Embedding Time: {result['performance']['embedding_time']}s\n")
            f.write(f"- Vector Time: {result['performance']['vector_time']}s\n")
            f.write(f"- RAG Time: {result['performance']['rag_time']}s\n")
            f.write(f"- Total Time: {result['performance']['total_time']}s\n\n")

            f.write("**RAG Queries:**\n")
            for i, rag_result in enumerate(result['rag_results'], 1):
                f.write(f"\n#### Query {i}: {rag_result['question']}\n\n")
                f.write(f"- **Response Source:** {'LLM' if rag_result['used_llm'] else 'Rule-Based Fallback'}\n")
                f.write(f"- **Query Time:** {rag_result['query_time']}s\n")
                f.write(f"- **Retrieved Documents:** {rag_result['retrieved_context']['document_count']}\n")
                f.write(f"- **Explanation Length:** {len(rag_result['explanation'])} characters\n")
                f.write(f"- **Recommendations:** {len(rag_result['recommendations'])}\n")
                f.write(f"- **Quality Assessment:** {rag_result['quality_assessment']}\n\n")
                f.write(f"**Explanation Preview:**\n")
                f.write(f"{rag_result['explanation'][:200]}...\n\n")
                f.write(f"**Recommendations:**\n")
                for j, rec in enumerate(rag_result['recommendations'][:3], 1):
                    f.write(f"{j}. {rec}\n")
                if len(rag_result['recommendations']) > 3:
                    f.write(f"... and {len(rag_result['recommendations']) - 3} more\n")
                f.write("\n---\n\n")

    print(f"Markdown report saved to: {output_file}")


if __name__ == "__main__":
    main()
