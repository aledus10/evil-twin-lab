import socket

import psutil


def get_hostname():
    return socket.gethostname()


def is_wireless_candidate(interface_name):
    wireless_keywords = ["wi-fi", "wifi", "wlan", "wireless"]

    normalized_name = interface_name.lower()

    return any(keyword in normalized_name for keyword in wireless_keywords)


def get_basic_network_info():
    return {
        "hostname": get_hostname(),
    }


def get_network_interfaces():
    interfaces = psutil.net_if_addrs()
    stats = psutil.net_if_stats()

    result = []

    for interface_name, addresses in interfaces.items():
        interface_stats = stats.get(interface_name)

        interface_data = {
            "name": interface_name,
            "ipv4": None,
            "ipv6": None,
            "mac": None,
            "addresses_count": len(addresses),
            "is_up": interface_stats.isup if interface_stats else False,
            "is_wireless_candidate": is_wireless_candidate(interface_name),
        }

        for address in addresses:
            family_name = address.family.name

            if family_name == "AF_INET":
                interface_data["ipv4"] = address.address

            elif family_name == "AF_INET6":
                interface_data["ipv6"] = address.address

            elif family_name in ("AF_LINK", "AF_PACKET"):
                interface_data["mac"] = address.address

        result.append(interface_data)

    return result