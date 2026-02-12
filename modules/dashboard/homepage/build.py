#!/usr/bin/env python3
"""
Homepage Config Builder

Merges modular config files from config/ into the volumes/homepage/ output directory.

Structure:
  config/
    sections/    -> merged into services.yaml (sorted by filename)
    widgets/     -> merged into widgets.yaml (sorted by filename)
    settings.yaml -> copied as settings.yaml
    bookmarks.yaml -> copied as bookmarks.yaml

Usage:
  python build.py                    # Build with defaults
  python build.py --restart          # Build and restart homepage container
"""

import shutil
import sys
import subprocess
from pathlib import Path

try:
    from loguru import logger
except ImportError:
    class SimpleLogger:
        def info(self, msg): print(f"INFO  | {msg}")
        def success(self, msg): print(f"OK    | {msg}")
        def error(self, msg): print(f"ERROR | {msg}")
        def warning(self, msg): print(f"WARN  | {msg}")
    logger = SimpleLogger()


def merge_yaml_files(input_dir: Path, output_file: Path) -> int:
    """Merge all YAML files in a directory into a single file.

    Each file should contain a YAML list (starting with -).
    Files are sorted by name to control order.
    Returns the number of files merged.
    """
    yaml_files = sorted(input_dir.glob("*.yaml"))

    if not yaml_files:
        logger.warning(f"No YAML files found in {input_dir}")
        return 0

    merged_lines = []
    count = 0

    for yaml_file in yaml_files:
        content = yaml_file.read_text(encoding="utf-8").strip()

        # Skip commented-out files (all lines start with #)
        active_lines = [l for l in content.split("\n") if l.strip() and not l.strip().startswith("#")]
        if not active_lines:
            logger.info(f"  Skipping {yaml_file.name} (commented out)")
            continue

        merged_lines.append(content)
        merged_lines.append("")  # blank line between sections
        count += 1
        logger.info(f"  + {yaml_file.name}")

    output_file.write_text("\n".join(merged_lines), encoding="utf-8")
    return count


def copy_file(src: Path, dst: Path) -> bool:
    """Copy a file if it exists."""
    if src.exists():
        shutil.copy2(src, dst)
        logger.info(f"  Copied {src.name}")
        return True
    else:
        logger.warning(f"  {src.name} not found, skipping")
        return False


def build(config_dir: Path = None, output_dir: Path = None):
    """Build Homepage configuration from modular files."""

    base_dir = Path(__file__).resolve().parent

    if config_dir is None:
        config_dir = base_dir / "config"
    if output_dir is None:
        output_dir = base_dir.parent.parent.parent / "volumes" / "homepage"

    sections_dir = config_dir / "sections"
    widgets_dir = config_dir / "widgets"

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Building Homepage configuration...")
    logger.info(f"  Source:  {config_dir}")
    logger.info(f"  Output:  {output_dir}")
    logger.info("")

    # 1. Merge sections -> services.yaml
    logger.info("Services (sections/):")
    count = merge_yaml_files(sections_dir, output_dir / "services.yaml")
    logger.success(f"  -> services.yaml ({count} sections)")
    logger.info("")

    # 2. Merge widgets -> widgets.yaml
    logger.info("Widgets (widgets/):")
    count = merge_yaml_files(widgets_dir, output_dir / "widgets.yaml")
    logger.success(f"  -> widgets.yaml ({count} widgets)")
    logger.info("")

    # 3. Copy settings and bookmarks
    logger.info("Static files:")
    copy_file(config_dir / "settings.yaml", output_dir / "settings.yaml")
    copy_file(config_dir / "bookmarks.yaml", output_dir / "bookmarks.yaml")

    # 4. Copy other config files that might exist (docker.yaml, kubernetes.yaml, etc.)
    for extra in config_dir.glob("*.yaml"):
        if extra.name not in ("settings.yaml", "bookmarks.yaml"):
            copy_file(extra, output_dir / extra.name)

    logger.info("")
    logger.success("Homepage config built successfully!")


def restart_container():
    """Restart the homepage container."""
    try:
        subprocess.run(
            ["docker", "restart", "homepage-infra"],
            capture_output=True, text=True, timeout=30
        )
        logger.success("Homepage container restarted")
    except Exception as e:
        logger.error(f"Failed to restart: {e}")


if __name__ == "__main__":
    build()

    if "--restart" in sys.argv:
        restart_container()
