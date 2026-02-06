#!/usr/bin/env python3
"""
Docker Infrastructure CLI
Modular Docker service management for development.
Generates a unified docker-compose for all services.

Requirements: uv add loguru pyyaml
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List, Set

try:
    from loguru import logger
except ImportError:
    print("Installing loguru...")
    subprocess.run([sys.executable, "-m", "pip", "install", "loguru"], check=True)
    from loguru import logger

try:
    import yaml
except ImportError:
    print("Installing pyyaml...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], check=True)
    import yaml

# Configure loguru
logger.remove()
logger.add(
    sys.stderr,
    format="<level>{level: <8}</level> | <cyan>{message}</cyan>",
    level="INFO",
    colorize=True
)
logger.add(
    "logs/deploy.log",
    rotation="1 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}"
)

# Base paths
BASE_DIR = Path(__file__).parent.resolve()
CORE_DIR = BASE_DIR / "core"
INFRA_DIR = BASE_DIR / "infra"
MODULES_DIR = BASE_DIR / "modules"
CONFIG_DIR = BASE_DIR / "config"
PROFILES_DIR = BASE_DIR / "profiles"
VOLUMES_DIR = BASE_DIR / "volumes"
TEMP_DIR = BASE_DIR / ".temp"
LOGS_DIR = BASE_DIR / "logs"

# Config files
DEPENDENCIES_FILE = CONFIG_DIR / "dependencies.yaml"
CREDENTIALS_ENV = CONFIG_DIR / "credentials.env"
SERVICES_ENV = CONFIG_DIR / "services.env"
DASHBOARD_CONFIG = CONFIG_DIR / "dashboard.yaml"
EXTERNAL_LINKS = CONFIG_DIR / "external-links.yaml"
STATE_FILE = BASE_DIR / ".state.json"

# Shared network
NETWORK_NAME = "infra-network"
PROJECT_NAME = "infra"


# ============================================================================
# UTILITIES
# ============================================================================

def load_yaml(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_json(file_path: Path) -> dict:
    if not file_path.exists():
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path: Path, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def save_yaml(file_path: Path, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_state() -> dict:
    return load_json(STATE_FILE)


def save_state(state: dict):
    save_json(STATE_FILE, state)


def load_dashboard_config() -> dict:
    """Load dashboard configuration."""
    default = {
        "enabled_dashboards": ["dashy"],  # dashy, homepage, heimdall
        "theme": "glass",
        "title": "Dev Infrastructure",
        "description": "Development Dashboard"
    }
    if DASHBOARD_CONFIG.exists():
        config = load_yaml(DASHBOARD_CONFIG)
        default.update(config)
    return default


def load_external_links() -> list:
    """Load external service links."""
    if EXTERNAL_LINKS.exists():
        data = load_yaml(EXTERNAL_LINKS)
        return data.get("links", [])
    return []


def run_command(cmd: list, cwd: Optional[Path] = None, capture: bool = False) -> tuple:
    try:
        logger.debug(f"Running: {' '.join(str(c) for c in cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=capture,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout if capture else ""
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return False, str(e)


def ensure_network():
    """Ensure shared network exists."""
    ok, output = run_command(
        ["docker", "network", "ls", "--format", "{{.Name}}"],
        capture=True
    )
    if ok and NETWORK_NAME not in output:
        logger.info(f"Creating network {NETWORK_NAME}...")
        run_command(["docker", "network", "create", NETWORK_NAME])


def ensure_directories():
    """Create required directories."""
    for dir_path in [CONFIG_DIR, PROFILES_DIR, VOLUMES_DIR, TEMP_DIR, LOGS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
# SERVICE DISCOVERY
# ============================================================================

def discover_services() -> dict:
    """Discover all available services."""
    services = {
        "core": {},
        "infra": {},
        "modules": {}
    }

    # Core
    if CORE_DIR.exists():
        for item in CORE_DIR.iterdir():
            if item.is_dir() and (item / "docker-compose.yml").exists():
                service_json = load_json(item / "service.json") if (item / "service.json").exists() else {}
                services["core"][item.name] = {
                    "path": item,
                    "category": "core",
                    "name": item.name,
                    "meta": service_json
                }

    # Infra (nested)
    if INFRA_DIR.exists():
        for category_dir in INFRA_DIR.iterdir():
            if category_dir.is_dir():
                for item in category_dir.iterdir():
                    if item.is_dir() and (item / "docker-compose.yml").exists():
                        service_json = load_json(item / "service.json") if (item / "service.json").exists() else {}
                        services["infra"][item.name] = {
                            "path": item,
                            "category": f"infra/{category_dir.name}",
                            "name": item.name,
                            "meta": service_json
                        }

    # Modules (nested)
    if MODULES_DIR.exists():
        for category_dir in MODULES_DIR.iterdir():
            if category_dir.is_dir():
                for item in category_dir.iterdir():
                    if item.is_dir() and (item / "docker-compose.yml").exists():
                        service_json = load_json(item / "service.json") if (item / "service.json").exists() else {}
                        services["modules"][item.name] = {
                            "path": item,
                            "category": f"modules/{category_dir.name}",
                            "name": item.name,
                            "meta": service_json
                        }

    return services


def find_service(name: str, services: dict) -> Optional[dict]:
    """Find a service by name."""
    for category in ["core", "infra", "modules"]:
        if name in services[category]:
            return services[category][name]
    return None


def get_dependencies(service_name: str) -> list:
    """Get service dependencies."""
    deps_config = load_yaml(DEPENDENCIES_FILE)
    return deps_config.get(service_name, [])


def get_running_containers() -> Set[str]:
    """Get running containers from this project only."""
    ok, output = run_command(
        ["docker", "compose", "-p", PROJECT_NAME, "ps", "--format", "{{.Name}}"],
        capture=True
    )
    if ok:
        containers = set(output.strip().split("\n")) if output.strip() else set()
        # Filter only containers with -infra suffix
        return {c for c in containers if c.endswith("-infra")}
    return set()


def get_running_services() -> List[str]:
    """Get list of running services (without -infra suffix)."""
    containers = get_running_containers()
    return sorted([c.replace("-infra", "") for c in containers if c])


# ============================================================================
# UNIFIED DOCKER-COMPOSE GENERATION
# ============================================================================

def resolve_volume_path(volume_str: str, service_path: Path) -> str:
    """Convert relative volume paths to absolute paths."""
    if ":" not in volume_str:
        return volume_str  # Named volume

    parts = volume_str.split(":")
    host_path = parts[0]

    # If relative path (starts with . or ..)
    if host_path.startswith("./") or host_path.startswith("../"):
        abs_path = (service_path / host_path).resolve()
        parts[0] = str(abs_path)
        return ":".join(parts)

    return volume_str


def merge_compose_files(service_paths: List[Path]) -> dict:
    """Merge multiple docker-compose.yml into one."""
    merged = {
        "services": {},
        "volumes": {},
        "networks": {
            "infra-network": {
                "external": True
            }
        }
    }

    for path in service_paths:
        compose_file = path / "docker-compose.yml"
        if not compose_file.exists():
            continue

        compose = load_yaml(compose_file)

        # Merge services
        if "services" in compose:
            for svc_name, svc_config in compose["services"].items():
                # Ensure all services use shared network
                if "networks" not in svc_config:
                    svc_config["networks"] = ["infra-network"]
                elif "infra-network" not in svc_config.get("networks", []):
                    if isinstance(svc_config["networks"], list):
                        svc_config["networks"].append("infra-network")

                # Remove local network config
                if isinstance(svc_config.get("networks"), dict):
                    svc_config["networks"] = ["infra-network"]

                # Convert relative volume paths to absolute
                if "volumes" in svc_config:
                    resolved_volumes = []
                    for vol in svc_config["volumes"]:
                        if isinstance(vol, str):
                            resolved_volumes.append(resolve_volume_path(vol, path))
                        else:
                            resolved_volumes.append(vol)
                    svc_config["volumes"] = resolved_volumes

                merged["services"][svc_name] = svc_config

        # Merge volumes
        if "volumes" in compose:
            for vol_name, vol_config in compose["volumes"].items():
                if vol_name not in merged["volumes"]:
                    merged["volumes"][vol_name] = vol_config

    return merged


def generate_unified_compose(services_to_start: Set[str], all_services: dict) -> Path:
    """Generate unified docker-compose.yml in .temp/"""
    ensure_directories()

    # Collect service paths
    service_paths = []
    for name in services_to_start:
        service = find_service(name, all_services)
        if service:
            service_paths.append(service["path"])

    # Merge
    merged_compose = merge_compose_files(service_paths)

    # Save
    output_file = TEMP_DIR / "docker-compose.yml"
    save_yaml(output_file, merged_compose)

    return output_file


def generate_env_file() -> Path:
    """Generate combined .env in .temp/"""
    ensure_directories()

    env_content = []

    # Load credentials.env
    if CREDENTIALS_ENV.exists():
        with open(CREDENTIALS_ENV, "r", encoding="utf-8") as f:
            env_content.append(f"# === CREDENTIALS ===\n{f.read()}")

    # Load services.env
    if SERVICES_ENV.exists():
        with open(SERVICES_ENV, "r", encoding="utf-8") as f:
            env_content.append(f"\n# === SERVICES ===\n{f.read()}")

    # Save combined
    output_file = TEMP_DIR / ".env"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(env_content))

    return output_file


def docker_compose_unified(action: str, compose_file: Path = None) -> bool:
    """Execute docker compose with unified file."""
    if compose_file is None:
        compose_file = TEMP_DIR / "docker-compose.yml"

    if not compose_file.exists():
        logger.error(f"File not found: {compose_file}")
        return False

    env_file = TEMP_DIR / ".env"

    cmd = ["docker", "compose", "-p", PROJECT_NAME, "-f", str(compose_file)]

    if env_file.exists():
        cmd.extend(["--env-file", str(env_file)])

    if action == "up":
        cmd.extend(["up", "-d", "--remove-orphans"])
    elif action == "down":
        cmd.extend(["down", "--remove-orphans"])
    elif action == "restart":
        cmd.extend(["restart"])
    elif action == "logs":
        cmd.extend(["logs", "-f"])
    elif action == "ps":
        cmd.extend(["ps"])
    else:
        cmd.append(action)

    ok, _ = run_command(cmd, cwd=TEMP_DIR)
    return ok


# ============================================================================
# DASHBOARD GENERATION
# ============================================================================

def regenerate_dashy(active_services: List[str], all_services: dict, include_core: bool = True):
    """Regenerate Dashy configuration."""
    dashboard_config = load_dashboard_config()
    external_links = load_external_links()

    dashy_config = {
        "pageInfo": {
            "title": dashboard_config.get("title", "Dev Infrastructure"),
            "description": dashboard_config.get("description", "Development Dashboard"),
            "navLinks": []
        },
        "appConfig": {
            "theme": dashboard_config.get("theme", "glass"),
            "layout": "auto",
            "iconSize": "medium"
        },
        "sections": []
    }

    categories = {}

    # Always include core
    if include_core:
        for core_name in ["traefik", "dashy", "portainer"]:
            core_service = find_service(core_name, all_services)
            if core_service:
                fragment_file = core_service["path"] / "dashy.fragment.json"
                if fragment_file.exists():
                    fragment = load_json(fragment_file)
                    category = "CORE"
                    if category not in categories:
                        categories[category] = []
                    categories[category].append({
                        "title": fragment.get("name", core_name),
                        "icon": fragment.get("icon", "fas fa-cube"),
                        "url": fragment.get("url", f"http://{core_name}.127.0.0.1.traefik.me:9000"),
                        "tags": fragment.get("tags", [])
                    })

    # Active services
    for service_name in active_services:
        if service_name in ["traefik", "dashy", "portainer"]:
            continue  # Already included in core

        service = find_service(service_name, all_services)
        if not service:
            continue

        fragment_file = service["path"] / "dashy.fragment.json"
        if fragment_file.exists():
            fragment = load_json(fragment_file)
            category = fragment.get("category", "OTHER")

            if category not in categories:
                categories[category] = []

            categories[category].append({
                "title": fragment.get("name", service_name),
                "icon": fragment.get("icon", "fas fa-cube"),
                "url": fragment.get("url", f"http://{service_name}.127.0.0.1.traefik.me:9000"),
                "tags": fragment.get("tags", [])
            })

    # Add external links section
    if external_links:
        categories["EXTERNAL"] = []
        for link in external_links:
            categories["EXTERNAL"].append({
                "title": link.get("name", "External"),
                "icon": link.get("icon", "fas fa-external-link-alt"),
                "url": link.get("url", "#"),
                "tags": link.get("tags", ["external"])
            })

    # Category icons
    category_icons = {
        "CORE": "fas fa-cog",
        "INFRA": "fas fa-database",
        "DATABASES": "fas fa-database",
        "MESSAGING": "fas fa-envelope",
        "STORAGE": "fas fa-hdd",
        "DATA": "fas fa-chart-bar",
        "AUTOMATION": "fas fa-robot",
        "MONITORING": "fas fa-chart-line",
        "SECURITY": "fas fa-shield-alt",
        "AUTH": "fas fa-key",
        "SOCIAL": "fas fa-users",
        "IOT": "fas fa-microchip",
        "LOWCODE": "fas fa-puzzle-piece",
        "DEVELOPER": "fas fa-code",
        "CORPORATIVO": "fas fa-building",
        "AI": "fas fa-brain",
        "VECTORDB": "fas fa-vector-square",
        "OPS": "fas fa-server",
        "DEVOPS": "fas fa-infinity",
        "DNS": "fas fa-globe",
        "EMAIL": "fas fa-envelope",
        "NOTIFICATIONS": "fas fa-bell",
        "WIKI": "fas fa-book",
        "DOCUMENTS": "fas fa-file-alt",
        "SCHEDULING": "fas fa-calendar",
        "ANALYTICS": "fas fa-chart-pie",
        "DASHBOARD": "fas fa-tachometer-alt",
        "EXTERNAL": "fas fa-external-link-alt",
        "CRM": "fas fa-address-book"
    }

    # Preferred order
    category_order = ["CORE", "INFRA", "DATABASES", "MESSAGING", "AI", "DATA", "MONITORING",
                      "AUTOMATION", "DEVELOPER", "DEVOPS", "CORPORATIVO", "CRM", "LOWCODE",
                      "SECURITY", "AUTH", "SOCIAL", "IOT", "OPS", "DNS", "EMAIL",
                      "NOTIFICATIONS", "DASHBOARD", "EXTERNAL", "OTHER"]

    # Sort categories
    sorted_categories = []
    for cat in category_order:
        if cat in categories:
            sorted_categories.append(cat)
    for cat in categories:
        if cat not in sorted_categories:
            sorted_categories.append(cat)

    for category in sorted_categories:
        items = categories[category]
        section = {
            "name": category,
            "icon": category_icons.get(category.upper(), "fas fa-folder"),
            "items": items
        }
        dashy_config["sections"].append(section)

    # Save
    dashy_dir = CORE_DIR / "dashy"
    dashy_dir.mkdir(parents=True, exist_ok=True)
    config_file = dashy_dir / "conf.yml"
    save_yaml(config_file, dashy_config)

    # Restart Dashy to load new config
    run_command(["docker", "restart", "dashy-infra"], capture=True)
    logger.success("Dashy updated")


def regenerate_homepage(active_services: List[str], all_services: dict):
    """Regenerate Homepage configuration."""
    dashboard_config = load_dashboard_config()
    external_links = load_external_links()

    homepage_dir = VOLUMES_DIR / "homepage"
    homepage_dir.mkdir(parents=True, exist_ok=True)

    # settings.yaml
    settings = {
        "title": dashboard_config.get("title", "Dev Infrastructure"),
        "theme": "dark",
        "color": "slate",
        "headerStyle": "clean",
        "layout": {
            "CORE": {"style": "row", "columns": 3},
            "INFRA": {"style": "row", "columns": 4},
            "SERVICES": {"style": "row", "columns": 4}
        }
    }
    save_yaml(homepage_dir / "settings.yaml", settings)

    # services.yaml
    services_config = []

    # Core services
    core_items = []
    for core_name in ["traefik", "dashy", "portainer"]:
        core_items.append({
            core_name.capitalize(): {
                "href": f"http://{core_name}.127.0.0.1.traefik.me:9000",
                "icon": f"si-{core_name}" if core_name != "dashy" else "mdi-view-dashboard",
                "description": f"{core_name.capitalize()} service"
            }
        })
    if core_items:
        services_config.append({"CORE": core_items})

    # Active services grouped by category
    categories = {}
    for service_name in active_services:
        if service_name in ["traefik", "dashy", "portainer"]:
            continue
        service = find_service(service_name, all_services)
        if service:
            cat = service["category"].split("/")[-1].upper() if "/" in service["category"] else "OTHER"
            if cat not in categories:
                categories[cat] = []
            categories[cat].append({
                service_name.capitalize(): {
                    "href": f"http://{service_name}.127.0.0.1.traefik.me:9000",
                    "description": f"{service_name} service"
                }
            })

    for cat, items in categories.items():
        services_config.append({cat: items})

    # External links
    if external_links:
        ext_items = []
        for link in external_links:
            ext_items.append({
                link.get("name", "Link"): {
                    "href": link.get("url", "#"),
                    "icon": link.get("icon", "mdi-link"),
                    "description": link.get("description", "External link")
                }
            })
        services_config.append({"EXTERNAL": ext_items})

    save_yaml(homepage_dir / "services.yaml", services_config)

    # widgets.yaml
    widgets = [
        {"resources": {"cpu": True, "memory": True, "disk": "/"}},
        {"datetime": {"format": {"dateStyle": "short", "timeStyle": "short"}}}
    ]
    save_yaml(homepage_dir / "widgets.yaml", widgets)

    # bookmarks.yaml
    bookmarks = []
    if external_links:
        bookmarks.append({
            "External Services": [
                {link.get("name"): [{"href": link.get("url")}]}
                for link in external_links
            ]
        })
    save_yaml(homepage_dir / "bookmarks.yaml", bookmarks)

    # Restart Homepage
    run_command(["docker", "restart", "homepage-infra"], capture=True)
    logger.success("Homepage updated")


def regenerate_heimdall(active_services: List[str], all_services: dict):
    """Heimdall uses database-based config, just restart it."""
    run_command(["docker", "restart", "heimdall-infra"], capture=True)
    logger.success("Heimdall restarted")


def regenerate_all_dashboards(active_services: List[str], all_services: dict):
    """Regenerate all enabled dashboards."""
    dashboard_config = load_dashboard_config()
    enabled = dashboard_config.get("enabled_dashboards", ["dashy"])

    if "dashy" in enabled:
        regenerate_dashy(active_services, all_services, include_core=True)
    if "homepage" in enabled:
        regenerate_homepage(active_services, all_services)
    if "heimdall" in enabled:
        regenerate_heimdall(active_services, all_services)


# ============================================================================
# COMMANDS
# ============================================================================

def cmd_core(args):
    """Manage core services."""
    ensure_network()
    services = discover_services()

    if args.action == "up":
        logger.info("Starting Core...")

        # Generate compose only with core
        core_services = set(services["core"].keys())
        generate_env_file()
        compose_file = generate_unified_compose(core_services, services)

        if docker_compose_unified("up", compose_file):
            logger.success("Core started")
        else:
            logger.error("Error starting core")
            return

        # Regenerate dashboards with core
        regenerate_all_dashboards([], services)

        print()
        logger.info("Access URLs:")
        print("  - http://traefik.127.0.0.1.traefik.me:9000 (Dashboard)")
        print("  - http://dashy.127.0.0.1.traefik.me:9000")
        print("  - http://portainer.127.0.0.1.traefik.me:9000")

    elif args.action == "down":
        logger.info("Stopping Core...")
        docker_compose_unified("down")
        logger.success("Core stopped")

    elif args.action == "restart":
        logger.info("Restarting Core...")
        docker_compose_unified("restart")
        logger.success("Core restarted")


def cmd_up(args):
    """Start services (replaces existing)."""
    ensure_network()
    services = discover_services()
    state = load_state()
    current = set(state.get("active", []))
    requested = set(args.services)

    # Check existing services
    if current and current != requested and not args.force:
        logger.warning(f"Active services: {', '.join(current)}")
        response = input("Replace? [y/N]: ").strip().lower()
        if response != "y":
            logger.info("Use 'deploy.py add' to add without replacing")
            return

    # Resolve dependencies
    all_to_start = set()
    for service_name in requested:
        all_to_start.add(service_name)
        deps = get_dependencies(service_name)
        all_to_start.update(deps)

    if all_to_start - requested:
        logger.info(f"Dependencies: {', '.join(all_to_start - requested)}")

    logger.info(f"Starting: {', '.join(all_to_start)}")

    # Add core
    core_services = set(services["core"].keys())
    all_to_start.update(core_services)

    # Generate unified compose
    generate_env_file()
    compose_file = generate_unified_compose(all_to_start, services)

    # Execute
    if docker_compose_unified("up", compose_file):
        logger.success("Services started")
    else:
        logger.error("Error starting services")
        return

    # Update state (without core)
    state["active"] = list(all_to_start - core_services)
    save_state(state)

    # Regenerate dashboards
    regenerate_all_dashboards(state["active"], services)

    # URLs
    print()
    logger.info("Access URLs:")
    for name in sorted(all_to_start - core_services):
        print(f"  - http://{name}.127.0.0.1.traefik.me:9000")


def cmd_add(args):
    """Add services to existing ones."""
    ensure_network()
    services = discover_services()
    state = load_state()
    current = set(state.get("active", []))
    requested = set(args.services)

    # Resolve new dependencies
    new_to_add = set()
    for service_name in requested:
        if service_name not in current:
            new_to_add.add(service_name)
            deps = get_dependencies(service_name)
            for dep in deps:
                if dep not in current:
                    new_to_add.add(dep)

    if not new_to_add:
        logger.info("All services are already active")
        return

    logger.info(f"Adding: {', '.join(new_to_add)}")

    # Combine with existing + core
    all_services_set = current.union(new_to_add)
    core_services = set(services["core"].keys())
    all_services_set.update(core_services)

    # Generate unified compose
    generate_env_file()
    compose_file = generate_unified_compose(all_services_set, services)

    # Execute
    if docker_compose_unified("up", compose_file):
        logger.success("Services added")
    else:
        logger.error("Error adding services")
        return

    # Update state
    current.update(new_to_add)
    state["active"] = list(current)
    save_state(state)

    # Regenerate dashboards
    regenerate_all_dashboards(state["active"], services)

    # New URLs
    print()
    logger.info("New URLs:")
    for name in sorted(new_to_add):
        print(f"  - http://{name}.127.0.0.1.traefik.me:9000")


def cmd_down(args):
    """Stop services."""
    services = discover_services()
    state = load_state()
    current = set(state.get("active", []))

    if args.all:
        logger.info("Stopping all services...")
        docker_compose_unified("down")
        state["active"] = []
        save_state(state)
        logger.success("All services stopped")
        return

    if not args.services:
        logger.error("Specify services or use --all")
        return

    to_stop = set(args.services)
    remaining = current - to_stop

    logger.info(f"Stopping: {', '.join(to_stop)}")

    if remaining:
        # Regenerate compose without stopped services
        core_services = set(services["core"].keys())
        all_services_set = remaining.union(core_services)

        generate_env_file()
        compose_file = generate_unified_compose(all_services_set, services)
        docker_compose_unified("up", compose_file)
    else:
        # Leave only core
        core_services = set(services["core"].keys())
        generate_env_file()
        compose_file = generate_unified_compose(core_services, services)
        docker_compose_unified("up", compose_file)

    # Update state
    state["active"] = list(remaining)
    save_state(state)

    # Regenerate dashboards
    regenerate_all_dashboards(state["active"], services)

    logger.success("Services stopped")


def cmd_restart(args):
    """Restart services."""
    services = discover_services()
    state = load_state()
    current = set(state.get("active", []))

    to_restart = set(args.services) if args.services else current

    logger.info(f"Restarting: {', '.join(to_restart)}")

    # Regenerate and restart
    core_services = set(services["core"].keys())
    all_services_set = current.union(core_services)

    generate_env_file()
    compose_file = generate_unified_compose(all_services_set, services)

    if docker_compose_unified("restart", compose_file):
        logger.success("Services restarted")
    else:
        logger.error("Error restarting")


def cmd_status(args):
    """Show current status."""
    state = load_state()

    logger.info("Current status")

    # Running containers
    ok, output = run_command(
        ["docker", "compose", "-p", PROJECT_NAME, "ps", "--format", "table {{.Name}}\t{{.Status}}"],
        capture=True
    )

    if ok and output.strip():
        print(output)
    else:
        print("No running containers")

    # Running services list
    running = get_running_services()
    if running:
        print(f"\nRunning services (this environment): {', '.join(running)}")

    # Saved state
    active = state.get("active", [])
    if active:
        print(f"Configured services: {', '.join(sorted(active))}")


def cmd_list(args):
    """List available services."""
    services = discover_services()

    if args.category:
        logger.info(f"Services in {args.category}")
        for category in ["infra", "modules"]:
            for name, service in services[category].items():
                if args.category.lower() in service["category"].lower():
                    print(f"  - {name}")
    else:
        logger.info("Available services")

        print(f"\nCORE:")
        for name in sorted(services["core"].keys()):
            print(f"  - {name}")

        print(f"\nINFRA:")
        infra_cats = {}
        for name, service in services["infra"].items():
            cat = service["category"].split("/")[1] if "/" in service["category"] else "other"
            if cat not in infra_cats:
                infra_cats[cat] = []
            infra_cats[cat].append(name)

        for cat, items in sorted(infra_cats.items()):
            print(f"  [{cat}] {', '.join(sorted(items))}")

        print(f"\nMODULES:")
        mod_cats = {}
        for name, service in services["modules"].items():
            cat = service["category"].split("/")[1] if "/" in service["category"] else "other"
            if cat not in mod_cats:
                mod_cats[cat] = []
            mod_cats[cat].append(name)

        for cat, items in sorted(mod_cats.items()):
            print(f"  [{cat}] {', '.join(sorted(items))}")


def cmd_running(args):
    """List only running services from this environment."""
    running = get_running_services()

    if running:
        logger.info(f"Running services ({len(running)} total):")
        for svc in running:
            print(f"  - {svc}")
    else:
        logger.info("No services running in this environment")


def cmd_info(args):
    """Show service info."""
    services = discover_services()
    service = find_service(args.service, services)

    if not service:
        logger.error(f"Service not found: {args.service}")
        return

    logger.info(f"Info: {args.service}")
    print(f"Category: {service['category']}")
    print(f"Path: {service['path']}")

    deps = get_dependencies(args.service)
    if deps:
        print(f"Dependencies: {', '.join(deps)}")

    print(f"URL: http://{args.service}.127.0.0.1.traefik.me:9000")

    # README
    readme = service["path"] / "README.md"
    if readme.exists():
        print(f"\nREADME:")
        with open(readme, "r", encoding="utf-8") as f:
            print(f.read()[:2000])


def cmd_profile(args):
    """Manage profiles."""
    if args.action == "list" or not args.name:
        logger.info("Available profiles")
        if PROFILES_DIR.exists():
            for profile_file in PROFILES_DIR.glob("*.yaml"):
                profile = load_yaml(profile_file)
                name = profile_file.stem
                desc = profile.get("description", "")
                profile_services = profile.get("services", [])
                print(f"  - {name}: {desc}")
                print(f"    Services: {', '.join(profile_services)}")
        return

    # Load and execute profile
    profile_file = PROFILES_DIR / f"{args.name}.yaml"
    if not profile_file.exists():
        logger.error(f"Profile not found: {args.name}")
        return

    profile = load_yaml(profile_file)
    profile_services = profile.get("services", [])

    if not profile_services:
        logger.error("Profile has no services")
        return

    logger.info(f"Profile: {args.name}")
    logger.info(f"Services: {', '.join(profile_services)}")

    # Execute as up
    class UpArgs:
        services = profile_services
        force = False

    cmd_up(UpArgs())


def cmd_logs(args):
    """Show logs."""
    cmd = ["docker", "compose", "-p", PROJECT_NAME, "logs", "-f"]
    if args.service:
        cmd.append(args.service)

    subprocess.run(cmd)


def cmd_clean(args):
    """Clean resources."""
    logger.info("Cleaning...")

    # Stop all
    docker_compose_unified("down")

    # Clean state
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    # Clean temp
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)

    logger.success("Cleanup completed")


# ============================================================================
# MAIN
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Docker Infrastructure CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python deploy.py core up              # Start core
  python deploy.py up n8n grafana       # Start services
  python deploy.py add prometheus       # Add without replacing
  python deploy.py down grafana         # Stop service
  python deploy.py down --all           # Stop all
  python deploy.py profile monitoring   # Use profile
  python deploy.py status               # Show status
  python deploy.py running              # Show running services only
  python deploy.py list                 # List services
"""
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # core
    core_parser = subparsers.add_parser("core", help="Manage core")
    core_parser.add_argument("action", choices=["up", "down", "restart"])
    core_parser.set_defaults(func=cmd_core)

    # up
    up_parser = subparsers.add_parser("up", help="Start services")
    up_parser.add_argument("services", nargs="+", help="Services")
    up_parser.add_argument("-f", "--force", action="store_true", help="Don't ask")
    up_parser.set_defaults(func=cmd_up)

    # add
    add_parser = subparsers.add_parser("add", help="Add services")
    add_parser.add_argument("services", nargs="+", help="Services")
    add_parser.set_defaults(func=cmd_add)

    # down
    down_parser = subparsers.add_parser("down", help="Stop services")
    down_parser.add_argument("services", nargs="*", help="Services")
    down_parser.add_argument("--all", action="store_true", help="All")
    down_parser.set_defaults(func=cmd_down)

    # restart
    restart_parser = subparsers.add_parser("restart", help="Restart")
    restart_parser.add_argument("services", nargs="*", help="Services")
    restart_parser.set_defaults(func=cmd_restart)

    # status
    status_parser = subparsers.add_parser("status", help="Status")
    status_parser.set_defaults(func=cmd_status)

    # running
    running_parser = subparsers.add_parser("running", help="Running services only")
    running_parser.set_defaults(func=cmd_running)

    # list
    list_parser = subparsers.add_parser("list", help="List services")
    list_parser.add_argument("-c", "--category", help="Filter")
    list_parser.set_defaults(func=cmd_list)

    # info
    info_parser = subparsers.add_parser("info", help="Service info")
    info_parser.add_argument("service", help="Name")
    info_parser.set_defaults(func=cmd_info)

    # profile
    profile_parser = subparsers.add_parser("profile", help="Use profile")
    profile_parser.add_argument("name", nargs="?", help="Name")
    profile_parser.add_argument("--list", dest="action", action="store_const", const="list")
    profile_parser.set_defaults(func=cmd_profile)

    # logs
    logs_parser = subparsers.add_parser("logs", help="View logs")
    logs_parser.add_argument("service", nargs="?", help="Service")
    logs_parser.set_defaults(func=cmd_logs)

    # clean
    clean_parser = subparsers.add_parser("clean", help="Clean all")
    clean_parser.set_defaults(func=cmd_clean)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create directories
    ensure_directories()

    args.func(args)


if __name__ == "__main__":
    main()
