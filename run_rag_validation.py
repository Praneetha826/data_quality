"""
Focused RAG Validation
Tests RAG with representative problematic and clean files
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingestion import LoaderFactory, DataNormalizer
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline
from src.llm_client import LLMClient
import json

def test_rag(filepath, query):
    """Test RAG with a specific file and query"""
    print(f"\n{'='*60}")
    print(f"Testing RAG: {os.path.basename(filepath)}")
    print(f"Query: {query}")
    print(f"{'='*60}")
    
    try:
        # Load and process file
        asset = LoaderFactory.load_file(filepath)
        normalized = DataNormalizer.normalize(asset)
        
        # Quality assessment
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        
        # Metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)
        textual_metadata = metadata_gen.generate_textual_metadata(metadata)
        
        # Embeddings
        embed_gen = EmbeddingGenerator()
        embedding = embed_gen.generate_embedding(textual_metadata)
        
        # Vector store
        dimension = embed_gen.get_embedding_dimension()
        vector_store = VectorStore(dimension=dimension, index_type="flat")
        document = {
            "source_file": metadata.source_file,
            "format": metadata.source_format,
            "quality_score": metadata.quality_score,
            "metadata": textual_metadata
        }
        vector_store.add_embeddings([embedding], [document])
        
        # LLM client - use Gemini from environment
        provider = os.getenv("LLM_PROVIDER", "local").lower()
        if provider == "gemini":
            llm_client = LLMClient(device="cpu")  # Don't pass model_name for Gemini
        else:
            llm_client = LLMClient(model_name="meta-llama/Meta-Llama-3-8B-Instruct", device="cpu")
        
        # RAG pipeline
        rag = RAGPipeline(vector_store, embed_gen, llm_client=llm_client)
        
        # Generate response
        response = rag.query(query, metadata, k=2, use_llm=True)
        
        # Results
        results = {
            'file': os.path.basename(filepath),
            'query': query,
            'python_quality_score': float(quality_report.quality_score),
            'used_llm': response.used_llm,
            'llm_model': response.model_name,
            'llm_provider': llm_client.provider if llm_client else 'unknown',
            'response_explanation': response.explanation,
            'response_recommendations': response.recommendations,
            'detected_issues': [(i.issue_type, i.severity.value, i.description) for i in quality_report.issues],
            'component_scores_applicable': quality_report.component_scores_applicable,
            'success': True
        }
        
        # Print results
        print(f"Python Quality Score: {results['python_quality_score']:.1f}/100")
        print(f"Used LLM: {results['used_llm']}")
        print(f"LLM Model: {results['llm_model']}")
        print(f"LLM Provider: {results['llm_provider']}")
        print(f"\nDetected Issues ({len(results['detected_issues'])}):")
        for issue_type, severity, desc in results['detected_issues']:
            print(f"  - [{severity.upper()}] {issue_type}: {desc}")
        
        print(f"\nRAG Explanation:")
        print(results['response_explanation'][:500] + "..." if len(results['response_explanation']) > 500 else results['response_explanation'])
        
        print(f"\nRecommendations ({len(results['response_recommendations'])}):")
        for i, rec in enumerate(results['response_recommendations'][:3], 1):
            print(f"  {i}. {rec[:100]}..." if len(rec) > 100 else f"  {i}. {rec}")
        
        return results
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'file': os.path.basename(filepath),
            'success': False,
            'error': str(e)
        }

def main():
    print("="*60)
    print("FOCUSED RAG VALIDATION")
    print("="*60)
    
    test_cases = [
        # CSV - problematic
        {
            'file': 'data/sample/test_csv_issues.csv',
            'query': 'What are the main quality issues in this dataset and what should be done about them?'
        },
        # CSV - clean
        {
            'file': 'data/sample/test_csv_clean.csv',
            'query': 'What is the quality of this dataset?'
        },
        # TXT - problematic
        {
            'file': 'data/sample/test_txt_problematic.txt',
            'query': 'What quality issues does this text have?'
        },
        # TXT - clean
        {
            'file': 'data/sample/test_txt_clean.txt',
            'query': 'Is this text high quality?'
        },
        # PDF - problematic
        {
            'file': 'data/sample/test_pdf_problematic.pdf',
            'query': 'What are the quality issues in this document?'
        },
        # PDF - clean
        {
            'file': 'data/sample/test_pdf_clean.pdf',
            'query': 'Is this document high quality?'
        },
    ]
    
    all_results = []
    
    for test_case in test_cases:
        result = test_rag(test_case['file'], test_case['query'])
        all_results.append(result)
    
    # Summary
    print("\n" + "="*60)
    print("RAG VALIDATION SUMMARY")
    print("="*60)
    
    successful = sum(1 for r in all_results if r.get('success', False))
    llm_used = sum(1 for r in all_results if r.get('used_llm', False))
    failed = len(all_results) - successful
    
    print(f"Total Tests: {len(all_results)}")
    print(f"Successful (no errors): {successful}")
    print(f"LLM Used: {llm_used}")
    print(f"Failed: {failed}")
    
    print("\nDetailed Results:")
    for result in all_results:
        if result.get('success'):
            llm_status = "[LLM]" if result.get('used_llm') else "[NO LLM]"
            print(f"[PASS] {result['file']}: {llm_status} Python Score {result['python_quality_score']:.1f}/100")
        else:
            print(f"[FAIL] {result['file']}: {result.get('error', 'Unknown error')}")
    
    # Save results
    with open('rag_validation.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to rag_validation.json")

if __name__ == "__main__":
    main()
