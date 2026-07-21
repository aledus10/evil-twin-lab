"""Generate validated hostapd configuration files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config.settings import AppSettings
from core.logger import get_logger


logger = get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
GENERATED_CONFIG_DIRECTORY = PROJECT_ROOT / "config" / "generated"
HOSTAPD_CONFIG_PATH = GENERATED_CONFIG_DIRECTORY / "hostapd.conf"

DEFAULT_LAB_SSID = "EvilTwin-Lab"


class HostapdConfigError(ValueError):
    """Raised when a valid hostapd configuration cannot be generated."""


def _validate_ssid(value: Any) -> str:
    """Validate an SSID using its UTF-8 encoded size."""

    if not isinstance(value, str) or not value:
        raise HostapdConfigError(
            "SSID must be a non-empty string"
        )

    if "\n" in value or "\r" in value:
        raise HostapdConfigError(
            "SSID cannot contain line breaks"
        )

    if len(value.encode("utf-8")) > 32:
        raise HostapdConfigError(
            "SSID cannot exceed 32 UTF-8 bytes"
        )

    return value


def _validate_interface(value: Any) -> str:
    """Validate the configured laboratory interface name."""

    if not isinstance(value, str) or not value.strip():
        raise HostapdConfigError(
            "Lab interface must be a non-empty string"
        )

    interface_name = value.strip()

    if len(interface_name) > 15:
        raise HostapdConfigError(
            "Lab interface name cannot exceed 15 characters"
        )

    if "\n" in interface_name or "\r" in interface_name:
        raise HostapdConfigError(
            "Lab interface contains invalid characters"
        )

    return interface_name


def _validate_channel(value: Any) -> int:
    """Validate the channel taken from the selected target."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise HostapdConfigError(
            "Selected target channel must be an integer"
        )

    if value <= 0:
        raise HostapdConfigError(
            "Selected target channel must be greater than zero"
        )

    return value


def _band_to_hw_mode(band: Any) -> str:
    """Map the selected WiFi band to a hostapd hardware mode."""

    if band == "2.4 GHz":
        return "g"

    if band == "5 GHz":
        return "a"

    if band == "6 GHz":
        raise HostapdConfigError(
            "6 GHz configuration is not supported yet"
        )

    raise HostapdConfigError(
        f"Unsupported or unknown WiFi band: {band}"
    )


def build_hostapd_config(
    settings: AppSettings,
    *,
    use_target_ssid: bool = False,
) -> str:
    """Build an open laboratory AP configuration.

    When use_target_ssid is false, the AP uses EvilTwin-Lab.
    When true, it uses the SSID from the selected target.

    This function only creates configuration text. It does not run hostapd.
    """

    target = settings.target_profile

    if target is None:
        raise HostapdConfigError(
            "Select a target network before generating hostapd configuration"
        )

    interface_name = _validate_interface(
        settings.lab_interface
    )
    channel = _validate_channel(
        target.get("channel")
    )
    hw_mode = _band_to_hw_mode(
        target.get("band")
    )

    if use_target_ssid:
        ssid = _validate_ssid(
            target.get("ssid")
        )
    else:
        ssid = DEFAULT_LAB_SSID

    lines = [
        f"interface={interface_name}",
        "driver=nl80211",
        f"ssid={ssid}",
        f"country_code={settings.country_code}",
        f"hw_mode={hw_mode}",
        f"channel={channel}",
        "ieee80211d=1",
        "wmm_enabled=1",
        "auth_algs=1",
        "ignore_broadcast_ssid=0",
    ]

    config_text = "\n".join(lines) + "\n"

    logger.info(
        "Generated hostapd configuration: interface=%s ssid=%s channel=%d",
        interface_name,
        ssid,
        channel,
    )

    return config_text


def save_hostapd_config(
    settings: AppSettings,
    *,
    use_target_ssid: bool = False,
    output_path: Path = HOSTAPD_CONFIG_PATH,
) -> Path:
    """Generate and atomically save hostapd configuration."""

    config_text = build_hostapd_config(
        settings,
        use_target_ssid=use_target_ssid,
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_path = output_path.with_suffix(
        f"{output_path.suffix}.tmp"
    )

    try:
        temporary_path.write_text(
            config_text,
            encoding="utf-8",
        )
        temporary_path.replace(output_path)

    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass

        raise HostapdConfigError(
            f"Could not save hostapd configuration: {exc}"
        ) from exc

    logger.success(
        "hostapd configuration saved to %s",
        output_path,
    )

    return output_path