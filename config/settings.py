"""Persistent application settings for Evil Twin Lab."""

from __future__ import annotations

import ipaddress
import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from core.logger import get_logger


logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIRECTORY = PROJECT_ROOT / "config"
DEFAULT_CONFIG_PATH = CONFIG_DIRECTORY / "default.json"
RUNTIME_CONFIG_PATH = CONFIG_DIRECTORY / "runtime.json"

VALID_LOG_LEVELS = {
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


class SettingsError(Exception):
    """Base exception for configuration errors."""


class SettingsFileError(SettingsError):
    """Raised when a configuration file cannot be read or decoded."""


class SettingsValidationError(SettingsError):
    """Raised when configuration values are invalid."""


@dataclass
class AppSettings:
    """Validated settings used by the application."""

    lab_interface: str
    protected_interface: str
    country_code: str
    dashboard_host: str
    dashboard_port: int
    log_level: str
    dhcp_subnet: str
    dhcp_start: str
    dhcp_end: str
    gateway_ip: str
    target_profile: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Return the settings as a JSON-compatible dictionary."""
        return asdict(self)


def _read_json_file(path: Path) -> dict[str, Any]:
    """Read a JSON object from disk."""

    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError as exc:
        raise SettingsFileError(
            f"Configuration file not found: {path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise SettingsFileError(
            f"Invalid JSON in {path}: line {exc.lineno}, column {exc.colno}"
        ) from exc
    except OSError as exc:
        raise SettingsFileError(
            f"Could not read configuration file {path}: {exc}"
        ) from exc

    if not isinstance(data, dict):
        raise SettingsFileError(
            f"Configuration root must be a JSON object: {path}"
        )

    return data


def _merge_settings(
    defaults: dict[str, Any],
    overrides: dict[str, Any],
) -> dict[str, Any]:
    """Return defaults updated with runtime overrides."""

    merged = deepcopy(defaults)

    for key, value in overrides.items():
        if key not in defaults:
            logger.warning(
                "Ignoring unknown runtime setting: %s",
                key,
            )
            continue

        merged[key] = value

    return merged


def _validate_interface_name(value: Any, field_name: str) -> str:
    """Validate a Linux network-interface name."""

    if not isinstance(value, str) or not value.strip():
        raise SettingsValidationError(
            f"{field_name} must be a non-empty string"
        )

    interface_name = value.strip()

    if len(interface_name) > 15:
        raise SettingsValidationError(
            f"{field_name} is longer than 15 characters"
        )

    return interface_name


def _validate_port(value: Any) -> int:
    """Validate a TCP port."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise SettingsValidationError(
            "dashboard_port must be an integer"
        )

    if not 1 <= value <= 65535:
        raise SettingsValidationError(
            "dashboard_port must be between 1 and 65535"
        )

    return value


def _validate_log_level(value: Any) -> str:
    """Validate and normalize a logging level."""

    if not isinstance(value, str):
        raise SettingsValidationError(
            "log_level must be a string"
        )

    normalized = value.strip().upper()

    if normalized not in VALID_LOG_LEVELS:
        allowed = ", ".join(sorted(VALID_LOG_LEVELS))
        raise SettingsValidationError(
            f"log_level must be one of: {allowed}"
        )

    return normalized


def _validate_host(value: Any) -> str:
    """Validate the dashboard bind host."""

    if not isinstance(value, str) or not value.strip():
        raise SettingsValidationError(
            "dashboard_host must be a non-empty string"
        )

    host = value.strip()

    if host not in {"127.0.0.1", "localhost"}:
        raise SettingsValidationError(
            "dashboard_host must be 127.0.0.1 or localhost"
        )

    return host


def _validate_network_settings(
    subnet_value: Any,
    start_value: Any,
    end_value: Any,
    gateway_value: Any,
) -> tuple[str, str, str, str]:
    """Validate that DHCP addresses belong to the configured subnet."""

    try:
        subnet = ipaddress.ip_network(str(subnet_value), strict=False)
        dhcp_start = ipaddress.ip_address(str(start_value))
        dhcp_end = ipaddress.ip_address(str(end_value))
        gateway = ipaddress.ip_address(str(gateway_value))
    except ValueError as exc:
        raise SettingsValidationError(
            f"Invalid DHCP network configuration: {exc}"
        ) from exc

    if subnet.version != 4:
        raise SettingsValidationError(
            "dhcp_subnet must be an IPv4 network"
        )

    for name, address in (
        ("dhcp_start", dhcp_start),
        ("dhcp_end", dhcp_end),
        ("gateway_ip", gateway),
    ):
        if address not in subnet:
            raise SettingsValidationError(
                f"{name} must belong to {subnet}"
            )

    if dhcp_start > dhcp_end:
        raise SettingsValidationError(
            "dhcp_start must not be greater than dhcp_end"
        )

    if gateway in {dhcp_start, dhcp_end}:
        raise SettingsValidationError(
            "gateway_ip must not equal a DHCP range endpoint"
        )

    if gateway == subnet.network_address:
        raise SettingsValidationError(
            "gateway_ip cannot be the network address"
        )

    if gateway == subnet.broadcast_address:
        raise SettingsValidationError(
            "gateway_ip cannot be the broadcast address"
        )

    return (
        str(subnet),
        str(dhcp_start),
        str(dhcp_end),
        str(gateway),
    )

def _validate_country_code(value: Any) -> str:
    """Validate and normalize an ISO-style two-letter country code."""

    if not isinstance(value, str):
        raise SettingsValidationError(
            "country_code must be a string"
        )

    country_code = value.strip().upper()

    if len(country_code) != 2 or not country_code.isalpha():
        raise SettingsValidationError(
            "country_code must contain exactly two letters"
        )

    return country_code

def validate_settings(data: dict[str, Any]) -> AppSettings:
    """Validate raw configuration and return an AppSettings object."""

    required_fields = {
        "country_code",
        "lab_interface",
        "protected_interface",
        "dashboard_host",
        "dashboard_port",
        "log_level",
        "dhcp_subnet",
        "dhcp_start",
        "dhcp_end",
        "gateway_ip",
        "target_profile",
    }

    missing_fields = required_fields - data.keys()

    if missing_fields:
        missing = ", ".join(sorted(missing_fields))
        raise SettingsValidationError(
            f"Missing required settings: {missing}"
        )

    lab_interface = _validate_interface_name(
        data["lab_interface"],
        "lab_interface",
    )
    protected_interface = _validate_interface_name(
        data["protected_interface"],
        "protected_interface",
    )

    if lab_interface == protected_interface:
        raise SettingsValidationError(
            "lab_interface and protected_interface must be different"
        )

    target_profile = data["target_profile"]

    if target_profile is not None and not isinstance(target_profile, dict):
        raise SettingsValidationError(
            "target_profile must be an object or null"
        )

    (
        dhcp_subnet,
        dhcp_start,
        dhcp_end,
        gateway_ip,
    ) = _validate_network_settings(
        data["dhcp_subnet"],
        data["dhcp_start"],
        data["dhcp_end"],
        data["gateway_ip"],
    )

    return AppSettings(
        country_code=_validate_country_code(data["country_code"]),
        lab_interface=lab_interface,
        protected_interface=protected_interface,
        dashboard_host=_validate_host(data["dashboard_host"]),
        dashboard_port=_validate_port(data["dashboard_port"]),
        log_level=_validate_log_level(data["log_level"]),
        dhcp_subnet=dhcp_subnet,
        dhcp_start=dhcp_start,
        dhcp_end=dhcp_end,
        gateway_ip=gateway_ip,
        target_profile=deepcopy(target_profile),
    )


def load_settings(
    default_path: Path = DEFAULT_CONFIG_PATH,
    runtime_path: Path = RUNTIME_CONFIG_PATH,
) -> AppSettings:
    """Load defaults, apply runtime overrides, and validate the result."""

    defaults = _read_json_file(default_path)

    if runtime_path.exists():
        runtime_values = _read_json_file(runtime_path)
        logger.debug(
            "Loading runtime configuration from %s",
            runtime_path,
        )
    else:
        runtime_values = {}
        logger.debug(
            "Runtime configuration does not exist; using defaults"
        )

    merged = _merge_settings(defaults, runtime_values)
    settings = validate_settings(merged)

    logger.info(
        "Configuration loaded: lab=%s protected=%s dashboard=%s:%d",
        settings.lab_interface,
        settings.protected_interface,
        settings.dashboard_host,
        settings.dashboard_port,
    )

    return settings


def save_runtime_settings(
    settings: AppSettings,
    runtime_path: Path = RUNTIME_CONFIG_PATH,
) -> None:
    """Persist validated runtime settings atomically."""

    validated = validate_settings(settings.to_dict())
    runtime_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = runtime_path.with_suffix(
        f"{runtime_path.suffix}.tmp"
    )

    try:
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(
                validated.to_dict(),
                file,
                indent=2,
                ensure_ascii=False,
            )
            file.write("\n")

        temporary_path.replace(runtime_path)
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise SettingsFileError(
            f"Could not save runtime settings to {runtime_path}: {exc}"
        ) from exc

    logger.success(
        "Runtime configuration saved to %s",
        runtime_path,
    )


def update_settings(
    settings: AppSettings,
    **changes: Any,
) -> AppSettings:
    """Return a validated copy with selected values changed."""

    data = settings.to_dict()

    unknown_fields = set(changes) - set(data)

    if unknown_fields:
        unknown = ", ".join(sorted(unknown_fields))
        raise SettingsValidationError(
            f"Unknown settings: {unknown}"
        )

    data.update(changes)
    return validate_settings(data)