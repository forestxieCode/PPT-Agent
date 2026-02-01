"""
Custom exceptions for PPT-Agent
"""


class PPTAgentException(Exception):
    """Base exception class for PPT-Agent"""

    pass


class TemplateError(PPTAgentException):
    """Template related errors"""

    pass


class TemplateNotFoundError(TemplateError):
    """Template file not found"""

    pass


class InvalidTemplateError(TemplateError):
    """Invalid template format"""

    pass


class OutlineGenerationError(PPTAgentException):
    """Outline generation errors"""

    pass


class LLMAPIError(OutlineGenerationError):
    """LLM API call failed"""

    pass


class PPTGenerationError(PPTAgentException):
    """PPT generation errors"""

    pass


class ValidationError(PPTAgentException):
    """Data validation errors"""

    pass
