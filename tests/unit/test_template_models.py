"""
Unit tests for template models
"""

import pytest
from pydantic import ValidationError

from src.template.models import (
    Template,
    Layout,
    Placeholder,
    ColorScheme,
    FontConfig,
    LayoutType,
    PlaceholderType,
)


class TestColorScheme:
    """Test ColorScheme model"""

    def test_valid_color_scheme(self):
        """Test creating valid color scheme"""
        colors = ColorScheme(
            primary="#1F4788",
            secondary="#F5A623",
            accent="#50E3C2",
            text_dark="#333333",
            text_light="#FFFFFF",
            background="#FFFFFF",
        )
        assert colors.primary == "#1F4788"
        assert colors.text_light == "#FFFFFF"

    def test_invalid_hex_color(self):
        """Test invalid hex color format"""
        with pytest.raises(ValidationError):
            ColorScheme(
                primary="invalid",
                secondary="#F5A623",
                accent="#50E3C2",
                text_dark="#333333",
                text_light="#FFFFFF",
                background="#FFFFFF",
            )


class TestFontConfig:
    """Test FontConfig model"""

    def test_valid_font_config(self):
        """Test creating valid font config"""
        font = FontConfig(name="微软雅黑", size=24, bold=True)
        assert font.name == "微软雅黑"
        assert font.size == 24
        assert font.bold is True
        assert font.italic is False

    def test_invalid_font_size(self):
        """Test invalid font size"""
        with pytest.raises(ValidationError):
            FontConfig(name="Arial", size=200, bold=False)


class TestPlaceholder:
    """Test Placeholder model"""

    def test_valid_placeholder(self):
        """Test creating valid placeholder"""
        ph = Placeholder(
            id="title",
            type=PlaceholderType.TITLE,
            x=0.1,
            y=0.2,
            width=0.8,
            height=0.3,
        )
        assert ph.id == "title"
        assert ph.type == PlaceholderType.TITLE
        assert ph.x == 0.1

    def test_invalid_coordinates(self):
        """Test invalid coordinates"""
        with pytest.raises(ValidationError):
            Placeholder(
                id="title",
                type=PlaceholderType.TITLE,
                x=1.5,  # Invalid: > 1
                y=0.2,
                width=0.8,
                height=0.3,
            )

    def test_zero_size(self):
        """Test zero width/height"""
        with pytest.raises(ValidationError):
            Placeholder(
                id="title",
                type=PlaceholderType.TITLE,
                x=0.1,
                y=0.2,
                width=0,  # Invalid: must be > 0
                height=0.3,
            )


class TestLayout:
    """Test Layout model"""

    def test_valid_layout(self):
        """Test creating valid layout"""
        placeholders = [
            Placeholder(
                id="title",
                type=PlaceholderType.TITLE,
                x=0.1,
                y=0.2,
                width=0.8,
                height=0.3,
            )
        ]
        layout = Layout(type=LayoutType.COVER, placeholders=placeholders)
        assert layout.type == LayoutType.COVER
        assert len(layout.placeholders) == 1

    def test_empty_placeholders(self):
        """Test layout with no placeholders"""
        with pytest.raises(ValidationError):
            Layout(type=LayoutType.COVER, placeholders=[])


class TestTemplate:
    """Test Template model"""

    def test_valid_template(self, sample_template_data):
        """Test creating valid template"""
        template = Template(**sample_template_data)
        assert template.template_id == "test_template"
        assert template.template_name == "Test Template"
        assert "cover" in template.layouts
        assert "toc" in template.layouts
        assert "ending" in template.layouts

    def test_missing_required_layout(self, sample_template_data):
        """Test template missing required layout"""
        data = sample_template_data.copy()
        del data["layouts"]["cover"]  # Remove required layout

        with pytest.raises(ValidationError):
            Template(**data)

    def test_invalid_template_id(self, sample_template_data):
        """Test invalid template ID format"""
        data = sample_template_data.copy()
        data["template_id"] = "Invalid ID!"  # Contains invalid characters

        with pytest.raises(ValidationError):
            Template(**data)
