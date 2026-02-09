"""
Dashboard Manager - Central coordinator for dashboard generation.

Manages the collection of service fragments and generation of
dashboard configurations for different platforms.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from loguru import logger

from libs.dashboard.converters.dashy import DashyConverter
from libs.dashboard.converters.heimdall import HeimdallConverter
from libs.dashboard.converters.homepage import HomepageConverter
from libs.dashboard.fragment import ServiceFragment, collect_fragments


class DashboardManager:
    """
    Central manager for dashboard configuration generation.

    Collects service fragments from the project and converts them
    to different dashboard formats (Dashy, Heimdall, etc.).

    Usage:
        manager = DashboardManager(base_dir)
        manager.collect()
        manager.generate_dashy(output_path)
        manager.generate_heimdall(db_path)
    """

    def __init__(
        self,
        base_dir: Path,
        core_dir: str = "core",
        infra_dir: str = "infra",
        modules_dir: str = "modules",
    ):
        """
        Initialize the DashboardManager.

        Args:
            base_dir: Base directory of the project (docker-infra)
            core_dir: Name of core services directory
            infra_dir: Name of infrastructure services directory
            modules_dir: Name of modules directory
        """
        self.base_dir = Path(base_dir)
        self.core_dir = core_dir
        self.infra_dir = infra_dir
        self.modules_dir = modules_dir

        self.fragments: List[ServiceFragment] = []
        self.dashy_converter = DashyConverter()
        self.heimdall_converter = HeimdallConverter()
        self.homepage_converter = HomepageConverter()

    def collect(self) -> List[ServiceFragment]:
        """
        Collect all service fragments from the project.

        Returns:
            List of collected ServiceFragment objects
        """
        self.fragments = collect_fragments(
            self.base_dir,
            core_dir=self.core_dir,
            infra_dir=self.infra_dir,
            modules_dir=self.modules_dir,
        )
        return self.fragments

    def add_fragment(self, fragment: ServiceFragment) -> None:
        """Add a fragment manually."""
        self.fragments.append(fragment)

    def add_external_links(self, links: List[Dict[str, Any]]) -> None:
        """
        Add external links as fragments.

        Args:
            links: List of link dictionaries with name, url, icon, homepage_icon, etc.
        """
        for link in links:
            fragment = ServiceFragment(
                name=link.get("name", link.get("title", "External")),
                url=link.get("url", "#"),
                icon=link.get("icon", "fas fa-external-link-alt"),
                homepage_icon=link.get("homepage_icon", ""),
                category="EXTERNAL",
                description=link.get("description", ""),
                color=link.get("color", link.get("colour", "#3498db")),
            )
            self.fragments.append(fragment)

    def generate_dashy(
        self,
        output_path: Optional[Path] = None,
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate Dashy configuration from collected fragments.

        Args:
            output_path: Optional path to save the config file
            base_config: Optional base configuration to extend

        Returns:
            Dashy configuration dictionary
        """
        if not self.fragments:
            logger.warning("No fragments collected. Call collect() first.")

        config = self.dashy_converter.convert_all(self.fragments, base_config)

        if output_path:
            self.dashy_converter.save(config, output_path)

        return config

    def generate_heimdall(
        self,
        output_path: Optional[Path] = None,
        db_path: Optional[Path] = None,
        clear_existing: bool = False,
    ) -> Union[Dict[str, Any], Tuple[int, int]]:
        """
        Generate Heimdall configuration from collected fragments.

        Can either save to JSON file or import directly to database.

        Args:
            output_path: Optional path to save JSON config
            db_path: Optional path to Heimdall SQLite database
            clear_existing: If True and db_path provided, clear existing items

        Returns:
            If db_path: tuple of (imported, skipped)
            Otherwise: Heimdall configuration dictionary
        """
        if not self.fragments:
            logger.warning("No fragments collected. Call collect() first.")

        if db_path:
            return self.heimdall_converter.import_to_database(
                self.fragments, db_path, clear_existing
            )

        config = self.heimdall_converter.convert_all(self.fragments)

        if output_path:
            self.heimdall_converter.save(config, output_path)

        return config

    def generate_homepage(
        self,
        output_dir: Optional[Path] = None,
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate Homepage configuration from collected fragments.

        Args:
            output_dir: Optional directory to save config files
            base_config: Optional base configuration (title, theme, etc.)

        Returns:
            Homepage configuration dictionary
        """
        if not self.fragments:
            logger.warning("No fragments collected. Call collect() first.")

        config = self.homepage_converter.convert_all(self.fragments, base_config)

        if output_dir:
            self.homepage_converter.save(config, output_dir)

        return config

    def sync_all(
        self,
        dashy_output: Optional[Path] = None,
        heimdall_db: Optional[Path] = None,
        external_links: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Collect fragments and sync to all dashboards.

        Args:
            dashy_output: Path to save Dashy config
            heimdall_db: Path to Heimdall SQLite database
            external_links: Optional external links to include

        Returns:
            Summary of sync operations
        """
        self.collect()

        if external_links:
            self.add_external_links(external_links)

        result = {
            "fragments_collected": len(self.fragments),
            "dashy": None,
            "heimdall": None,
        }

        if dashy_output:
            config = self.generate_dashy(dashy_output)
            result["dashy"] = {
                "output": str(dashy_output),
                "sections": len(config.get("sections", [])),
            }

        if heimdall_db:
            imported, skipped = self.generate_heimdall(db_path=heimdall_db)
            result["heimdall"] = {
                "database": str(heimdall_db),
                "imported": imported,
                "skipped": skipped,
            }

        logger.info(f"Dashboard sync complete: {result}")
        return result
