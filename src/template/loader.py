"""
Template loader and manager
"""

from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache

from src.template.models import Template
from src.utils.file_utils import load_json
from src.utils.logger import get_logger
from src.utils.config import settings
from src.exceptions import TemplateNotFoundError, InvalidTemplateError

logger = get_logger(__name__)


class TemplateLoader:
    """Template loader and cache manager"""

    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize template loader

        Args:
            template_dir: Template directory path (defaults to settings)
        """
        self.template_dir = Path(template_dir or settings.template_dir)
        if not self.template_dir.exists():
            logger.warning(f"Template directory does not exist: {self.template_dir}")
            self.template_dir.mkdir(parents=True, exist_ok=True)

    @lru_cache(maxsize=20)
    def load_template(self, template_id: str) -> Template:
        """
        Load template by ID with caching

        Args:
            template_id: Template identifier

        Returns:
            Template object

        Raises:
            TemplateNotFoundError: Template not found
            InvalidTemplateError: Template validation failed
        """
        template_path = self.template_dir / f"{template_id}.json"

        if not template_path.exists():
            raise TemplateNotFoundError(
                f"Template '{template_id}' not found at {template_path}"
            )

        logger.info(f"Loading template: {template_id}")

        try:
            data = load_json(template_path)
            template = Template(**data)
            logger.debug(f"Template loaded successfully: {template.template_name}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template '{template_id}': {e}")
            raise InvalidTemplateError(f"Invalid template format: {e}")

    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates

        Returns:
            List of template metadata (id, name, version)
        """
        templates = []

        if not self.template_dir.exists():
            logger.warning(f"Template directory not found: {self.template_dir}")
            return templates

        for template_file in self.template_dir.glob("*.json"):
            try:
                data = load_json(template_file)
                templates.append(
                    {
                        "template_id": data.get("template_id", ""),
                        "template_name": data.get("template_name", ""),
                        "version": data.get("version", "1.0"),
                        "description": data.get("description", ""),
                    }
                )
            except Exception as e:
                logger.warning(f"Failed to read template {template_file}: {e}")
                continue

        logger.info(f"Found {len(templates)} templates")
        return templates

    def get_template_info(self, template_id: str) -> Dict[str, str]:
        """
        Get template metadata without loading full template

        Args:
            template_id: Template identifier

        Returns:
            Template metadata dictionary
        """
        template_path = self.template_dir / f"{template_id}.json"

        if not template_path.exists():
            raise TemplateNotFoundError(f"Template '{template_id}' not found")

        data = load_json(template_path)
        return {
            "template_id": data.get("template_id", ""),
            "template_name": data.get("template_name", ""),
            "version": data.get("version", "1.0"),
            "description": data.get("description", ""),
        }

    def clear_cache(self) -> None:
        """Clear template cache"""
        self.load_template.cache_clear()
        logger.info("Template cache cleared")
