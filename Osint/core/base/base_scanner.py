from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional
from datetime import datetime

import httpx

from utils.config_manager import ConfigManager
from utils.logger import Logger


class BaseScanner(ABC):
    """
    BaseScanner adalah fondasi utama seluruh engine scanning
    dalam OSINT Fusion.

    Responsibilities:
    - HTTP request handling
    - Retry mechanism
    - Header management
    - Error handling
    - Logging integration
    - Response standardization
    - Runtime configuration loading
    """

    def __init__(self, base_dir: str = "Osint"):

        # =========================
        # CORE ATTRIBUTES
        # =========================
        self.base_dir = base_dir

        # =========================
        # CONFIGURATION
        # =========================
        self.config_manager = ConfigManager(
            base_dir=base_dir
        )

        self.config = self.config_manager.load_config()

        # =========================
        # LOGGER
        # =========================
        self.logger = Logger(
            base_dir=base_dir
        )

        # =========================
        # LOAD RUNTIME CONFIG
        # =========================
        runtime_config = self.config.get(
            "runtime",
            {}
        )

        network_config = self.config.get(
            "network",
            {}
        )

        # =========================
        # NETWORK SETTINGS
        # =========================
        self.timeout = runtime_config.get(
            "timeout",
            10
        )

        self.retries = runtime_config.get(
            "retries",
            2
        )

        self.verify_ssl = runtime_config.get(
            "verify_ssl",
            True
        )

        # =========================
        # USER AGENT
        # =========================
        self.user_agent = network_config.get(
            "user_agent",
            "OSINT-Fusion/1.0"
        )

        # =========================
        # DEFAULT HEADERS
        # =========================
        self.default_headers = {
            "User-Agent": self.user_agent,
            "Accept": (
                "text/html,"
                "application/xhtml+xml,"
                "application/xml;q=0.9,"
                "*/*;q=0.8"
            ),
            "Accept-Language": "en-US,en;q=0.9,id;q=0.8",
            "Connection": "close",
        }

    # =========================================================
    # HEADER MANAGEMENT
    # =========================================================

    def build_headers(
        self,
        extra_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Menggabungkan default headers dengan custom headers.
        """

        headers = self.default_headers.copy()

        if extra_headers:
            headers.update(extra_headers)

        return headers

    # =========================================================
    # HTTP CLIENT
    # =========================================================

    def create_http_client(
        self,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True
    ) -> httpx.Client:
        """
        Membuat reusable HTTP client.
        """

        return httpx.Client(
            timeout=self.timeout,
            verify=self.verify_ssl,
            headers=self.build_headers(headers),
            follow_redirects=follow_redirects,
        )

    # =========================================================
    # MAIN REQUEST ENGINE
    # =========================================================

    def request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
    ) -> Dict[str, Any]:
        """
        HTTP request engine utama.

        Features:
        - retry handling
        - timeout handling
        - standardized response
        - integrated logging
        """

        method = method.upper()

        final_headers = self.build_headers(
            headers
        )

        last_error: Optional[str] = None

        self.logger.info(
            f"Preparing {method} request -> {url}"
        )

        for attempt in range(
            1,
            self.retries + 2
        ):

            try:

                self.logger.info(
                    f"Attempt {attempt} -> {url}"
                )

                with self.create_http_client(
                    headers=final_headers,
                    follow_redirects=follow_redirects
                ) as client:

                    response = client.request(
                        method=method,
                        url=url,
                        params=params,
                        data=data,
                        json=json_data,
                    )

                self.logger.success(
                    f"{method} {response.status_code} -> {url}"
                )

                return self.build_response(
                    success=True,
                    url=str(response.url),
                    method=method,
                    status_code=response.status_code,
                    response_text=response.text,
                    response_headers=dict(response.headers),
                    error=None,
                )

            # ==========================================
            # TIMEOUT
            # ==========================================
            except httpx.TimeoutException:

                last_error = (
                    f"Timeout after {self.timeout} seconds"
                )

                self.logger.warning(
                    f"{last_error} -> {url}"
                )

            # ==========================================
            # CONNECTION ERROR
            # ==========================================
            except httpx.ConnectError:

                last_error = (
                    "Failed to connect to target server"
                )

                self.logger.warning(
                    f"{last_error} -> {url}"
                )

            # ==========================================
            # GENERIC HTTP ERROR
            # ==========================================
            except httpx.HTTPError as exc:

                last_error = str(exc)

                self.logger.warning(
                    f"HTTP error -> {url} | {last_error}"
                )

            # ==========================================
            # UNKNOWN ERROR
            # ==========================================
            except Exception as exc:

                last_error = str(exc)

                self.logger.error(
                    f"Unexpected error -> {url} | {last_error}"
                )

                break

        # ==============================================
        # FINAL FAILED RESPONSE
        # ==============================================
        return self.build_response(
            success=False,
            url=url,
            method=method,
            status_code=None,
            response_text=None,
            response_headers=None,
            error=last_error,
        )

    # =========================================================
    # RESPONSE BUILDER
    # =========================================================

    def build_response(
        self,
        success: bool,
        url: str,
        method: str,
        status_code: Optional[int],
        response_text: Optional[str],
        response_headers: Optional[Dict[str, Any]],
        error: Optional[str],
    ) -> Dict[str, Any]:
        """
        Standardized response builder.
        """

        return {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "method": method,
            "status_code": status_code,
            "response_text": response_text,
            "response_headers": response_headers,
            "error": error,
        }

    # =========================================================
    # SHORTCUT METHODS
    # =========================================================

    def get(
        self,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Shortcut GET request.
        """

        return self.request(
            url=url,
            method="GET",
            **kwargs
        )

    def post(
        self,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Shortcut POST request.
        """

        return self.request(
            url=url,
            method="POST",
            **kwargs
        )

    def head(
        self,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Shortcut HEAD request.
        """

        return self.request(
            url=url,
            method="HEAD",
            **kwargs
        )

    # =========================================================
    # URL CHECKER
    # =========================================================

    def check_url_exists(
        self,
        url: str
    ) -> Dict[str, Any]:
        """
        Mengecek apakah target URL valid/exist.
        """

        self.logger.info(
            f"Checking target URL -> {url}"
        )

        result = self.head(
            url
        )

        if result["success"]:

            status_code = result["status_code"]

            if status_code in (
                200,
                301,
                302,
                303,
                307,
                308
            ):

                self.logger.success(
                    f"Target FOUND -> {url}"
                )

            elif status_code == 404:

                self.logger.info(
                    f"Target NOT FOUND -> {url}"
                )

            else:

                self.logger.warning(
                    f"Unknown target status ({status_code}) -> {url}"
                )

        else:

            self.logger.error(
                f"Failed checking target -> {url}"
            )

        return result

    # =========================================================
    # RESULT BUILDER
    # =========================================================

    def create_result(
        self,
        module_name: str,
        target: str,
        status: str,
        url: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Standardized OSINT result builder.
        """

        return {
            "module": module_name,
            "target": target,
            "status": status,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "details": details or {},
        }