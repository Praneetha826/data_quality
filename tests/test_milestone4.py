"""
Milestone 4 Test Suite
Tests for Metadata Generation, Embeddings, and Vector Store
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from src.ingestion import LoaderFactory, DataNormalizer
from src.profiling import DataProfiler
from src.quality_metrics import QualityMetrics
from src.metadata_generator import MetadataGenerator, DatasetMetadata
from src.embeddings import EmbeddingGenerator
from src.vector_store import VectorStore


def test_metadata_generation():
    """Test metadata generation for tabular data"""
    print("=" * 60)
    print("TEST: Metadata Generation - Tabular Data")
    print("=" * 60)

    try:
        # Load CSV
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate quality report
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        # Generate metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Verify metadata
        assert metadata.source_file == asset.source_file, "Source file mismatch"
        assert metadata.source_format == "CSV", "Format mismatch"
        assert metadata.data_category == "structured", "Category mismatch"
        assert metadata.total_rows == 20, "Row count mismatch"
        assert metadata.total_columns == 7, "Column count mismatch"
        assert metadata.quality_score == 75.0, "Quality score mismatch"
        assert len(metadata.quality_issues) == 5, "Issue count mismatch"

        print("[PASS] Metadata generated successfully")
        print(f"  Source file: {metadata.source_file}")
        print(f"  Format: {metadata.source_format}")
        print(f"  Rows: {metadata.total_rows}")
        print(f"  Columns: {metadata.total_columns}")
        print(f"  Quality score: {metadata.quality_score}")
        print(f"  Total issues: {metadata.total_issues}")
        print(f"  Issues by type: {metadata.issues_by_type}")

        return True
    except Exception as e:
        print(f"[FAIL] Metadata generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_metadata_generation_text():
    """Test metadata generation for text data"""
    print("\n" + "=" * 60)
    print("TEST: Metadata Generation - Text Data")
    print("=" * 60)

    try:
        # Load TXT
        asset = LoaderFactory.load_file('data/sample/sample_document.txt')
        normalized = DataNormalizer.normalize(asset)

        # Generate quality report
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        # Generate metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Verify metadata
        assert metadata.source_file == asset.source_file, "Source file mismatch"
        assert metadata.source_format == "TXT", "Format mismatch"
        assert metadata.data_category == "unstructured", "Category mismatch"
        assert metadata.character_count > 0, "Character count mismatch"
        assert metadata.word_count > 0, "Word count mismatch"
        assert metadata.line_count > 0, "Line count mismatch"

        print("[PASS] Text metadata generated successfully")
        print(f"  Source file: {metadata.source_file}")
        print(f"  Format: {metadata.source_format}")
        print(f"  Character count: {metadata.character_count}")
        print(f"  Word count: {metadata.word_count}")
        print(f"  Line count: {metadata.line_count}")
        print(f"  Quality score: {metadata.quality_score}")

        return True
    except Exception as e:
        print(f"[FAIL] Text metadata generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_textual_metadata():
    """Test textual metadata generation for embedding"""
    print("\n" + "=" * 60)
    print("TEST: Textual Metadata Generation")
    print("=" * 60)

    try:
        # Load CSV
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate quality report
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        # Generate metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Generate textual metadata
        textual_metadata = metadata_gen.generate_textual_metadata(metadata)

        # Verify textual metadata
        assert len(textual_metadata) > 0, "Textual metadata is empty"
        assert "Dataset:" in textual_metadata, "Dataset information missing"
        assert "Format:" in textual_metadata, "Format information missing"
        assert "Quality score:" in textual_metadata, "Quality score missing"

        print("[PASS] Textual metadata generated successfully")
        print(f"  Text length: {len(textual_metadata)} characters")
        print(f"  Preview (first 200 chars):")
        print("  " + textual_metadata[:200] + "...")

        return True
    except Exception as e:
        print(f"[FAIL] Textual metadata generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chunked_metadata():
    """Test chunked metadata generation"""
    print("\n" + "=" * 60)
    print("TEST: Chunked Metadata Generation")
    print("=" * 60)

    try:
        # Load CSV
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Generate quality report
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        # Generate metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Generate chunked metadata
        chunks = metadata_gen.generate_chunked_metadata(metadata, chunk_size=300)

        # Verify chunks
        assert len(chunks) > 0, "No chunks generated"
        for chunk in chunks:
            assert len(chunk) <= 300, f"Chunk too long: {len(chunk)}"

        print("[PASS] Chunked metadata generated successfully")
        print(f"  Number of chunks: {len(chunks)}")
        print(f"  Chunk sizes: {[len(c) for c in chunks]}")

        return True
    except Exception as e:
        print(f"[FAIL] Chunked metadata generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_embedding_generation():
    """Test embedding generation"""
    print("\n" + "=" * 60)
    print("TEST: Embedding Generation")
    print("=" * 60)

    try:
        # Initialize embedding generator
        embed_gen = EmbeddingGenerator()

        # Test single text embedding
        test_text = "This is a test sentence for embedding generation."
        embedding = embed_gen.generate_embedding(test_text)

        # Verify embedding
        assert isinstance(embedding, np.ndarray), "Embedding is not numpy array"
        assert len(embedding) > 0, "Embedding is empty"
        assert embedding.dtype == np.float32, "Embedding dtype incorrect"

        # Get dimension
        dimension = embed_gen.get_embedding_dimension()
        assert len(embedding) == dimension, "Embedding dimension mismatch"

        print("[PASS] Embedding generated successfully")
        print(f"  Embedding dimension: {dimension}")
        print(f"  Embedding shape: {embedding.shape}")
        print(f"  Embedding dtype: {embedding.dtype}")

        return True
    except Exception as e:
        print(f"[FAIL] Embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_embedding_generation():
    """Test batch embedding generation"""
    print("\n" + "=" * 60)
    print("TEST: Batch Embedding Generation")
    print("=" * 60)

    try:
        # Initialize embedding generator
        embed_gen = EmbeddingGenerator()

        # Test batch embedding
        texts = [
            "First test sentence",
            "Second test sentence",
            "Third test sentence"
        ]
        embeddings = embed_gen.generate_embeddings(texts)

        # Verify embeddings
        assert isinstance(embeddings, np.ndarray), "Embeddings is not numpy array"
        assert embeddings.shape[0] == len(texts), "Number of embeddings mismatch"
        assert embeddings.shape[1] > 0, "Embedding dimension is zero"

        print("[PASS] Batch embeddings generated successfully")
        print(f"  Number of texts: {len(texts)}")
        print(f"  Embeddings shape: {embeddings.shape}")

        return True
    except Exception as e:
        print(f"[FAIL] Batch embedding generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store():
    """Test vector store operations"""
    print("\n" + "=" * 60)
    print("TEST: Vector Store Operations")
    print("=" * 60)

    try:
        # Initialize embedding generator
        embed_gen = EmbeddingGenerator()
        dimension = embed_gen.get_embedding_dimension()

        # Initialize vector store
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        # Test adding embeddings
        texts = [
            "This is a document about data quality",
            "This is a document about data preprocessing",
            "This is a document about data analysis"
        ]
        embeddings = embed_gen.generate_embeddings(texts)

        documents = [
            {"id": 1, "content": texts[0]},
            {"id": 2, "content": texts[1]},
            {"id": 3, "content": texts[2]}
        ]

        vector_store.add_embeddings(embeddings, documents)

        # Verify addition
        assert vector_store.get_size() == 3, "Vector store size mismatch"
        assert not vector_store.is_empty(), "Vector store should not be empty"

        print("[PASS] Vector store operations successful")
        print(f"  Vector store size: {vector_store.get_size()}")
        print(f"  Vector store empty: {vector_store.is_empty()}")

        return True
    except Exception as e:
        print(f"[FAIL] Vector store operations failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_search():
    """Test vector similarity search"""
    print("\n" + "=" * 60)
    print("TEST: Vector Similarity Search")
    print("=" * 60)

    try:
        # Initialize embedding generator
        embed_gen = EmbeddingGenerator()
        dimension = embed_gen.get_embedding_dimension()

        # Initialize vector store
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        # Add documents
        texts = [
            "This is a document about data quality assessment",
            "This is a document about machine learning",
            "This is a document about data preprocessing"
        ]
        embeddings = embed_gen.generate_embeddings(texts)

        documents = [
            {"id": 1, "content": texts[0]},
            {"id": 2, "content": texts[1]},
            {"id": 3, "content": texts[2]}
        ]

        vector_store.add_embeddings(embeddings, documents)

        # Test search
        query_text = "data quality metrics"
        query_embedding = embed_gen.generate_embedding(query_text)
        results = vector_store.search(query_embedding, k=2)

        # Verify results
        assert len(results) > 0, "No search results returned"
        assert len(results) <= 2, "Too many results returned"

        print("[PASS] Vector search successful")
        print(f"  Query: {query_text}")
        print(f"  Number of results: {len(results)}")
        for i, (dist, doc) in enumerate(results):
            print(f"  Result {i+1}: Distance={dist:.4f}, Content={doc['content'][:50]}...")

        return True
    except Exception as e:
        print(f"[FAIL] Vector search failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_vector_store_persistence():
    """Test vector store save and load"""
    print("\n" + "=" * 60)
    print("TEST: Vector Store Persistence")
    print("=" * 60)

    try:
        # Initialize embedding generator
        embed_gen = EmbeddingGenerator()
        dimension = embed_gen.get_embedding_dimension()

        # Initialize vector store
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        # Add data
        texts = ["Test document for persistence"]
        embeddings = embed_gen.generate_embeddings(texts)
        documents = [{"id": 1, "content": texts[0]}]

        vector_store.add_embeddings(embeddings, documents)

        # Save
        save_path = "data/test_vector_store.pkl"
        vector_store.save(save_path)

        # Load
        new_vector_store = VectorStore(dimension=dimension, index_type="flat")
        new_vector_store.load(save_path)

        # Verify
        assert new_vector_store.get_size() == 1, "Loaded vector store size mismatch"

        # Cleanup
        if os.path.exists(save_path):
            os.remove(save_path)

        print("[PASS] Vector store persistence successful")
        print(f"  Saved to: {save_path}")
        print(f"  Loaded size: {new_vector_store.get_size()}")

        return True
    except Exception as e:
        print(f"[FAIL] Vector store persistence failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_end_to_end_pipeline():
    """Test end-to-end pipeline from ingestion to vector store"""
    print("\n" + "=" * 60)
    print("TEST: End-to-End Pipeline")
    print("=" * 60)

    try:
        # Load data
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        # Quality assessment
        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        # Generate metadata
        metadata_gen = MetadataGenerator()
        metadata = metadata_gen.generate_metadata(normalized, quality_report)

        # Generate textual metadata
        textual_metadata = metadata_gen.generate_textual_metadata(metadata)

        # Generate embedding
        embed_gen = EmbeddingGenerator()
        embedding = embed_gen.generate_embedding(textual_metadata)

        # Store in vector store
        dimension = embed_gen.get_embedding_dimension()
        vector_store = VectorStore(dimension=dimension, index_type="flat")

        documents = [{
            "source_file": metadata.source_file,
            "format": metadata.source_format,
            "quality_score": metadata.quality_score,
            "metadata": textual_metadata
        }]

        vector_store.add_embeddings([embedding], documents)

        # Verify
        assert vector_store.get_size() == 1, "Vector store should have 1 document"

        print("[PASS] End-to-end pipeline successful")
        print(f"  Source: {metadata.source_file}")
        print(f"  Quality score: {metadata.quality_score}")
        print(f"  Textual metadata length: {len(textual_metadata)}")
        print(f"  Embedding dimension: {dimension}")
        print(f"  Vector store size: {vector_store.get_size()}")

        return True
    except Exception as e:
        print(f"[FAIL] End-to-end pipeline failed: {e}")
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

        # Test that all still work
        asset = LoaderFactory.load_file('data/sample/sample_dataset.csv')
        normalized = DataNormalizer.normalize(asset)

        metrics = QualityMetrics()
        quality_report = metrics.assess_quality(normalized)

        assert quality_report.quality_score == 75.0, "Quality score changed"

        print("[PASS] Backward compatibility maintained")
        print("  Milestone 1: DataIngestion, DataProfiler - OK")
        print("  Milestone 2: LoaderFactory, DataNormalizer - OK")
        print("  Milestone 3: QualityMetrics - OK")

        return True
    except Exception as e:
        print(f"[FAIL] Backward compatibility test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("MILESTONE 4 TEST SUITE")
    print("Metadata Generation, Embeddings, and Vector Store")
    print("=" * 60)

    tests = [
        ("Metadata Generation - Tabular", test_metadata_generation),
        ("Metadata Generation - Text", test_metadata_generation_text),
        ("Textual Metadata Generation", test_textual_metadata),
        ("Chunked Metadata Generation", test_chunked_metadata),
        ("Embedding Generation", test_embedding_generation),
        ("Batch Embedding Generation", test_batch_embedding_generation),
        ("Vector Store Operations", test_vector_store),
        ("Vector Similarity Search", test_vector_search),
        ("Vector Store Persistence", test_vector_store_persistence),
        ("End-to-End Pipeline", test_end_to_end_pipeline),
        ("Backward Compatibility", test_backward_compatibility)
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
