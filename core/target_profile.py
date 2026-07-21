"""Build validated target profiles from WiFi scan results."""

from __future__ import annotations

from typing import Any


class TargetProfileError(ValueError):
    """Raised when a WiFi network cannot become a valid target profile."""


def build_target_profile_from_scan(
    network: dict[str, Any],
) -> dict[str, Any]:
    """Create a persistent target profile from a parsed WiFi network."""

    if not isinstance(network, dict):
        raise TargetProfileError(
            "The selected network must be a dictionary"
        )

    ssid = network.get("ssid")

    if (
        network.get("is_hidden")
        or not isinstance(ssid, str)
        or not ssid.strip()
        or ssid == "<Hidden>"
    ):
        raise TargetProfileError(
            "A hidden network cannot be selected because its SSID is unknown"
        )

    bssid = network.get("bssid")

    if not isinstance(bssid, str) or not bssid.strip():
        raise TargetProfileError(
            "The selected network does not have a valid BSSID"
        )

    channel = network.get("channel")

    if (
        isinstance(channel, bool)
        or not isinstance(channel, int)
        or channel <= 0
    ):
        raise TargetProfileError(
            "The selected network does not have a valid channel"
        )

    frequency = network.get("frequency")

    if frequency is not None:
        if isinstance(frequency, bool) or not isinstance(
            frequency,
            (int, float),
        ):
            raise TargetProfileError(
                "The selected network has an invalid frequency"
            )

        frequency = int(frequency)

    signal = network.get("signal")

    if signal is not None:
        if isinstance(signal, bool) or not isinstance(
            signal,
            (int, float),
        ):
            raise TargetProfileError(
                "The selected network has an invalid signal value"
            )

        signal = float(signal)

    interface = network.get("interface")

    if interface is not None and not isinstance(interface, str):
        raise TargetProfileError(
            "The selected network has an invalid interface"
        )

    band = network.get("band")
    security = network.get("security")

    return {
        "ssid": ssid.strip(),
        "bssid": bssid.strip().lower(),
        "channel": channel,
        "frequency": frequency,
        "band": band if isinstance(band, str) else "Unknown",
        "signal": signal,
        "security": (
            security if isinstance(security, str) else "Unknown"
        ),
        "interface": interface,
        "source": "wifi_scan",
    }