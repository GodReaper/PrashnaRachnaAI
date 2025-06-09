"""
Ollama service for local LLM integration using LangChain
Supports DeepSeek R1, Llama, and other open-source models with LangChain abstractions
"""

import logging
import json
import re
import asyncio
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

try:
    from langchain_ollama import OllamaLLM, ChatOllama
    from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
    from langchain_core.messages import SystemMessage, HumanMessage
    LANGCHAIN_OLLAMA_AVAILABLE = True
except ImportError:
    LANGCHAIN_OLLAMA_AVAILABLE = False

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from config.settings import settings

logger = logging.getLogger(__name__)

class OllamaService:
    """Service for interacting with Ollama LLMs using LangChain"""
    
    def __init__(self):
        """Initialize Ollama service with LangChain"""
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        self.fallback_model = settings.OLLAMA_FALLBACK_MODEL
        self.available_models = []
        
        # LangChain components
        self.chat_llm = None
        self.text_llm = None
        self.ollama_client = None  # For admin operations
        
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize LangChain Ollama service"""
        if not LANGCHAIN_OLLAMA_AVAILABLE:
            logger.error("❌ LangChain Ollama package not available. Install with: pip install langchain-ollama")
            return
        
        if not OLLAMA_AVAILABLE:
            logger.error("❌ Ollama package not available. Install with: pip install ollama")
            return
        
        try:
            # Initialize direct Ollama client for admin operations
            self.ollama_client = ollama.Client(host=self.base_url)
            
            # Initialize LangChain Chat model for conversations
            self.chat_llm = ChatOllama(
                model=self.default_model,
                base_url=self.base_url,
                temperature=0.7,
                num_predict=2000,  # max tokens
            )
            
            # Initialize LangChain text model for simple completions
            self.text_llm = OllamaLLM(
                model=self.default_model,
                base_url=self.base_url,
                temperature=0.7,
                num_predict=2000,
            )
            
            logger.info(f"✅ LangChain Ollama service initialized: {self.base_url}")
            
            # Get available models
            self._update_available_models()
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain Ollama service: {e}")
            self.chat_llm = None
            self.text_llm = None
    
    def _update_available_models(self):
        """Update list of available models"""
        try:
            if not self.ollama_client:
                return
            
            models_response = self.ollama_client.list()
            
            # Handle different response formats
            if hasattr(models_response, 'models'):
                models = models_response.models
            elif isinstance(models_response, dict):
                models = models_response.get('models', [])
            else:
                models = []
            
            self.available_models = []
            
            for model in models:
                if hasattr(model, 'model'):  # Ollama model object
                    self.available_models.append(model.model)
                elif isinstance(model, dict) and 'name' in model:
                    self.available_models.append(model['name'])
                elif hasattr(model, 'name'):
                    self.available_models.append(model.name)
                else:
                    logger.warning(f"Unexpected model format: {model}")
            
            logger.info(f"📋 Available Ollama models: {self.available_models}")
            
        except Exception as e:
            logger.warning(f"Failed to get available models: {e}")
            self.available_models = []
    
    def health_check(self) -> bool:
        """Check if Ollama service is healthy"""
        try:
            if not self.ollama_client:
                return False
            
            # Try to list models as a health check
            models_response = self.ollama_client.list()
            return bool(models_response.get('models'))
            
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        try:
            if not self.available_models:
                self._update_available_models()
            
            return model_name in self.available_models
            
        except Exception as e:
            logger.error(f"Error checking model availability: {e}")
            return False
    
    def pull_model(self, model_name: str) -> bool:
        """Pull a model if not available"""
        try:
            if not self.ollama_client:
                logger.error("Ollama client not available")
                return False
            
            if self.is_model_available(model_name):
                logger.info(f"Model {model_name} already available")
                return True
            
            logger.info(f"Pulling model {model_name}...")
            self.ollama_client.pull(model_name)
            
            # Update available models
            self._update_available_models()
            
            return self.is_model_available(model_name)
            
        except Exception as e:
            logger.error(f"Failed to pull model {model_name}: {e}")
            return False
    
    def _ensure_model_available(self, model_name: str) -> str:
        """Ensure model is available, fallback if needed"""
        # Check if model is available, try to pull if not
        if not self.is_model_available(model_name):
            logger.info(f"Model {model_name} not available, trying to pull...")
            if not self.pull_model(model_name):
                # Fallback to alternative model
                if model_name != self.fallback_model:
                    logger.info(f"Falling back to {self.fallback_model}")
                    model_name = self.fallback_model
                    if not self.is_model_available(model_name):
                        if not self.pull_model(model_name):
                            raise Exception(f"Neither {model_name} nor fallback model {self.fallback_model} available")
                else:
                    raise Exception(f"Model {model_name} not available and could not be pulled")
        
        return model_name
    
    def _parse_json_with_repair(self, json_str: str) -> dict:
        """Parse JSON with automatic repair for common issues"""
        
        try:
            # First try normal parsing
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}, attempting repair...")
            
            try:
                # Common JSON repair strategies
                repaired_json = json_str
                
                # Fix common issues
                # 1. Remove trailing commas
                repaired_json = re.sub(r',(\s*[}\]])', r'\1', repaired_json)
                
                # 2. Fix missing commas between objects/arrays
                repaired_json = re.sub(r'}\s*{', '},{', repaired_json)
                repaired_json = re.sub(r']\s*\[', '],[', repaired_json)
                
                # 3. Fix unquoted keys (simple cases)
                repaired_json = re.sub(r'(\w+):', r'"\1":', repaired_json)
                
                # 4. Fix single quotes to double quotes
                repaired_json = repaired_json.replace("'", '"')
                
                # 5. Remove any non-JSON content at the end
                last_brace = repaired_json.rfind('}')
                if last_brace != -1:
                    repaired_json = repaired_json[:last_brace + 1]
                
                return json.loads(repaired_json)
                
            except json.JSONDecodeError as repair_error:
                logger.error(f"JSON repair also failed: {repair_error}")
                logger.error(f"Original JSON: {json_str[:500]}...")
                
                # Last resort: extract just the questions array if possible
                try:
                    questions_match = re.search(r'"questions"\s*:\s*(\[.*?\])', json_str, re.DOTALL)
                    if questions_match:
                        questions_array = questions_match.group(1)
                        return {"questions": json.loads(questions_array)}
                except:
                    pass
                
                # Final fallback: return error structure
                return {
                    "error": "Failed to parse JSON",
                    "raw_response": json_str,
                    "parse_error": str(repair_error)
                }
    
    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        use_json: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response using LangChain Ollama model
        
        Args:
            prompt: User prompt
            model: Model name (defaults to configured default)
            system_prompt: System prompt for context
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream response (not implemented yet)
            use_json: Whether to expect JSON output
        
        Returns:
            Dict with response and metadata
        """
        try:
            if not self.chat_llm:
                raise Exception("LangChain Ollama service not available")
            
            # Select and ensure model is available
            model_name = model or self.default_model
            model_name = self._ensure_model_available(model_name)
            
            # Update model if different from current
            if self.chat_llm.model != model_name:
                self.chat_llm.model = model_name
            
            # Update parameters
            self.chat_llm.temperature = temperature
            if max_tokens:
                self.chat_llm.num_predict = max_tokens
            
            # Create messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response
            start_time = datetime.utcnow()
            
            if use_json:
                # Use JSON output parser with fallback
                json_parser = JsonOutputParser()
                chain = self.chat_llm | json_parser
                
                try:
                    response_content = chain.invoke(messages)
                    
                    # Check if JSON parser returned None or empty result
                    if response_content is None:
                        logger.warning("JSON parser returned None, falling back to string parsing")
                        raise ValueError("JSON parser returned None")
                        
                except Exception as e:
                    # Fallback to string parsing if JSON parsing fails
                    logger.warning(f"JSON parsing failed, falling back to string: {e}")
                    string_parser = StrOutputParser()
                    chain = self.chat_llm | string_parser
                    response_text = chain.invoke(messages)
                    
                    # Try to parse as JSON manually
                    try:
                        if response_text and response_text.strip():
                            # Handle DeepSeek thinking patterns - extract JSON after </think> or <think>
                            json_part = response_text.strip()
                            
                            if "</think>" in response_text:
                                # Extract content after </think>
                                json_part = response_text.split("</think>", 1)[1].strip()
                            elif "<think>" in response_text:
                                # Handle case where thinking starts but doesn't close properly
                                # Find the first opening brace after <think>
                                think_pos = response_text.find("<think>")
                                json_start_after_think = response_text.find('{', think_pos)
                                if json_start_after_think != -1:
                                    json_part = response_text[json_start_after_think:].strip()
                            
                            # Remove any leading/trailing text that's not JSON
                            json_start = json_part.find('{')
                            json_end = json_part.rfind('}') + 1
                            
                            if json_start != -1 and json_end > json_start:
                                clean_json = json_part[json_start:json_end]
                                response_content = self._parse_json_with_repair(clean_json)
                            else:
                                # Fallback: try to parse the whole part as JSON
                                response_content = self._parse_json_with_repair(json_part)
                        else:
                            response_content = {"error": "Empty response from LLM", "raw_response": response_text}
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from response: {e}")
                        logger.warning(f"Response text: {response_text[:500]}...")
                        response_content = {"error": "Failed to parse JSON", "raw_response": response_text}
            else:
                # Use string output parser
                string_parser = StrOutputParser()
                chain = self.chat_llm | string_parser
                response_content = chain.invoke(messages)
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            # Count tokens (approximate)
            token_count = len(str(response_content).split()) if response_content else 0
            
            return {
                "success": True,
                "content": response_content,
                "model": model_name,
                "generation_time": generation_time,
                "token_count": token_count,
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "timestamp": start_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"LangChain Ollama generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "model": model_name if 'model_name' in locals() else model,
                "generation_time": 0,
                "token_count": 0
            }
    
    def generate_with_prompt_template(
        self,
        template: str,
        template_variables: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_json: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response using LangChain prompt template
        
        Args:
            template: LangChain prompt template string
            template_variables: Variables to fill in the template
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            use_json: Whether to expect JSON output
        
        Returns:
            Dict with response and metadata
        """
        try:
            if not self.chat_llm:
                raise Exception("LangChain Ollama service not available")
            
            # Create prompt template
            prompt_template = ChatPromptTemplate.from_template(template)
            
            # Format prompt with variables
            formatted_prompt = prompt_template.format(**template_variables)
            
            # Generate response
            return self.generate_response(
                prompt=formatted_prompt,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                use_json=use_json
            )
            
        except Exception as e:
            logger.error(f"Prompt template generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "model": model,
                "generation_time": 0,
                "token_count": 0
            }
    
    async def generate_response_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        use_json: bool = False
    ) -> Dict[str, Any]:
        """
        Async version of generate_response using LangChain
        """
        try:
            if not self.chat_llm:
                raise Exception("LangChain Ollama service not available")
            
            # Select and ensure model is available
            model_name = model or self.default_model
            model_name = self._ensure_model_available(model_name)
            
            # Update model if different from current
            if self.chat_llm.model != model_name:
                self.chat_llm.model = model_name
            
            # Update parameters
            self.chat_llm.temperature = temperature
            if max_tokens:
                self.chat_llm.num_predict = max_tokens
            
            # Create messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=prompt))
            
            # Generate response asynchronously
            start_time = datetime.utcnow()
            
            if use_json:
                # Use JSON output parser with fallback
                json_parser = JsonOutputParser()
                chain = self.chat_llm | json_parser
                
                try:
                    response_content = await chain.ainvoke(messages)
                    
                    # Check if JSON parser returned None or empty result
                    if response_content is None:
                        logger.warning("JSON parser returned None, falling back to string parsing")
                        raise ValueError("JSON parser returned None")
                        
                except Exception as e:
                    # Fallback to string parsing if JSON parsing fails
                    logger.warning(f"JSON parsing failed, falling back to string: {e}")
                    string_parser = StrOutputParser()
                    chain = self.chat_llm | string_parser
                    response_text = await chain.ainvoke(messages)
                    
                    # Try to parse as JSON manually
                    try:
                        if response_text and response_text.strip():
                            # Handle DeepSeek thinking patterns - extract JSON after </think> or <think>
                            json_part = response_text.strip()
                            
                            if "</think>" in response_text:
                                # Extract content after </think>
                                json_part = response_text.split("</think>", 1)[1].strip()
                            elif "<think>" in response_text:
                                # Handle case where thinking starts but doesn't close properly
                                # Find the first opening brace after <think>
                                think_pos = response_text.find("<think>")
                                json_start_after_think = response_text.find('{', think_pos)
                                if json_start_after_think != -1:
                                    json_part = response_text[json_start_after_think:].strip()
                            
                            # Remove any leading/trailing text that's not JSON
                            json_start = json_part.find('{')
                            json_end = json_part.rfind('}') + 1
                            
                            if json_start != -1 and json_end > json_start:
                                clean_json = json_part[json_start:json_end]
                                response_content = self._parse_json_with_repair(clean_json)
                            else:
                                # Fallback: try to parse the whole part as JSON
                                response_content = self._parse_json_with_repair(json_part)
                        else:
                            response_content = {"error": "Empty response from LLM", "raw_response": response_text}
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON from response: {e}")
                        logger.warning(f"Response text: {response_text[:500]}...")
                        response_content = {"error": "Failed to parse JSON", "raw_response": response_text}
            else:
                # Use string output parser
                string_parser = StrOutputParser()
                chain = self.chat_llm | string_parser
                response_content = await chain.ainvoke(messages)
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            # Count tokens (approximate)
            token_count = len(str(response_content).split()) if response_content else 0
            
            return {
                "success": True,
                "content": response_content,
                "model": model_name,
                "generation_time": generation_time,
                "token_count": token_count,
                "metadata": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "timestamp": start_time.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Async LangChain Ollama generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None,
                "model": model_name if 'model_name' in locals() else model,
                "generation_time": 0,
                "token_count": 0
            }
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            target_model = model_name or self.default_model
            
            if not self.ollama_client:
                raise Exception("Ollama client not available")
            
            # Get model details
            models_response = self.ollama_client.list()
            models = models_response.get('models', [])
            
            for model in models:
                model_info_name = None
                if hasattr(model, 'model'):
                    model_info_name = model.model
                elif isinstance(model, dict) and 'name' in model:
                    model_info_name = model['name']
                elif hasattr(model, 'name'):
                    model_info_name = model.name
                
                if model_info_name == target_model:
                    return {
                        "name": model_info_name,
                        "size": model.get('size', 0) if isinstance(model, dict) else getattr(model, 'size', 0),
                        "modified_at": model.get('modified_at') if isinstance(model, dict) else getattr(model, 'modified_at', None),
                        "details": model.get('details', {}) if isinstance(model, dict) else getattr(model, 'details', {}),
                        "available": True,
                        "langchain_compatible": True
                    }
            
            return {
                "name": target_model,
                "available": False,
                "langchain_compatible": True,
                "error": "Model not found"
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {
                "name": target_model if 'target_model' in locals() else model_name,
                "available": False,
                "langchain_compatible": True,
                "error": str(e)
            }
    
    def get_recommended_models(self) -> Dict[str, Any]:
        """Get recommended models with LangChain compatibility info"""
        return {
            "recommended": [
                {
                    "name": "deepseek-r1:1.5b",
                    "description": "DeepSeek R1 1.5B - Fast, efficient reasoning model",
                    "size": "1.5B parameters",
                    "use_case": "Speed-optimized question generation",
                    "langchain_compatible": True,
                    "available": self.is_model_available("deepseek-r1:1.5b")
                },
                {
                    "name": "deepseek-r1:7b", 
                    "description": "DeepSeek R1 7B - High-quality reasoning model",
                    "size": "7B parameters", 
                    "use_case": "Quality-focused question generation",
                    "langchain_compatible": True,
                    "available": self.is_model_available("deepseek-r1:7b")
                },
                {
                    "name": "llama3.2:3b",
                    "description": "Llama 3.2 3B - Balanced performance and quality",
                    "size": "3B parameters",
                    "use_case": "General-purpose question generation",
                    "langchain_compatible": True,
                    "available": self.is_model_available("llama3.2:3b")
                },
                {
                    "name": "llama3.2:1b",
                    "description": "Llama 3.2 1B - Lightweight and fast",
                    "size": "1B parameters",
                    "use_case": "Quick question generation",
                    "langchain_compatible": True,
                    "available": self.is_model_available("llama3.2:1b")
                }
            ],
            "current_default": self.default_model,
            "fallback": self.fallback_model,
            "service_type": "LangChain + Ollama",
            "available_models": self.available_models
        }

# Global service instance
ollama_service = OllamaService() 