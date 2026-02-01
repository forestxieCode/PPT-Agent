"""
LLM client for outline generation
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic

from src.utils.logger import get_logger
from src.utils.config import settings
from src.exceptions import LLMAPIError

logger = get_logger(__name__)


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """
        Generate text from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text

        Raises:
            LLMAPIError: API call failed
        """
        pass

    @abstractmethod
    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON from LLM

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Parsed JSON object

        Raises:
            LLMAPIError: API call failed or JSON parsing failed
        """
        pass


class OpenAIClient(LLMClient):
    """OpenAI API client"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize OpenAI client

        Args:
            api_key: OpenAI API key (defaults to settings)
            model: Model name (defaults to settings.default_model)
        """
        self.api_key = api_key or settings.openai_api_key
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")

        self.model = model or settings.default_model
        self.client = OpenAI(api_key=self.api_key)
        logger.info(f"Initialized OpenAI client with model: {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate text from OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"Calling OpenAI API with model: {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            logger.info(f"Generated {len(content)} characters from OpenAI")
            return content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMAPIError(f"OpenAI API call failed: {e}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """Generate structured JSON from OpenAI API"""
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            logger.debug(f"Calling OpenAI API (JSON mode) with model: {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)
            logger.info(f"Generated JSON with {len(result)} keys from OpenAI")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI JSON response: {e}")
            raise LLMAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMAPIError(f"OpenAI API call failed: {e}")


class AnthropicClient(LLMClient):
    """Anthropic Claude API client"""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize Anthropic client

        Args:
            api_key: Anthropic API key (defaults to settings)
            model: Model name (defaults to claude-3-5-sonnet)
        """
        self.api_key = api_key or settings.anthropic_api_key
        if not self.api_key:
            raise ValueError("Anthropic API key not configured")

        self.model = model
        self.client = Anthropic(api_key=self.api_key)
        logger.info(f"Initialized Anthropic client with model: {self.model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Generate text from Anthropic API"""
        try:
            logger.debug(f"Calling Anthropic API with model: {self.model}")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
            logger.info(f"Generated {len(content)} characters from Anthropic")
            return content

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise LLMAPIError(f"Anthropic API call failed: {e}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """Generate structured JSON from Anthropic API"""
        try:
            # Add JSON instruction to system prompt
            json_instruction = (
                "\n\nYou must respond with valid JSON only. "
                "Do not include any text before or after the JSON object."
            )
            final_system_prompt = (system_prompt or "") + json_instruction

            logger.debug(f"Calling Anthropic API (JSON mode) with model: {self.model}")

            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=final_system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )

            content = message.content[0].text
            
            # Try to extract JSON from response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            result = json.loads(content)
            logger.info(f"Generated JSON with {len(result)} keys from Anthropic")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Anthropic JSON response: {e}")
            raise LLMAPIError(f"Invalid JSON response: {e}")
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise LLMAPIError(f"Anthropic API call failed: {e}")


def create_llm_client(
    provider: str = "openai", api_key: Optional[str] = None, model: Optional[str] = None
) -> LLMClient:
    """
    Factory function to create LLM client

    Args:
        provider: LLM provider ("openai" or "anthropic")
        api_key: API key (optional, uses settings if not provided)
        model: Model name (optional, uses default if not provided)

    Returns:
        LLM client instance

    Raises:
        ValueError: Invalid provider
    """
    provider = provider.lower()

    if provider == "openai":
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == "anthropic":
        return AnthropicClient(api_key=api_key, model=model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")
