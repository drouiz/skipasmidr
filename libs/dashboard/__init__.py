"""
Dashboard configuration converters.

Converts service fragment files to different dashboard formats:
- Dashy
- Heimdall
- Homepage (future)

Usage:
    from libs.dashboard import DashboardManager

    manager = DashboardManager(base_dir)
    manager.collect()
    manager.generate_dashy(output_path)
    manager.generate_heimdall(db_path=db_path)

    # Or sync all at once
    manager.sync_all(
        dashy_output=Path("core/dashy/conf.yml"),
        heimdall_db=Path("volumes/heimdall/www/app.sqlite"),
    )
"""

from libs.dashboard.fragment import ServiceFragment, collect_fragments
from libs.dashboard.manager import DashboardManager
from libs.dashboard.converters.base import BaseConverter
from libs.dashboard.converters.dashy import DashyConverter
from libs.dashboard.converters.heimdall import HeimdallConverter

__all__ = [
    "DashboardManager",
    "ServiceFragment",
    "collect_fragments",
    "BaseConverter",
    "DashyConverter",
    "HeimdallConverter",
]
