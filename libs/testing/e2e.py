"""E2E Test class for testing infrastructure services."""

import subprocess
import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

try:
    from loguru import logger
except ImportError:
    # Fallback simple logger
    class SimpleLogger:
        def info(self, msg): print(f"INFO  | {msg}")
        def success(self, msg): print(f"OK    | {msg}")
        def error(self, msg): print(f"ERROR | {msg}")
        def warning(self, msg): print(f"WARN  | {msg}")
        def debug(self, msg): pass
    logger = SimpleLogger()


class TestStatus(Enum):
    """Test result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    REDIRECT = "REDIRECT"


@dataclass
class TestResult:
    """Result of a single test."""
    name: str
    url: str
    status: TestStatus
    http_code: int
    response_time_ms: float
    message: str = ""
    redirect_url: Optional[str] = None

    def log(self) -> None:
        """Log the result using loguru."""
        time_str = f"{self.response_time_ms:.0f}ms"
        msg = f" - {self.message}" if self.message else ""

        if self.status == TestStatus.PASS:
            logger.success(f"{self.name}: {self.http_code} ({time_str}){msg} -> {self.url}")
        elif self.status == TestStatus.REDIRECT:
            logger.info(f"{self.name}: {self.http_code} ({time_str}){msg} -> {self.url}")
        elif self.status == TestStatus.SKIP:
            logger.warning(f"{self.name}: SKIPPED{msg} -> {self.url}")
        else:
            logger.error(f"{self.name}: {self.http_code} ({time_str}){msg} -> {self.url}")


@dataclass
class TestReport:
    """Full test report."""
    results: List[TestResult] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return len([r for r in self.results if r.status in (TestStatus.PASS, TestStatus.REDIRECT)])

    @property
    def failed(self) -> int:
        return len([r for r in self.results if r.status == TestStatus.FAIL])

    @property
    def skipped(self) -> int:
        return len([r for r in self.results if r.status == TestStatus.SKIP])

    def log_summary(self) -> None:
        """Log the summary using loguru."""
        if self.failed == 0:
            logger.success(f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed} | Skipped: {self.skipped}")
        else:
            logger.error(f"Total: {self.total} | Passed: {self.passed} | Failed: {self.failed} | Skipped: {self.skipped}")


class E2ETest:
    """E2E Test class for infrastructure services."""

    def __init__(self, base_domain: str = "127.0.0.1.traefik.me", port: int = 9000):
        self.base_domain = base_domain
        self.port = port
        self._results: List[TestResult] = []

    def _build_url(self, service: str) -> str:
        """Build URL for a service."""
        return f"http://{service}.{self.base_domain}:{self.port}"

    def _curl_test(self, url: str, follow_redirects: bool = False, timeout: int = 10, use_get: bool = False) -> Tuple[int, float, str]:
        """Execute curl test and return (status_code, response_time_ms, redirect_url)."""
        try:
            cmd = [
                "curl", "-s",
                "-w", "%{http_code}|%{time_total}|%{redirect_url}",
                "-o", "nul" if subprocess.sys.platform == "win32" else "/dev/null",
                "--max-time", str(timeout),
            ]
            if not use_get:
                cmd.insert(1, "-I")
            if follow_redirects:
                cmd.append("-L")
            cmd.append(url)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )

            output = result.stdout.strip()

            if "|" in output:
                parts = output.split("|")
                if len(parts) >= 3:
                    http_code = int(parts[-3].split()[-1]) if parts[-3] else 0
                    time_total = float(parts[-2]) * 1000 if parts[-2] else 0
                    redirect_url = parts[-1] if parts[-1] else ""
                    return http_code, time_total, redirect_url

            for line in output.split("\n"):
                if line.startswith("HTTP/"):
                    match = re.search(r"HTTP/[\d.]+ (\d+)", line)
                    if match:
                        return int(match.group(1)), 0, ""

            return 0, 0, ""

        except subprocess.TimeoutExpired:
            return 0, timeout * 1000, ""
        except Exception:
            return 0, 0, ""

    def _test_service(self, name: str, url: str, accept_redirects: bool = True, use_get: bool = False) -> TestResult:
        """Test a single service."""
        http_code, response_time, redirect_url = self._curl_test(url, use_get=use_get)

        if http_code == 0:
            status = TestStatus.FAIL
            message = "Connection failed or timeout"
        elif 200 <= http_code < 300:
            status = TestStatus.PASS
            message = "OK"
        elif 300 <= http_code < 400:
            if accept_redirects:
                status = TestStatus.REDIRECT
                message = f"Redirects to {redirect_url}" if redirect_url else "Redirect"
            else:
                status = TestStatus.FAIL
                message = "Unexpected redirect"
        elif http_code == 404:
            status = TestStatus.FAIL
            message = "Not Found - Check Traefik routing"
        elif http_code in (405, 406):
            # Method Not Allowed / Not Acceptable - service is up
            status = TestStatus.PASS
            message = "OK (HEAD not supported)"
        elif http_code == 502:
            status = TestStatus.FAIL
            message = "Bad Gateway - Service down"
        elif http_code == 503:
            status = TestStatus.FAIL
            message = "Service Unavailable"
        else:
            status = TestStatus.FAIL
            message = f"HTTP {http_code}"

        return TestResult(
            name=name,
            url=url,
            status=status,
            http_code=http_code,
            response_time_ms=response_time,
            message=message,
            redirect_url=redirect_url if redirect_url else None
        )

    # === Private test methods ===

    def _test_traefik(self) -> TestResult:
        return self._test_service("Traefik", self._build_url("traefik"))

    def _test_dashy(self) -> TestResult:
        return self._test_service("Dashy", self._build_url("dashy"))

    def _test_portainer(self) -> TestResult:
        return self._test_service("Portainer", self._build_url("portainer"))

    def _test_heimdall(self) -> TestResult:
        return self._test_service("Heimdall", self._build_url("heimdall"))

    def _test_homepage(self) -> TestResult:
        return self._test_service("Homepage", self._build_url("homepage"))

    def _test_pgadmin(self) -> TestResult:
        return self._test_service("pgAdmin", self._build_url("pgadmin"))

    def _test_redis(self) -> TestResult:
        return self._test_service("Redis Commander", self._build_url("redis"))

    def _test_airflow(self) -> TestResult:
        return self._test_service("Airflow", self._build_url("airflow"))

    def _test_dagster(self) -> TestResult:
        return self._test_service("Dagster", self._build_url("dagster"))

    def _test_trino(self) -> TestResult:
        return self._test_service("Trino", self._build_url("trino"))

    def _test_n8n(self) -> TestResult:
        return self._test_service("n8n", self._build_url("n8n"))

    def _test_odoo(self) -> TestResult:
        return self._test_service("Odoo", self._build_url("odoo"))

    def _test_dolibarr(self) -> TestResult:
        return self._test_service("Dolibarr", self._build_url("dolibarr"))

    def _test_openproject(self) -> TestResult:
        return self._test_service("OpenProject", self._build_url("openproject"))

    def _test_mautic(self) -> TestResult:
        return self._test_service("Mautic", self._build_url("mautic"))

    def _test_nocodb(self) -> TestResult:
        return self._test_service("NocoDB", self._build_url("nocodb"))

    def _test_phpmyadmin(self) -> TestResult:
        return self._test_service("phpMyAdmin", self._build_url("phpmyadmin"))

    def _test_superset(self) -> TestResult:
        return self._test_service("Superset", self._build_url("superset"))

    def _test_grafana(self) -> TestResult:
        return self._test_service("Grafana", self._build_url("grafana"))

    # DEVELOPER
    def _test_code_server(self) -> TestResult:
        return self._test_service("Code Server", self._build_url("code"))

    def _test_backstage(self) -> TestResult:
        return self._test_service("Backstage", self._build_url("backstage"))

    def _test_lighthouse(self) -> TestResult:
        return self._test_service("Lighthouse", self._build_url("lighthouse"))

    def _test_lhci(self) -> TestResult:
        return self._test_service("LHCI Server", self._build_url("lhci"))

    def _test_hoppscotch(self) -> TestResult:
        return self._test_service("Hoppscotch", self._build_url("hoppscotch"))

    # DEVOPS
    def _test_nexus(self) -> TestResult:
        return self._test_service("Nexus", self._build_url("nexus"))

    def _test_harbor(self) -> TestResult:
        return self._test_service("Harbor", self._build_url("harbor"))

    def _test_headlamp(self) -> TestResult:
        return self._test_service("Headlamp", self._build_url("headlamp"))

    def _test_argocd(self) -> TestResult:
        return self._test_service("ArgoCD", self._build_url("argocd"))

    def _test_sonarqube(self) -> TestResult:
        return self._test_service("SonarQube", self._build_url("sonarqube"))

    def _test_gitlab(self) -> TestResult:
        return self._test_service("GitLab", self._build_url("gitlab"))

    def _test_jfrog(self) -> TestResult:
        return self._test_service("JFrog", self._build_url("jfrog"))

    # EDITORS
    def _test_drawio(self) -> TestResult:
        return self._test_service("Draw.io", self._build_url("drawio"))

    def _test_excalidraw(self) -> TestResult:
        return self._test_service("Excalidraw", self._build_url("excalidraw"))

    def _test_hedgedoc(self) -> TestResult:
        return self._test_service("HedgeDoc", self._build_url("hedgedoc"))

    def _test_kroki(self) -> TestResult:
        return self._test_service("Kroki", self._build_url("kroki"), use_get=True)

    def _test_swagger(self) -> TestResult:
        return self._test_service("Swagger", self._build_url("swagger"))

    def _test_jsoncrack(self) -> TestResult:
        return self._test_service("JSON Crack", self._build_url("jsoncrack"))

    def _test_it_tools(self) -> TestResult:
        return self._test_service("IT-Tools", self._build_url("tools"))

    # DOCUMENTS
    def _test_paperless(self) -> TestResult:
        return self._test_service("Paperless", self._build_url("paperless"))

    def _test_tandoor(self) -> TestResult:
        return self._test_service("Tandoor", self._build_url("tandoor"))

    # DATA (missing)
    def _test_prefect(self) -> TestResult:
        return self._test_service("Prefect", self._build_url("prefect"))

    def _test_jupyter(self) -> TestResult:
        return self._test_service("Jupyter", self._build_url("jupyter"))

    # === Public methods ===

    def test_service(self, service_name: str) -> TestResult:
        """Test a specific service by name."""
        url = self._build_url(service_name)
        return self._test_service(service_name, url)

    def test_url(self, name: str, url: str) -> TestResult:
        """Test a specific URL."""
        return self._test_service(name, url)

    def test_core(self) -> TestReport:
        """Test all core services."""
        report = TestReport()
        logger.info("Testing CORE services...")

        tests = [
            self._test_traefik,
            self._test_dashy,
            self._test_portainer,
            self._test_heimdall,
            self._test_homepage,
        ]

        for test in tests:
            result = test()
            report.results.append(result)
            result.log()

        return report

    def test_infra(self) -> TestReport:
        """Test all infrastructure services."""
        report = TestReport()
        logger.info("Testing INFRA services...")

        tests = [
            self._test_pgadmin,
            self._test_redis,
        ]

        for test in tests:
            result = test()
            report.results.append(result)
            result.log()

        return report

    def test_data(self) -> TestReport:
        """Test all data services."""
        report = TestReport()
        logger.info("Testing DATA services...")

        tests = [
            self._test_airflow,
            self._test_dagster,
            self._test_trino,
        ]

        for test in tests:
            result = test()
            report.results.append(result)
            result.log()

        return report

    def test_all(self, verbose: bool = True, active_services: Optional[List[str]] = None) -> TestReport:
        """Run all tests and return a complete report.

        Args:
            verbose: Print detailed output
            active_services: List of active service names from .state.json.
                            If None, all services are tested.
        """
        report = TestReport()

        # Map service names (from .state.json) to test functions
        service_tests = {
            # CORE - always tested (core infra)
            "traefik": self._test_traefik,
            "dashy": self._test_dashy,
            "portainer": self._test_portainer,
            "heimdall": self._test_heimdall,
            "homepage": self._test_homepage,
            # INFRA
            "pgadmin": self._test_pgadmin,
            "postgres": self._test_pgadmin,  # pgadmin tests postgres access
            "mariadb": self._test_phpmyadmin,  # phpmyadmin tests mariadb access
            "redis": self._test_redis,
            # DATA
            "airflow": self._test_airflow,
            "dagster": self._test_dagster,
            "trino": self._test_trino,
            "n8n": self._test_n8n,
            "nocodb": self._test_nocodb,
            "superset": self._test_superset,
            # CORPORATIVO
            "odoo": self._test_odoo,
            "dolibarr": self._test_dolibarr,
            "openproject": self._test_openproject,
            "mautic": self._test_mautic,
            # DEVELOPER
            "code-server": self._test_code_server,
            "backstage": self._test_backstage,
            "lighthouse": self._test_lighthouse,
            "lhci": self._test_lhci,
            "hoppscotch": self._test_hoppscotch,
            # MONITORING
            "grafana": self._test_grafana,
            # DEVOPS
            "nexus": self._test_nexus,
            "harbor": self._test_harbor,
            "headlamp": self._test_headlamp,
            "argocd": self._test_argocd,
            "sonarqube": self._test_sonarqube,
            "gitlab": self._test_gitlab,
            "jfrog": self._test_jfrog,
            # EDITORS
            "drawio": self._test_drawio,
            "excalidraw": self._test_excalidraw,
            "hedgedoc": self._test_hedgedoc,
            "kroki": self._test_kroki,
            "swagger": self._test_swagger,
            "swagger-editor": self._test_swagger,
            "jsoncrack": self._test_jsoncrack,
            "it-tools": self._test_it_tools,
            # DOCUMENTS
            "paperless": self._test_paperless,
            "tandoor": self._test_tandoor,
            # DATA (extra)
            "prefect": self._test_prefect,
            "jupyter": self._test_jupyter,
        }

        # Core services are always tested
        core_services = ["traefik", "dashy", "portainer", "heimdall", "homepage"]

        # Determine which tests to run
        if active_services is None:
            # Test all
            tests_to_run = [
                ("CORE", [service_tests[s] for s in core_services]),
                ("INFRA", [self._test_pgadmin, self._test_redis]),
                ("DATA", [self._test_airflow, self._test_dagster, self._test_trino, self._test_n8n]),
            ]
        else:
            # Filter based on active services
            active_set = set(active_services)

            # Always run core tests
            core_tests = [service_tests[s] for s in core_services]

            # Filter infra tests
            infra_tests = []
            if "postgres" in active_set or "pgadmin" in active_set:
                infra_tests.append(self._test_pgadmin)
            if "mariadb" in active_set:
                infra_tests.append(self._test_phpmyadmin)
            if "redis" in active_set:
                infra_tests.append(self._test_redis)

            # Filter data tests
            data_tests = []
            if "airflow" in active_set:
                data_tests.append(self._test_airflow)
            if "dagster" in active_set:
                data_tests.append(self._test_dagster)
            if "trino" in active_set:
                data_tests.append(self._test_trino)
            if "n8n" in active_set:
                data_tests.append(self._test_n8n)
            if "nocodb" in active_set:
                data_tests.append(self._test_nocodb)
            if "superset" in active_set:
                data_tests.append(self._test_superset)
            if "prefect" in active_set:
                data_tests.append(self._test_prefect)

            # Filter corporativo tests
            corp_tests = []
            if "odoo" in active_set:
                corp_tests.append(self._test_odoo)
            if "dolibarr" in active_set:
                corp_tests.append(self._test_dolibarr)
            if "openproject" in active_set:
                corp_tests.append(self._test_openproject)
            if "mautic" in active_set:
                corp_tests.append(self._test_mautic)

            # Filter developer tests
            dev_tests = []
            if "code-server" in active_set:
                dev_tests.append(self._test_code_server)
            if "backstage" in active_set:
                dev_tests.append(self._test_backstage)
            if "lighthouse" in active_set:
                dev_tests.append(self._test_lhci)  # lighthouse and lhci both point to LHCI server
            if "hoppscotch" in active_set:
                dev_tests.append(self._test_hoppscotch)
            if "jupyter" in active_set:
                dev_tests.append(self._test_jupyter)

            # Filter monitoring tests
            mon_tests = []
            if "grafana" in active_set:
                mon_tests.append(self._test_grafana)

            # Filter devops tests
            devops_tests = []
            if "nexus" in active_set:
                devops_tests.append(self._test_nexus)
            if "harbor" in active_set:
                devops_tests.append(self._test_harbor)
            if "headlamp" in active_set:
                devops_tests.append(self._test_headlamp)
            if "argocd" in active_set:
                devops_tests.append(self._test_argocd)
            if "sonarqube" in active_set:
                devops_tests.append(self._test_sonarqube)
            if "gitlab" in active_set:
                devops_tests.append(self._test_gitlab)
            if "jfrog" in active_set:
                devops_tests.append(self._test_jfrog)

            # Filter editor tests
            editor_tests = []
            if "drawio" in active_set:
                editor_tests.append(self._test_drawio)
            if "excalidraw" in active_set:
                editor_tests.append(self._test_excalidraw)
            if "hedgedoc" in active_set:
                editor_tests.append(self._test_hedgedoc)
            if "kroki" in active_set:
                editor_tests.append(self._test_kroki)
            if "swagger" in active_set or "swagger-editor" in active_set:
                editor_tests.append(self._test_swagger)
            if "jsoncrack" in active_set:
                editor_tests.append(self._test_jsoncrack)
            if "it-tools" in active_set:
                editor_tests.append(self._test_it_tools)

            # Filter document tests
            doc_tests = []
            if "paperless" in active_set:
                doc_tests.append(self._test_paperless)
            if "tandoor" in active_set:
                doc_tests.append(self._test_tandoor)

            tests_to_run = [
                ("CORE", core_tests),
            ]
            if infra_tests:
                tests_to_run.append(("INFRA", infra_tests))
            if data_tests:
                tests_to_run.append(("DATA", data_tests))
            if corp_tests:
                tests_to_run.append(("CORPORATIVO", corp_tests))
            if dev_tests:
                tests_to_run.append(("DEVELOPER", dev_tests))
            if mon_tests:
                tests_to_run.append(("MONITORING", mon_tests))
            if devops_tests:
                tests_to_run.append(("DEVOPS", devops_tests))
            if editor_tests:
                tests_to_run.append(("EDITORS", editor_tests))
            if doc_tests:
                tests_to_run.append(("DOCUMENTS", doc_tests))

        if verbose:
            logger.info("=" * 50)
            logger.info("E2E Infrastructure Tests")
            logger.info("=" * 50)

        for category, tests in tests_to_run:
            if verbose:
                logger.info(f"--- {category} ---")

            for test in tests:
                result = test()
                report.results.append(result)
                if verbose:
                    result.log()

        if verbose:
            logger.info("=" * 50)
            report.log_summary()

        return report

    def test_from_fragments(self, fragments_dir: Path) -> TestReport:
        """Discover and test all services from dashy.fragment.json files."""
        report = TestReport()

        fragment_files = list(fragments_dir.rglob("dashy.fragment.json"))

        logger.info(f"Found {len(fragment_files)} service fragments")
        logger.info("=" * 50)

        for fragment_file in sorted(fragment_files):
            try:
                with open(fragment_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                name = data.get("name", fragment_file.parent.name)
                url = data.get("url", "")

                if url and url.startswith("http"):
                    result = self._test_service(name, url)
                    report.results.append(result)
                    result.log()

            except Exception as e:
                logger.warning(f"{fragment_file.parent.name}: Error reading fragment - {e}")

        logger.info("=" * 50)
        report.log_summary()

        return report


def run_tests():
    """CLI entry point for running tests."""
    tester = E2ETest()
    report = tester.test_all()
    exit(0 if report.failed == 0 else 1)


if __name__ == "__main__":
    run_tests()
