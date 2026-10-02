"""
Milestone 5 Test Suite
Tests for RAG Pipeline with LLM (Rule-based implementation)
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ingestion import LoaderFactory, DataNormalizer
from src.profiling import DataProfiler
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore
from src.rag_pipeline import RAGPipeline, RAGContext, RAGResponse


def test_context_retrieval():
    """Test context retrieval from vector store"""
    print("=" * 60)
    print("TEST: Context Retrieval")
    print("=" * 60)

    try:
        # Setup
        embed_gen = EmbeddingGenerator()
        dimension = embed_gen.get_embedding_dimension()
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        # Add test documents
        texts = [
            "Document about data quality assessment",
            "Document about machine learning",
            "Document about data preprocessing"
        ]
        embeddings = embed_gen.generate_embeddings(texts)
        documents = [{"id": i+1, "content": texts[i]} for i in range(len(texts))]
        vector_store.add_embeddings(embeddings, documents)

        # Create RAG pipeline
        rag = RAGPipeline(vector_store, embed_gen)

        # Test retrieval
        query = "data quality metrics"
        context = rag.retrieve_context(query, k=2)

        # Verify
        assert context.query == query, "Query mismatch"
        assert len(context.retrieved_documents) == 2, "Should retrieve 2 documents"
        assert len(context.similarities) == 2, "Should have 2 similarities"
        assert len(context.context_text) > 0, "Context text should not be empty"

        print("[PASS] Context retrieval successful")
        print(f"  Query: {context.query}")
        print(f"  Retrieved documents: {len(context.retrieved_documents)}")
        print(f"  Context text length: {len(context.context_text)}")

        return True
    except Exception as e:
        print(f"[FAIL] Context retrieval failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_construction():
    """Test prompt construction for LLM"""
    print("\n" + "=" * 60)
    print("TEST: Prompt Construction")
    print("=" * 60)

    try:
        # Load sample data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate metadata
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Create mock context
        from src.rag_pipeline import RAGContext
        context = RAGContext(
            query="Why is the quality score low?",
            retrieved_documents=[{"source_file": "test.csv", "format": "CSV", "quality_score": 75}],
            similarities=[0.5],
            context_text="Mock context"
        )

        # Create RAG pipeline
        embed_gen = EmbeddingGenerator()
        vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
        rag = RAGPipeline(vector_store, embed_gen)

        # Construct prompt
        prompt = rag.construct_prompt("Why is the quality score low?", context, metadata)

        # Verify
        assert len(prompt) > 0, "Prompt should not be empty"
        assert "data quality expert" in prompt.lower(), "Prompt should contain role description"
        assert str(metadata.quality_score) in prompt, "Prompt should contain quality score"
        assert context.context_text in prompt, "Prompt should contain context"

        print("[PASS] Prompt construction successful")
        print(f"  Prompt length: {len(prompt)} characters")
        print(f"  Contains quality score: {str(metadata.quality_score) in prompt}")
        print(f"  Contains context: {context.context_text in prompt}")

        return True
    except Exception as e:
        print(f"[FAIL] Prompt construction failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rule_based_response():
    """Test rule-based response generation"""
    print("\n" + "=" * 60)
    print("TEST: Rule-Based Response Generation")
    print("=" * 60)

    try:
        # Load sample data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate metadata
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Create mock context
        context = RAGContext(
            query="What are the main quality issues?",
            retrieved_documents=[{"source_file": "test.csv", "format": "CSV", "quality_score": 75}],
            similarities=[0.5],
            context_text="Mock context"
        )

        # Create RAG pipeline
        embed_gen = EmbeddingGenerator()
        vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
        rag = RAGPipeline(vector_store, embed_gen)

        # Generate response
        response = rag.generate_response_rule_based("What are the main quality issues?", context, metadata)

        # Verify
        assert response.query == "What are the main quality issues?", "Query mismatch"
        assert len(response.explanation) > 0, "Explanation should not be empty"
        assert len(response.recommendations) > 0, "Should have recommendations"
        assert len(response.quality_assessment) > 0, "Should have quality assessment"
        assert len(response.sources) > 0, "Should have sources"

        print("[PASS] Rule-based response generation successful")
        print(f"  Explanation length: {len(response.explanation)}")
        print(f"  Recommendations: {len(response.recommendations)}")
        print(f"  Quality assessment: {response.quality_assessment}")
        print(f"  Sources: {response.sources}")

        return True
    except Exception as e:
        print(f"[FAIL] Rule-based response generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_response_placeholder():
    """Test LLM response generation (placeholder)"""
    print("\n" + "=" * 60)
    print("TEST: LLM Response Generation (Placeholder)")
    print("=" * 60)

    try:
        # Load sample data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate metadata
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Create mock context
        context = RAGContext(
            query="How can I improve data quality?",
            retrieved_documents=[{"source_file": "test.csv", "format": "CSV", "quality_score": 75}],
            similarities=[0.5],
            context_text="Mock context"
        )

        # Create RAG pipeline
        embed_gen = EmbeddingGenerator()
        vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
        rag = RAGPipeline(vector_store, embed_gen)

        # Generate response without LLM (should fall back to rule-based)
        response = rag.generate_response_llm("How can I improve data quality?", context, metadata, llm_client=None)

        # Verify
        assert response.query == "How can I improve data quality?", "Query mismatch"
        assert len(response.explanation) > 0, "Explanation should not be empty"
        assert len(response.recommendations) > 0, "Should have recommendations"

        print("[PASS] LLM response placeholder successful (falls back to rule-based)")
        print(f"  Explanation length: {len(response.explanation)}")
        print(f"  Recommendations: {len(response.recommendations)}")

        return True
    except Exception as e:
        print(f"[FAIL] LLM response placeholder failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_complete_rag_pipeline():
    """Test complete RAG pipeline"""
    print("\n" + "=" * 60)
    print("TEST: Complete RAG Pipeline")
    print("=" * 60)

    try:
        # Load sample data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate metadata
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Generate textual metadata
        textual_metadata = metadata_gen.generate_textual_metadata(metadata)

        # Setup vector store
        embed_gen = EmbeddingGenerator()
        dimension = embed_gen.get_embedding_dimension()
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        # Add document to vector store
        embedding = embed_gen.generate_embedding(textual_metadata)
        document = {
            "source_file": metadata.source_file,
            "format": metadata.source_format,
            "quality_score": metadata.quality_score,
            "metadata": textual_metadata
        }
        vector_store.add_embeddings([embedding], [document])

        # Create RAG pipeline
        rag = RAGPipeline(vector_store, embed_gen)

        # Execute query
        query = "What are the main data quality issues?"
        response = rag.query(query, metadata, k=1, use_llm=False)

        # Verify
        assert response.query == query, "Query mismatch"
        assert len(response.explanation) > 0, "Explanation should not be empty"
        assert len(response.recommendations) > 0, "Should have recommendations"
        assert len(response.quality_assessment) > 0, "Should have quality assessment"

        print("[PASS] Complete RAG pipeline successful")
        print(f"  Query: {response.query}")
        print(f"  Explanation length: {len(response.explanation)}")
        print(f"  Recommendations: {len(response.recommendations)}")
        print(f"  Quality assessment: {response.quality_assessment}")
        print(f"  Retrieved documents: {len(response.context.retrieved_documents)}")

        return True
    except Exception as e:
        print(f"[FAIL] Complete RAG pipeline failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_backward_compatibility():
    """Test backward compatibility with previous milestones"""
    print("\n" + "=" * 60)
    print("TEST: Backward Compatibility")
    print("=" * 60)

    try:
        # Test Milestone 1 functionality
        from src.data_ingestion import DataIngestion
        from src.profiling import DataProfiler

        # Test Milestone 2 functionality
        from src.ingestion import LoaderFactory, DataNormalizer

        # Test Milestone 3 functionality
        from src.quality_metrics import QualityMetrics

        # Test Milestone 4 functionality
        from src.metadata_generator import MetadataGenerator
        from src.embeddings import EmbeddingGenerator
        from src.vector_store import VectorStore

        # Test that all still work
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        assert quality_report.quality_score == 75.0, "Quality score changed"

        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        embed_gen = EmbeddingGenerator()
        embedding = embed_gen.generate_embedding("test")

        vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")

        print("[PASS] Backward compatibility maintained")
        print("  Milestone 1: DataIngestion, DataProfiler - OK")
        print("  Milestone 2: LoaderFactory, DataNormalizer - OK")
        print("  Milestone 3: QualityMetrics - OK")
        print("  Milestone 4: MetadataGenerator, EmbeddingGenerator, VectorStore - OK")

        return True
    except Exception as e:
        print(f"[FAIL] Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rag_with_different_quality_scores():
    """Test RAG with different quality scores"""
    print("\n" + "=" * 60)
    print("TEST: RAG with Different Quality Scores")
    print("=" * 60)

    try:
        # Create RAG pipeline
        embed_gen = EmbeddingGenerator()
        vector_store = VectorStore(dimension=embed_gen.get_embedding_dimension(), index_type="flat")
        rag = RAGPipeline(vector_store, embed_gen)

        # Test with high quality score
        from src.rag_pipeline import RAGContext
        high_quality_context = RAGContext(
            query="How is the data quality?",
            retrieved_documents=[],
            similarities=[],
            context_text=""
        )

        # Create mock metadata with high quality
        from src.metadata_generator import DatasetMetadata
        high_metadata = DatasetMetadata(
            source_file="high_quality.csv",
            source_format="CSV",
            data_category="structured",
            quality_score=95.0,
            completeness_score=98.0,
            consistency_score=97.0,
            validity_score=96.0,
            quality_issues=[]
        )

        high_response = rag.generate_response_rule_based("How is the data quality?", high_quality_context, high_metadata)

        # Test with low quality score
        low_metadata = DatasetMetadata(
            source_file="low_quality.csv",
            source_format="CSV",
            data_category="structured",
            quality_score=35.0,
            completeness_score=40.0,
            consistency_score=45.0,
            validity_score=50.0,
            quality_issues=[
                {"issue_type": "missing_values", "severity": "critical", "description": "Many missing values"}
            ]
        )

        low_response = rag.generate_response_rule_based("How is the data quality?", high_quality_context, low_metadata)

        # Verify different assessments
        assert "Excellent" in high_response.quality_assessment or "Good" in high_response.quality_assessment, "High quality should have positive assessment"
        assert "Critical" in low_response.quality_assessment or "Poor" in low_response.quality_assessment, "Low quality should have negative assessment"

        print("[PASS] RAG with different quality scores successful")
        print(f"  High quality assessment: {high_response.quality_assessment}")
        print(f"  Low quality assessment: {low_response.quality_assessment}")

        return True
    except Exception as e:
        print(f"[FAIL] RAG with different quality scores failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MILESTONE 5 TEST SUITE")
    print("RAG Pipeline with LLM (Rule-based Implementation)")
    print("=" * 60)

    tests = [
        ("Context Retrieval", test_context_retrieval),
        ("Prompt Construction", test_prompt_construction),
        ("Rule-Based Response Generation", test_rule_based_response),
        ("LLM Response Placeholder", test_llm_response_placeholder),
        ("Complete RAG Pipeline", test_complete_rag_pipeline),
        ("Backward Compatibility", test_backward_compatibility),
        ("RAG with Different Quality Scores", test_rag_with_different_quality_scores)
    ]

    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("ALL TESTS PASSED [PASS]")
    else:
        print("SOME TESTS FAILED [FAIL]")
    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
