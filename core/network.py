import socket

import psutil


def get_hostname():
    return socket.gethostname()


def get_basic_network_info():
    return {
        "hostname": get_hostname(),
    }


def get_network_interfaces():
    interfaces = psutil.net_if_addrs()

    result = []

    for interface_name, addresses in interfaces.items():
        interface_data = {
            "name": interface_name,
            "ipv4": None,
            "ipv6": None,
            "mac": None,
            "addresses_count": len(addresses),
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