from core.linux_commands import run_command
from core.wifi import get_wireless_interfaces


def get_wireless_interface_names():
    result = get_wireless_interfaces()

    if not result["success"]:
        return {
            "success": False,
            "error": result["error"],
            "interfaces": [],
        }

    interface_names = []

    for interface in result["interfaces"]:
        interface_names.append(interface["name"])

    return {
        "success": True,
        "error": None,
        "interfaces": interface_names,
    }


def scan_wifi_networks(interface_name):
    return run_command(["sudo", "iw", "dev", interface_name, "scan"])


def set_interface_down(interface_name):
    return run_command(["sudo", "ip", "link", "set", interface_name, "down"])


def set_interface_up(interface_name):
    return run_command(["sudo", "ip", "link", "set", interface_name, "up"])


def set_monitor_mode(interface_name):
    steps = []

    steps.append(set_interface_down(interface_name))
    steps.append(run_command(["sudo", "iw", "dev", interface_name, "set", "type", "monitor"]))
    steps.append(set_interface_up(interface_name))

    return steps


def set_managed_mode(interface_name):
    steps = []

    steps.append(set_interface_down(interface_name))
    steps.append(run_command(["sudo", "iw", "dev", interface_name, "set", "type", "managed"]))
    steps.append(set_interface_up(interface_name))

    return steps