from pathlib import Path

from core.linux_commands import run_command
from core.wifi import get_wireless_interfaces


def get_udev_properties(interface_name):
    result = run_command(
        ["udevadm", "info", "-q", "property", "-p", f"/sys/class/net/{interface_name}"]
    )

    if result["return_code"] != 0:
        return {}

    properties = {}

    for line in result["stdout"].splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        properties[key] = value

    return properties


def get_interface_driver(interface_name):
    driver_path = Path(f"/sys/class/net/{interface_name}/device/driver")

    if not driver_path.exists():
        return None

    return driver_path.resolve().name


def get_interface_device_path(interface_name):
    device_path = Path(f"/sys/class/net/{interface_name}/device")

    if not device_path.exists():
        return None

    return str(device_path.resolve())


def is_usb_interface(interface_name, udev_properties):
    if udev_properties.get("ID_BUS") == "usb":
        return True

    device_path = get_interface_device_path(interface_name)

    if not device_path:
        return False

    return "usb" in device_path.lower()


def build_role_hint(interface_info, inventory_data):
    name = interface_info["name"]
    ssid = interface_info.get("ssid")
    is_usb = inventory_data["is_usb"]
    driver = inventory_data["driver"]

    if name == "wlan0" or ssid:
        return "likely SSH/network connection - avoid"

    if is_usb:
        return "recommended lab adapter"

    if driver == "brcmfmac":
        return "internal Raspberry Pi WiFi"

    return "wireless interface"


def get_wireless_inventory():
    result = get_wireless_interfaces()

    if not result["success"]:
        return {
            "success": False,
            "error": result["error"],
            "interfaces": [],
        }

    inventory = []

    for interface in result["interfaces"]:
        interface_name = interface["name"]
        udev_properties = get_udev_properties(interface_name)
        driver = udev_properties.get("ID_NET_DRIVER") or get_interface_driver(interface_name)
        is_usb = is_usb_interface(interface_name, udev_properties)

        inventory_data = {
            "name": interface_name,
            "phy": interface.get("phy"),
            "type": interface.get("type"),
            "ssid": interface.get("ssid"),
            "channel": interface.get("channel"),
            "txpower": interface.get("txpower"),
            "driver": driver,
            "bus": udev_properties.get("ID_BUS"),
            "vendor": (
                udev_properties.get("ID_VENDOR_FROM_DATABASE")
                or udev_properties.get("ID_VENDOR")
            ),
            "model": (
                udev_properties.get("ID_MODEL_FROM_DATABASE")
                or udev_properties.get("ID_MODEL")
            ),
            "vendor_id": udev_properties.get("ID_VENDOR_ID"),
            "model_id": udev_properties.get("ID_MODEL_ID"),
            "is_usb": is_usb,
        }

        inventory_data["role_hint"] = build_role_hint(interface, inventory_data)

        inventory.append(inventory_data)

    return {
        "success": True,
        "error": None,
        "interfaces": inventory,
    }