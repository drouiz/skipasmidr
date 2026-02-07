"""
Base converter class for dashboard configurations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

from libs.dashboard.fragment import ServiceFragment


class BaseConverter(ABC):
    """
    Abstract base class for dashboard converters.

    All dashboard converters inherit from this class and implement
    the convert and save methods for their specific format.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Converter name (e.g., 'dashy', 'heimdall')."""
        pass

    @abstractmethod
    def convert_fragment(self, fragment: ServiceFragment) -> Dict[str, Any]:
        """
        Convert a single ServiceFragment to the target format.

        Args:
            fragment: ServiceFragment to convert

        Returns:
            Dictionary in the target format
        """
        pass

    @abstractmethod
    def convert_all(
        self,
        fragments: List[ServiceFragment],
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert all fragments to a complete configuration.

        Args:
            fragments: List of ServiceFragment objects
            base_config: Optional base configuration to extend

        Returns:
            Complete configuration dictionary
        """
        pass

    @abstractmethod
    def save(self, config: Dict[str, Any], output_path: Path) -> None:
        """
        Save the configuration to a file.

        Args:
            config: Configuration dictionary
            output_path: Path to save the file
        """
        pass

    def group_by_category(
        self, fragments: List[ServiceFragment]
    ) -> Dict[str, List[ServiceFragment]]:
        """
        Group fragments by category.

        Args:
            fragments: List of ServiceFragment objects

        Returns:
            Dictionary with category as key and list of fragments as value
        """
        groups: Dict[str, List[ServiceFragment]] = {}
        for fragment in fragments:
            if fragment.enabled:
                category = fragment.category.upper()
                if category not in groups:
                    groups[category] = []
                groups[category].append(fragment)
        return groups
