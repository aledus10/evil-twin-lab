import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from config.settings import (
    AppSettings,
    SettingsFileError,
    SettingsValidationError,
    load_settings,
    save_runtime_settings,
    update_settings,
    validate_settings,
)


VALID_SETTINGS = {
    "lab_interface": "wlan1",
    "protected_interface": "wlan0",
    "country_code": "ES",
    "dashboard_host": "127.0.0.1",
    "dashboard_port": 5000,
    "log_level": "INFO",
    "dhcp_subnet": "10.20.0.0/24",
    "dhcp_start": "10.20.0.10",
    "dhcp_end": "10.20.0.100",
    "gateway_ip": "10.20.0.1",
    "target_profile": None,
}


class SettingsTests(unittest.TestCase):
    def test_validate_settings_returns_dataclass(self):
        settings = validate_settings(VALID_SETTINGS)

        self.assertIsInstance(settings, AppSettings)
        self.assertEqual(settings.lab_interface, "wlan1")
        self.assertEqual(settings.dashboard_port, 5000)

    def test_rejects_same_lab_and_protected_interface(self):
        data = VALID_SETTINGS.copy()
        data["protected_interface"] = "wlan1"

        with self.assertRaises(SettingsValidationError):
            validate_settings(data)

    def test_rejects_invalid_dashboard_port(self):
        data = VALID_SETTINGS.copy()
        data["dashboard_port"] = 70000

        with self.assertRaises(SettingsValidationError):
            validate_settings(data)

    def test_rejects_dhcp_address_outside_subnet(self):
        data = VALID_SETTINGS.copy()
        data["dhcp_end"] = "192.168.1.100"

        with self.assertRaises(SettingsValidationError):
            validate_settings(data)

    def test_runtime_values_override_defaults(self):
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            default_path = directory / "default.json"
            runtime_path = directory / "runtime.json"

            default_path.write_text(
                json.dumps(VALID_SETTINGS),
                encoding="utf-8",
            )
            runtime_path.write_text(
                json.dumps({"dashboard_port": 5050}),
                encoding="utf-8",
            )

            settings = load_settings(
                default_path=default_path,
                runtime_path=runtime_path,
            )

            self.assertEqual(settings.dashboard_port, 5050)
            self.assertEqual(settings.lab_interface, "wlan1")

    def test_invalid_json_raises_file_error(self):
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            default_path = directory / "default.json"
            runtime_path = directory / "runtime.json"

            default_path.write_text("{not-json", encoding="utf-8")

            with self.assertRaises(SettingsFileError):
                load_settings(
                    default_path=default_path,
                    runtime_path=runtime_path,
                )

    def test_save_and_reload_runtime_settings(self):
        with TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            default_path = directory / "default.json"
            runtime_path = directory / "runtime.json"

            default_path.write_text(
                json.dumps(VALID_SETTINGS),
                encoding="utf-8",
            )

            settings = validate_settings(VALID_SETTINGS)
            updated = update_settings(
                settings,
                dashboard_port=5050,
                log_level="DEBUG",
            )

            save_runtime_settings(
                updated,
                runtime_path=runtime_path,
            )

            loaded = load_settings(
                default_path=default_path,
                runtime_path=runtime_path,
            )

            self.assertEqual(loaded.dashboard_port, 5050)
            self.assertEqual(loaded.log_level, "DEBUG")


if __name__ == "__main__":
    unittest.main()