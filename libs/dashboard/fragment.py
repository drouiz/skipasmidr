"""
Service Fragment - Universal service definition for dashboards.

This is the canonical format that all dashboard converters use.
Each service defines a dashy.fragment.json that follows this schema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, List
import json

from loguru import logger


@dataclass
class ServiceFragment:
    """
    Universal service fragment definition.

    This is the source format (based on dashy.fragment.json) that
    gets converted to different dashboard formats.

    Attributes:
        name: Display name of the service
        icon: Icon (FontAwesome format: "fas fa-xxx")
        url: Service URL
        category: Category for grouping (e.g., "DATABASES", "AI")
        description: Optional description
        tags: Optional list of tags
        color: Optional color (hex format: "#3498db")
        pinned: Whether to pin/highlight this service
        enabled: Whether service is enabled
        service_path: Path to the service directory
    """

    name: str
    icon: str = "fas fa-cube"
    url: str = "#"
    category: str = "OTHER"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    color: str = "#3498db"
    pinned: bool = False
    enabled: bool = True
    service_path: Optional[Path] = None

    @classmethod
    def from_json(cls, data: dict, service_path: Optional[Path] = None) -> "ServiceFragment":
        """
        Create a ServiceFragment from JSON data.

        Supports both dashy.fragment.json format and extended format.
        """
        return cls(
            name=data.get("name", data.get("title", "Unknown")),
            icon=data.get("icon", "fas fa-cube"),
            url=data.get("url", "#"),
            category=data.get("category", "OTHER").upper(),
            description=data.get("description", ""),
            tags=data.get("tags", []),
            color=data.get("color", data.get("colour", "#3498db")),
            pinned=data.get("pinned", False),
            enabled=data.get("enabled", True),
            service_path=service_path,
        )

    @classmethod
    def from_file(cls, file_path: Path) -> "ServiceFragment":
        """Load fragment from a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_json(data, service_path=file_path.parent)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "icon": self.icon,
            "url": self.url,
            "category": self.category,
            "description": self.description,
            "tags": self.tags,
            "color": self.color,
            "pinned": self.pinned,
            "enabled": self.enabled,
        }


def collect_fragments(
    base_dir: Path,
    core_dir: str = "core",
    infra_dir: str = "infra",
    modules_dir: str = "modules",
) -> List[ServiceFragment]:
    """
    Collect all service fragments from the project.

    Searches for dashy.fragment.json files in:
    - core/*/
    - infra/*/*/
    - modules/*/*/

    Returns:
        List of ServiceFragment objects
    """
    fragments = []

    # Core services
    core_path = base_dir / core_dir
    if core_path.exists():
        for service_dir in core_path.iterdir():
            if service_dir.is_dir():
                fragment_file = service_dir / "dashy.fragment.json"
                if fragment_file.exists():
                    try:
                        fragment = ServiceFragment.from_file(fragment_file)
                        fragments.append(fragment)
                        logger.debug(f"Loaded fragment: {fragment.name}")
                    except Exception as e:
                        logger.warning(f"Failed to load {fragment_file}: {e}")

    # Infra and Modules (nested structure)
    for dir_name in [infra_dir, modules_dir]:
        parent_path = base_dir / dir_name
        if parent_path.exists():
            for category_dir in parent_path.iterdir():
                if category_dir.is_dir():
                    for service_dir in category_dir.iterdir():
                        if service_dir.is_dir():
                            fragment_file = service_dir / "dashy.fragment.json"
                            if fragment_file.exists():
                                try:
                                    fragment = ServiceFragment.from_file(fragment_file)
                                    fragments.append(fragment)
                                    logger.debug(f"Loaded fragment: {fragment.name}")
                                except Exception as e:
                                    logger.warning(f"Failed to load {fragment_file}: {e}")

    logger.info(f"Collected {len(fragments)} service fragments")
    return fragments
