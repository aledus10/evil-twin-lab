import subprocess

from core.logger import get_logger


logger = get_logger(__name__)


def run_command(command):
    logger.debug("Running command: %s", " ".join(command))

    try:
        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        logger.error("Command not found: %s", command[0])
        return {
            "command": command,
            "return_code": 127,
            "stdout": "",
            "stderr": f"Command not found: {command[0]}",
        }

    result = {
        "command": command,
        "return_code": completed_process.returncode,
        "stdout": completed_process.stdout.strip(),
        "stderr": completed_process.stderr.strip(),
    }

    if result["return_code"] == 0:
        logger.debug("Command completed successfully: %s", " ".join(command))
    else:
        logger.warning(
            "Command failed with return code %d: %s",
            result["return_code"],
            " ".join(command),
        )

    return result


def get_ip_link_output():
    return run_command(["ip", "link"])


def get_iw_dev_output():
    return run_command(["iw", "dev"])


def get_lsusb_output():
    return run_command(["lsusb"])
