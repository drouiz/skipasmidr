#!/usr/bin/env python3
"""
Import apps into Heimdall database from heimdall.fragment.json files.
Run this after Heimdall starts to populate the dashboard.
"""

import json
import sqlite3
import sys
from pathlib import Path

from loguru import logger

# Paths
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
VOLUMES_DIR = BASE_DIR / "volumes"
HEIMDALL_DB = VOLUMES_DIR / "heimdall" / "www" / "app.sqlite"
CORE_DIR = BASE_DIR / "core"
INFRA_DIR = BASE_DIR / "infra"
MODULES_DIR = BASE_DIR / "modules"


def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_next_order(cursor) -> int:
    """Get next order number for apps."""
    cursor.execute("SELECT MAX(\"order\") FROM items")
    result = cursor.fetchone()[0]
    return (result or 0) + 1


def app_exists(cursor, title: str) -> bool:
    """Check if app already exists."""
    cursor.execute("SELECT id FROM items WHERE title = ?", (title,))
    return cursor.fetchone() is not None


def insert_app(cursor, app: dict, order: int):
    """Insert a new app into Heimdall."""
    cursor.execute("""
        INSERT INTO items (title, colour, icon, url, description, pinned, "order", type, class)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, 'App\\\\Item')
    """, (
        app.get("title", "App"),
        app.get("colour", "#3498db"),
        app.get("icon", "fas fa-cube"),
        app.get("url", "#"),
        app.get("description", ""),
        1 if app.get("pinned", False) else 0,
        order
    ))


def collect_fragments() -> list:
    """Collect all heimdall.fragment.json files."""
    fragments = []

    # Core heimdall fragment (base apps)
    core_fragment = CORE_DIR / "heimdall" / "heimdall.fragment.json"
    if core_fragment.exists():
        data = load_json(core_fragment)
        fragments.extend(data.get("apps", []))
        fragments.extend(data.get("external", []))

    # Service fragments from core
    for item in CORE_DIR.iterdir():
        if item.is_dir() and item.name != "heimdall":
            fragment_file = item / "heimdall.fragment.json"
            if fragment_file.exists():
                data = load_json(fragment_file)
                if isinstance(data, dict):
                    fragments.append(data)
                elif isinstance(data, list):
                    fragments.extend(data)

    # Service fragments from infra
    if INFRA_DIR.exists():
        for category_dir in INFRA_DIR.iterdir():
            if category_dir.is_dir():
                for item in category_dir.iterdir():
                    if item.is_dir():
                        fragment_file = item / "heimdall.fragment.json"
                        if fragment_file.exists():
                            data = load_json(fragment_file)
                            if isinstance(data, dict):
                                fragments.append(data)
                            elif isinstance(data, list):
                                fragments.extend(data)

    # Service fragments from modules
    if MODULES_DIR.exists():
        for category_dir in MODULES_DIR.iterdir():
            if category_dir.is_dir():
                for item in category_dir.iterdir():
                    if item.is_dir():
                        fragment_file = item / "heimdall.fragment.json"
                        if fragment_file.exists():
                            data = load_json(fragment_file)
                            if isinstance(data, dict):
                                fragments.append(data)
                            elif isinstance(data, list):
                                fragments.extend(data)

    return fragments


def main():
    if not HEIMDALL_DB.exists():
        logger.error(f"Heimdall database not found: {HEIMDALL_DB}")
        logger.info("Make sure Heimdall is running first.")
        sys.exit(1)

    logger.info(f"Connecting to: {HEIMDALL_DB}")
    conn = sqlite3.connect(str(HEIMDALL_DB))
    cursor = conn.cursor()

    # Collect all fragments
    apps = collect_fragments()
    logger.info(f"Found {len(apps)} apps to import")

    order = get_next_order(cursor)
    imported = 0
    skipped = 0

    for app in apps:
        title = app.get("title", app.get("name", ""))
        if not title:
            continue

        if app_exists(cursor, title):
            logger.debug(f"Skip (exists): {title}")
            skipped += 1
            continue

        insert_app(cursor, app, order)
        logger.info(f"Added: {title}")
        order += 1
        imported += 1

    conn.commit()
    conn.close()

    logger.success(f"Done! Imported: {imported}, Skipped: {skipped}")
    logger.info("Refresh Heimdall in your browser to see the apps.")


if __name__ == "__main__":
    main()
