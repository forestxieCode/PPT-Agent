"""
Unit tests for outline models
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.outline.models import Outline, SlideOutline, OutlineMetadata


class TestSlideOutline:
    """Test SlideOutline model"""

    def test_valid_slide_outline(self):
        """Test creating valid slide outline"""
        slide = SlideOutline(
            slide_number=1,
            layout_type="cover",
            content={"title": "Test Title", "subtitle": "Test Subtitle"},
        )
        assert slide.slide_number == 1
        assert slide.layout_type == "cover"
        assert slide.content["title"] == "Test Title"
        assert slide.notes is None

    def test_slide_with_notes(self):
        """Test slide with speaker notes"""
        slide = SlideOutline(
            slide_number=2,
            layout_type="content_single",
            content={"title": "Content", "content": "Details"},
            notes="Remember to emphasize this point",
        )
        assert slide.notes == "Remember to emphasize this point"

    def test_invalid_slide_number(self):
        """Test invalid slide number"""
        with pytest.raises(ValidationError):
            SlideOutline(
                slide_number=0,  # Invalid: must be >= 1
                layout_type="cover",
                content={"title": "Test"},
            )


class TestOutlineMetadata:
    """Test OutlineMetadata model"""

    def test_valid_metadata(self):
        """Test creating valid metadata"""
        metadata = OutlineMetadata(
            total_slides=10,
            llm_model="gpt-4",
            prompt="Create a presentation about AI",
        )
        assert metadata.total_slides == 10
        assert metadata.llm_model == "gpt-4"
        assert isinstance(metadata.generated_at, datetime)
        assert metadata.temperature == 0.7  # Default

    def test_custom_temperature(self):
        """Test custom temperature"""
        metadata = OutlineMetadata(
            total_slides=5, llm_model="claude-3", prompt="Test", temperature=0.9
        )
        assert metadata.temperature == 0.9


class TestOutline:
    """Test Outline model"""

    def test_valid_outline(self):
        """Test creating valid outline"""
        slides = [
            SlideOutline(
                slide_number=1,
                layout_type="cover",
                content={"title": "Test Presentation"},
            ),
            SlideOutline(
                slide_number=2, layout_type="toc", content={"title": "Table of Contents"}
            ),
            SlideOutline(
                slide_number=3,
                layout_type="content_single",
                content={"title": "Content"},
            ),
            SlideOutline(
                slide_number=4,
                layout_type="ending",
                content={"message": "Thank you!"},
            ),
        ]

        metadata = OutlineMetadata(
            total_slides=4, llm_model="gpt-4", prompt="Test presentation"
        )

        outline = Outline(
            outline_id="test_001",
            title="Test Presentation",
            author="Test Author",
            template_id="business_001",
            slides=slides,
            metadata=metadata,
        )

        assert outline.outline_id == "test_001"
        assert outline.title == "Test Presentation"
        assert len(outline.slides) == 4

    def test_empty_slides(self):
        """Test outline with no slides"""
        metadata = OutlineMetadata(total_slides=1, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_002",
                title="Empty Presentation",
                template_id="business_001",
                slides=[],  # Invalid: must have at least one slide
                metadata=metadata,
            )

    def test_non_sequential_slides(self):
        """Test slides with non-sequential numbers"""
        slides = [
            SlideOutline(
                slide_number=1, layout_type="cover", content={"title": "Cover"}
            ),
            SlideOutline(
                slide_number=3, layout_type="ending", content={"message": "End"}
            ),  # Skip 2
        ]

        metadata = OutlineMetadata(total_slides=2, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_003",
                title="Test",
                template_id="business_001",
                slides=slides,
                metadata=metadata,
            )

    def test_missing_cover_slide(self):
        """Test outline without cover slide"""
        slides = [
            SlideOutline(
                slide_number=1,
                layout_type="content_single",  # Should be cover
                content={"title": "Content"},
            ),
            SlideOutline(
                slide_number=2, layout_type="ending", content={"message": "End"}
            ),
        ]

        metadata = OutlineMetadata(total_slides=2, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_004",
                title="Test",
                template_id="business_001",
                slides=slides,
                metadata=metadata,
            )

    def test_missing_toc_slide(self):
        """Test outline without table of contents"""
        slides = [
            SlideOutline(
                slide_number=1, layout_type="cover", content={"title": "Cover"}
            ),
            SlideOutline(
                slide_number=2, layout_type="ending", content={"message": "End"}
            ),
        ]

        metadata = OutlineMetadata(total_slides=2, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_005",
                title="Test",
                template_id="business_001",
                slides=slides,
                metadata=metadata,
            )

    def test_missing_ending_slide(self):
        """Test outline without ending slide"""
        slides = [
            SlideOutline(
                slide_number=1, layout_type="cover", content={"title": "Cover"}
            ),
            SlideOutline(
                slide_number=2, layout_type="toc", content={"title": "TOC"}
            ),
            SlideOutline(
                slide_number=3,
                layout_type="content_single",  # Should be ending
                content={"title": "Content"},
            ),
        ]

        metadata = OutlineMetadata(total_slides=3, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_006",
                title="Test",
                template_id="business_001",
                slides=slides,
                metadata=metadata,
            )

    def test_empty_title(self):
        """Test outline with empty title"""
        slides = [
            SlideOutline(
                slide_number=1, layout_type="cover", content={"title": "Cover"}
            ),
            SlideOutline(
                slide_number=2, layout_type="toc", content={"title": "TOC"}
            ),
            SlideOutline(
                slide_number=3, layout_type="ending", content={"message": "End"}
            ),
        ]

        metadata = OutlineMetadata(total_slides=3, llm_model="gpt-4", prompt="Test")

        with pytest.raises(ValidationError):
            Outline(
                outline_id="test_007",
                title="   ",  # Invalid: empty after strip
                template_id="business_001",
                slides=slides,
                metadata=metadata,
            )
