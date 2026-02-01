"""
Pytest configuration and fixtures
"""

import pytest
from pathlib import Path


@pytest.fixture
def template_dir():
    """Template directory fixture"""
    return Path("templates/json")


@pytest.fixture
def output_dir(tmp_path):
    """Temporary output directory fixture"""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def sample_template_data():
    """Sample template data fixture"""
    return {
        "template_id": "test_template",
        "template_name": "Test Template",
        "version": "1.0",
        "theme": {
            "colors": {
                "primary": "#1F4788",
                "secondary": "#F5A623",
                "accent": "#50E3C2",
                "text_dark": "#333333",
                "text_light": "#FFFFFF",
                "background": "#FFFFFF",
            },
            "fonts": {
                "title": {"name": "Arial", "size": 44, "bold": True},
                "body": {"name": "Arial", "size": 18, "bold": False},
            },
        },
        "layouts": {
            "cover": {
                "type": "cover",
                "placeholders": [
                    {
                        "id": "title",
                        "type": "title",
                        "x": 0.1,
                        "y": 0.3,
                        "width": 0.8,
                        "height": 0.2,
                        "alignment": "center",
                    }
                ],
            },
            "toc": {
                "type": "table_of_contents",
                "placeholders": [
                    {
                        "id": "title",
                        "type": "title",
                        "x": 0.1,
                        "y": 0.1,
                        "width": 0.8,
                        "height": 0.15,
                        "alignment": "left",
                    }
                ],
            },
            "ending": {
                "type": "ending",
                "placeholders": [
                    {
                        "id": "message",
                        "type": "title",
                        "x": 0.2,
                        "y": 0.4,
                        "width": 0.6,
                        "height": 0.2,
                        "alignment": "center",
                    }
                ],
            },
        },
    }
