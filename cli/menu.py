from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config.settings import AppSettings
from core.linux_commands import get_ip_link_output, get_iw_dev_output, get_lsusb_output
from core.network import get_basic_network_info, get_network_interfaces
from core.system import get_project_status, get_python_info
from core.wifi_inventory import get_wireless_inventory
from core.wifi_scan import scan_wifi_networks
from core.wifi_lab import (
    set_managed_mode,
    set_monitor_mode,
)


console = Console()

# Centralized Rich theme: red carries the tool identity and danger states;
# green is reserved for confirmed/active states.
PRIMARY = "bold red"
PRIMARY_BORDER = "red"
SUCCESS = "bold bright_green"
WARNING = "bold yellow"
ERROR = "bold bright_red"
TEXT = "white"
MUTED = "grey70"

SECTION = PRIMARY
TABLE_HEADER = PRIMARY
OPTION_NUMBER = PRIMARY
EXIT_ACTION = ERROR
LAB_ACTION = SUCCESS
INTERFACE_NAME = "bold white"
UNKNOWN = WARNING


def print_banner(title, subtitle):
    content = Text(justify="center")
    content.append(f"{title.upper()}\n", style=PRIMARY)
    content.append(subtitle, style=MUTED)
    console.print()
    console.print(
        Panel(
            content,
            border_style=PRIMARY_BORDER,
            box=box.DOUBLE,
            padding=(1, 6),
            width=64,
        )
    )


def print_success(text):
    console.print(text, style=SUCCESS)


def print_warning(text):
    console.print(text, style=WARNING)


def print_error(text):
    console.print(text, style=ERROR)


def print_info(text):
    console.print(text, style=MUTED)


def print_section(text):
    console.print(text, style=SECTION)


def print_label_value(label, value, value_style=TEXT):
    line = Text()
    line.append(label, style=MUTED)
    line.append(str(value), style=value_style)
    console.print(line)


def print_unknown_label_value(label, value):
    value_style = UNKNOWN if value in (None, "", "N/A") else TEXT
    print_label_value(label, value or "N/A", value_style)


def print_header():
    print_banner("Evil Twin Lab CLI", "Raspberry Pi Wireless Toolkit")


def print_menu():
    options = (
        "Show project status",
        "Show Python/system info",
        "Show basic network info",
        "Show network interfaces",
        "Show Linux WiFi commands",
        "Show wireless inventory",
        "Show application settings",
        "WiFi lab controls",
        "Exit",
    )
    print_options_table("Main Menu", options)


def print_options_table(title, options):
    table = Table(
        title=title,
        title_style=TABLE_HEADER,
        box=box.ROUNDED,
        border_style=PRIMARY_BORDER,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Option", justify="right", no_wrap=True)
    table.add_column("Action")

    for number, option in enumerate(options, start=1):
        action_style = TEXT
        if option in ("Exit", "Back"):
            action_style = EXIT_ACTION
        elif option == "WiFi lab controls":
            action_style = LAB_ACTION

        table.add_row(
            Text(str(number), style=OPTION_NUMBER),
            Text(option, style=action_style),
        )

    console.print()
    console.print(table)
    console.print()


def print_step_results(results):
    for result in results:
        print()
        print_label_value("Command: ", " ".join(result["command"]), MUTED)

        if result["return_code"] == 0:
            print_success(f"Return code: {result['return_code']}")
        else:
            print_error(f"Return code: {result['return_code']}")

        if result["stdout"]:
            console.print(result["stdout"], style=TEXT)

        if result["stderr"]:
            print_error("Errors:")
            print_error(result["stderr"])


def print_command_result(title, result):
    print()
    print_section(title)
    print_section("-" * len(title))
    print_label_value("Command: ", " ".join(result["command"]), MUTED)

    if result["return_code"] == 0:
        print_success(f"Return code: {result['return_code']}")
    else:
        print_error(f"Return code: {result['return_code']}")

    if result["stdout"]:
        print()
        console.print(result["stdout"], style=TEXT)

    if result["stderr"]:
        print()
        print_error("Errors:")
        print_error(result["stderr"])


def get_signal_style(signal):
    if signal is None:
        return MUTED
    if signal >= -50:
        return SUCCESS
    if signal >= -70:
        return WARNING
    return ERROR


def get_security_style(security):
    if security == "Open":
        return ERROR
    if "WPA2" in security or "WPA3" in security:
        return SUCCESS
    if security == "Encrypted":
        return WARNING
    return TEXT


def format_scan_value(value, suffix=""):
    if value is None:
        return "N/A"
    return f"{value:g}{suffix}" if isinstance(value, float) else f"{value}{suffix}"


def print_wifi_scan_results(result):
    if result["return_code"] != 0:
        print_error("WiFi scan failed.")
        print_error(f"Return code: {result['return_code']}")
        if result["stderr"]:
            print_error(result["stderr"])
        return

    networks = result["networks"]
    if not networks:
        print_warning("No WiFi networks detected.")
        return

    table = Table(
        title="Nearby WiFi Networks",
        title_style=TABLE_HEADER,
        box=box.HEAVY_HEAD,
        border_style=PRIMARY_BORDER,
        header_style=TABLE_HEADER,
        pad_edge=False,
    )
    table.add_column("#", justify="right", style=OPTION_NUMBER, no_wrap=True)
    table.add_column("SSID", max_width=24, overflow="ellipsis")
    table.add_column("BSSID", style=MUTED, no_wrap=True)
    table.add_column("Ch", justify="right", no_wrap=True)
    table.add_column("Band", style=MUTED, no_wrap=True)
    table.add_column("Signal", justify="right", no_wrap=True)
    table.add_column("Security", no_wrap=True)

    for index, network in enumerate(networks, start=1):
        ssid_style = WARNING if network["is_hidden"] else TEXT
        ssid = network["ssid"] if network["ssid"] is not None else "N/A"
        signal = network["signal"]
        security = network["security"]
        table.add_row(
            str(index),
            Text(ssid, style=ssid_style),
            network["bssid"] or "N/A",
            format_scan_value(network["channel"]),
            network["band"] or "N/A",
            Text(format_scan_value(signal, " dBm"), style=get_signal_style(signal)),
            Text(security or "N/A", style=get_security_style(security)),
        )

    console.print(table)


def show_project_status():
    status = get_project_status()

    print()
    print_section("Project status")
    print_section("--------------")
    print_label_value("Project: ", status["project"])
    print_label_value("Status:  ", status["status"])
    print_label_value("Version: ", status["version"])


def show_python_info():
    info = get_python_info()

    print()
    print_section("Python/system info")
    print_section("------------------")
    print_label_value("Python version:   ", info["python_version"])
    print_label_value("Platform:         ", info["platform"])
    print_label_value("Platform release: ", info["platform_release"])
    print_label_value("Machine:          ", info["machine"])


def show_basic_network_info():
    info = get_basic_network_info()

    print()
    print_section("Basic network info")
    print_section("------------------")
    print_label_value("Hostname: ", info["hostname"])


def show_network_interfaces():
    interfaces = get_network_interfaces()

    print()
    print_section("Network interfaces")
    print_section("------------------")

    for interface in interfaces:
        status = "up" if interface["is_up"] else "down"
        interface_type = (
            "wireless candidate"
            if interface["is_wireless_candidate"]
            else "generic network interface"
        )

        print()
        print_label_value("Interface: ", interface["name"], INTERFACE_NAME)
        print_unknown_label_value("  IPv4:      ", interface["ipv4"])
        print_unknown_label_value("  IPv6:      ", interface["ipv6"])
        print_unknown_label_value("  MAC:       ", interface["mac"])

        if status == "up":
            print_success(f"  Status:    {status}")
        else:
            print_warning(f"  Status:    {status}")

        print_label_value("  Type:      ", interface_type)
        print_label_value("  Addresses: ", interface["addresses_count"])


def show_linux_wifi_commands():
    print_command_result("ip link", get_ip_link_output())
    print_command_result("iw dev", get_iw_dev_output())
    print_command_result("lsusb", get_lsusb_output())


def show_wireless_inventory():
    result = get_wireless_inventory()

    print()
    print_section("Wireless inventory")
    print_section("------------------")

    if not result["success"]:
        print_error("Could not build wireless inventory.")
        print_error(f"Error: {result['error']}")
        return

    if not result["interfaces"]:
        print_warning("No wireless interfaces detected.")
        return

    for interface in result["interfaces"]:
        print()
        print_label_value("Interface: ", interface["name"], INTERFACE_NAME)
        print_unknown_label_value("  PHY:       ", interface["phy"])
        print_unknown_label_value("  Type:      ", interface["type"])
        print_unknown_label_value("  SSID:      ", interface["ssid"])
        print_unknown_label_value("  Channel:   ", interface["channel"])
        print_unknown_label_value("  TxPower:   ", interface["txpower"])
        print_unknown_label_value("  Driver:    ", interface["driver"])
        print_unknown_label_value("  Bus:       ", interface["bus"])
        print_unknown_label_value("  Vendor:    ", interface["vendor"])
        print_unknown_label_value("  Model:     ", interface["model"])
        print_label_value("  USB:       ", "yes" if interface["is_usb"] else "no")

        role = interface["role_hint"]

        if "recommended" in role:
            print_success(f"  Role:      {role}")
        elif "avoid" in role:
            print_error(f"  Role:      {role}")
        else:
            print_label_value("  Role:      ", role)

def show_application_settings(settings: AppSettings) -> None:
    """Display the active validated application settings."""

    print()
    print_section("Application settings")
    print_section("--------------------")

    print_label_value(
        "Lab interface:         ",
        settings.lab_interface,
        SUCCESS,
    )
    print_label_value(
        "Protected interface:   ",
        settings.protected_interface,
        ERROR,
    )
    print_label_value(
        "Dashboard:             ",
        f"{settings.dashboard_host}:{settings.dashboard_port}",
    )
    print_label_value(
        "Log level:             ",
        settings.log_level,
    )
    print_label_value(
        "DHCP subnet:           ",
        settings.dhcp_subnet,
    )
    print_label_value(
        "DHCP range:            ",
        f"{settings.dhcp_start} - {settings.dhcp_end}",
    )
    print_label_value(
        "Gateway:               ",
        settings.gateway_ip,
    )

    if settings.target_profile is None:
        print_label_value(
            "Selected target:       ",
            "None",
            WARNING,
        )
    else:
        target_name = (
            settings.target_profile.get("ssid")
            or settings.target_profile.get("bssid")
            or "Configured target"
        )

        print_label_value(
            "Selected target:       ",
            target_name,
            SUCCESS,
        )

def choose_wireless_interface():
    result = get_wireless_inventory()

    if not result["success"]:
        print()
        print_error("Could not read wireless inventory.")
        print_error(f"Error: {result['error']}")
        return None

    interfaces = result["interfaces"]

    if not interfaces:
        print()
        print_warning("No wireless interfaces detected.")
        return None

    print()
    print_section("Available wireless interfaces")
    print_section("-----------------------------")

    for index, interface in enumerate(interfaces, start=1):
        name = interface["name"]
        driver = interface["driver"] or "unknown-driver"
        bus = interface["bus"] or "unknown-bus"
        model = interface["model"] or "unknown-model"
        role = interface["role_hint"]

        print_label_value(f"{index}) ", name, INTERFACE_NAME)
        print_label_value("   Driver: ", driver, UNKNOWN if driver == "unknown-driver" else MUTED)
        print_label_value("   Bus:    ", bus, UNKNOWN if bus == "unknown-bus" else MUTED)
        print_label_value("   Model:  ", model, UNKNOWN if model == "unknown-model" else MUTED)

        if "recommended" in role:
            print_success(f"   Role:   {role}")
        elif "avoid" in role:
            print_error(f"   Role:   {role}")
        else:
            print_label_value("   Role:   ", role)

    selected = input("\nSelect interface: ").strip()

    if not selected.isdigit():
        print_warning("Invalid selection.")
        return None

    selected_index = int(selected)

    if selected_index < 1 or selected_index > len(interfaces):
        print_warning("Invalid selection.")
        return None

    return interfaces[selected_index - 1]["name"]


def show_wifi_lab_menu(settings: AppSettings) -> None:
    while True:
        print_banner("WiFi Lab Controls", "Scan | Monitor | Restore")
        print_options_table(
            "Lab Actions",
            (
                "Scan nearby WiFi networks",
                "Enable monitor mode",
                "Restore managed mode",
                "Back",
            ),
        )

        option = input("Select an option: ").strip()

        if option == "1":
            interface_name = choose_wireless_interface()

            if interface_name:
                print()
                print_info(f"Scanning nearby WiFi networks using {interface_name}...")
                result = scan_wifi_networks(interface_name)
                print_wifi_scan_results(result)

        elif option == "2":
            interface_name = choose_wireless_interface()

            if interface_name == settings.protected_interface:
                print()
                print_warning(
                    f"Refusing to change {interface_name} because it is configured "
                    "as the protected network interface."
                )
                print_warning(
                    f"Use the configured lab interface: {settings.lab_interface}."
                )
                continue

            if interface_name:
                print()
                print_info(f"Enabling monitor mode on {interface_name}...")
                results = set_monitor_mode(interface_name)
                print_step_results(results)

        elif option == "3":
            interface_name = choose_wireless_interface()

            if interface_name == settings.protected_interface:
                print()
                print_warning(
                    f"Refusing to modify {interface_name} because it is configured "
                    "as the protected network interface."
                    )
                continue

            if interface_name:
                print()
                print_info(f"Restoring managed mode on {interface_name}...")
                results = set_managed_mode(interface_name)
                print_step_results(results)

            elif option == "4":
                    break

            else:
                    print()
                    print_warning("Invalid option. Please choose 1, 2, 3 or 4.")

            input("\nPress Enter to continue...")


def run_menu(settings: AppSettings) -> None:
    while True:
        print_header()
        print_menu()
        option = input("Select an option: ").strip()
        if option == "1":
            show_project_status()
        elif option == "2":
            show_python_info()
        elif option == "3":
            show_basic_network_info()
        elif option == "4":
            show_network_interfaces()
        elif option == "5":
            show_linux_wifi_commands()
        elif option == "6":
            show_wireless_inventory()
        elif option == "7":
            show_application_settings(settings)
        elif option == "8":
            show_wifi_lab_menu(settings)
        elif option == "9":
            print()
            print_success("Exiting Evil Twin Lab. Bye!")
            break
        else:
            print()
            print_warning(
                "Invalid option. Please choose 1, 2, 3, 4, 5, 6, 7, 8 or 9."
            )
        input("\nPress Enter to continue...")
