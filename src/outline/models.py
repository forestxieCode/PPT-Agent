"""
Outline data models using Pydantic
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class SlideOutline(BaseModel):
    """Single slide outline definition"""

    slide_number: int = Field(..., ge=1, description="Slide number (starting from 1)")
    layout_type: str = Field(..., description="Layout type (e.g., cover, toc, content_single)")
    content: Dict[str, Any] = Field(..., description="Content for each placeholder")
    notes: Optional[str] = Field(default=None, description="Speaker notes")

    @field_validator("slide_number")
    @classmethod
    def validate_slide_number(cls, v: int) -> int:
        """Validate slide number is positive"""
        if v < 1:
            raise ValueError("Slide number must be >= 1")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "slide_number": 1,
                "layout_type": "cover",
                "content": {
                    "title": "2023年度工作述职报告",
                    "subtitle": "个人年度工作总结与展望",
                    "author": "张三 | 产品部",
                    "date": "2024年1月"
                },
                "notes": "开场白：感谢大家参加本次述职报告"
            }
        }
    }


class OutlineMetadata(BaseModel):
    """Outline metadata"""

    total_slides: int = Field(..., ge=1, description="Total number of slides")
    generated_at: datetime = Field(
        default_factory=datetime.now, description="Generation timestamp"
    )
    llm_model: str = Field(..., description="LLM model used for generation")
    prompt: str = Field(..., description="Original user prompt")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total_slides": 10,
                "generated_at": "2024-01-15T10:30:00Z",
                "llm_model": "gpt-4",
                "prompt": "年终述职报告",
                "temperature": 0.7
            }
        }
    }


class Outline(BaseModel):
    """Complete PPT outline"""

    outline_id: str = Field(..., description="Unique outline identifier")
    title: str = Field(..., min_length=1, max_length=200, description="Presentation title")
    author: Optional[str] = Field(default=None, description="Author name")
    template_id: str = Field(..., description="Template ID to use")
    slides: List[SlideOutline] = Field(..., min_length=1, description="List of slide outlines")
    metadata: OutlineMetadata = Field(..., description="Outline metadata")

    @field_validator("slides")
    @classmethod
    def validate_slides(cls, v: List[SlideOutline]) -> List[SlideOutline]:
        """Validate slides have sequential numbers and required types"""
        if not v:
            raise ValueError("Outline must have at least one slide")

        # Check slide numbers are sequential
        slide_numbers = [slide.slide_number for slide in v]
        if slide_numbers != list(range(1, len(v) + 1)):
            raise ValueError("Slide numbers must be sequential starting from 1")

        # Check required slide types exist
        layout_types = [slide.layout_type for slide in v]
        
        # First slide should be cover
        if v[0].layout_type != "cover":
            raise ValueError("First slide must be of type 'cover'")
        
        # Last slide should be ending
        if v[-1].layout_type != "ending":
            raise ValueError("Last slide must be of type 'ending'")
        
        # Should have a table of contents (toc)
        if "toc" not in layout_types and "table_of_contents" not in layout_types:
            raise ValueError("Outline must include a table of contents slide")

        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Validate title is not empty after stripping"""
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "outline_id": "annual_report_2023",
                "title": "2023年度工作述职报告",
                "author": "张三",
                "template_id": "business_001",
                "slides": [
                    {
                        "slide_number": 1,
                        "layout_type": "cover",
                        "content": {"title": "2023年度工作述职报告"}
                    }
                ],
                "metadata": {
                    "total_slides": 10,
                    "llm_model": "gpt-4",
                    "prompt": "年终述职报告"
                }
            }
        }
    }
