"""
Outline generator service
"""

import uuid
from datetime import datetime
from typing import Dict, Optional, Any
from pydantic import ValidationError

from src.outline.models import Outline, SlideOutline, OutlineMetadata
from src.outline.llm_client import LLMClient, create_llm_client
from src.outline.prompts import PromptTemplate
from src.template.loader import TemplateLoader
from src.utils.logger import get_logger
from src.utils.config import settings
from src.exceptions import OutlineGenerationError, LLMAPIError

logger = get_logger(__name__)


class OutlineGenerator:
    """PPT outline generator using LLM"""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        template_loader: Optional[TemplateLoader] = None,
        provider: str = "openai",
    ):
        """
        Initialize outline generator

        Args:
            llm_client: LLM client instance (optional, creates default if not provided)
            template_loader: Template loader instance (optional)
            provider: LLM provider ("openai" or "anthropic")
        """
        self.llm_client = llm_client or create_llm_client(provider=provider)
        self.template_loader = template_loader or TemplateLoader()
        self.prompt_template = PromptTemplate()
        logger.info("Initialized OutlineGenerator")

    def generate_outline(
        self,
        user_input: str,
        template_id: Optional[str] = None,
        author: Optional[str] = None,
        max_slides: Optional[int] = None,
        temperature: Optional[float] = None,
        retries: int = 3,
    ) -> Outline:
        """
        Generate PPT outline from user input

        Args:
            user_input: User's presentation topic/requirements
            template_id: Specific template to use (optional)
            author: Author name (optional)
            max_slides: Maximum number of slides (defaults to settings)
            temperature: LLM temperature (defaults to settings)
            retries: Number of retries on failure

        Returns:
            Generated outline object

        Raises:
            OutlineGenerationError: Failed to generate valid outline
        """
        max_slides = max_slides or settings.max_slides
        temperature = temperature or settings.temperature

        logger.info(f"Generating outline for: {user_input[:50]}...")

        # Create prompt
        prompt = self.prompt_template.create_outline_prompt(
            user_input=user_input,
            template_id=template_id,
            max_slides=max_slides,
            author=author,
        )

        # Try generation with retries
        for attempt in range(retries):
            try:
                logger.debug(f"Generation attempt {attempt + 1}/{retries}")

                # Call LLM to generate outline JSON
                outline_json = self.llm_client.generate_json(
                    prompt=prompt,
                    system_prompt=self.prompt_template.SYSTEM_PROMPT,
                    temperature=temperature,
                )

                # Validate and create outline object
                outline = self._parse_outline_json(outline_json, user_input, temperature)

                # Validate template exists if specified
                if template_id:
                    self.template_loader.load_template(template_id)
                elif outline.template_id:
                    # Validate recommended template
                    try:
                        self.template_loader.load_template(outline.template_id)
                    except Exception as e:
                        logger.warning(
                            f"Recommended template '{outline.template_id}' not found: {e}"
                        )
                        outline.template_id = "business_001"  # Fallback

                logger.info(
                    f"Successfully generated outline with {len(outline.slides)} slides"
                )
                return outline

            except LLMAPIError as e:
                logger.warning(f"LLM API error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    raise OutlineGenerationError(f"LLM API failed after {retries} attempts: {e}")

            except (ValidationError, ValueError) as e:
                logger.warning(f"Validation error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    raise OutlineGenerationError(f"Failed to generate valid outline: {e}")

            except Exception as e:
                logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
                if attempt == retries - 1:
                    raise OutlineGenerationError(f"Outline generation failed: {e}")

        raise OutlineGenerationError(f"Failed to generate outline after {retries} attempts")

    def refine_outline(
        self,
        current_outline: Outline,
        user_feedback: str,
        temperature: Optional[float] = None,
    ) -> Outline:
        """
        Refine existing outline based on user feedback

        Args:
            current_outline: Current outline object
            user_feedback: User's feedback/modification request
            temperature: LLM temperature (optional)

        Returns:
            Refined outline object

        Raises:
            OutlineGenerationError: Failed to refine outline
        """
        temperature = temperature or settings.temperature

        logger.info(f"Refining outline based on feedback: {user_feedback[:50]}...")

        try:
            # Convert current outline to dict
            current_dict = current_outline.model_dump(mode="json")

            # Create refinement prompt
            prompt = self.prompt_template.create_refinement_prompt(
                current_outline=current_dict,
                user_feedback=user_feedback,
            )

            # Generate refined outline
            refined_json = self.llm_client.generate_json(
                prompt=prompt,
                system_prompt=self.prompt_template.SYSTEM_PROMPT,
                temperature=temperature,
            )

            # Parse and validate
            refined_outline = self._parse_outline_json(
                refined_json,
                current_outline.metadata.prompt + f" (refined: {user_feedback})",
                temperature,
            )

            # Keep original outline_id
            refined_outline.outline_id = current_outline.outline_id

            logger.info("Successfully refined outline")
            return refined_outline

        except Exception as e:
            logger.error(f"Failed to refine outline: {e}")
            raise OutlineGenerationError(f"Outline refinement failed: {e}")

    def _parse_outline_json(
        self, outline_json: Dict[str, Any], prompt: str, temperature: float
    ) -> Outline:
        """
        Parse and validate outline JSON

        Args:
            outline_json: Raw JSON from LLM
            prompt: Original user prompt
            temperature: LLM temperature used

        Returns:
            Validated Outline object

        Raises:
            ValueError: Invalid outline structure
        """
        # Generate outline ID if not present
        outline_id = outline_json.get("outline_id") or f"outline_{uuid.uuid4().hex[:8]}"

        # Extract slides
        slides_data = outline_json.get("slides", [])
        if not slides_data:
            raise ValueError("Outline must contain slides")

        # Create slide objects
        slides = [SlideOutline(**slide) for slide in slides_data]

        # Create metadata
        metadata = OutlineMetadata(
            total_slides=len(slides),
            generated_at=datetime.now(),
            llm_model=getattr(self.llm_client, "model", "unknown"),
            prompt=prompt,
            temperature=temperature,
        )

        # Create outline object
        outline = Outline(
            outline_id=outline_id,
            title=outline_json.get("title", "Untitled Presentation"),
            author=outline_json.get("author"),
            template_id=outline_json.get("template_id", "business_001"),
            slides=slides,
            metadata=metadata,
        )

        return outline
