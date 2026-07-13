from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from core.linux_commands import get_ip_link_output, get_iw_dev_output, get_lsusb_output
from core.network import get_basic_network_info, get_network_interfaces
from core.system import get_project_status, get_python_info
from core.wifi import get_wireless_interfaces
from core.wifi_inventory import get_wireless_inventory
from core.wifi_lab import (
    scan_wifi_networks,
    set_managed_mode,
    set_monitor_mode,
)


console = Console()


def print_banner(title, subtitle):
    content = Text(justify="center")
    content.append(f"{title.upper()}\n", style="bold white")
    content.append(subtitle, style="bright_cyan")
    console.print()
    console.print(
        Panel(
            content,
            border_style="bright_cyan",
            box=box.DOUBLE,
            padding=(1, 6),
            width=64,
        )
    )


def print_success(text):
    console.print(text, style="green")


def print_warning(text):
    console.print(text, style="yellow")


def print_error(text):
    console.print(text, style="red")


def print_info(text):
    console.print(text, style="cyan")


def print_header():
    print_banner("Evil Twin Lab CLI", "Raspberry Pi Wireless Toolkit")


def print_menu():
    options = (
        "Show project status",
        "Show Python/system info",
        "Show basic network info",
        "Show network interfaces",
        "Show Linux WiFi commands",
        "Show wireless interfaces",
        "Show wireless inventory",
        "WiFi lab controls",
        "Exit",
    )
    print_options_table("Main Menu", options)


def print_options_table(title, options):
    table = Table(
        title=title,
        title_style="bold cyan",
        box=box.ROUNDED,
        border_style="cyan",
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Option", justify="right", style="bold cyan", no_wrap=True)
    table.add_column("Action", style="white")

    for number, option in enumerate(options, start=1):
        style = "yellow" if option == "Exit" else "white"
        table.add_row(str(number), option, style=style)

    console.print()
    console.print(table)
    console.print()


def print_step_results(results):
    for result in results:
        print()
        print_info(f"Command: {' '.join(result['command'])}")

        if result["return_code"] == 0:
            print_success(f"Return code: {result['return_code']}")
        else:
            print_error(f"Return code: {result['return_code']}")

        if result["stdout"]:
            print(result["stdout"])

        if result["stderr"]:
            print_error("Errors:")
            print_error(result["stderr"])


def print_command_result(title, result):
    print()
    print_info(title)
    print_info("-" * len(title))
    print_info(f"Command: {' '.join(result['command'])}")

    if result["return_code"] == 0:
        print_success(f"Return code: {result['return_code']}")
    else:
        print_error(f"Return code: {result['return_code']}")

    if result["stdout"]:
        print()
        print(result["stdout"])

    if result["stderr"]:
        print()
        print_error("Errors:")
        print_error(result["stderr"])


def show_project_status():
    status = get_project_status()

    print()
    print_info("Project status")
    print_info("--------------")
    print(f"Project: {status['project']}")
    print(f"Status:  {status['status']}")
    print(f"Version: {status['version']}")


def show_python_info():
    info = get_python_info()

    print()
    print_info("Python/system info")
    print_info("------------------")
    print(f"Python version:   {info['python_version']}")
    print(f"Platform:         {info['platform']}")
    print(f"Platform release: {info['platform_release']}")
    print(f"Machine:          {info['machine']}")


def show_basic_network_info():
    info = get_basic_network_info()

    print()
    print_info("Basic network info")
    print_info("------------------")
    print(f"Hostname: {info['hostname']}")


def show_network_interfaces():
    interfaces = get_network_interfaces()

    print()
    print_info("Network interfaces")
    print_info("------------------")

    for interface in interfaces:
        status = "up" if interface["is_up"] else "down"
        interface_type = (
            "wireless candidate"
            if interface["is_wireless_candidate"]
            else "generic network interface"
        )

        print_info(f"\nInterface: {interface['name']}")
        print(f"  IPv4:      {interface['ipv4'] or 'N/A'}")
        print(f"  IPv6:      {interface['ipv6'] or 'N/A'}")
        print(f"  MAC:       {interface['mac'] or 'N/A'}")

        if status == "up":
            print_success(f"  Status:    {status}")
        else:
            print_warning(f"  Status:    {status}")

        print(f"  Type:      {interface_type}")
        print(f"  Addresses: {interface['addresses_count']}")


def show_linux_wifi_commands():
    print_command_result("ip link", get_ip_link_output())
    print_command_result("iw dev", get_iw_dev_output())
    print_command_result("lsusb", get_lsusb_output())


def show_wireless_interfaces():
    result = get_wireless_interfaces()

    print()
    print_info("Wireless interfaces")
    print_info("-------------------")

    if not result["success"]:
        print_error("Could not read wireless interfaces.")
        print_error(f"Error: {result['error']}")
        return

    if not result["interfaces"]:
        print_warning("No wireless interfaces detected.")
        return

    for interface in result["interfaces"]:
        print_info(f"\nInterface: {interface['name']}")
        print(f"  PHY:      {interface['phy'] or 'N/A'}")
        print(f"  Type:     {interface['type'] or 'N/A'}")
        print(f"  SSID:     {interface['ssid'] or 'N/A'}")
        print(f"  Channel:  {interface['channel'] or 'N/A'}")
        print(f"  TxPower:  {interface['txpower'] or 'N/A'}")


def show_wireless_inventory():
    result = get_wireless_inventory()

    print()
    print_info("Wireless inventory")
    print_info("------------------")

    if not result["success"]:
        print_error("Could not build wireless inventory.")
        print_error(f"Error: {result['error']}")
        return

    if not result["interfaces"]:
        print_warning("No wireless interfaces detected.")
        return

    for interface in result["interfaces"]:
        print_info(f"\nInterface: {interface['name']}")
        print(f"  PHY:       {interface['phy'] or 'N/A'}")
        print(f"  Type:      {interface['type'] or 'N/A'}")
        print(f"  SSID:      {interface['ssid'] or 'N/A'}")
        print(f"  Driver:    {interface['driver'] or 'N/A'}")
        print(f"  Bus:       {interface['bus'] or 'N/A'}")
        print(f"  Vendor:    {interface['vendor'] or 'N/A'}")
        print(f"  Model:     {interface['model'] or 'N/A'}")
        print(f"  USB:       {'yes' if interface['is_usb'] else 'no'}")

        role = interface["role_hint"]

        if "recommended" in role:
            print_success(f"  Role:      {role}")
        elif "avoid" in role:
            print_warning(f"  Role:      {role}")
        else:
            print(f"  Role:      {role}")


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
    print_info("Available wireless interfaces")
    print_info("-----------------------------")

    for index, interface in enumerate(interfaces, start=1):
        name = interface["name"]
        driver = interface["driver"] or "unknown-driver"
        bus = interface["bus"] or "unknown-bus"
        model = interface["model"] or "unknown-model"
        role = interface["role_hint"]

        print_info(f"{index}) {name}")
        print(f"   Driver: {driver}")
        print(f"   Bus:    {bus}")
        print(f"   Model:  {model}")

        if "recommended" in role:
            print_success(f"   Role:   {role}")
        elif "avoid" in role:
            print_warning(f"   Role:   {role}")
        else:
            print(f"   Role:   {role}")

    selected = input("\nSelect interface: ").strip()

    if not selected.isdigit():
        print_warning("Invalid selection.")
        return None

    selected_index = int(selected)

    if selected_index < 1 or selected_index > len(interfaces):
        print_warning("Invalid selection.")
        return None

    return interfaces[selected_index - 1]["name"]


def show_wifi_lab_menu():
    while True:
        print_banner("WiFi Lab Controls", "Scan | Monitor | Restore")
        print_options_table(
            "Lab Actions",
            (
                "Show wireless interfaces",
                "Scan nearby WiFi networks",
                "Enable monitor mode",
                "Restore managed mode",
                "Back",
            ),
        )

        option = input("Select an option: ").strip()

        if option == "1":
            show_wireless_interfaces()

        elif option == "2":
            interface_name = choose_wireless_interface()

            if interface_name:
                print()
                print_info(f"Scanning nearby WiFi networks using {interface_name}...")
                result = scan_wifi_networks(interface_name)
                print_command_result("WiFi scan", result)

        elif option == "3":
            interface_name = choose_wireless_interface()

            if interface_name == "wlan0":
                print()
                print_warning("Refusing to change wlan0 because it may be your SSH connection.")
                print_warning("Use the external adapter, usually wlan1.")
                continue

            if interface_name:
                print()
                print_info(f"Enabling monitor mode on {interface_name}...")
                results = set_monitor_mode(interface_name)
                print_step_results(results)

        elif option == "4":
            interface_name = choose_wireless_interface()

            if interface_name:
                print()
                print_info(f"Restoring managed mode on {interface_name}...")
                results = set_managed_mode(interface_name)
                print_step_results(results)

        elif option == "5":
            break

        else:
            print()
            print_warning("Invalid option. Please choose 1, 2, 3, 4 or 5.")

        input("\nPress Enter to continue...")


def run_menu():
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
            show_wireless_interfaces()
        elif option == "7":
            show_wireless_inventory()
        elif option == "8":
            show_wifi_lab_menu()
        elif option == "9":
            print()
            print_success("Exiting Evil Twin Lab. Bye!")
            break
        else:
            print()
            print_warning("Invalid option. Please choose 1, 2, 3, 4, 5, 6, 7, 8 or 9.")

        input("\nPress Enter to continue...")
