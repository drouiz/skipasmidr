"""
Homepage dashboard converter.

Converts ServiceFragment objects to Homepage YAML configuration files.
Homepage uses multiple YAML files: services.yaml, settings.yaml, widgets.yaml, bookmarks.yaml
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from loguru import logger

from libs.dashboard.converters.base import BaseConverter
from libs.dashboard.fragment import ServiceFragment


# Icon mapping from FontAwesome to Homepage format (mdi/si)
ICON_MAP = {
    # Basic MDI icons
    "fas fa-database": "mdi-database",
    "fas fa-brain": "mdi-brain",
    "fas fa-chart-line": "mdi-chart-line",
    "fas fa-cog": "mdi-cog",
    "fas fa-cube": "mdi-cube",
    "fas fa-cubes": "mdi-hexagon-multiple",
    "fas fa-home": "mdi-home",
    "fas fa-th": "mdi-view-dashboard",
    "fas fa-external-link-alt": "mdi-open-in-new",
    "fas fa-folder": "mdi-folder",
    "fas fa-server": "mdi-server",
    "fas fa-network-wired": "mdi-network",
    "fas fa-terminal": "mdi-console",
    "fas fa-code": "mdi-code-tags",
    "fas fa-robot": "mdi-robot",
    "fas fa-comments": "mdi-message",
    "fas fa-envelope": "mdi-email",
    "fas fa-file": "mdi-file",
    "fas fa-image": "mdi-image",
    "fas fa-video": "mdi-video",
    "fas fa-music": "mdi-music",
    "fas fa-download": "mdi-download",
    "fas fa-upload": "mdi-upload",
    "fas fa-cloud": "mdi-cloud",
    "fas fa-lock": "mdi-lock",
    "fas fa-key": "mdi-key",
    "fas fa-user": "mdi-account",
    "fas fa-users": "mdi-account-group",
    "fas fa-wind": "mdi-weather-windy",
    "fas fa-route": "mdi-routes",
    "fas fa-project-diagram": "mdi-sitemap",
    "fas fa-bolt": "mdi-lightning-bolt",
    "fas fa-globe": "mdi-web",
    "fas fa-palette": "mdi-palette",
    "fas fa-yin-yang": "mdi-yin-yang",
    "fab fa-docker": "si-docker",
    "fab fa-github": "si-github",
    "fab fa-gitlab": "si-gitlab",
    # Simple Icons (si-) for known services
    "traefik": "si-traefikproxy",
    "portainer": "si-portainer",
    "grafana": "si-grafana",
    "prometheus": "si-prometheus",
    "docker": "si-docker",
    "github": "si-github",
    "gitlab": "si-gitlab",
    "redis": "si-redis",
    "postgresql": "si-postgresql",
    "mongodb": "si-mongodb",
    "elasticsearch": "si-elasticsearch",
    "nginx": "si-nginx",
    "jenkins": "si-jenkins",
    "kubernetes": "si-kubernetes",
    "airflow": "si-apacheairflow",
    "n8n": "si-n8n",
    "dagster": "si-dagster",
}


class HomepageConverter(BaseConverter):
    """
    Converts ServiceFragment objects to Homepage dashboard format.

    Homepage uses YAML files for configuration:
    - services.yaml: Service definitions grouped by category
    - settings.yaml: Dashboard settings
    - widgets.yaml: Dashboard widgets
    - bookmarks.yaml: External bookmarks
    """

    @property
    def name(self) -> str:
        return "homepage"

    def _convert_icon(self, icon: str, service_name: str = "") -> str:
        """
        Convert FontAwesome icon to Homepage format (mdi/si).

        Args:
            icon: FontAwesome icon string (e.g., "fas fa-database")
            service_name: Optional service name for si- icons

        Returns:
            Homepage-compatible icon string
        """
        # Check if already in Homepage format
        if icon.startswith("mdi-") or icon.startswith("si-"):
            return icon

        # Check direct mapping
        if icon in ICON_MAP:
            return ICON_MAP[icon]

        # Check service name for si- icons
        name_lower = service_name.lower()
        if name_lower in ICON_MAP:
            return ICON_MAP[name_lower]

        # Try to extract icon name and map
        if icon.startswith("fas fa-") or icon.startswith("far fa-"):
            icon_name = icon.split(" ")[-1]
            if icon_name in ICON_MAP:
                return ICON_MAP[icon_name]
            # Default mdi conversion
            return f"mdi-{icon_name.replace('fa-', '')}"

        # Default fallback
        return "mdi-cube"

    def convert_fragment(self, fragment: ServiceFragment) -> Dict[str, Any]:
        """
        Convert a ServiceFragment to a Homepage service item.

        Args:
            fragment: ServiceFragment to convert

        Returns:
            Homepage service dictionary
        """
        # Use homepage_icon if specified, otherwise auto-convert
        if fragment.homepage_icon:
            icon = fragment.homepage_icon
        else:
            icon = self._convert_icon(fragment.icon, fragment.name)

        item = {
            "href": fragment.url,
            "icon": icon,
        }

        if fragment.description:
            item["description"] = fragment.description

        return {fragment.name: item}

    def convert_all(
        self,
        fragments: List[ServiceFragment],
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert all fragments to Homepage configuration files.

        Args:
            fragments: List of ServiceFragment objects
            base_config: Optional base configuration with settings

        Returns:
            Dictionary with 'services', 'settings', 'widgets', 'bookmarks' keys
        """
        base_config = base_config or {}

        # Group by category
        groups = self.group_by_category(fragments)

        # Build services list
        services = []
        category_order = ["CORE", "INFRA", "DATABASES", "AI", "MONITORING", "SERVICES", "EXTERNAL", "OTHER"]

        # Sort categories
        sorted_categories = [c for c in category_order if c in groups]
        sorted_categories.extend([c for c in groups if c not in sorted_categories])

        for category in sorted_categories:
            items = []
            for fragment in groups[category]:
                items.append(self.convert_fragment(fragment))
            services.append({category: items})

        # Build settings
        settings = {
            "title": base_config.get("title", "Dev Infrastructure"),
            "theme": base_config.get("theme", "dark"),
            "color": base_config.get("color", "slate"),
            "headerStyle": base_config.get("headerStyle", "clean"),
            "layout": {},
        }

        # Add layout for each category
        for category in sorted_categories:
            settings["layout"][category] = {
                "style": "row",
                "columns": min(len(groups[category]), 4),
            }

        # Build widgets
        widgets = base_config.get("widgets", [
            {"resources": {"cpu": True, "memory": True, "disk": "/"}},
            {"datetime": {"format": {"dateStyle": "short", "timeStyle": "short"}}},
        ])

        # Build bookmarks (external links)
        bookmarks = []
        if "EXTERNAL" in groups:
            ext_items = []
            for fragment in groups["EXTERNAL"]:
                ext_items.append({
                    fragment.name: [{"href": fragment.url}]
                })
            if ext_items:
                bookmarks.append({"External": ext_items})

        config = {
            "services": services,
            "settings": settings,
            "widgets": widgets,
            "bookmarks": bookmarks,
        }

        logger.info(f"Generated Homepage config with {len(services)} categories")
        return config

    def save(self, config: Dict[str, Any], output_path: Path) -> None:
        """
        Save Homepage configuration to YAML files.

        Args:
            config: Configuration dictionary with services, settings, widgets, bookmarks
            output_path: Directory path to save the files
        """
        output_dir = Path(output_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each file
        files = ["services", "settings", "widgets", "bookmarks"]
        for file_name in files:
            if file_name in config:
                file_path = output_dir / f"{file_name}.yaml"
                with open(file_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        config[file_name],
                        f,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                    )
                logger.debug(f"Saved {file_path}")

        logger.info(f"Saved Homepage config to {output_dir}")

    def generate_from_fragments(
        self,
        fragments: List[ServiceFragment],
        output_dir: Path,
        title: str = "Dev Infrastructure",
        theme: str = "dark",
    ) -> None:
        """
        Convenience method to generate and save Homepage config.

        Args:
            fragments: List of ServiceFragment objects
            output_dir: Directory to save configuration files
            title: Dashboard title
            theme: Dashboard theme
        """
        base_config = {
            "title": title,
            "theme": theme,
        }
        config = self.convert_all(fragments, base_config)
        self.save(config, output_dir)
