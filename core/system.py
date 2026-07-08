import platform
import sys


def get_project_status():
    return {
        "project": "Evil Twin Lab",
        "status": "initialized",
        "version": "0.1.0",
    }


def get_python_info():
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.system(),
        "platform_release": platform.release(),
        "machine": platform.machine(),
    }