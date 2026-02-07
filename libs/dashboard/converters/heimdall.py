"""
Heimdall dashboard converter.

Converts ServiceFragment objects to Heimdall format and imports them to SQLite.
Heimdall stores apps in an SQLite database.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from loguru import logger

from libs.dashboard.converters.base import BaseConverter
from libs.dashboard.fragment import ServiceFragment


class HeimdallConverter(BaseConverter):
    """
    Converts ServiceFragment objects to Heimdall dashboard format.

    Heimdall stores applications in an SQLite database with fields:
    - title: Display name
    - url: Service URL
    - colour: Hex color
    - icon: FontAwesome icon
    - description: Description
    - pinned: Whether to pin
    - order: Display order
    - type: 0 for app
    - class: 'App\\Item'
    """

    @property
    def name(self) -> str:
        return "heimdall"

    def convert_fragment(self, fragment: ServiceFragment) -> Dict[str, Any]:
        """
        Convert a ServiceFragment to a Heimdall item.

        Args:
            fragment: ServiceFragment to convert

        Returns:
            Heimdall item dictionary
        """
        return {
            "title": fragment.name,
            "url": fragment.url,
            "colour": fragment.color,
            "icon": fragment.icon,
            "description": fragment.description,
            "pinned": fragment.pinned,
        }

    def convert_all(
        self,
        fragments: List[ServiceFragment],
        base_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Convert all fragments to a Heimdall apps list.

        Args:
            fragments: List of ServiceFragment objects
            base_config: Optional base config with external apps

        Returns:
            Dictionary with 'apps' and optionally 'external' lists
        """
        config = base_config.copy() if base_config else {}

        apps = []
        for fragment in fragments:
            if fragment.enabled:
                apps.append(self.convert_fragment(fragment))

        config["apps"] = apps
        logger.info(f"Generated Heimdall config with {len(apps)} apps")
        return config

    def save(self, config: Dict[str, Any], output_path: Path) -> None:
        """
        Save Heimdall apps to JSON file.

        This generates a heimdall.fragment.json that can be imported.

        Args:
            config: Heimdall apps configuration
            output_path: Path to save the JSON file
        """
        import json

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved Heimdall config to {output_path}")

    def import_to_database(
        self,
        fragments: List[ServiceFragment],
        db_path: Path,
        clear_existing: bool = False,
    ) -> Tuple[int, int]:
        """
        Import fragments directly into Heimdall's SQLite database.

        Args:
            fragments: List of ServiceFragment objects
            db_path: Path to Heimdall's app.sqlite
            clear_existing: If True, remove all existing items first

        Returns:
            Tuple of (imported_count, skipped_count)
        """
        if not db_path.exists():
            logger.error(f"Heimdall database not found: {db_path}")
            return (0, 0)

        # Use timeout to avoid blocking if DB is locked
        conn = sqlite3.connect(str(db_path), timeout=5.0)
        cursor = conn.cursor()

        if clear_existing:
            cursor.execute("DELETE FROM items")
            logger.info("Cleared existing Heimdall items")

        # Get next order number
        cursor.execute('SELECT MAX("order") FROM items')
        result = cursor.fetchone()[0]
        order = (result or 0) + 1

        imported = 0
        skipped = 0

        for fragment in fragments:
            if not fragment.enabled:
                continue

            # Check if already exists
            cursor.execute("SELECT id FROM items WHERE title = ?", (fragment.name,))
            if cursor.fetchone() is not None:
                logger.debug(f"Skip (exists): {fragment.name}")
                skipped += 1
                continue

            # Insert new item
            cursor.execute(
                """
                INSERT INTO items (title, colour, icon, url, description, pinned, "order", type, class)
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'App\\Item')
                """,
                (
                    fragment.name,
                    fragment.color,
                    fragment.icon,
                    fragment.url,
                    fragment.description,
                    1 if fragment.pinned else 0,
                    order,
                ),
            )
            logger.debug(f"Added: {fragment.name}")
            order += 1
            imported += 1

        conn.commit()
        conn.close()

        logger.info(f"Heimdall import: {imported} added, {skipped} skipped")
        return (imported, skipped)

    def export_from_database(self, db_path: Path) -> List[ServiceFragment]:
        """
        Export existing Heimdall items as ServiceFragment objects.

        Args:
            db_path: Path to Heimdall's app.sqlite

        Returns:
            List of ServiceFragment objects
        """
        if not db_path.exists():
            logger.error(f"Heimdall database not found: {db_path}")
            return []

        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT title, url, colour, icon, description, pinned
            FROM items
            ORDER BY "order"
            """
        )

        fragments = []
        for row in cursor.fetchall():
            fragment = ServiceFragment(
                name=row[0] or "Unknown",
                url=row[1] or "#",
                color=row[2] or "#3498db",
                icon=row[3] or "fas fa-cube",
                description=row[4] or "",
                pinned=bool(row[5]),
            )
            fragments.append(fragment)

        conn.close()
        logger.info(f"Exported {len(fragments)} items from Heimdall")
        return fragments
