"""
Dashy dashboard converter.

Converts ServiceFragment objects to Dashy configuration format.
Dashy config: https://dashy.to/docs/configuring
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from libs.dashboard.converters.base import BaseConverter
from libs.dashboard.fragment import ServiceFragment


# Category icons for Dashy sections
CATEGORY_ICONS = {
    "CORE": "fas fa-cog",
    "INFRA": "fas fa-server",
    "DATABASES": "fas fa-database",
    "MESSAGING": "fas fa-envelope",
    "STORAGE": "fas fa-hdd",
    "REGISTRY": "fas fa-box",
    "DNS": "fas fa-globe",
    "VECTORDB": "fas fa-project-diagram",
    "MONITORING": "fas fa-chart-line",
    "AUTOMATION": "fas fa-robot",
    "DATA": "fas fa-table",
    "AUTH": "fas fa-key",
    "SECURITY": "fas fa-shield-alt",
    "AI": "fas fa-brain",
    "DEVELOPER": "fas fa-code",
    "LOWCODE": "fas fa-puzzle-piece",
    "IOT": "fas fa-microchip",
    "WIKI": "fas fa-book",
    "DOCUMENTS": "fas fa-file-alt",
    "SOCIAL": "fas fa-users",
    "CORPORATIVO": "fas fa-building",
    "EMAIL": "fas fa-at",
    "NOTIFICATIONS": "fas fa-bell",
    "OPS": "fas fa-tools",
    "SCHEDULING": "fas fa-calendar",
    "EXTERNAL": "fas fa-external-link-alt",
    "OTHER": "fas fa-cube",
}


class DashyConverter(BaseConverter):
    """
    Converts ServiceFragment objects to Dashy dashboard configuration.

    Dashy config structure:
    - pageInfo: Title, description, nav links
    - appConfig: Theme, layout, icon size
    - sections: List of sections with items
    """

    @property
    def name(self) -> str:
        return "dashy"

    def convert_fragment(self, fragment: ServiceFragment) -> Dict[str, Any]:
        """
        Convert a ServiceFragment to a Dashy item.

        Args:
            fragment: ServiceFragment to convert

        Returns:
            Dashy item dictionary
        """
        item: Dict[str, Any] = {
            "title": fragment.name,
            "icon": fragment.icon,
            "url": fragment.url,
        }

        if fragment.tags:
            item["tags"] = fragment.tags

        if fragment.description:
            item["description"] = fragment.description

        if fragment.color and fragment.color != "#3498db":
            item["color"] = fragment.color

        return item

    def convert_all(
        self,
        fragments: List[ServiceFragment],
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert all fragments to a complete Dashy configuration.

        Args:
            fragments: List of ServiceFragment objects
            base_config: Optional base configuration to extend

        Returns:
            Complete Dashy configuration
        """
        config = base_config.copy() if base_config else {}

        # Set default pageInfo
        if "pageInfo" not in config:
            config["pageInfo"] = {
                "title": "Dev Infrastructure",
                "description": "Development Environment Dashboard",
                "navLinks": [],
            }

        # Set default appConfig
        if "appConfig" not in config:
            config["appConfig"] = {
                "theme": "glass",
                "layout": "auto",
                "iconSize": "medium",
            }

        # Group fragments by category
        grouped = self.group_by_category(fragments)

        # Convert to sections
        sections = []

        # Define category order (CORE first, then alphabetical)
        priority_order = ["CORE", "INFRA", "DATABASES", "AI", "MONITORING"]
        sorted_categories = []

        for cat in priority_order:
            if cat in grouped:
                sorted_categories.append(cat)

        for cat in sorted(grouped.keys()):
            if cat not in sorted_categories:
                sorted_categories.append(cat)

        for category in sorted_categories:
            frags = grouped[category]
            section = {
                "name": category,
                "icon": CATEGORY_ICONS.get(category, "fas fa-cube"),
                "items": [self.convert_fragment(f) for f in frags],
            }
            sections.append(section)

        config["sections"] = sections
        logger.info(f"Generated Dashy config with {len(sections)} sections")
        return config

    def save(self, config: Dict[str, Any], output_path: Path) -> None:
        """
        Save Dashy configuration to YAML file.

        Args:
            config: Dashy configuration dictionary
            output_path: Path to save the YAML file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"Saved Dashy config to {output_path}")
