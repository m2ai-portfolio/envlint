"""Data models for EnvLint."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Schema:
    """Schema definition for .env file validation."""
    required: List[str]
    pattern: Dict[str, str]
    allowed: Optional[List[str]] = None


@dataclass
class LintResult:
    """Results from running EnvLint validation."""
    schema_errors: List[str] = field(default_factory=list)
    usage_missing: List[str] = field(default_factory=list)
    usage_unused: List[str] = field(default_factory=list)
    git_tracked: bool = False

    @property
    def has_errors(self) -> bool:
        """Check if any errors were found."""
        return bool(self.schema_errors or self.usage_missing or self.git_tracked)

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were found."""
        return bool(self.usage_unused)
