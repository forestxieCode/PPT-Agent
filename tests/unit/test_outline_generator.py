"""
Unit tests for outline generator (mocked LLM)
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.outline.generator import OutlineGenerator
from src.outline.models import Outline
from src.exceptions import OutlineGenerationError


class TestOutlineGenerator:
    """Test OutlineGenerator class"""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client fixture"""
        client = Mock()
        # Mock successful JSON response
        client.generate_json.return_value = {
            "title": "测试演示",
            "author": "测试作者",
            "template_id": "business_001",
            "slides": [
                {
                    "slide_number": 1,
                    "layout_type": "cover",
                    "content": {
                        "title": "测试演示",
                        "subtitle": "副标题",
                        "author": "测试作者",
                    },
                },
                {
                    "slide_number": 2,
                    "layout_type": "toc",
                    "content": {"title": "目录", "items": ["第一部分", "第二部分"]},
                },
                {
                    "slide_number": 3,
                    "layout_type": "content_single",
                    "content": {"title": "第一部分", "content": "详细内容"},
                },
                {
                    "slide_number": 4,
                    "layout_type": "ending",
                    "content": {"message": "感谢聆听！"},
                },
            ],
        }
        client.model = "gpt-4"
        return client

    @pytest.fixture
    def generator(self, mock_llm_client):
        """Generator fixture with mocked LLM"""
        return OutlineGenerator(llm_client=mock_llm_client)

    def test_generate_outline_success(self, generator, mock_llm_client):
        """Test successful outline generation"""
        outline = generator.generate_outline(user_input="创建一个测试演示")

        assert isinstance(outline, Outline)
        assert outline.title == "测试演示"
        assert outline.author == "测试作者"
        assert outline.template_id == "business_001"
        assert len(outline.slides) == 4
        assert outline.slides[0].layout_type == "cover"
        assert outline.slides[-1].layout_type == "ending"

        # Verify LLM was called
        mock_llm_client.generate_json.assert_called_once()

    def test_generate_outline_with_template(self, generator, mock_llm_client):
        """Test outline generation with specified template"""
        outline = generator.generate_outline(
            user_input="测试演示", template_id="simple_001", author="自定义作者"
        )

        assert outline is not None
        # Verify prompt included template
        call_args = mock_llm_client.generate_json.call_args
        assert "simple_001" in call_args[1]["prompt"]

    def test_generate_outline_invalid_response(self, generator, mock_llm_client):
        """Test handling of invalid LLM response"""
        # Mock invalid response (missing required slides)
        mock_llm_client.generate_json.return_value = {
            "title": "Invalid",
            "template_id": "business_001",
            "slides": [
                {
                    "slide_number": 1,
                    "layout_type": "content_single",  # Wrong: should be cover
                    "content": {"title": "Test"},
                }
            ],
        }

        with pytest.raises(OutlineGenerationError):
            generator.generate_outline(user_input="测试", retries=1)

    def test_generate_outline_llm_error(self, generator, mock_llm_client):
        """Test handling of LLM API errors"""
        from src.exceptions import LLMAPIError

        mock_llm_client.generate_json.side_effect = LLMAPIError("API Error")

        with pytest.raises(OutlineGenerationError):
            generator.generate_outline(user_input="测试", retries=2)

    def test_refine_outline(self, generator, mock_llm_client):
        """Test outline refinement"""
        # Create initial outline
        original_outline = generator.generate_outline(user_input="原始演示")

        # Mock refined response
        mock_llm_client.generate_json.return_value = {
            "title": "修改后的演示",
            "template_id": "business_001",
            "slides": [
                {
                    "slide_number": 1,
                    "layout_type": "cover",
                    "content": {"title": "修改后的演示"},
                },
                {
                    "slide_number": 2,
                    "layout_type": "toc",
                    "content": {"title": "目录"},
                },
                {
                    "slide_number": 3,
                    "layout_type": "content_single",
                    "content": {"title": "新增内容"},
                },
                {
                    "slide_number": 4,
                    "layout_type": "ending",
                    "content": {"message": "谢谢！"},
                },
            ],
        }

        refined = generator.refine_outline(
            current_outline=original_outline, user_feedback="增加更多技术细节"
        )

        assert refined.outline_id == original_outline.outline_id  # ID preserved
        assert refined.title == "修改后的演示"

    def test_generate_outline_with_max_slides(self, generator, mock_llm_client):
        """Test outline generation with max slides limit"""
        generator.generate_outline(user_input="测试", max_slides=10)

        call_args = mock_llm_client.generate_json.call_args
        assert "10" in call_args[1]["prompt"]
