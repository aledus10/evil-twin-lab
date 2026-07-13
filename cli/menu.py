from core.network import get_basic_network_info, get_network_interfaces
from core.system import get_project_status, get_python_info
from core.linux_commands import get_ip_link_output, get_iw_dev_output, get_lsusb_output
from core.wifi import get_wireless_interfaces

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
    print("7) Exit")
    print()


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
            print()
            print("Exiting Evil Twin Lab. Bye!")
        elif option == "7":
            show_wireless_interfaces()
        elif option == "8":
            print()
            print("Exiting Evil Twin Lab. Bye!")
            break
        else:
            print()
            print("Invalid option. Please choose 1, 2, 3, 4, 5, 6 or 7.")

        input("\nPress Enter to continue...")