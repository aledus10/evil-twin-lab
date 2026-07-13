from core.network import get_basic_network_info, get_network_interfaces
from core.system import get_project_status, get_python_info
from core.linux_commands import get_ip_link_output, get_iw_dev_output, get_lsusb_output
from core.wifi import get_wireless_interfaces
from core.wifi_lab import (
    get_wireless_interface_names,
    scan_wifi_networks,
    set_managed_mode,
    set_monitor_mode,
)
from core.wifi_inventory import get_wireless_inventory

def print_header():
    print()
    print("===================================")
    print("        Evil Twin Lab CLI")
    print("===================================")


def print_menu():
    print()
    print("1) Show project status")
    print("2) Show Python/system info")
    print("3) Show basic network info")
    print("4) Show network interfaces")
    print("5) Show Linux WiFi commands")
    print("6) Show wireless interfaces")
    print("7) Show wireless inventory")
    print("8) WiFi lab controls")
    print("9) Exit")
    print()

def print_step_results(results):
    for result in results:
        print()
        print(f"Command: {' '.join(result['command'])}")
        print(f"Return code: {result['return_code']}")

        if result["stdout"]:
            print(result["stdout"])

        if result["stderr"]:
            print("Errors:")
            print(result["stderr"])


def show_wireless_inventory():
    result = get_wireless_inventory()

    print()
    print("Wireless inventory")
    print("------------------")

    if not result["success"]:
        print("Could not build wireless inventory.")
        print(f"Error: {result['error']}")
        return

    if not result["interfaces"]:
        print("No wireless interfaces detected.")
        return

    for interface in result["interfaces"]:
        print(f"\nInterface: {interface['name']}")
        print(f"  PHY:       {interface['phy'] or 'N/A'}")
        print(f"  Type:      {interface['type'] or 'N/A'}")
        print(f"  SSID:      {interface['ssid'] or 'N/A'}")
        print(f"  Driver:    {interface['driver'] or 'N/A'}")
        print(f"  Bus:       {interface['bus'] or 'N/A'}")
        print(f"  Vendor:    {interface['vendor'] or 'N/A'}")
        print(f"  Model:     {interface['model'] or 'N/A'}")
        print(f"  USB:       {'yes' if interface['is_usb'] else 'no'}")
        print(f"  Role:      {interface['role_hint']}")


def choose_wireless_interface():
    result = get_wireless_inventory()

    if not result["success"]:
        print()
        print("Could not read wireless inventory.")
        print(f"Error: {result['error']}")
        return None

    interfaces = result["interfaces"]

    if not interfaces:
        print()
        print("No wireless interfaces detected.")
        return None

    print()
    print("Available wireless interfaces")
    print("-----------------------------")

    for index, interface in enumerate(interfaces, start=1):
        name = interface["name"]
        driver = interface["driver"] or "unknown-driver"
        bus = interface["bus"] or "unknown-bus"
        model = interface["model"] or "unknown-model"
        role = interface["role_hint"]

        print(f"{index}) {name}")
        print(f"   Driver: {driver}")
        print(f"   Bus:    {bus}")
        print(f"   Model:  {model}")
        print(f"   Role:   {role}")

    selected = input("\nSelect interface: ").strip()

    if not selected.isdigit():
        print("Invalid selection.")
        return None

    selected_index = int(selected)

    if selected_index < 1 or selected_index > len(interfaces):
        print("Invalid selection.")
        return None

    return interfaces[selected_index - 1]["name"]


def show_wifi_lab_menu():
    while True:
        print()
        print("===================================")
        print("        WiFi Lab Controls")
        print("===================================")
        print()
        print("1) Show wireless interfaces")
        print("2) Scan nearby WiFi networks")
        print("3) Enable monitor mode")
        print("4) Restore managed mode")
        print("5) Back")
        print()

        option = input("Select an option: ").strip()

        if option == "1":
            show_wireless_interfaces()

        elif option == "2":
            interface_name = choose_wireless_interface()

            if interface_name:
                print()
                print(f"Scanning nearby WiFi networks using {interface_name}...")
                result = scan_wifi_networks(interface_name)
                print_command_result("WiFi scan", result)

        elif option == "3":
            interface_name = choose_wireless_interface()

            if interface_name == "wlan0":
                print()
                print("Refusing to change wlan0 because it may be your SSH connection.")
                print("Use the external adapter, usually wlan1.")
                continue

            if interface_name:
                print()
                print(f"Enabling monitor mode on {interface_name}...")
                results = set_monitor_mode(interface_name)
                print_step_results(results)

        elif option == "4":
            interface_name = choose_wireless_interface()

            if interface_name:
                print()
                print(f"Restoring managed mode on {interface_name}...")
                results = set_managed_mode(interface_name)
                print_step_results(results)

        elif option == "5":
            break

        else:
            print()
            print("Invalid option. Please choose 1, 2, 3, 4 or 5.")

        input("\nPress Enter to continue...")


def show_wireless_interfaces():
    result = get_wireless_interfaces()

    print()
    print("Wireless interfaces")
    print("-------------------")

    if not result["success"]:
        print("Could not read wireless interfaces.")
        print(f"Error: {result['error']}")
        return

    if not result["interfaces"]:
        print("No wireless interfaces detected.")
        return

    for interface in result["interfaces"]:
        print(f"\nInterface: {interface['name']}")
        print(f"  PHY:      {interface['phy'] or 'N/A'}")
        print(f"  Type:     {interface['type'] or 'N/A'}")
        print(f"  SSID:     {interface['ssid'] or 'N/A'}")
        print(f"  Channel:  {interface['channel'] or 'N/A'}")
        print(f"  TxPower:  {interface['txpower'] or 'N/A'}")


def show_project_status():
    status = get_project_status()

    print()
    print("Project status")
    print("--------------")
    print(f"Project: {status['project']}")
    print(f"Status:  {status['status']}")
    print(f"Version: {status['version']}")

def show_network_interfaces():
    interfaces = get_network_interfaces()

    print()
    print("Network interfaces")
    print("------------------")

    for interface in interfaces:
        status = "up" if interface["is_up"] else "down"
        interface_type = (
            "wireless candidate"
            if interface["is_wireless_candidate"]
            else "generic network interface"
        )

        print(f"\nInterface: {interface['name']}")
        print(f"  IPv4:      {interface['ipv4'] or 'N/A'}")
        print(f"  IPv6:      {interface['ipv6'] or 'N/A'}")
        print(f"  MAC:       {interface['mac'] or 'N/A'}")
        print(f"  Status:    {status}")
        print(f"  Type:      {interface_type}")
        print(f"  Addresses: {interface['addresses_count']}")
        
def show_python_info():
    info = get_python_info()

    print()
    print("Python/system info")
    print("------------------")
    print(f"Python version:   {info['python_version']}")
    print(f"Platform:         {info['platform']}")
    print(f"Platform release: {info['platform_release']}")
    print(f"Machine:          {info['machine']}")

def show_basic_network_info():
    info = get_basic_network_info()

    print()
    print("Basic network info")
    print("------------------")
    print(f"Hostname: {info['hostname']}")


def print_command_result(title, result):
    print()
    print(title)
    print("-" * len(title))
    print(f"Command: {' '.join(result['command'])}")
    print(f"Return code: {result['return_code']}")

    if result["stdout"]:
        print()
        print(result["stdout"])

    if result["stderr"]:
        print()
        print("Errors:")
        print(result["stderr"])


def show_linux_wifi_commands():
    print_command_result("ip link", get_ip_link_output())
    print_command_result("iw dev", get_iw_dev_output())
    print_command_result("lsusb", get_lsusb_output())


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
            print("Exiting Evil Twin Lab. Bye!")
            break
        else:
            print()
            print("Invalid option. Please choose 1, 2, 3, 4, 5, 6, 7, 8 or 9.")

        input("\nPress Enter to continue...")