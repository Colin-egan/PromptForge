"""
IBM watsonx.ai Client Wrapper

This module provides a high-level interface to IBM watsonx.ai services,
specifically for Granite model interactions including text generation and embeddings.
"""

import os
import time
import logging
from typing import Optional, Dict, Any, List, AsyncIterator
from enum import Enum

from ibm_watsonx_ai import APIClient, Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class WatsonxConfig(BaseSettings):
    """Configuration for IBM watsonx.ai client"""
    
    watsonx_api_key: str = Field(default="", env="WATSONX_API_KEY")
    watsonx_project_id: str = Field(default="", env="WATSONX_PROJECT_ID")
    watsonx_url: str = Field(
        default="https://us-south.ml.cloud.ibm.com",
        env="WATSONX_URL"
    )
    
    # Granite model configuration
    granite_model_id: str = Field(
        default="ibm/granite-3-8b-instruct",
        env="GRANITE_MODEL_ID"
    )
    granite_temperature: float = Field(default=0.2, env="GRANITE_TEMPERATURE")
    granite_max_tokens: int = Field(default=2048, env="GRANITE_MAX_TOKENS")
    granite_top_p: float = Field(default=0.95, env="GRANITE_TOP_P")
    granite_top_k: int = Field(default=50, env="GRANITE_TOP_K")
    
    # Retry configuration
    max_retries: int = Field(default=3, env="WATSONX_MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="WATSONX_RETRY_DELAY")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


class GraniteModelVariant(str, Enum):
    """Available Granite model variants"""
    GRANITE_3_8B_INSTRUCT = "ibm/granite-3-8b-instruct"
    GRANITE_3_2B_INSTRUCT = "ibm/granite-3-2b-instruct"
    GRANITE_20B_CODE = "ibm/granite-20b-code-instruct"
    GRANITE_34B_CODE = "ibm/granite-34b-code-instruct"


class GenerationParams(BaseModel):
    """Parameters for text generation"""
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    top_k: int = Field(default=50, ge=1, le=100)
    repetition_penalty: float = Field(default=1.0, ge=1.0, le=2.0)
    stop_sequences: Optional[List[str]] = None
    random_seed: Optional[int] = None


class WatsonxClient:
    """
    High-level client for IBM watsonx.ai services.
    
    Provides methods for:
    - Text generation with Granite models
    - Streaming text generation
    - Text embeddings
    - Retry logic and error handling
    """
    
    def __init__(self, config: Optional[WatsonxConfig] = None):
        """
        Initialize the watsonx.ai client.
        
        Args:
            config: Configuration object. If None, loads from environment.
        """
        self.config = config or WatsonxConfig()
        self._validate_config()
        
        # Initialize IBM watsonx.ai client
        self.credentials = Credentials(
            url=self.config.watsonx_url,
            api_key=self.config.watsonx_api_key
        )
        
        self.api_client = APIClient(
            credentials=self.credentials,
            project_id=self.config.watsonx_project_id
        )
        
        # Initialize model inference
        self.model = None
        self.embeddings_model = None
        
        logger.info(
            f"Initialized WatsonxClient with model: {self.config.granite_model_id}"
        )
    
    def _validate_config(self):
        """Validate required configuration"""
        if not self.config.watsonx_api_key:
            raise ValueError("WATSONX_API_KEY is required")
        if not self.config.watsonx_project_id:
            raise ValueError("WATSONX_PROJECT_ID is required")
    
    def _get_model(self, model_id: Optional[str] = None) -> ModelInference:
        """
        Get or create model inference instance.
        
        Args:
            model_id: Optional model ID override
            
        Returns:
            ModelInference instance
        """
        model_id = model_id or self.config.granite_model_id
        
        if self.model is None or self.model.model_id != model_id:
            self.model = ModelInference(
                model_id=model_id,
                api_client=self.api_client,
                project_id=self.config.watsonx_project_id
            )
        
        return self.model
    
    def _get_embeddings_model(self, model_id: str = "ibm/slate-125m-english-rtrvr") -> Embeddings:
        """
        Get or create embeddings model instance.
        
        Args:
            model_id: Embeddings model ID
            
        Returns:
            Embeddings instance
        """
        if self.embeddings_model is None:
            self.embeddings_model = Embeddings(
                model_id=model_id,
                api_client=self.api_client,
                project_id=self.config.watsonx_project_id
            )
        
        return self.embeddings_model
    
    def _build_generation_params(
        self,
        params: Optional[GenerationParams] = None
    ) -> Dict[str, Any]:
        """
        Build generation parameters dictionary.
        
        Args:
            params: Optional custom parameters
            
        Returns:
            Dictionary of generation parameters
        """
        if params is None:
            params = GenerationParams(
                temperature=self.config.granite_temperature,
                max_tokens=self.config.granite_max_tokens,
                top_p=self.config.granite_top_p,
                top_k=self.config.granite_top_k
            )
        
        gen_params = {
            GenParams.TEMPERATURE: params.temperature,
            GenParams.MAX_NEW_TOKENS: params.max_tokens,
            GenParams.TOP_P: params.top_p,
            GenParams.TOP_K: params.top_k,
            GenParams.REPETITION_PENALTY: params.repetition_penalty,
        }
        
        if params.stop_sequences:
            gen_params[GenParams.STOP_SEQUENCES] = params.stop_sequences
        
        if params.random_seed is not None:
            gen_params[GenParams.RANDOM_SEED] = params.random_seed
        
        return gen_params
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """
        Execute function with exponential backoff retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.config.max_retries - 1:
                    delay = self.config.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay}s..."
                    )
                    time.sleep(delay)
                else:
                    logger.error(
                        f"All {self.config.max_retries} attempts failed: {str(e)}"
                    )
        
        raise last_exception
    
    def generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        params: Optional[GenerationParams] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Generate text using Granite model.
        
        Args:
            prompt: Input prompt
            model_id: Optional model ID override
            params: Optional generation parameters
            system_prompt: Optional system prompt for instruction
            
        Returns:
            Generated text
        """
        model = self._get_model(model_id)
        gen_params = self._build_generation_params(params)
        
        # Format prompt with system instruction if provided
        if system_prompt:
            formatted_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        else:
            formatted_prompt = prompt
        
        def _generate():
            response = model.generate(
                prompt=formatted_prompt,
                params=gen_params
            )
            return response.get("results", [{}])[0].get("generated_text", "")
        
        try:
            result = self._retry_with_backoff(_generate)
            logger.info(f"Generated {len(result)} characters")
            return result
        except Exception as e:
            logger.error(f"Generation failed: {str(e)}")
            raise
    
    async def generate_stream(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        params: Optional[GenerationParams] = None,
        system_prompt: Optional[str] = None
    ) -> AsyncIterator[str]:
        """
        Generate text with streaming response.
        
        Args:
            prompt: Input prompt
            model_id: Optional model ID override
            params: Optional generation parameters
            system_prompt: Optional system prompt
            
        Yields:
            Text chunks as they are generated
        """
        model = self._get_model(model_id)
        gen_params = self._build_generation_params(params)
        
        # Format prompt with system instruction if provided
        if system_prompt:
            formatted_prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{prompt}\n<|assistant|>\n"
        else:
            formatted_prompt = prompt
        
        try:
            # Note: IBM watsonx.ai SDK may not support async streaming natively
            # This is a placeholder for when streaming is available
            response = model.generate_text_stream(
                prompt=formatted_prompt,
                params=gen_params
            )
            
            for chunk in response:
                if chunk:
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Streaming generation failed: {str(e)}")
            raise
    
    def embed(
        self,
        texts: List[str],
        model_id: str = "ibm/slate-125m-english-rtrvr"
    ) -> List[List[float]]:
        """
        Generate embeddings for text inputs.
        
        Args:
            texts: List of texts to embed
            model_id: Embeddings model ID
            
        Returns:
            List of embedding vectors
        """
        embeddings_model = self._get_embeddings_model(model_id)
        
        def _embed():
            response = embeddings_model.embed_documents(texts)
            return response
        
        try:
            embeddings = self._retry_with_backoff(_embed)
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    def format_code_prompt(
        self,
        task: str,
        context: Optional[str] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Format a prompt for code generation tasks.
        
        Args:
            task: Description of the code generation task
            context: Optional context (e.g., existing code, documentation)
            examples: Optional few-shot examples
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        if context:
            prompt_parts.append(f"Context:\n{context}\n")
        
        if examples:
            prompt_parts.append("Examples:")
            for i, example in enumerate(examples, 1):
                prompt_parts.append(f"\nExample {i}:")
                prompt_parts.append(f"Input: {example.get('input', '')}")
                prompt_parts.append(f"Output: {example.get('output', '')}")
            prompt_parts.append("")
        
        prompt_parts.append(f"Task: {task}")
        
        return "\n".join(prompt_parts)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the watsonx.ai service is accessible.
        
        Returns:
            Dictionary with health status
        """
        try:
            # Try a simple generation to verify connectivity
            test_prompt = "Hello"
            params = GenerationParams(max_tokens=5)
            self.generate(test_prompt, params=params)
            
            return {
                "status": "healthy",
                "model_id": self.config.granite_model_id,
                "url": self.config.watsonx_url
            }
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "model_id": self.config.granite_model_id,
                "url": self.config.watsonx_url
            }


# Singleton instance
_client_instance: Optional[WatsonxClient] = None


def get_watsonx_client() -> WatsonxClient:
    """
    Get or create singleton WatsonxClient instance.
    
    Returns:
        WatsonxClient instance
    """
    global _client_instance
    
    if _client_instance is None:
        _client_instance = WatsonxClient()
    
    return _client_instance

# Made with Bob
