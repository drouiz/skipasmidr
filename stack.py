#!/usr/bin/env python3
"""
stack.py -- Infrastructure stack manager
Reads stack.yaml and manages startup order with dependency waits.

Usage:
  python stack.py up              Arranca toda la infra (excluye optional)
  python stack.py up <grupo>      Arranca solo ese grupo
  python stack.py down            Para toda la infra (orden inverso)
  python stack.py down <grupo>    Para solo ese grupo
  python stack.py restart <grupo> Para y arranca un grupo
  python stack.py status          Estado de cada grupo
  python stack.py list            Lista grupos y servicios con sus deps
  python stack.py deps <servicio> Muestra de que depende un servicio
  python stack.py test            Health check solo de servicios desplegados
  python stack.py test <grupo>    Health check de un grupo (solo desplegados)
  python stack.py add <path>      Añade un servicio a stack.yaml desde su docker-compose
  python stack.py remove <svc>    Elimina un servicio de stack.yaml
"""
from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    print("PyYAML no instalado. Ejecuta: pip install pyyaml")
    sys.exit(1)


BASE_DIR = Path(__file__).parent

# -- ANSI colors (off on Windows without TERM set) ----------------------------
_NO_COLOR = os.environ.get("NO_COLOR") or (
    sys.platform == "win32" and not os.environ.get("TERM")
)


class C:
    GREEN = "" if _NO_COLOR else "\033[92m"
    YELLOW = "" if _NO_COLOR else "\033[93m"
    RED = "" if _NO_COLOR else "\033[91m"
    BLUE = "" if _NO_COLOR else "\033[94m"
    BOLD = "" if _NO_COLOR else "\033[1m"
    DIM = "" if _NO_COLOR else "\033[2m"
    RESET = "" if _NO_COLOR else "\033[0m"


def _ok(msg):
    print(f"{C.GREEN}[OK]{C.RESET}   {msg}")


def _err(msg):
    print(f"{C.RED}[ERR]{C.RESET}  {msg}")


def _warn(msg):
    print(f"{C.YELLOW}[WARN]{C.RESET} {msg}")


def _info(msg):
    print(f"{C.BLUE}--{C.RESET}     {msg}")


# -- YAML loading --------------------------------------------------------------

def load_stack() -> dict:
    stack_file = BASE_DIR / "stack.yaml"
    if not stack_file.exists():
        _err(f"stack.yaml no encontrado en {BASE_DIR}")
        sys.exit(1)
    with open(stack_file, encoding="utf-8") as f:
        return yaml.safe_load(f)


# -- TCP wait ------------------------------------------------------------------

def tcp_wait(
    host: str,
    port: int,
    timeout: int = 120,
    label: str = "",
) -> bool:
    """Wait until host:port accepts TCP. Returns True if ready."""
    deadline = time.time() + timeout
    label = label or f"{host}:{port}"
    sys.stdout.write(f"  Esperando {C.BOLD}{label}{C.RESET}...")
    sys.stdout.flush()
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=2):
                print(f" {C.GREEN}listo{C.RESET}")
                return True
        except (OSError, ConnectionRefusedError):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(2)
    print(f" {C.RED}TIMEOUT{C.RESET}")
    return False


# -- Docker Compose helpers ----------------------------------------------------

def _compose(args: list, path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", "compose"] + args,
        cwd=path,
        capture_output=True,
        text=True,
    )


def compose_up(path: Path) -> bool:
    return _compose(["up", "-d"], path).returncode == 0


def compose_down(path: Path) -> bool:
    return _compose(["down"], path).returncode == 0


def compose_ps(path: Path) -> list:
    r = _compose(["ps", "--format", "json"], path)
    if r.returncode != 0 or not r.stdout.strip():
        return []
    result = []
    for line in r.stdout.strip().splitlines():
        try:
            result.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return result


def get_running_containers() -> set:
    r = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    if not r.stdout.strip():
        return set()
    return set(r.stdout.strip().splitlines())


# -- Dependency resolution -----------------------------------------------------

def _needed_waits(group_cfg: dict, wait_conditions: dict) -> list:
    """Return list of (label, condition) the group needs before starting."""
    seen: dict = {}
    for svc_cfg in group_cfg.get("services", {}).values():
        for key in svc_cfg.get("wait_for", []):
            if key in wait_conditions and key not in seen:
                seen[key] = wait_conditions[key]
    return list(seen.items())


# -- Group start / stop --------------------------------------------------------

def _start_group(
    group_name: str,
    group_cfg: dict,
    wait_conditions: dict,
) -> bool:
    services = group_cfg.get("services", {})
    if not services:
        return True

    desc = group_cfg.get("description", "")
    print(f"\n{C.BOLD}[{group_name}]{C.RESET}  {C.DIM}{desc}{C.RESET}")

    # 1. Wait for TCP conditions
    for label, wc in _needed_waits(group_cfg, wait_conditions):
        ok = tcp_wait(wc["host"], wc["port"], label=label)
        if not ok:
            _warn(f"No se pudo alcanzar {label} -- continuando de todos modos")

    # 2. Start all services in parallel
    results: list = []
    lock = threading.Lock()

    def _up(name: str, cfg: dict) -> None:
        path = BASE_DIR / cfg["path"]
        if not path.exists():
            with lock:
                results.append((name, False))
                _warn(f"{name}: ruta no existe ({path})")
            return
        success = compose_up(path)
        with lock:
            results.append((name, success))

    threads = [
        threading.Thread(target=_up, args=(n, c))
        for n, c in services.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 3. Report results
    all_ok = True
    for name, success in sorted(results):
        if success:
            _ok(name)
        else:
            _err(name)
            all_ok = False
    return all_ok


def _stop_group(group_name: str, group_cfg: dict) -> bool:
    services = group_cfg.get("services", {})
    if not services:
        return True

    desc = group_cfg.get("description", "")
    print(f"\n{C.BOLD}[{group_name}]{C.RESET}  {C.DIM}{desc}{C.RESET}")

    results: list = []
    lock = threading.Lock()

    def _down(name: str, cfg: dict) -> None:
        path = BASE_DIR / cfg["path"]
        if not path.exists():
            with lock:
                results.append((name, False))
            return
        success = compose_down(path)
        with lock:
            results.append((name, success))

    threads = [
        threading.Thread(target=_down, args=(n, c))
        for n, c in services.items()
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    all_ok = True
    for name, success in sorted(results):
        if success:
            _ok(f"detenido: {name}")
        else:
            _err(f"fallo al detener: {name}")
            all_ok = False
    return all_ok


# -- Tier helpers --------------------------------------------------------------

def _sorted_groups(groups: dict, reverse: bool = False) -> list:
    return sorted(
        groups.items(),
        key=lambda x: x[1].get("order", 99),
        reverse=reverse,
    )


def _run_tiers(groups: dict, fn, reverse: bool = False) -> None:
    """Run fn(name, cfg) for each group, grouping same-order tiers in parallel."""
    current_order = None
    tier: list = []

    def _flush(t: list) -> None:
        if not t:
            return
        ts = [threading.Thread(target=fn, args=(n, c)) for n, c in t]
        for x in ts:
            x.start()
        for x in ts:
            x.join()

    for name, cfg in _sorted_groups(groups, reverse=reverse):
        order = cfg.get("order", 99)
        if order != current_order:
            _flush(tier)
            tier = [(name, cfg)]
            current_order = order
        else:
            tier.append((name, cfg))
    _flush(tier)


# -- Commands ------------------------------------------------------------------

def cmd_up(stack: dict, target_group: Optional[str] = None) -> None:
    wait_conditions = stack.get("wait_conditions", {})
    groups = stack.get("groups", {})

    if target_group:
        if target_group not in groups:
            _err(f"Grupo '{target_group}' no encontrado en stack.yaml")
            sys.exit(1)
        _start_group(target_group, groups[target_group], wait_conditions)
        return

    def _start(name: str, cfg: dict) -> None:
        if not cfg.get("optional"):
            _start_group(name, cfg, wait_conditions)

    _run_tiers(groups, _start)
    print(f"\n{C.GREEN}{C.BOLD}Stack arrancado.{C.RESET}")


def cmd_down(stack: dict, target_group: Optional[str] = None) -> None:
    groups = stack.get("groups", {})

    if target_group:
        if target_group not in groups:
            _err(f"Grupo '{target_group}' no encontrado en stack.yaml")
            sys.exit(1)
        _stop_group(target_group, groups[target_group])
        return

    _run_tiers(groups, _stop_group, reverse=True)
    print(f"\n{C.GREEN}{C.BOLD}Stack detenido.{C.RESET}")


def cmd_restart(stack: dict, target_group: str) -> None:
    cmd_down(stack, target_group)
    cmd_up(stack, target_group)


def cmd_status(stack: dict) -> None:
    running = get_running_containers()
    groups = stack.get("groups", {})

    print(f"\n{C.BOLD}Infrastructure Status{C.RESET}")
    print("=" * 55)

    total_up = 0
    total_all = 0

    for group_name, group_cfg in _sorted_groups(groups):
        services = group_cfg.get("services", {})
        if not services:
            continue

        group_up = 0
        group_total = 0
        lines = []

        for svc_name, svc_cfg in services.items():
            expected = svc_cfg.get("containers", [f"{svc_name}-infra"])
            up_count = sum(1 for c in expected if c in running)
            group_total += len(expected)
            group_up += up_count

            if up_count == len(expected):
                lines.append(f"  {C.GREEN}+{C.RESET} {svc_name}")
            elif up_count > 0:
                lines.append(
                    f"  {C.YELLOW}~{C.RESET} {svc_name}"
                    f" ({up_count}/{len(expected)} containers)"
                )
            else:
                lines.append(f"  {C.DIM}-{C.RESET} {svc_name}")

        total_up += group_up
        total_all += group_total

        opt = f" {C.DIM}(optional){C.RESET}" if group_cfg.get("optional") else ""
        if group_up == group_total:
            badge = f"{C.GREEN}{group_up}/{group_total}{C.RESET}"
        elif group_up == 0:
            badge = f"{C.DIM}{group_up}/{group_total}{C.RESET}"
        else:
            badge = f"{C.YELLOW}{group_up}/{group_total}{C.RESET}"

        print(f"\n{C.BOLD}[{group_name}]{C.RESET}{opt}  {badge}")
        for line in lines:
            print(line)

    print("\n" + "=" * 55)
    pct = int(100 * total_up / total_all) if total_all else 0
    color = C.GREEN if pct == 100 else (C.YELLOW if pct > 0 else C.DIM)
    print(
        f"{color}{C.BOLD}"
        f"Total: {total_up}/{total_all} containers running ({pct}%)"
        f"{C.RESET}\n"
    )


def cmd_list(stack: dict) -> None:
    wait_conditions = stack.get("wait_conditions", {})
    groups = stack.get("groups", {})

    print(f"\n{C.BOLD}Stack -- grupos de arranque{C.RESET}")
    current_order = None

    for group_name, group_cfg in _sorted_groups(groups):
        order = group_cfg.get("order", 99)
        if order != current_order:
            parallel = "(paralelo)" if order > 1 else ""
            print(f"\n{C.BLUE}-- Tier {order} {parallel}{C.RESET}")
            current_order = order

        opt = f"  {C.DIM}[optional]{C.RESET}" if group_cfg.get("optional") else ""
        desc = group_cfg.get("description", "")
        print(f"  {C.BOLD}[{group_name}]{C.RESET}{opt}  {C.DIM}{desc}{C.RESET}")

        for svc_name, svc_cfg in group_cfg.get("services", {}).items():
            waits = svc_cfg.get("wait_for", [])
            if waits:
                details = [
                    "{} ({}:{})".format(
                        w,
                        wait_conditions.get(w, {}).get("host", "?"),
                        wait_conditions.get(w, {}).get("port", "?"),
                    )
                    for w in waits
                ]
                wait_str = f"  {C.DIM}-> espera: {', '.join(details)}{C.RESET}"
            else:
                wait_str = ""
            print(f"    - {svc_name}{wait_str}")


def cmd_deps(stack: dict, service_name: str) -> None:
    wait_conditions = stack.get("wait_conditions", {})
    groups = stack.get("groups", {})
    running = get_running_containers()

    for group_name, group_cfg in groups.items():
        services = group_cfg.get("services", {})
        if service_name not in services:
            continue

        svc = services[service_name]
        waits = svc.get("wait_for", [])
        provides = svc.get("provides", [])
        order = group_cfg.get("order", "?")

        print(
            f"\n{C.BOLD}{service_name}{C.RESET}"
            f"  (grupo: {group_name}, tier: {order})"
        )
        print(f"  Path: {svc.get('path', '?')}")

        if waits:
            print(f"  {C.YELLOW}Espera a:{C.RESET}")
            for w in waits:
                wc = wait_conditions.get(w, {})
                print(f"    - {w}  ->  {wc.get('host', '?')}:{wc.get('port', '?')}")
        else:
            print(f"  {C.DIM}Sin dependencias (arranca inmediatamente){C.RESET}")

        if provides:
            print(f"  {C.GREEN}Provee:{C.RESET} {', '.join(provides)}")

        containers = svc.get("containers", [f"{service_name}-infra"])
        print("  Containers:")
        for c in containers:
            if c in running:
                state = f"{C.GREEN}running{C.RESET}"
            else:
                state = f"{C.DIM}stopped{C.RESET}"
            print(f"    - {c}  [{state}]")
        return

    _err(f"Servicio '{service_name}' no encontrado en stack.yaml")
    sys.exit(1)


# -- HTTP test -----------------------------------------------------------------

# Traefik port used in this setup
_TRAEFIK_PORT = 9000
_TRAEFIK_DOMAIN = "127.0.0.1.traefik.me"


def _http_check(url: str, timeout: int = 5) -> tuple:
    """Return (status_code, ms) or (-1, ms) on connection error."""
    t0 = time.time()
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, int((time.time() - t0) * 1000)
    except urllib.error.HTTPError as e:
        return e.code, int((time.time() - t0) * 1000)
    except Exception:
        return -1, int((time.time() - t0) * 1000)


def _tcp_check(host: str, port: int, timeout: int = 3) -> bool:
    """Return True if host:port accepts TCP within timeout."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def cmd_test(stack: dict, target_group: Optional[str] = None) -> None:
    """Health check solo de servicios que tienen contenedores corriendo."""
    groups = stack.get("groups", {})
    wait_conditions = stack.get("wait_conditions", {})
    running = get_running_containers()

    passed = failed = 0
    print(f"\n{C.BOLD}Health Check{C.RESET}  "
          f"{C.DIM}(solo servicios desplegados){C.RESET}")
    print("=" * 60)

    for group_name, group_cfg in _sorted_groups(groups):
        if target_group and group_name != target_group:
            continue
        services = group_cfg.get("services", {})
        if not services:
            continue

        group_lines = []

        for svc_name, svc_cfg in services.items():
            expected = svc_cfg.get("containers", [f"{svc_name}-infra"])
            if not any(c in running for c in expected):
                continue  # no desplegado, omitir

            # TCP-only services (databases): check TCP port
            if svc_cfg.get("skip_http"):
                # find wait_condition port for this service or use provides
                provides = svc_cfg.get("provides", [])
                wc = None
                for key in provides:
                    if key in wait_conditions:
                        wc = wait_conditions[key]
                        break
                if wc:
                    ok = _tcp_check(wc["host"], wc["port"])
                    if ok:
                        group_lines.append(
                            f"  {C.GREEN}OK{C.RESET} {svc_name}"
                            f"  {C.DIM}tcp:{wc['port']}{C.RESET}"
                        )
                        passed += 1
                    else:
                        group_lines.append(
                            f"  {C.RED}KO{C.RESET} {svc_name}"
                            f"  {C.RED}tcp:{wc['port']} unreachable{C.RESET}"
                        )
                        failed += 1
                else:
                    group_lines.append(
                        f"  {C.GREEN}OK{C.RESET} {svc_name}"
                        f"  {C.DIM}running (tcp-only){C.RESET}"
                    )
                    passed += 1
                continue

            # HTTP check via Traefik
            traefik_url = svc_cfg.get(
                "traefik_url",
                f"http://{svc_name}.{_TRAEFIK_DOMAIN}:{_TRAEFIK_PORT}",
            )
            code, ms = _http_check(traefik_url)

            if code == -1:
                group_lines.append(
                    f"  {C.RED}KO{C.RESET} {svc_name}"
                    f"  {C.RED}no responde{C.RESET}"
                    f"  {C.DIM}{traefik_url}{C.RESET}"
                )
                failed += 1
            elif code < 400:
                group_lines.append(
                    f"  {C.GREEN}OK{C.RESET} {svc_name}"
                    f"  {C.DIM}{code} ({ms}ms){C.RESET}"
                )
                passed += 1
            else:
                group_lines.append(
                    f"  {C.RED}KO{C.RESET} {svc_name}"
                    f"  {C.RED}{code}{C.RESET} ({ms}ms)"
                    f"  {C.DIM}{traefik_url}{C.RESET}"
                )
                failed += 1

        if group_lines:
            print(f"\n{C.BOLD}[{group_name}]{C.RESET}")
            for line in group_lines:
                print(line)

    print("\n" + "=" * 60)
    color = C.GREEN if failed == 0 else C.RED
    print(f"{color}{C.BOLD}Passed: {passed}  Failed: {failed}{C.RESET}\n")


# -- Add service ---------------------------------------------------------------

# Mapping from compose path segments to default group
_PATH_TO_GROUP = {
    "core": "dashboards",
    "infra/databases": "databases",
    "infra/storage": "data",
    "infra/messaging": "data",
    "modules/data": "data",
    "modules/developer": "developer",
    "modules/devops": "devops",
    "modules/monitoring": "monitoring",
    "modules/editors": "editors",
    "modules/corporativo": "apps",
    "modules/automation": "apps",
    "modules/auth": "devops",
    "modules/wiki": "wiki",
    "modules/ai": "ai",
    "modules/iot": "iot",
}

# Env var patterns that imply a wait condition
_ENV_TO_WAIT = [
    (re.compile(r"postgres|postgresql|pghost", re.I), "postgres"),
    (re.compile(r"mysql|mariadb", re.I), "mariadb"),
    (re.compile(r"mongo", re.I), "mongodb"),
    (re.compile(r"redis", re.I), "redis"),
    (re.compile(r"minio|s3.*endpoint", re.I), "minio"),
]


def _infer_group(rel_path: str) -> str:
    for prefix, group in _PATH_TO_GROUP.items():
        if rel_path.startswith(prefix):
            return group
    return "apps"


def _infer_wait_for(compose: dict) -> list:
    """Scan env vars in all services to detect dependencies."""
    found: set = set()
    for svc in compose.get("services", {}).values():
        env = svc.get("environment", {})
        # environment can be a dict or a list of KEY=VAL strings
        if isinstance(env, dict):
            keys = list(env.keys()) + list(str(v) for v in env.values())
        else:
            keys = [str(e) for e in env]
        for key in keys:
            for pattern, wait_key in _ENV_TO_WAIT:
                if pattern.search(key):
                    found.add(wait_key)
    return sorted(found)


def _extract_containers(compose: dict) -> list:
    names = []
    for svc in compose.get("services", {}).values():
        cn = svc.get("container_name")
        if cn:
            names.append(cn)
    return names


def _extract_traefik_hostname(compose: dict) -> Optional[str]:
    """Try to find Host(`...`) rule in Traefik labels."""
    for svc in compose.get("services", {}).values():
        labels = svc.get("labels", [])
        if isinstance(labels, dict):
            items = labels.values()
        else:
            items = labels
        for label in items:
            m = re.search(r"Host\(`([^`]+)`\)", str(label))
            if m:
                return m.group(1)
    return None


def _format_service_entry(name: str, entry: dict) -> str:
    """Format a service entry matching the rest of stack.yaml style (6-space key indent)."""
    lines = [f"      {name}:"]
    lines.append(f"        path: {entry['path']}")
    if entry.get("containers"):
        clist = "[" + ", ".join(entry["containers"]) + "]"
        lines.append(f"        containers: {clist}")
    if entry.get("wait_for"):
        wlist = "[" + ", ".join(entry["wait_for"]) + "]"
        lines.append(f"        wait_for: {wlist}")
    if entry.get("traefik_url"):
        lines.append(f"        traefik_url: {entry['traefik_url']}")
    if entry.get("skip_http"):
        lines.append(f"        skip_http: true")
    return "\n".join(lines)


def _find_services_insert_pos(raw: str, group_name: str) -> int:
    """Return byte position after the last service line in group's services block.
    Returns -1 if not found."""
    lines = raw.splitlines(keepends=True)
    state = "find_group"
    last_content_end = -1
    pos = 0

    for line in lines:
        if state == "find_group":
            if re.match(r"^  " + re.escape(group_name) + r":\s*$", line):
                state = "find_services"
        elif state == "find_services":
            if re.match(r"^    services:\s*$", line):
                state = "in_services"
                last_content_end = pos + len(line)
        elif state == "in_services":
            stripped = line.strip()
            if not stripped:
                pass  # blank lines: don't update position
            elif line.startswith("      ") or line.startswith("        "):
                last_content_end = pos + len(line)
            else:
                break  # left the services block
        pos += len(line)

    return last_content_end


def cmd_add(stack: dict, rel_path: str) -> None:
    """Read a docker-compose.yml and add the service to stack.yaml."""
    compose_path = BASE_DIR / rel_path / "docker-compose.yml"
    if not compose_path.exists():
        _err(f"No encontrado: {compose_path}")
        sys.exit(1)

    with open(compose_path, encoding="utf-8") as f:
        compose = yaml.safe_load(f)

    # Infer fields
    service_name = Path(rel_path).name
    group_name = _infer_group(rel_path)
    containers = _extract_containers(compose)
    wait_for = _infer_wait_for(compose)
    traefik_host = _extract_traefik_hostname(compose)

    # Check if already in stack
    groups = stack.get("groups", {})
    for gname, gcfg in groups.items():
        if service_name in gcfg.get("services", {}):
            _warn(f"'{service_name}' ya existe en el grupo [{gname}]")
            return

    if group_name not in groups:
        _warn(f"Grupo '{group_name}' no existe, usando 'apps'")
        group_name = "apps"

    # Build entry
    entry: dict = {"path": rel_path}
    if containers:
        entry["containers"] = containers
    if wait_for:
        entry["wait_for"] = wait_for
    if traefik_host:
        entry["traefik_url"] = f"http://{traefik_host}:{_TRAEFIK_PORT}"

    # Format and insert
    stack_file = BASE_DIR / "stack.yaml"
    with open(stack_file, encoding="utf-8") as f:
        raw = f.read()

    insert_pos = _find_services_insert_pos(raw, group_name)
    if insert_pos == -1:
        _err(f"No se pudo localizar el bloque services de [{group_name}] en stack.yaml")
        _info(f"Añade manualmente bajo groups.{group_name}.services:")
        print(_format_service_entry(service_name, entry))
        return

    formatted = _format_service_entry(service_name, entry)
    new_raw = raw[:insert_pos] + formatted + "\n" + raw[insert_pos:]

    with open(stack_file, "w", encoding="utf-8") as f:
        f.write(new_raw)

    print(f"\n{C.GREEN}{C.BOLD}Servicio '{service_name}' añadido a [{group_name}]{C.RESET}")
    print(f"  path:       {rel_path}")
    print(f"  containers: {containers or '(ninguno detectado)'}")
    if wait_for:
        print(f"  wait_for:   {wait_for}")
    if traefik_host:
        print(f"  url:        http://{traefik_host}:{_TRAEFIK_PORT}")
    print(f"\n{C.DIM}Revisa stack.yaml para ajustar grupo o dependencias.{C.RESET}\n")


# -- Remove service ------------------------------------------------------------

def cmd_remove(stack: dict, service_name: str) -> None:
    """Remove a service entry from stack.yaml."""
    groups = stack.get("groups", {})

    # Find which group owns the service
    found_group = None
    for gname, gcfg in groups.items():
        if service_name in gcfg.get("services", {}):
            found_group = gname
            break

    if not found_group:
        _err(f"Servicio '{service_name}' no encontrado en stack.yaml")
        sys.exit(1)

    stack_file = BASE_DIR / "stack.yaml"
    with open(stack_file, encoding="utf-8") as f:
        raw = f.read()

    # Match the service block: key at 6 spaces, body at 8+ spaces
    pattern = re.compile(
        r"      " + re.escape(service_name) + r":[ \t]*\n"
        r"(?:[ ]{8,}[^\n]*\n)*"
    )
    m = pattern.search(raw)
    if not m:
        _err(f"No se pudo localizar el bloque de '{service_name}' en stack.yaml")
        sys.exit(1)

    new_raw = raw[: m.start()] + raw[m.end() :]

    with open(stack_file, "w", encoding="utf-8") as f:
        f.write(new_raw)

    print(
        f"\n{C.GREEN}{C.BOLD}Servicio '{service_name}' eliminado de [{found_group}]{C.RESET}\n"
    )


# -- Main ----------------------------------------------------------------------

def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    stack = load_stack()
    cmd = args[0]

    if cmd == "up":
        cmd_up(stack, args[1] if len(args) > 1 else None)
    elif cmd == "down":
        cmd_down(stack, args[1] if len(args) > 1 else None)
    elif cmd == "restart":
        if len(args) < 2:
            _err("restart requiere un grupo. Ej: python stack.py restart data")
            sys.exit(1)
        cmd_restart(stack, args[1])
    elif cmd == "status":
        cmd_status(stack)
    elif cmd == "list":
        cmd_list(stack)
    elif cmd == "deps":
        if len(args) < 2:
            _err("deps requiere un servicio. Ej: python stack.py deps backstage")
            sys.exit(1)
        cmd_deps(stack, args[1])
    elif cmd == "test":
        cmd_test(stack, args[1] if len(args) > 1 else None)
    elif cmd == "add":
        if len(args) < 2:
            _err("add requiere un path. Ej: python stack.py add modules/data/superset")
            sys.exit(1)
        cmd_add(stack, args[1])
    elif cmd == "remove":
        if len(args) < 2:
            _err("remove requiere un servicio. Ej: python stack.py remove ntfy")
            sys.exit(1)
        cmd_remove(stack, args[1])
    else:
        _err(f"Comando desconocido: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
