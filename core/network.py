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
        result.append(
            {
                "name": interface_name,
                "addresses_count": len(addresses),
            }
        )

    return result