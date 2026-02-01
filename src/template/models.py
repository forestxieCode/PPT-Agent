"""
Template data models using Pydantic
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LayoutType(str, Enum):
    """Slide layout types"""

    COVER = "cover"
    TOC = "table_of_contents"
    CONTENT_SINGLE = "content_single"
    CONTENT_TWO_COLUMN = "content_two_column"
    CONTENT_IMAGE = "content_image"
    ENDING = "ending"


class PlaceholderType(str, Enum):
    """Placeholder types"""

    TEXT = "text"
    TITLE = "title"
    SUBTITLE = "subtitle"
    BODY = "body"
    LIST = "list"
    IMAGE = "image"
    CHART = "chart"


class ColorScheme(BaseModel):
    """Color scheme configuration"""

    primary: str = Field(..., description="Primary color (hex)")
    secondary: str = Field(..., description="Secondary color (hex)")
    accent: str = Field(..., description="Accent color (hex)")
    text_dark: str = Field(..., description="Dark text color (hex)")
    text_light: str = Field(..., description="Light text color (hex)")
    background: str = Field(..., description="Background color (hex)")

    @field_validator("primary", "secondary", "accent", "text_dark", "text_light", "background")
    @classmethod
    def validate_hex_color(cls, v: str) -> str:
        """Validate hex color format"""
        if not v.startswith("#") or len(v) not in [7, 9]:
            raise ValueError(f"Invalid hex color format: {v}")
        return v.upper()


class FontConfig(BaseModel):
    """Font configuration"""

    name: str = Field(..., description="Font name")
    size: int = Field(..., ge=8, le=96, description="Font size (8-96)")
    bold: bool = Field(default=False, description="Bold style")
    italic: bool = Field(default=False, description="Italic style")
    color: Optional[str] = Field(default=None, description="Font color (hex)")


class BackgroundConfig(BaseModel):
    """Background configuration"""

    type: str = Field(..., description="Background type: solid/gradient/image")
    color: Optional[str] = Field(default=None, description="Solid color or gradient start")
    color_end: Optional[str] = Field(default=None, description="Gradient end color")
    image_path: Optional[str] = Field(default=None, description="Background image path")
    opacity: float = Field(default=1.0, ge=0.0, le=1.0, description="Opacity (0-1)")


class Placeholder(BaseModel):
    """Placeholder definition for slide elements"""

    id: str = Field(..., description="Placeholder unique identifier")
    type: PlaceholderType = Field(..., description="Placeholder type")
    x: float = Field(..., ge=0, le=1, description="X position (relative 0-1)")
    y: float = Field(..., ge=0, le=1, description="Y position (relative 0-1)")
    width: float = Field(..., ge=0, le=1, description="Width (relative 0-1)")
    height: float = Field(..., ge=0, le=1, description="Height (relative 0-1)")
    font: Optional[FontConfig] = Field(default=None, description="Font configuration")
    alignment: Optional[str] = Field(
        default="left", description="Text alignment: left/center/right"
    )

    @field_validator("width", "height")
    @classmethod
    def check_size(cls, v: float) -> float:
        """Validate width and height are positive"""
        if v <= 0:
            raise ValueError("Width and height must be greater than 0")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "title",
                "type": "title",
                "x": 0.1,
                "y": 0.3,
                "width": 0.8,
                "height": 0.2,
                "font": {"name": "微软雅黑", "size": 44, "bold": True},
                "alignment": "center",
            }
        }
    }


class Layout(BaseModel):
    """Layout definition for slide type"""

    type: LayoutType = Field(..., description="Layout type")
    placeholders: List[Placeholder] = Field(..., description="List of placeholders")
    background: Optional[BackgroundConfig] = Field(
        default=None, description="Background configuration"
    )

    @field_validator("placeholders")
    @classmethod
    def validate_placeholders(cls, v: List[Placeholder]) -> List[Placeholder]:
        """Validate at least one placeholder exists"""
        if not v:
            raise ValueError("Layout must have at least one placeholder")
        return v


class ThemeConfig(BaseModel):
    """Theme configuration"""

    colors: ColorScheme = Field(..., description="Color scheme")
    fonts: Dict[str, FontConfig] = Field(..., description="Font configurations")
    spacing: Optional[Dict[str, float]] = Field(
        default=None, description="Spacing configuration"
    )


class Template(BaseModel):
    """PPT Template definition"""

    template_id: str = Field(
        ..., pattern=r"^[a-z0-9_]+$", description="Template unique identifier"
    )
    template_name: str = Field(..., description="Template display name")
    version: str = Field(default="1.0", description="Template version")
    description: Optional[str] = Field(default=None, description="Template description")
    theme: ThemeConfig = Field(..., description="Theme configuration")
    layouts: Dict[str, Layout] = Field(..., description="Layout definitions")

    @field_validator("layouts")
    @classmethod
    def validate_layouts(cls, v: Dict[str, Layout]) -> Dict[str, Layout]:
        """Validate required layouts exist"""
        required = ["cover", "toc", "ending"]
        missing = [layout for layout in required if layout not in v]
        if missing:
            raise ValueError(f"Missing required layouts: {missing}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "template_id": "business_001",
                "template_name": "商务风格模板",
                "version": "1.0",
                "description": "专业商务演示模板",
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
                        "title": {"name": "微软雅黑", "size": 44, "bold": True},
                        "subtitle": {"name": "微软雅黑", "size": 28, "bold": False},
                        "body": {"name": "微软雅黑", "size": 18, "bold": False},
                    },
                },
                "layouts": {},
            }
        }
    }
