from core.linux_commands import get_iw_dev_output


def parse_iw_dev_output(output):
    wireless_interfaces = []
    current_phy = None
    current_interface = None

    for raw_line in output.splitlines():
        line = raw_line.strip()

        if line.startswith("phy#"):
            if current_interface:
                wireless_interfaces.append(current_interface)
                current_interface = None
            current_phy = line

        elif line.startswith("Interface "):
            if current_interface:
                wireless_interfaces.append(current_interface)

            interface_name = line.split(" ", 1)[1]

            current_interface = {
                "phy": current_phy,
                "name": interface_name,
                "type": None,
                "ssid": None,
                "channel": None,
                "txpower": None,
            }

        elif line.startswith("Unnamed/non-netdev interface"):
            if current_interface:
                wireless_interfaces.append(current_interface)
                current_interface = None

        elif current_interface:
            if line.startswith("type "):
                current_interface["type"] = line.replace("type ", "", 1)

            elif line.startswith("ssid "):
                current_interface["ssid"] = line.replace("ssid ", "", 1)

            elif line.startswith("channel "):
                current_interface["channel"] = line.replace("channel ", "", 1)

            elif line.startswith("txpower "):
                current_interface["txpower"] = line.replace("txpower ", "", 1)

    if current_interface:
        wireless_interfaces.append(current_interface)

    return wireless_interfaces


def get_wireless_interfaces():
    result = get_iw_dev_output()

    if result["return_code"] != 0:
        return {
            "success": False,
            "error": result["stderr"],
            "interfaces": [],
        }

    return {
        "success": True,
        "error": None,
        "interfaces": parse_iw_dev_output(result["stdout"]),
    }
