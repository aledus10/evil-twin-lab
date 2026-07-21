import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from config.settings import validate_settings
from core.hostapd_config import (
    HostapdConfigError,
    build_hostapd_config,
    save_hostapd_config,
)


BASE_SETTINGS = {
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
    "target_profile": {
        "ssid": "Home-Test",
        "bssid": "aa:bb:cc:dd:ee:ff",
        "channel": 40,
        "frequency": 5200,
        "band": "5 GHz",
        "signal": -40.0,
        "security": "WPA2-PSK",
        "interface": "wlan1",
        "source": "wifi_scan",
    },
}


class HostapdConfigTests(unittest.TestCase):
    def test_builds_default_lab_configuration(self):
        settings = validate_settings(BASE_SETTINGS)

        config = build_hostapd_config(settings)

        self.assertIn("interface=wlan1", config)
        self.assertIn("ssid=EvilTwin-Lab", config)
        self.assertIn("country_code=ES", config)
        self.assertIn("hw_mode=a", config)
        self.assertIn("channel=40", config)

    def test_can_use_selected_target_ssid(self):
        settings = validate_settings(BASE_SETTINGS)

        config = build_hostapd_config(
            settings,
            use_target_ssid=True,
        )

        self.assertIn("ssid=Home-Test", config)

    def test_maps_24_ghz_to_g_mode(self):
        data = BASE_SETTINGS.copy()
        data["target_profile"] = {
            **BASE_SETTINGS["target_profile"],
            "channel": 6,
            "frequency": 2437,
            "band": "2.4 GHz",
        }

        settings = validate_settings(data)
        config = build_hostapd_config(settings)

        self.assertIn("hw_mode=g", config)
        self.assertIn("channel=6", config)

    def test_rejects_missing_target(self):
        data = BASE_SETTINGS.copy()
        data["target_profile"] = None

        settings = validate_settings(data)

        with self.assertRaises(HostapdConfigError):
            build_hostapd_config(settings)

    def test_saves_configuration(self):
        settings = validate_settings(BASE_SETTINGS)

        with TemporaryDirectory() as directory:
            output_path = (
                Path(directory) / "hostapd.conf"
            )

            saved_path = save_hostapd_config(
                settings,
                output_path=output_path,
            )

            self.assertEqual(saved_path, output_path)
            self.assertTrue(output_path.exists())
            self.assertIn(
                "ssid=EvilTwin-Lab",
                output_path.read_text(
                    encoding="utf-8"
                ),
            )


if __name__ == "__main__":
    unittest.main()