"""
Unit tests for IBM watsonx.ai client wrapper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.watsonx_client import (
    WatsonxClient,
    WatsonxConfig,
    GenerationParams,
    GraniteModelVariant,
    get_watsonx_client
)


@pytest.fixture
def mock_config():
    """Create a mock configuration"""
    return WatsonxConfig(
        watsonx_api_key="test_api_key",
        watsonx_project_id="test_project_id",
        watsonx_url="https://test.ml.cloud.ibm.com",
        granite_model_id="ibm/granite-3-8b-instruct",
        granite_temperature=0.2,
        granite_max_tokens=2048,
        granite_top_p=0.95,
        granite_top_k=50,
        max_retries=3,
        retry_delay=1.0
    )


@pytest.fixture
def mock_api_client():
    """Create a mock IBM watsonx.ai API client"""
    with patch('app.watsonx_client.APIClient') as mock:
        yield mock


@pytest.fixture
def mock_model_inference():
    """Create a mock ModelInference"""
    with patch('app.watsonx_client.ModelInference') as mock:
        yield mock


@pytest.fixture
def mock_embeddings():
    """Create a mock Embeddings"""
    with patch('app.watsonx_client.Embeddings') as mock:
        yield mock


class TestWatsonxConfig:
    """Test WatsonxConfig class"""
    
    def test_default_values(self):
        """Test default configuration values"""
        config = WatsonxConfig(
            watsonx_api_key="test_key",
            watsonx_project_id="test_project"
        )
        
        assert config.watsonx_url == "https://us-south.ml.cloud.ibm.com"
        assert config.granite_model_id == "ibm/granite-3-8b-instruct"
        assert config.granite_temperature == 0.2
        assert config.granite_max_tokens == 2048
        assert config.granite_top_p == 0.95
        assert config.granite_top_k == 50
        assert config.max_retries == 3
        assert config.retry_delay == 1.0
    
    def test_custom_values(self):
        """Test custom configuration values"""
        config = WatsonxConfig(
            watsonx_api_key="custom_key",
            watsonx_project_id="custom_project",
            granite_temperature=0.5,
            granite_max_tokens=4096
        )
        
        assert config.watsonx_api_key == "custom_key"
        assert config.watsonx_project_id == "custom_project"
        assert config.granite_temperature == 0.5
        assert config.granite_max_tokens == 4096


class TestGenerationParams:
    """Test GenerationParams class"""
    
    def test_default_params(self):
        """Test default generation parameters"""
        params = GenerationParams()
        
        assert params.temperature == 0.2
        assert params.max_tokens == 2048
        assert params.top_p == 0.95
        assert params.top_k == 50
        assert params.repetition_penalty == 1.0
        assert params.stop_sequences is None
        assert params.random_seed is None
    
    def test_custom_params(self):
        """Test custom generation parameters"""
        params = GenerationParams(
            temperature=0.7,
            max_tokens=1024,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.2,
            stop_sequences=["END", "STOP"],
            random_seed=42
        )
        
        assert params.temperature == 0.7
        assert params.max_tokens == 1024
        assert params.top_p == 0.9
        assert params.top_k == 40
        assert params.repetition_penalty == 1.2
        assert params.stop_sequences == ["END", "STOP"]
        assert params.random_seed == 42
    
    def test_validation(self):
        """Test parameter validation"""
        # Temperature out of range
        with pytest.raises(ValueError):
            GenerationParams(temperature=3.0)
        
        # Max tokens too low
        with pytest.raises(ValueError):
            GenerationParams(max_tokens=0)
        
        # Top_p out of range
        with pytest.raises(ValueError):
            GenerationParams(top_p=1.5)


class TestWatsonxClient:
    """Test WatsonxClient class"""
    
    def test_initialization(self, mock_config, mock_api_client):
        """Test client initialization"""
        client = WatsonxClient(config=mock_config)
        
        assert client.config == mock_config
        assert client.model is None
        assert client.embeddings_model is None
    
    def test_validation_missing_api_key(self):
        """Test validation fails with missing API key"""
        config = WatsonxConfig(
            watsonx_api_key="",
            watsonx_project_id="test_project"
        )
        
        with pytest.raises(ValueError, match="WATSONX_API_KEY is required"):
            WatsonxClient(config=config)
    
    def test_validation_missing_project_id(self):
        """Test validation fails with missing project ID"""
        config = WatsonxConfig(
            watsonx_api_key="test_key",
            watsonx_project_id=""
        )
        
        with pytest.raises(ValueError, match="WATSONX_PROJECT_ID is required"):
            WatsonxClient(config=config)
    
    def test_build_generation_params(self, mock_config, mock_api_client):
        """Test building generation parameters"""
        client = WatsonxClient(config=mock_config)
        
        params = GenerationParams(
            temperature=0.5,
            max_tokens=1024,
            top_p=0.9,
            top_k=40,
            stop_sequences=["END"]
        )
        
        gen_params = client._build_generation_params(params)
        
        assert gen_params["temperature"] == 0.5
        assert gen_params["max_new_tokens"] == 1024
        assert gen_params["top_p"] == 0.9
        assert gen_params["top_k"] == 40
        assert gen_params["stop_sequences"] == ["END"]
    
    def test_build_generation_params_defaults(self, mock_config, mock_api_client):
        """Test building generation parameters with defaults"""
        client = WatsonxClient(config=mock_config)
        
        gen_params = client._build_generation_params(None)
        
        assert gen_params["temperature"] == mock_config.granite_temperature
        assert gen_params["max_new_tokens"] == mock_config.granite_max_tokens
        assert gen_params["top_p"] == mock_config.granite_top_p
        assert gen_params["top_k"] == mock_config.granite_top_k
    
    @patch('app.watsonx_client.ModelInference')
    def test_generate_success(self, mock_model_class, mock_config, mock_api_client):
        """Test successful text generation"""
        # Setup mock
        mock_model = Mock()
        mock_model.generate.return_value = {
            "results": [{"generated_text": "Generated code here"}]
        }
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        
        result = client.generate("Create a box")
        
        assert result == "Generated code here"
        assert mock_model.generate.called
    
    @patch('app.watsonx_client.ModelInference')
    def test_generate_with_system_prompt(self, mock_model_class, mock_config, mock_api_client):
        """Test generation with system prompt"""
        mock_model = Mock()
        mock_model.generate.return_value = {
            "results": [{"generated_text": "Generated code"}]
        }
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        
        result = client.generate(
            "Create a box",
            system_prompt="You are a CadQuery expert"
        )
        
        assert result == "Generated code"
        
        # Check that system prompt was included
        call_args = mock_model.generate.call_args
        prompt = call_args[1]["prompt"]
        assert "<|system|>" in prompt
        assert "You are a CadQuery expert" in prompt
    
    @patch('app.watsonx_client.ModelInference')
    def test_generate_retry_on_failure(self, mock_model_class, mock_config, mock_api_client):
        """Test retry logic on failure"""
        mock_model = Mock()
        # Fail twice, then succeed
        mock_model.generate.side_effect = [
            Exception("API Error"),
            Exception("API Error"),
            {"results": [{"generated_text": "Success"}]}
        ]
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        client.config.retry_delay = 0.01  # Speed up test
        
        result = client.generate("Create a box")
        
        assert result == "Success"
        assert mock_model.generate.call_count == 3
    
    @patch('app.watsonx_client.ModelInference')
    def test_generate_max_retries_exceeded(self, mock_model_class, mock_config, mock_api_client):
        """Test failure after max retries"""
        mock_model = Mock()
        mock_model.generate.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        client.config.retry_delay = 0.01  # Speed up test
        
        with pytest.raises(Exception, match="API Error"):
            client.generate("Create a box")
        
        assert mock_model.generate.call_count == mock_config.max_retries
    
    @patch('app.watsonx_client.Embeddings')
    def test_embed_success(self, mock_embeddings_class, mock_config, mock_api_client):
        """Test successful embedding generation"""
        mock_embeddings = Mock()
        mock_embeddings.embed_documents.return_value = [
            [0.1, 0.2, 0.3],
            [0.4, 0.5, 0.6]
        ]
        mock_embeddings_class.return_value = mock_embeddings
        
        client = WatsonxClient(config=mock_config)
        
        texts = ["text1", "text2"]
        embeddings = client.embed(texts)
        
        assert len(embeddings) == 2
        assert embeddings[0] == [0.1, 0.2, 0.3]
        assert embeddings[1] == [0.4, 0.5, 0.6]
    
    def test_format_code_prompt_basic(self, mock_config, mock_api_client):
        """Test basic code prompt formatting"""
        client = WatsonxClient(config=mock_config)
        
        prompt = client.format_code_prompt("Create a box")
        
        assert "Task: Create a box" in prompt
    
    def test_format_code_prompt_with_context(self, mock_config, mock_api_client):
        """Test code prompt formatting with context"""
        client = WatsonxClient(config=mock_config)
        
        prompt = client.format_code_prompt(
            "Create a box",
            context="CadQuery is a Python library"
        )
        
        assert "Context:" in prompt
        assert "CadQuery is a Python library" in prompt
        assert "Task: Create a box" in prompt
    
    def test_format_code_prompt_with_examples(self, mock_config, mock_api_client):
        """Test code prompt formatting with examples"""
        client = WatsonxClient(config=mock_config)
        
        examples = [
            {"input": "Create a sphere", "output": "cq.Workplane().sphere(10)"},
            {"input": "Create a cylinder", "output": "cq.Workplane().cylinder(10, 20)"}
        ]
        
        prompt = client.format_code_prompt(
            "Create a box",
            examples=examples
        )
        
        assert "Examples:" in prompt
        assert "Example 1:" in prompt
        assert "Create a sphere" in prompt
        assert "Example 2:" in prompt
        assert "Create a cylinder" in prompt
    
    @patch('app.watsonx_client.ModelInference')
    def test_health_check_healthy(self, mock_model_class, mock_config, mock_api_client):
        """Test health check when service is healthy"""
        mock_model = Mock()
        mock_model.generate.return_value = {
            "results": [{"generated_text": "Hello"}]
        }
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        
        health = client.health_check()
        
        assert health["status"] == "healthy"
        assert health["model_id"] == mock_config.granite_model_id
        assert health["url"] == mock_config.watsonx_url
    
    @patch('app.watsonx_client.ModelInference')
    def test_health_check_unhealthy(self, mock_model_class, mock_config, mock_api_client):
        """Test health check when service is unhealthy"""
        mock_model = Mock()
        mock_model.generate.side_effect = Exception("Connection failed")
        mock_model_class.return_value = mock_model
        
        client = WatsonxClient(config=mock_config)
        
        health = client.health_check()
        
        assert health["status"] == "unhealthy"
        assert "error" in health
        assert "Connection failed" in health["error"]


class TestSingletonPattern:
    """Test singleton pattern for client"""
    
    @patch('app.watsonx_client.WatsonxClient')
    def test_get_watsonx_client_singleton(self, mock_client_class):
        """Test that get_watsonx_client returns singleton"""
        # Reset singleton
        import app.watsonx_client
        app.watsonx_client._client_instance = None
        
        mock_instance = Mock()
        mock_client_class.return_value = mock_instance
        
        client1 = get_watsonx_client()
        client2 = get_watsonx_client()
        
        assert client1 is client2
        assert mock_client_class.call_count == 1


class TestGraniteModelVariant:
    """Test GraniteModelVariant enum"""
    
    def test_model_variants(self):
        """Test available model variants"""
        assert GraniteModelVariant.GRANITE_3_8B_INSTRUCT.value == "ibm/granite-3-8b-instruct"
        assert GraniteModelVariant.GRANITE_3_2B_INSTRUCT.value == "ibm/granite-3-2b-instruct"
        assert GraniteModelVariant.GRANITE_20B_CODE.value == "ibm/granite-20b-code-instruct"
        assert GraniteModelVariant.GRANITE_34B_CODE.value == "ibm/granite-34b-code-instruct"

# Made with Bob
