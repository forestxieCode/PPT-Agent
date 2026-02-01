"""
Unit tests for template loader
"""

import pytest
from pathlib import Path

from src.template.loader import TemplateLoader
from src.template.models import Template
from src.exceptions import TemplateNotFoundError, InvalidTemplateError


class TestTemplateLoader:
    """Test TemplateLoader class"""

    def test_load_business_template(self):
        """Test loading business template"""
        loader = TemplateLoader()
        template = loader.load_template("business_001")

        assert isinstance(template, Template)
        assert template.template_id == "business_001"
        assert template.template_name == "商务风格模板"
        assert "cover" in template.layouts
        assert "toc" in template.layouts
        assert "content_single" in template.layouts
        assert "ending" in template.layouts

    def test_load_simple_template(self):
        """Test loading simple template"""
        loader = TemplateLoader()
        template = loader.load_template("simple_001")

        assert isinstance(template, Template)
        assert template.template_id == "simple_001"
        assert template.template_name == "简约风格模板"

    def test_load_nonexistent_template(self):
        """Test loading non-existent template"""
        loader = TemplateLoader()

        with pytest.raises(TemplateNotFoundError):
            loader.load_template("nonexistent_template")

    def test_list_templates(self):
        """Test listing all templates"""
        loader = TemplateLoader()
        templates = loader.list_templates()

        assert len(templates) >= 2
        template_ids = [t["template_id"] for t in templates]
        assert "business_001" in template_ids
        assert "simple_001" in template_ids

    def test_get_template_info(self):
        """Test getting template metadata"""
        loader = TemplateLoader()
        info = loader.get_template_info("business_001")

        assert info["template_id"] == "business_001"
        assert info["template_name"] == "商务风格模板"
        assert "version" in info
        assert "description" in info

    def test_cache_mechanism(self):
        """Test template caching"""
        loader = TemplateLoader()

        # Load template twice
        template1 = loader.load_template("business_001")
        template2 = loader.load_template("business_001")

        # Should return same cached instance
        assert template1 is template2

        # Clear cache
        loader.clear_cache()

        # Should load fresh instance
        template3 = loader.load_template("business_001")
        assert template1 is not template3
