"""
Template validator
"""

from typing import Dict, Any

from src.template.models import Template, LayoutType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateValidator:
    """Template validation utility"""

    @staticmethod
    def validate_template(template: Template) -> bool:
        """
        Validate template completeness and correctness

        Args:
            template: Template object to validate

        Returns:
            True if valid

        Raises:
            ValueError: Validation failed
        """
        logger.debug(f"Validating template: {template.template_id}")

        # Check required layouts (using actual layout names in template)
        required_layout_types = [LayoutType.COVER, LayoutType.TOC, LayoutType.ENDING]
        existing_types = [layout.type for layout in template.layouts.values()]
        
        for required_type in required_layout_types:
            if required_type not in existing_types:
                raise ValueError(f"Missing required layout type: {required_type.value}")

        # Check at least one content layout exists
        content_layouts = [
            layout
            for layout in template.layouts.keys()
            if layout.startswith("content_")
        ]
        if not content_layouts:
            raise ValueError("Template must have at least one content layout")

        # Validate color scheme
        colors = template.theme.colors
        required_colors = [
            "primary",
            "secondary",
            "text_dark",
            "text_light",
            "background",
        ]
        for color_key in required_colors:
            if not getattr(colors, color_key, None):
                raise ValueError(f"Missing required color: {color_key}")

        # Validate fonts
        if not template.theme.fonts:
            raise ValueError("Template must define fonts")

        logger.info(f"Template '{template.template_id}' validated successfully")
        return True

    @staticmethod
    def validate_layout_content(
        layout_type: str, content: Dict[str, Any], template: Template
    ) -> bool:
        """
        Validate content matches layout requirements

        Args:
            layout_type: Layout type name
            content: Content data
            template: Template object

        Returns:
            True if valid

        Raises:
            ValueError: Content doesn't match layout
        """
        if layout_type not in template.layouts:
            raise ValueError(f"Layout '{layout_type}' not found in template")

        layout = template.layouts[layout_type]

        # Check all required placeholders have content
        for placeholder in layout.placeholders:
            # Optional placeholders (like images) can be missing
            if placeholder.type.value in ["image", "chart"]:
                continue

            if placeholder.id not in content:
                logger.warning(
                    f"Missing content for placeholder '{placeholder.id}' in layout '{layout_type}'"
                )

        return True
