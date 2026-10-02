"""
RAG Pipeline Module
Implements Retrieval-Augmented Generation pipeline for data quality explanations
"""

from typing import List, Dict, Any, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
import json
import os

if TYPE_CHECKING:
    from src.metadata_generator import DatasetMetadata
    from src.llm_client import LLMClient


@dataclass
class RAGContext:
    """
    Context retrieved from vector store for RAG
    """
    query: str
    retrieved_documents: List[Dict[str, Any]]
    similarities: List[float]
    context_text: str


@dataclass
class RAGResponse:
    """
    Response from RAG pipeline
    """
    query: str
    context: RAGContext
    explanation: str
    recommendations: List[str]
    quality_assessment: str
    sources: List[str]
    used_llm: bool = False  # True if LLM was used, False if rule-based fallback
    model_name: str = "rule-based"  # Name of the model that generated the response


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline for data quality explanations
    """

    def __init__(self, vector_store, embedding_generator, llm_client=None):
        """
        Initialize the RAG pipeline

        Args:
            vector_store: VectorStore instance for semantic search
            embedding_generator: EmbeddingGenerator for query embedding
            llm_client: LLMClient for LLM integration (optional)
        """
        self.vector_store = vector_store
        self.embedding_generator = embedding_generator
        self.llm_client = llm_client

    def retrieve_context(self, query: str, k: int = 3) -> RAGContext:
        """
        Retrieve relevant context from vector store

        Args:
            query: User query
            k: Number of documents to retrieve

        Returns:
            RAGContext with retrieved documents
        """
        # Generate query embedding
        query_embedding = self.embedding_generator.generate_embedding(query)

        # Search vector store
        results = self.vector_store.search(query_embedding, k=k)

        # Extract documents and similarities
        retrieved_documents = [doc for _, doc in results]
        similarities = [dist for dist, _ in results]

        # Build context text
        context_parts = []
        for i, (doc, similarity) in enumerate(zip(retrieved_documents, similarities)):
            context_parts.append(f"Document {i+1} (similarity: {similarity:.4f}):")
            context_parts.append(f"  Source: {doc.get('source_file', 'Unknown')}")
            context_parts.append(f"  Format: {doc.get('format', 'Unknown')}")
            context_parts.append(f"  Quality Score: {doc.get('quality_score', 'Unknown')}")
            if 'metadata' in doc:
                context_parts.append(f"  Metadata: {doc['metadata'][:500]}...")

        context_text = "\n".join(context_parts)

        return RAGContext(
            query=query,
            retrieved_documents=retrieved_documents,
            similarities=similarities,
            context_text=context_text
        )

    def construct_prompt(self, query: str, context: RAGContext, metadata: 'DatasetMetadata') -> str:
        """
        Construct prompt for LLM

        Args:
            query: User query
            context: Retrieved context
            metadata: Dataset metadata

        Returns:
            Constructed prompt string
        """
        prompt = f"""You are a data quality expert assistant. Your task is to analyze data quality issues and provide explanations and recommendations based on the provided context.

USER QUERY:
{query}

RETRIEVED CONTEXT (from similar datasets):
{context.context_text}

QUALITY INFORMATION:
- Source: {metadata.source_file}
- Format: {metadata.source_format}
- Category: {metadata.data_category}
- Quality Score: {metadata.quality_score}/100 (deterministically calculated by Python/Pandas - DO NOT MODIFY)
- Completeness: {metadata.completeness_score}/100
- Consistency: {metadata.consistency_score}/100
- Validity: {metadata.validity_score}/100

QUALITY ISSUES DETECTED:
"""

        # Add quality issues
        for issue in metadata.quality_issues:
            prompt += f"- {issue['issue_type']} ({issue['severity']}): {issue['description']}\n"

        prompt += f"""
INSTRUCTIONS:
1. Analyze the quality issues in the context of the user's query
2. Use ONLY the provided context for dataset-specific facts
3. Do NOT invent or modify quality metrics or scores
4. Do NOT change the calculated quality score of {metadata.quality_score}/100
5. Provide a clear explanation of the issues and their possible impact
6. Give specific, actionable recommendations based on the detected issues
7. Consider the severity of each issue when prioritizing recommendations
8. If the context does not contain enough information to answer the query, state that clearly

RESPONSE FORMAT:
EXPLANATION: [Your explanation of the quality issues and their impact]
RECOMMENDATIONS: [List of specific, actionable recommendations based on detected issues]
QUALITY ASSESSMENT: [Your assessment based on the provided quality score of {metadata.quality_score}/100]
"""

        return prompt

    def generate_response_rule_based(self, query: str, context: RAGContext, metadata: 'DatasetMetadata') -> RAGResponse:
        """
        Generate response using rule-based approach (for demonstration without LLM)

        Args:
            query: User query
            context: Retrieved context
            metadata: Dataset metadata

        Returns:
            RAGResponse with explanations and recommendations
        """
        # Generate explanation based on quality issues
        explanation_parts = []
        explanation_parts.append(f"Dataset {metadata.source_file} has a quality score of {metadata.quality_score}/100.")

        if metadata.quality_score >= 90:
            explanation_parts.append("The data quality is excellent with minimal issues.")
        elif metadata.quality_score >= 75:
            explanation_parts.append("The data quality is good with some minor issues that should be addressed.")
        elif metadata.quality_score >= 60:
            explanation_parts.append("The data quality is fair and requires attention for several issues.")
        elif metadata.quality_score >= 40:
            explanation_parts.append("The data quality is poor with significant issues that should be addressed.")
        else:
            explanation_parts.append("The data quality is critically compromised and requires immediate attention.")

        # Add specific issue explanations
        if metadata.quality_issues:
            explanation_parts.append("\nSpecific issues detected:")
            for issue in metadata.quality_issues[:5]:  # Limit to top 5
                explanation_parts.append(f"- {issue['issue_type']}: {issue['description']}")

        explanation = "\n".join(explanation_parts)

        # Generate recommendations
        recommendations = []

        if metadata.completeness_score < 100:
            recommendations.append("Address missing values by imputation or data collection")

        if metadata.consistency_score < 100:
            recommendations.append("Remove duplicate records and standardize data formats")

        if metadata.validity_score < 100:
            recommendations.append("Validate data types and correct invalid values")

        if metadata.quality_score < 75:
            recommendations.append("Implement data quality monitoring and validation processes")

        if metadata.quality_score < 60:
            recommendations.append("Consider comprehensive data cleaning and validation before use")

        # Add specific recommendations based on issue types
        issue_types = set(issue['issue_type'] for issue in metadata.quality_issues)
        if 'missing_values' in issue_types:
            recommendations.append("Investigate and address missing value patterns")
        if 'duplicate_rows' in issue_types:
            recommendations.append("Review and remove duplicate records")
        if 'outliers' in issue_types:
            recommendations.append("Analyze outliers and determine if they are valid or errors")
        if 'date_as_string' in issue_types:
            recommendations.append("Convert date strings to proper datetime format")

        # Quality assessment
        if metadata.quality_score >= 90:
            quality_assessment = "Excellent - Data is ready for use with minimal concerns"
        elif metadata.quality_score >= 75:
            quality_assessment = "Good - Data is suitable for most use cases with minor cleanup"
        elif metadata.quality_score >= 60:
            quality_assessment = "Fair - Data requires quality improvements before production use"
        elif metadata.quality_score >= 40:
            quality_assessment = "Poor - Data needs significant quality improvements"
        else:
            quality_assessment = "Critical - Data is not suitable for use without major corrections"

        # Sources
        sources = [doc.get('source_file', 'Unknown') for doc in context.retrieved_documents]

        return RAGResponse(
            query=query,
            context=context,
            explanation=explanation,
            recommendations=recommendations,
            quality_assessment=quality_assessment,
            sources=sources,
            used_llm=False,
            model_name="rule-based"
        )

    def generate_response_llm(self, query: str, context: RAGContext, metadata: 'DatasetMetadata', llm_client: Optional['LLMClient'] = None) -> RAGResponse:
        """
        Generate response using LLM

        Args:
            query: User query
            context: Retrieved context
            metadata: Dataset metadata
            llm_client: LLM client (optional, uses instance client if not provided)

        Returns:
            RAGResponse with explanations and recommendations
        """
        # Use provided client or instance client
        client = llm_client if llm_client is not None else self.llm_client

        debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        if debug_mode:
            print(f"DEBUG RAG: client is None: {client is None}")
            print(f"DEBUG RAG: client.is_available(): {client.is_available() if client else 'N/A'}")
            if client:
                print(f"DEBUG RAG: client.provider: {client.provider}")
                print(f"DEBUG RAG: client.model_name: {client.model_name}")

        # Check if LLM is available
        if client is None or not client.is_available():
            print("LLM not available, falling back to rule-based response")
            return self.generate_response_rule_based(query, context, metadata)

        try:
            # Get model name for tracking
            model_name = client.model_name
            if debug_mode:
                print(f"DEBUG RAG: Generating with model: {model_name}")

            # Construct prompt
            prompt = self.construct_prompt(query, context, metadata)
            if debug_mode:
                print(f"DEBUG RAG: Prompt constructed, length={len(prompt)}")

            # Generate response from LLM
            llm_response = client.generate(prompt)
            if debug_mode:
                print(f"DEBUG RAG: LLM generation succeeded")

            # Parse LLM response
            explanation, recommendations, quality_assessment = self._parse_llm_response(llm_response)

            # Fallback if parsing fails
            if not explanation or not recommendations:
                print("Failed to parse LLM response, falling back to rule-based")
                return self.generate_response_rule_based(query, context, metadata)

            # Sources
            sources = [doc.get('source_file', 'Unknown') for doc in context.retrieved_documents]

            return RAGResponse(
                query=query,
                context=context,
                explanation=explanation,
                recommendations=recommendations,
                quality_assessment=quality_assessment,
                sources=sources,
                used_llm=True,
                model_name=model_name
            )

        except Exception as e:
            debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
            if debug_mode:
                print(f"DEBUG RAG ERROR: LLM generation failed")
                print(f"DEBUG RAG ERROR: Exception type: {type(e).__name__}")
                print(f"DEBUG RAG ERROR: Exception message: {str(e)}")
                print(f"DEBUG RAG ERROR: falling back to rule-based")
            return self.generate_response_rule_based(query, context, metadata)

    def _parse_llm_response(self, llm_response: str) -> Tuple[str, List[str], str]:
        """
        Parse LLM response to extract explanation, recommendations, and quality assessment

        Args:
            llm_response: Raw response from LLM

        Returns:
            Tuple of (explanation, recommendations, quality_assessment)
        """
        explanation = ""
        recommendations = []
        quality_assessment = ""

        lines = llm_response.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("EXPLANATION:"):
                current_section = "explanation"
                explanation = line.replace("EXPLANATION:", "").strip()
            elif line.startswith("RECOMMENDATIONS:"):
                current_section = "recommendations"
                rec_text = line.replace("RECOMMENDATIONS:", "").strip()
                if rec_text:
                    recommendations.append(rec_text)
            elif line.startswith("QUALITY ASSESSMENT:"):
                current_section = "assessment"
                quality_assessment = line.replace("QUALITY ASSESSMENT:", "").strip()
            else:
                if current_section == "explanation":
                    explanation += " " + line
                elif current_section == "recommendations":
                    if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                        recommendations.append(line.lstrip("-*• "))
                    elif line and not line.isdigit():
                        recommendations.append(line)
                elif current_section == "assessment":
                    quality_assessment += " " + line

        # Clean up
        explanation = explanation.strip()
        quality_assessment = quality_assessment.strip()

        # Default values if parsing failed
        if not explanation:
            explanation = "Could not parse explanation from LLM response"
        if not recommendations:
            recommendations = ["Could not parse recommendations from LLM response"]
        if not quality_assessment:
            quality_assessment = "Could not parse quality assessment from LLM response"

        return explanation, recommendations, quality_assessment

    def query(self, user_query: str, metadata: 'DatasetMetadata', k: int = 3, use_llm: bool = False, llm_client=None) -> RAGResponse:
        """
        Execute complete RAG pipeline

        Args:
            user_query: User's query about data quality
            metadata: Dataset metadata
            k: Number of documents to retrieve
            use_llm: Whether to use LLM (if available)
            llm_client: LLM client (optional)

        Returns:
            RAGResponse with explanations and recommendations
        """
        # Retrieve context
        context = self.retrieve_context(user_query, k=k)

        # Generate response
        if use_llm:
            response = self.generate_response_llm(user_query, context, metadata, llm_client)
        else:
            response = self.generate_response_rule_based(user_query, context, metadata)

        return response
