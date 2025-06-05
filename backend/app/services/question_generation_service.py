"""
Question generation service using Ollama LLMs
Specialized for educational content with multiple question types and Bloom's taxonomy
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum

from app.services.ollama_service import ollama_service
from app.services.document_parser import document_parser
from app.services.embedding_service import embedding_service

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Supported question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    ESSAY = "essay"
    DEFINITION = "definition"
    EXPLANATION = "explanation"

class BloomLevel(Enum):
    """Bloom's taxonomy levels"""
    REMEMBER = "remember"
    UNDERSTAND = "understand"
    APPLY = "apply"
    ANALYZE = "analyze"
    EVALUATE = "evaluate"
    CREATE = "create"

class QuestionGenerationService:
    """Service for generating educational questions using LLMs"""
    
    def __init__(self):
        """Initialize question generation service"""
        self.ollama = ollama_service
        self.prompt_templates = self._load_prompt_templates()
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates for different question types"""
        return {
            "system_prompt": """You are an expert educational question generator. Your role is to create high-quality, pedagogically sound questions for educational assessment and learning.

Guidelines:
- Generate questions that are clear, unambiguous, and appropriate for the content level
- Ensure questions test understanding, not just memorization
- Include diverse question types when requested
- Provide accurate answers and explanations
- Consider Bloom's taxonomy levels when specified
- Format responses as valid JSON

Always respond with properly formatted JSON containing the requested questions.""",
            
            "multiple_choice": """Generate {num_questions} multiple choice question(s) based on the following content. 
Each question should have 4 options (A, B, C, D) with exactly one correct answer.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "multiple_choice",
      "question": "Question text here?",
      "options": {{
        "A": "Option A text",
        "B": "Option B text", 
        "C": "Option C text",
        "D": "Option D text"
      }},
      "correct_answer": "A",
      "explanation": "Why this answer is correct",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "true_false": """Generate {num_questions} true/false question(s) based on the following content.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "true_false",
      "question": "Statement to evaluate as true or false",
      "correct_answer": "true",
      "explanation": "Why this answer is correct",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "short_answer": """Generate {num_questions} short answer question(s) based on the following content.
Each question should require a brief 1-3 sentence response.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "short_answer",
      "question": "Question requiring a short answer?",
      "correct_answer": "Expected short answer",
      "explanation": "Detailed explanation of the answer",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "fill_in_the_blank": """Generate {num_questions} fill-in-the-blank question(s) based on the following content.
Use underscores or [blank] to indicate where students should fill in the answer.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "fill_in_the_blank",
      "question": "The process of _______ is essential for cellular respiration.",
      "correct_answer": "glycolysis",
      "explanation": "Why this answer is correct",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "essay": """Generate {num_questions} essay question(s) based on the following content.
Each question should require a comprehensive response with multiple paragraphs.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "essay",
      "question": "Essay question requiring detailed analysis?",
      "correct_answer": "Key points that should be covered in the essay",
      "explanation": "Detailed explanation of what makes a good answer",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "definition": """Generate {num_questions} definition question(s) based on the following content.
Ask students to define key terms or concepts.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "definition",
      "question": "Define [key term]",
      "correct_answer": "Complete definition of the term",
      "explanation": "Additional context and examples",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",

            "explanation": """Generate {num_questions} explanation question(s) based on the following content.
Ask students to explain processes, concepts, or relationships.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format:
{{
  "questions": [
    {{
      "id": "unique_id",
      "type": "explanation",
      "question": "Explain how/why [concept or process works]?",
      "correct_answer": "Clear explanation of the concept or process",
      "explanation": "Additional details and context",
      "bloom_level": "{bloom_level}",
      "difficulty": "{difficulty}",
      "topic": "Main topic covered"
    }}
  ]
}}""",
            
            "all_types": """Generate {num_questions} questions of different types based on the following content.
Generate exactly one question of each type: multiple_choice, true_false, short_answer, fill_in_the_blank, essay, definition, explanation.

Content: {content}

Bloom's Level: {bloom_level}
Difficulty: {difficulty}

Respond with JSON format containing an array of 7 questions, each of a different type."""
        }
    
    def generate_questions(
        self,
        content_chunks: List[Dict[str, Any]],
        question_type: str = "all_types",
        bloom_level: str = "understand",
        difficulty: str = "intermediate",
        num_questions: int = 7,
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate questions from content chunks
        
        Args:
            content_chunks: List of content chunks with text and metadata
            question_type: Type of questions to generate
            bloom_level: Bloom's taxonomy level
            difficulty: Difficulty level (basic, intermediate, advanced)
            num_questions: Number of questions to generate
            model: Specific Ollama model to use
            user_id: User ID for tracking
        
        Returns:
            Dict with generated questions and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Validate inputs
            if not content_chunks:
                return self._error_response("No content chunks provided")
            
            # Check if user wants all question types
            if question_type == "all_types":
                return self.generate_all_question_types(
                    content_chunks=content_chunks,
                    bloom_level=bloom_level,
                    difficulty=difficulty,
                    model=model,
                    user_id=user_id
                )
            
            # Prepare content for question generation
            content_text = self._prepare_content(content_chunks)
            
            if len(content_text) < 50:
                return self._error_response("Content too short for question generation")
            
            # Generate questions using LLM
            questions_response = self._generate_with_llm(
                content=content_text,
                question_type=question_type,
                bloom_level=bloom_level,
                difficulty=difficulty,
                num_questions=num_questions,
                model=model
            )
            
            if not questions_response["success"]:
                return questions_response
            
            # Process and validate generated questions
            processed_questions = self._process_generated_questions(
                questions_response["questions"],
                content_chunks,
                user_id
            )
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "questions": processed_questions,
                "metadata": {
                    "generation_time": generation_time,
                    "model": questions_response.get("model"),
                    "question_type": question_type,
                    "bloom_level": bloom_level,
                    "difficulty": difficulty,
                    "num_requested": num_questions,
                    "num_generated": len(processed_questions),
                    "content_chunks_used": len(content_chunks),
                    "user_id": user_id
                }
            }
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            return self._error_response(str(e))
    
    def generate_all_question_types(
        self,
        content_chunks: List[Dict[str, Any]],
        bloom_level: str = "understand",
        difficulty: str = "intermediate",
        model: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate one question of each available type
        
        Args:
            content_chunks: List of content chunks with text and metadata
            bloom_level: Bloom's taxonomy level
            difficulty: Difficulty level (basic, intermediate, advanced)
            model: Specific Ollama model to use
            user_id: User ID for tracking
        
        Returns:
            Dict with generated questions and metadata
        """
        try:
            start_time = datetime.utcnow()
            
            # Validate inputs
            if not content_chunks:
                return self._error_response("No content chunks provided")
            
            # Prepare content for question generation
            content_text = self._prepare_content(content_chunks)
            
            if len(content_text) < 50:
                return self._error_response("Content too short for question generation")
            
            # Get all question types
            question_types = [qtype.value for qtype in QuestionType]
            all_questions = []
            generation_metadata = []
            
            # Generate one question of each type
            for q_type in question_types:
                logger.info(f"Generating {q_type} question...")
                
                type_response = self._generate_with_llm(
                    content=content_text,
                    question_type=q_type,
                    bloom_level=bloom_level,
                    difficulty=difficulty,
                    num_questions=1,
                    model=model
                )
                
                if type_response["success"] and type_response["questions"]:
                    # Process the generated question
                    processed = self._process_generated_questions(
                        type_response["questions"],
                        content_chunks,
                        user_id
                    )
                    if processed:
                        all_questions.extend(processed)
                        generation_metadata.append({
                            "type": q_type,
                            "success": True,
                            "generation_time": type_response.get("generation_time", 0)
                        })
                else:
                    logger.warning(f"Failed to generate {q_type} question: {type_response.get('error', 'Unknown error')}")
                    generation_metadata.append({
                        "type": q_type,
                        "success": False,
                        "error": type_response.get("error", "Unknown error")
                    })
            
            end_time = datetime.utcnow()
            total_generation_time = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "questions": all_questions,
                "metadata": {
                    "generation_time": total_generation_time,
                    "model": model,
                    "question_type": "all_types",
                    "bloom_level": bloom_level,
                    "difficulty": difficulty,
                    "num_requested": len(question_types),
                    "num_generated": len(all_questions),
                    "content_chunks_used": len(content_chunks),
                    "user_id": user_id,
                    "type_breakdown": generation_metadata
                }
            }
            
        except Exception as e:
            logger.error(f"All types question generation failed: {e}")
            return self._error_response(str(e))
    
    def _prepare_content(self, content_chunks: List[Dict[str, Any]]) -> str:
        """Prepare content chunks for question generation"""
        try:
            # Extract text from chunks
            content_parts = []
            
            for chunk in content_chunks:
                text = chunk.get("text", "")
                if text.strip():
                    # Add context from metadata if available
                    metadata = chunk.get("metadata", {})
                    filename = metadata.get("filename", "")
                    page_num = metadata.get("page_number", "")
                    
                    context_info = ""
                    if filename:
                        context_info = f"[From: {filename}"
                        if page_num:
                            context_info += f", Page {page_num}"
                        context_info += "] "
                    
                    content_parts.append(context_info + text)
            
            # Combine content with separators
            combined_content = "\n\n---\n\n".join(content_parts)
            
            # Limit content length for LLM processing
            max_length = 4000  # Reasonable limit for most models
            if len(combined_content) > max_length:
                combined_content = combined_content[:max_length] + "\n\n[Content truncated for processing...]"
            
            return combined_content
            
        except Exception as e:
            logger.error(f"Content preparation failed: {e}")
            return ""
    
    def _generate_with_llm(
        self,
        content: str,
        question_type: str,
        bloom_level: str,
        difficulty: str,
        num_questions: int,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate questions using Ollama LLM"""
        try:
            # Select appropriate prompt template
            if question_type in self.prompt_templates:
                prompt_template = self.prompt_templates[question_type]
            else:
                prompt_template = self.prompt_templates["all_types"]
            
            # Format prompt
            prompt = prompt_template.format(
                content=content,
                bloom_level=bloom_level,
                difficulty=difficulty,
                num_questions=num_questions
            )
            
            # Generate response with JSON output
            response = self.ollama.generate_response(
                prompt=prompt,
                system_prompt=self.prompt_templates["system_prompt"],
                model=model,
                temperature=0.7,  # Slightly creative but consistent
                max_tokens=2000,
                use_json=True  # Use LangChain's JSON output parser
            )
            
            if not response["success"]:
                return {
                    "success": False,
                    "error": f"LLM generation failed: {response.get('error', 'Unknown error')}"
                }
            
            # Parse JSON response (LangChain may return JSON object directly)
            content_data = response["content"]
            try:
                # Check if content is already parsed JSON object
                if isinstance(content_data, dict):
                    questions_data = content_data
                elif isinstance(content_data, list):
                    # Handle case where LLM returns a list directly
                    questions_data = {"questions": content_data}
                else:
                    # Try to parse as JSON string
                    questions_data = json.loads(content_data)
                
                # Extract questions array
                if isinstance(questions_data, list):
                    questions = questions_data
                else:
                    questions = questions_data.get("questions", [])
                
                # If still no questions found, try different structures
                if not questions and isinstance(content_data, dict):
                    # Check if the response has questions in different formats
                    for key in ["question", "items", "data"]:
                        if key in content_data:
                            potential_questions = content_data[key]
                            if isinstance(potential_questions, list):
                                questions = potential_questions
                                break
                            elif isinstance(potential_questions, dict):
                                questions = [potential_questions]
                                break
                
                if not questions:
                    return {
                        "success": False,
                        "error": "No questions generated by LLM",
                        "raw_response": str(content_data)
                    }
                
                return {
                    "success": True,
                    "questions": questions,
                    "model": response.get("model"),
                    "generation_time": response.get("generation_time"),
                    "raw_response": str(content_data)
                }
                
            except (json.JSONDecodeError, TypeError) as e:
                logger.error(f"Failed to parse LLM JSON response: {e}")
                logger.error(f"Response content: {content_data}")
                return {
                    "success": False,
                    "error": f"Failed to parse LLM response: {e}",
                    "raw_response": str(content_data)
                }
                    
        except Exception as e:
            logger.error(f"LLM question generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_generated_questions(
        self,
        questions: List[Dict[str, Any]],
        content_chunks: List[Dict[str, Any]],
        user_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Process and enhance generated questions"""
        try:
            processed = []
            
            for i, question in enumerate(questions):
                # Add unique ID if not present
                if "id" not in question:
                    question["id"] = f"q_{i+1}_{str(uuid.uuid4())[:8]}"
                
                # Add metadata
                question["generated_at"] = datetime.utcnow().isoformat()
                question["user_id"] = user_id
                
                # Add source information
                if content_chunks:
                    source_info = []
                    for chunk in content_chunks:
                        metadata = chunk.get("metadata", {})
                        if metadata.get("filename"):
                            source_info.append({
                                "filename": metadata.get("filename"),
                                "page_number": metadata.get("page_number"),
                                "document_id": metadata.get("document_id")
                            })
                    
                    question["source_content"] = source_info
                
                # Validate question structure
                if self._validate_question(question):
                    processed.append(question)
                else:
                    logger.warning(f"Invalid question structure, skipping: {question.get('id', 'unknown')}")
            
            return processed
            
        except Exception as e:
            logger.error(f"Question processing failed: {e}")
            return questions  # Return original if processing fails
    
    def _validate_question(self, question: Dict[str, Any]) -> bool:
        """Validate question structure"""
        try:
            # Basic validation
            required_fields = ["id", "type", "question"]
            for field in required_fields:
                if field not in question:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Question validation failed: {e}")
            return False
    
    def _error_response(self, error_message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            "success": False,
            "error": error_message,
            "questions": [],
            "metadata": {
                "generation_time": 0,
                "num_generated": 0
            }
        }
    
    def get_question_types(self) -> List[str]:
        """Get supported question types"""
        return [qtype.value for qtype in QuestionType]
    
    def get_bloom_levels(self) -> List[str]:
        """Get supported Bloom's taxonomy levels"""
        return [level.value for level in BloomLevel]

# Global service instance
question_generation_service = QuestionGenerationService() 