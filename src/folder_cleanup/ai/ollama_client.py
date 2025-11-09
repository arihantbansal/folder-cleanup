"""Ollama client for AI interactions."""

import json
from typing import Any, Optional

import ollama
from ollama import Client

from ..models.schemas import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OllamaClientError(Exception):
    """Exception raised for Ollama client errors."""

    pass


class OllamaClient:
    """
    Client for interacting with Ollama API.

    This class handles communication with the Ollama service,
    including model selection, prompt generation, and response parsing.

    Attributes:
        config: Application configuration
        client: Ollama client instance
        model: Model name to use
    """

    def __init__(self, config: Config):
        """
        Initialize the Ollama client.

        Args:
            config: Application configuration with Ollama settings

        Raises:
            OllamaClientError: If Ollama service is not available
        """
        self.config = config
        self.model = config.ollama_model

        try:
            # Create client
            self.client = Client(host=config.ollama_host)

            # Test connection by listing models
            self._verify_connection()

            logger.info(f"Connected to Ollama at {config.ollama_host}")
            logger.info(f"Using model: {self.model}")

        except Exception as e:
            raise OllamaClientError(f"Failed to connect to Ollama: {e}") from e

    def _verify_connection(self) -> None:
        """
        Verify connection to Ollama service.

        Raises:
            OllamaClientError: If connection cannot be established
        """
        try:
            # Try to list models
            models = self.client.list()
            available_models = [m["name"] for m in models.get("models", [])]

            if not available_models:
                logger.warning("No models found in Ollama. Please pull a model first.")
                logger.warning(f"Example: ollama pull {self.model}")

            # Check if requested model is available
            if self.model not in available_models:
                logger.warning(f"Model '{self.model}' not found in Ollama")
                logger.warning(f"Available models: {', '.join(available_models)}")
                logger.warning(f"Pull it with: ollama pull {self.model}")

        except Exception as e:
            raise OllamaClientError(f"Cannot verify Ollama connection: {e}") from e

    def generate(
        self, prompt: str, temperature: float = 0.7, max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate a response from the AI model.

        Args:
            prompt: The prompt to send to the model
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
            max_retries: Maximum number of retry attempts

        Returns:
            Optional[str]: Generated response or None if failed

        Raises:
            OllamaClientError: If generation fails after all retries

        Example:
            >>> client = OllamaClient(config)
            >>> response = client.generate("Analyze this file: document.pdf")
            >>> print(response)
        """
        for attempt in range(max_retries):
            try:
                logger.debug(f"Generating response (attempt {attempt + 1}/{max_retries})")

                response = self.client.generate(
                    model=self.model,
                    prompt=prompt,
                    options={
                        "temperature": temperature,
                        "num_predict": 500,  # Limit response length
                    },
                )

                # Extract response text
                response_text = response.get("response", "").strip()

                if not response_text:
                    logger.warning("Empty response from model")
                    continue

                logger.debug(f"Generated {len(response_text)} characters")
                return response_text

            except Exception as e:
                logger.warning(f"Generation attempt {attempt + 1} failed: {e}")

                if attempt == max_retries - 1:
                    raise OllamaClientError(f"Failed to generate response: {e}") from e

                continue

        return None

    def generate_json(
        self, prompt: str, temperature: float = 0.3, max_retries: int = 3
    ) -> Optional[dict[str, Any]]:
        """
        Generate a JSON response from the AI model.

        Args:
            prompt: The prompt to send to the model (should request JSON output)
            temperature: Sampling temperature (lower for more consistent JSON)
            max_retries: Maximum number of retry attempts

        Returns:
            Optional[dict]: Parsed JSON response or None if failed

        Example:
            >>> client = OllamaClient(config)
            >>> result = client.generate_json("Return JSON: {...}")
            >>> print(result.get("suggested_name"))
        """
        response = self.generate(prompt, temperature=temperature, max_retries=max_retries)

        if not response:
            return None

        # Try to parse JSON from response
        try:
            # Sometimes models wrap JSON in markdown code blocks
            if "```json" in response:
                # Extract JSON from markdown code block
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            elif "```" in response:
                # Extract from generic code block
                start = response.find("```") + 3
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response

            # Find JSON object boundaries
            start_idx = json_str.find("{")
            end_idx = json_str.rfind("}") + 1

            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON object found in response")
                return None

            json_str = json_str[start_idx:end_idx]

            # Parse JSON
            result = json.loads(json_str)
            logger.debug(f"Parsed JSON response: {result}")
            return result

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {response}")
            return None

    def check_health(self) -> bool:
        """
        Check if Ollama service is healthy and responsive.

        Returns:
            bool: True if service is healthy

        Example:
            >>> client = OllamaClient(config)
            >>> if client.check_health():
            ...     print("Ollama is ready")
        """
        try:
            self._verify_connection()
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
