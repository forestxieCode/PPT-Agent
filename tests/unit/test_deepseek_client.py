"""
Unit tests for DeepSeek LLM client
"""

import pytest
from unittest.mock import Mock, patch

from src.outline.llm_client import DeepSeekClient, create_llm_client
from src.exceptions import LLMAPIError


class TestDeepSeekClient:
    """Test DeepSeek client"""

    @patch("src.outline.llm_client.OpenAI")
    def test_client_initialization(self, mock_openai):
        """Test DeepSeek client initialization"""
        client = DeepSeekClient(api_key="test-key", model="deepseek-chat")
        
        assert client.api_key == "test-key"
        assert client.model == "deepseek-chat"
        
        # Verify OpenAI client was created with DeepSeek base URL
        mock_openai.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.deepseek.com"
        )

    def test_missing_api_key(self):
        """Test initialization without API key"""
        with patch("src.outline.llm_client.settings") as mock_settings:
            mock_settings.deepseek_api_key = None
            
            with pytest.raises(ValueError, match="DeepSeek API key not configured"):
                DeepSeekClient()

    @patch("src.outline.llm_client.OpenAI")
    def test_generate_text(self, mock_openai):
        """Test text generation"""
        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated text"))]
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        # Test
        client = DeepSeekClient(api_key="test-key")
        result = client.generate("Test prompt", system_prompt="System")
        
        assert result == "Generated text"
        mock_client_instance.chat.completions.create.assert_called_once()

    @patch("src.outline.llm_client.OpenAI")
    def test_generate_json(self, mock_openai):
        """Test JSON generation"""
        # Setup mock
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content='{"key": "value"}'))]
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        # Test
        client = DeepSeekClient(api_key="test-key")
        result = client.generate_json("Test prompt")
        
        assert result == {"key": "value"}
        
        # Verify JSON mode was used
        call_args = mock_client_instance.chat.completions.create.call_args
        assert call_args.kwargs["response_format"] == {"type": "json_object"}

    @patch("src.outline.llm_client.OpenAI")
    def test_generate_json_invalid_response(self, mock_openai):
        """Test JSON generation with invalid response"""
        # Setup mock with invalid JSON
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="not json"))]
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client_instance
        
        # Test
        client = DeepSeekClient(api_key="test-key")
        
        with pytest.raises(LLMAPIError, match="Invalid JSON response"):
            client.generate_json("Test prompt")

    @patch("src.outline.llm_client.OpenAI")
    def test_api_error(self, mock_openai):
        """Test API error handling"""
        # Setup mock to raise error
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client_instance
        
        # Test
        client = DeepSeekClient(api_key="test-key")
        
        with pytest.raises(LLMAPIError, match="DeepSeek API call failed"):
            client.generate("Test prompt")


class TestLLMClientFactory:
    """Test LLM client factory with DeepSeek"""

    @patch("src.outline.llm_client.OpenAI")
    def test_create_deepseek_client(self, mock_openai):
        """Test creating DeepSeek client via factory"""
        client = create_llm_client(
            provider="deepseek",
            api_key="test-key",
            model="deepseek-chat"
        )
        
        assert isinstance(client, DeepSeekClient)
        assert client.model == "deepseek-chat"

    def test_invalid_provider_error_message(self):
        """Test error message includes DeepSeek"""
        with pytest.raises(ValueError) as exc_info:
            create_llm_client(provider="invalid")
        
        error_msg = str(exc_info.value)
        assert "deepseek" in error_msg.lower()
        assert "openai" in error_msg.lower()
        assert "anthropic" in error_msg.lower()
