"""
Embedding service for document chunks optimized for question generation
Handles multiple embedding models and formats for LLM integration
"""

import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

# Embedding model imports
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Service for generating and managing embeddings for document chunks"""
    
    def __init__(self):
        """Initialize embedding service with multiple model options"""
        self.models = {}
        self.default_model = "sentence-transformers"
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available embedding models"""
        
        # 1. Sentence Transformers (Local, Fast, Good for general use)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Use a model optimized for question-answering and retrieval
                self.models["sentence-transformers"] = SentenceTransformer(
                    'all-MiniLM-L6-v2'  # Fast and efficient for semantic search
                )
                logger.info("✅ Sentence Transformers model loaded: all-MiniLM-L6-v2")
            except Exception as e:
                logger.warning(f"Failed to load Sentence Transformers: {e}")
        
        # 2. Better model for question generation context
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                # Model specifically trained for question-answering tasks
                self.models["qa-optimized"] = SentenceTransformer(
                    'multi-qa-MiniLM-L6-cos-v1'  # Optimized for QA tasks
                )
                self.default_model = "qa-optimized"
                logger.info("✅ QA-optimized model loaded: multi-qa-MiniLM-L6-cos-v1")
            except Exception as e:
                logger.warning(f"Failed to load QA-optimized model: {e}")
        
        # 3. OpenAI Embeddings (High quality, requires API key)
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.models["openai"] = "text-embedding-ada-002"
            logger.info("✅ OpenAI embeddings available")
        
        if not self.models:
            logger.error("❌ No embedding models available!")
            raise RuntimeError("No embedding models could be initialized")
        
        logger.info(f"🎯 Default embedding model: {self.default_model}")
        logger.info(f"📊 Available models: {list(self.models.keys())}")
    
    def generate_embeddings(
        self, 
        texts: List[str], 
        model_name: Optional[str] = None,
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text chunks to embed
            model_name: Specific model to use (default: auto-select best)
            include_metadata: Include embedding metadata
        
        Returns:
            List of embedding results with vectors and metadata
        """
        if not texts:
            return []
        
        model_name = model_name or self.default_model
        
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not available, using {self.default_model}")
            model_name = self.default_model
        
        try:
            if model_name in ["sentence-transformers", "qa-optimized"]:
                return self._generate_sentence_transformer_embeddings(texts, model_name, include_metadata)
            elif model_name == "openai":
                return self._generate_openai_embeddings(texts, include_metadata)
            else:
                raise ValueError(f"Unknown model: {model_name}")
                
        except Exception as e:
            logger.error(f"Embedding generation failed for model {model_name}: {e}")
            # Fallback to default model if available
            if model_name != self.default_model and self.default_model in self.models:
                logger.info(f"Falling back to {self.default_model}")
                return self.generate_embeddings(texts, self.default_model, include_metadata)
            raise
    
    def _generate_sentence_transformer_embeddings(
        self, 
        texts: List[str], 
        model_name: str,
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Generate embeddings using Sentence Transformers"""
        model = self.models[model_name]
        
        # Generate embeddings
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        results = []
        for i, (text, embedding) in enumerate(zip(texts, embeddings)):
            result = {
                "text": text,
                "embedding": embedding.tolist(),  # Convert numpy to list for JSON serialization
                "embedding_model": model_name,
                "dimension": len(embedding)
            }
            
            if include_metadata:
                result["metadata"] = {
                    "text_length": len(text),
                    "word_count": len(text.split()),
                    "generated_at": datetime.utcnow().isoformat(),
                    "model_info": {
                        "name": model_name,
                        "type": "sentence-transformer",
                        "dimension": len(embedding)
                    }
                }
            
            results.append(result)
        
        logger.info(f"Generated {len(results)} embeddings using {model_name}")
        return results
    
    def _generate_openai_embeddings(
        self, 
        texts: List[str],
        include_metadata: bool
    ) -> List[Dict[str, Any]]:
        """Generate embeddings using OpenAI API"""
        try:
            # Use OpenAI client
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            
            results = []
            
            # Process in batches to avoid rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                response = client.embeddings.create(
                    input=batch_texts,
                    model="text-embedding-ada-002"
                )
                
                for j, embedding_data in enumerate(response.data):
                    text_idx = i + j
                    result = {
                        "text": texts[text_idx],
                        "embedding": embedding_data.embedding,
                        "embedding_model": "openai",
                        "dimension": len(embedding_data.embedding)
                    }
                    
                    if include_metadata:
                        result["metadata"] = {
                            "text_length": len(texts[text_idx]),
                            "word_count": len(texts[text_idx].split()),
                            "generated_at": datetime.utcnow().isoformat(),
                            "model_info": {
                                "name": "text-embedding-ada-002",
                                "type": "openai",
                                "dimension": len(embedding_data.embedding)
                            }
                        }
                    
                    results.append(result)
            
            logger.info(f"Generated {len(results)} embeddings using OpenAI")
            return results
            
        except Exception as e:
            logger.error(f"OpenAI embedding generation failed: {e}")
            raise
    
    def find_best_chunks_for_question_generation(
        self, 
        chunks: List[Dict[str, Any]], 
        query_context: str = "generate educational questions",
        max_chunks: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find the best chunks for question generation based on content analysis
        
        Args:
            chunks: List of document chunks with embeddings
            query_context: Context for what type of questions to generate
            max_chunks: Maximum number of chunks to return
        
        Returns:
            Ranked list of best chunks for question generation
        """
        try:
            if not chunks:
                return []
            
            # Generate embedding for query context
            query_embeddings = self.generate_embeddings([query_context], include_metadata=False)
            if not query_embeddings:
                return chunks[:max_chunks]  # Fallback to first chunks
            
            query_embedding = query_embeddings[0]["embedding"]
            
            # Score chunks based on similarity to query context
            scored_chunks = []
            for chunk in chunks:
                if "embedding" in chunk:
                    similarity = self.compute_similarity(
                        chunk["embedding"], 
                        query_embedding
                    )
                    
                    # Additional scoring factors for question generation
                    text = chunk.get("text", "")
                    
                    # Prefer chunks with good question generation potential
                    length_score = min(len(text) / 500, 1.0)  # Optimal length around 500 chars
                    complexity_score = self._assess_text_complexity(text)
                    
                    final_score = (
                        similarity * 0.5 +           # Semantic relevance
                        length_score * 0.2 +         # Appropriate length
                        complexity_score * 0.3       # Text complexity
                    )
                    
                    scored_chunks.append({
                        **chunk,
                        "question_generation_score": final_score,
                        "similarity_to_context": similarity
                    })
                else:
                    # If no embedding, use text-based scoring
                    scored_chunks.append({
                        **chunk,
                        "question_generation_score": 0.3,  # Medium score
                        "similarity_to_context": 0.0
                    })
            
            # Sort by score and return top chunks
            scored_chunks.sort(key=lambda x: x["question_generation_score"], reverse=True)
            return scored_chunks[:max_chunks]
            
        except Exception as e:
            logger.error(f"Failed to find best chunks for question generation: {e}")
            return chunks[:max_chunks]  # Fallback
    
    def compute_similarity(
        self, 
        embedding1: List[float], 
        embedding2: List[float],
        metric: str = "cosine"
    ) -> float:
        """Compute similarity between two embeddings"""
        try:
            emb1 = np.array(embedding1)
            emb2 = np.array(embedding2)
            
            if metric == "cosine":
                # Cosine similarity
                dot_product = np.dot(emb1, emb2)
                norm_a = np.linalg.norm(emb1)
                norm_b = np.linalg.norm(emb2)
                return dot_product / (norm_a * norm_b)
            
            elif metric == "euclidean":
                # Euclidean distance (converted to similarity)
                distance = np.linalg.norm(emb1 - emb2)
                return 1 / (1 + distance)
            
            elif metric == "dot":
                # Dot product
                return np.dot(emb1, emb2)
            
            else:
                raise ValueError(f"Unknown similarity metric: {metric}")
                
        except Exception as e:
            logger.error(f"Similarity computation failed: {e}")
            return 0.0
    
    def _assess_text_complexity(self, text: str) -> float:
        """Assess text complexity for question generation potential"""
        try:
            if not text.strip():
                return 0.0
            
            words = text.split()
            sentences = text.split('.')
            
            # Basic complexity metrics
            avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
            avg_sentence_length = len(words) / len(sentences) if sentences else 0
            
            # Normalize scores
            word_complexity = min(avg_word_length / 6, 1.0)  # Normalized to 6-char average
            sentence_complexity = min(avg_sentence_length / 15, 1.0)  # Normalized to 15-word average
            
            # Look for educational indicators
            educational_keywords = [
                'definition', 'example', 'process', 'method', 'principle', 'concept',
                'theory', 'analysis', 'conclusion', 'result', 'because', 'therefore',
                'however', 'furthermore', 'in contrast', 'specifically'
            ]
            
            keyword_score = sum(1 for keyword in educational_keywords 
                              if keyword.lower() in text.lower()) / len(educational_keywords)
            
            # Combined complexity score
            complexity = (word_complexity + sentence_complexity + keyword_score) / 3
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.warning(f"Text complexity assessment failed: {e}")
            return 0.5  # Default medium complexity
    
    def get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """Get information about available embedding models"""
        model_info = {}
        
        for model_name, model in self.models.items():
            if model_name in ["sentence-transformers", "qa-optimized"]:
                model_info[model_name] = {
                    "type": "sentence-transformer",
                    "local": True,
                    "dimension": 384,  # Standard for MiniLM models
                    "description": "Local sentence transformer model"
                }
            elif model_name == "openai":
                model_info[model_name] = {
                    "type": "openai",
                    "local": False,
                    "dimension": 1536,  # OpenAI ada-002 dimension
                    "description": "OpenAI text-embedding-ada-002"
                }
        
        return model_info

# Global service instance
embedding_service = EmbeddingService() 