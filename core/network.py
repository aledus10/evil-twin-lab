import socket


def get_hostname():
    return socket.gethostname()


def get_basic_network_info():
    return {
        "hostname": get_hostname(),
    }