"""Parse and execute WiFi scans without coupling them to the CLI."""

import re

from core.linux_commands import run_command
from core.logger import get_logger


logger = get_logger(__name__)


BSS_PATTERN = re.compile(
    r"^BSS\s+(?P<bssid>[0-9a-f:]{17})(?:\(on\s+(?P<interface>[^)]+)\))?",
    re.IGNORECASE,
)
FREQUENCY_PATTERN = re.compile(r"^freq:\s*(?P<frequency>\d+(?:\.\d+)?)", re.IGNORECASE)
SIGNAL_PATTERN = re.compile(r"^signal:\s*(?P<signal>-?\d+(?:\.\d+)?)\s*dBm", re.IGNORECASE)
CHANNEL_PATTERN = re.compile(
    r"^DS Parameter set:\s*channel\s*(?P<channel>\d+)", re.IGNORECASE
)


def frequency_to_channel(frequency):
    """Return the standard WiFi channel inferred from a frequency in MHz.

    The 2.4 GHz, 5 GHz, and 6 GHz channel plans use different base frequencies.
    Frequencies outside those common ranges cannot be mapped reliably and return
    ``None``.
    """
    if frequency is None:
        return None

    if frequency == 2484:
        return 14
    if 2400 <= frequency < 2500:
        return round((frequency - 2407) / 5)
    if 4900 <= frequency < 5900:
        return round((frequency - 5000) / 5)
    if 5955 <= frequency <= 7125:
        return round((frequency - 5950) / 5)
    return None


def frequency_to_band(frequency):
    """Return the WiFi band label associated with a frequency in MHz."""
    if frequency is None:
        return "Unknown"
    if 2400 <= frequency < 2500:
        return "2.4 GHz"
    if 4900 <= frequency < 5900:
        return "5 GHz"
    if 5955 <= frequency <= 7125:
        return "6 GHz"
    return "Unknown"


def _get_security(block):
    text = "\n".join(block)
    has_wpa = bool(re.search(r"^\s*WPA:\s*$", text, re.MULTILINE))
    has_rsn = bool(re.search(r"^\s*RSN:\s*$", text, re.MULTILINE))
    has_privacy = "Privacy" in text
    has_sae = bool(re.search(r"Authentication suites:.*\bSAE\b", text))
    has_psk = bool(re.search(r"Authentication suites:.*\bPSK\b", text))

    if has_sae and has_psk:
        return "WPA2/WPA3 Mixed"
    if has_sae:
        return "WPA3-SAE"
    if has_wpa and has_rsn:
        return "WPA/WPA2 Mixed"
    if has_rsn and has_psk:
        return "WPA2-PSK"
    if has_wpa:
        return "WPA"
    if has_rsn:
        return "Encrypted"
    if has_privacy:
        return "Encrypted"
    return "Open"


def _build_network(block):
    match = BSS_PATTERN.match(block[0])
    if not match:
        return None

    network = {
        "ssid": None,
        "bssid": match.group("bssid").lower(),
        "interface": match.group("interface"),
        "frequency": None,
        "channel": None,
        "band": "Unknown",
        "signal": None,
        "security": _get_security(block),
        "is_hidden": False,
    }

    for line in block[1:]:
        stripped_line = line.strip()

        if stripped_line.startswith("SSID:"):
            ssid = stripped_line.removeprefix("SSID:").strip()
            network["is_hidden"] = ssid == ""
            network["ssid"] = "<Hidden>" if network["is_hidden"] else ssid
            continue

        frequency_match = FREQUENCY_PATTERN.match(stripped_line)
        if frequency_match:
            network["frequency"] = int(float(frequency_match.group("frequency")))
            network["band"] = frequency_to_band(network["frequency"])
            continue

        signal_match = SIGNAL_PATTERN.match(stripped_line)
        if signal_match:
            network["signal"] = float(signal_match.group("signal"))
            continue

        channel_match = CHANNEL_PATTERN.match(stripped_line)
        if channel_match:
            network["channel"] = int(channel_match.group("channel"))

    if network["channel"] is None:
        network["channel"] = frequency_to_channel(network["frequency"])

    return network


def parse_iw_scan_output(output):
    """Transform ``iw dev <interface> scan`` output into unique WiFi networks."""
    blocks = []
    current_block = None

    for line in output.splitlines():
        if BSS_PATTERN.match(line):
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        elif current_block:
            current_block.append(line)

    if current_block:
        blocks.append(current_block)

    networks_by_bssid = {}
    for block in blocks:
        network = _build_network(block)
        if network and network["bssid"] not in networks_by_bssid:
            networks_by_bssid[network["bssid"]] = network

    return sorted(
        networks_by_bssid.values(),
        key=lambda network: (
            network["signal"] is None,
            -network["signal"] if network["signal"] is not None else 0,
        ),
    )


def scan_wifi_networks(interface_name):
    """Run an ``iw`` scan and attach parsed networks to the command result."""
    logger.info("Starting WiFi scan on %s", interface_name)
    result = run_command(["sudo", "iw", "dev", interface_name, "scan"])
    result["networks"] = (
        parse_iw_scan_output(result["stdout"]) if result["return_code"] == 0 else []
    )

    if result["return_code"] != 0:
        logger.error(
            "WiFi scan failed on %s with return code %d: %s",
            interface_name,
            result["return_code"],
            result["stderr"],
        )
    elif result["networks"]:
        logger.success("Found %d WiFi networks on %s", len(result["networks"]), interface_name)
    else:
        logger.warning("No WiFi networks found on %s", interface_name)

    return result
