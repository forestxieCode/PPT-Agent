"""
Unit tests for PPTAgent
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.agent import PPTAgent
from src.outline.models import Outline, SlideOutline, OutlineMetadata


class TestPPTAgent:
    """Test PPTAgent class"""

    @pytest.fixture
    def mock_llm_response(self):
        """Mock LLM response fixture"""
        return {
            "title": "Test Presentation",
            "author": "Test Author",
            "template_id": "business_001",
            "slides": [
                {
                    "slide_number": 1,
                    "layout_type": "cover",
                    "content": {"title": "Test"},
                },
                {
                    "slide_number": 2,
                    "layout_type": "toc",
                    "content": {"title": "TOC"},
                },
                {
                    "slide_number": 3,
                    "layout_type": "content_single",
                    "content": {"title": "Content"},
                },
                {
                    "slide_number": 4,
                    "layout_type": "ending",
                    "content": {"message": "End"},
                },
            ],
        }

    @pytest.fixture
    def agent_with_mock(self, mock_llm_response):
        """Agent with mocked LLM fixture"""
        mock_llm = Mock()
        mock_llm.model = "gpt-4-test"
        mock_llm.generate_json.return_value = mock_llm_response

        from src.outline.generator import OutlineGenerator

        outline_gen = OutlineGenerator(llm_client=mock_llm)
        agent = PPTAgent()
        agent.outline_generator = outline_gen
        return agent

    def test_agent_initialization(self):
        """Test agent initialization"""
        agent = PPTAgent(llm_provider="openai")
        assert agent.llm_provider == "openai"
        assert agent.outline_generator is not None
        assert agent.ppt_generator is not None

    def test_generate_presentation(self, agent_with_mock, tmp_path):
        """Test complete presentation generation"""
        result = agent_with_mock.generate_presentation(
            user_input="Test presentation",
            author="Test Author",
            output_dir=tmp_path,
        )

        assert "ppt" in result
        assert "outline" in result
        assert result["ppt"].exists()
        assert result["outline"].exists()
        assert result["ppt"].suffix == ".pptx"

    def test_generate_without_outline_save(self, agent_with_mock, tmp_path):
        """Test presentation generation without saving outline"""
        result = agent_with_mock.generate_presentation(
            user_input="Test",
            output_dir=tmp_path,
            save_outline=False,
        )

        assert "ppt" in result
        assert "outline" not in result

    def test_generate_with_template(self, agent_with_mock, tmp_path):
        """Test presentation with specific template"""
        result = agent_with_mock.generate_presentation(
            user_input="Test",
            template_id="business_001",
            output_dir=tmp_path,
        )

        assert result["ppt"].exists()

    def test_list_templates(self):
        """Test listing templates"""
        agent = PPTAgent()
        templates = agent.list_templates()

        assert len(templates) >= 2
        assert any(t["template_id"] == "business_001" for t in templates)
        assert any(t["template_id"] == "simple_001" for t in templates)

    def test_get_template_info(self):
        """Test getting template info"""
        agent = PPTAgent()
        info = agent.get_template_info("business_001")

        assert info["template_id"] == "business_001"
        assert info["template_name"] == "商务风格模板"
        assert "version" in info

    def test_refine_presentation(self, agent_with_mock, tmp_path):
        """Test presentation refinement"""
        # First generate a presentation
        initial_result = agent_with_mock.generate_presentation(
            user_input="Initial",
            output_dir=tmp_path,
        )

        # Then refine it
        refined_result = agent_with_mock.refine_presentation(
            outline_path=initial_result["outline"],
            user_feedback="Make it better",
            output_dir=tmp_path,
        )

        assert "ppt" in refined_result
        assert "outline" in refined_result
        assert refined_result["ppt"].exists()
        assert "_refined" in refined_result["ppt"].name

    def test_generate_invalid_template(self, agent_with_mock, tmp_path):
        """Test generation with invalid template - should fallback to default"""
        # Mock to return invalid template
        agent_with_mock.outline_generator.llm_client.generate_json.return_value = {
            "title": "Test",
            "template_id": "nonexistent",
            "slides": [
                {"slide_number": 1, "layout_type": "cover", "content": {"title": "Test"}},
                {"slide_number": 2, "layout_type": "toc", "content": {"title": "TOC"}},
                {"slide_number": 3, "layout_type": "ending", "content": {"message": "End"}},
            ],
        }

        # Should fallback to business_001 template
        result = agent_with_mock.generate_presentation(
            user_input="Test",
            output_dir=tmp_path,
        )

        assert result["ppt"].exists()
        # Verify it used fallback template
        from src.utils.file_utils import load_json
        outline_data = load_json(result["outline"])
        assert outline_data["template_id"] == "business_001"  # Fallback
