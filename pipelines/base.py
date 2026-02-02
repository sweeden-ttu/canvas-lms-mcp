"""Base types for validation pipelines."""

from typing import Any

from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    """Result of a validation check."""
    name: str = Field(..., description="Check name")
    passed: bool = Field(..., description="Whether check passed")
    message: str = Field(default="", description="Human-readable message")
    details: dict[str, Any] = Field(default_factory=dict)
