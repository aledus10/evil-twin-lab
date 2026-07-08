from core.network import get_basic_network_info, get_network_interfaces
from core.system import get_project_status, get_python_info


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
    print("5) Exit")
    print()


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
        print(f"- {interface['name']} ({interface['addresses_count']} addresses)")

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
            print()
            print("Exiting Evil Twin Lab. Bye!")
            break
        else:
            print()
            print("Invalid option. Please choose 1, 2, 3, 4 or 5.")

        input("\nPress Enter to continue...")