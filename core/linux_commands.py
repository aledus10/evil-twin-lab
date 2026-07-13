import subprocess


def run_command(command):
    completed_process = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )

    return {
        "command": command,
        "return_code": completed_process.returncode,
        "stdout": completed_process.stdout.strip(),
        "stderr": completed_process.stderr.strip(),
    }


def get_ip_link_output():
    return run_command(["ip", "link"])


def get_iw_dev_output():
    return run_command(["iw", "dev"])


def get_lsusb_output():
    return run_command(["lsusb"])