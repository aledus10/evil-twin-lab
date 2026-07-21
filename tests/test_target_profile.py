import unittest

from core.target_profile import (
    TargetProfileError,
    build_target_profile_from_scan,
)


VALID_NETWORK = {
    "ssid": "EvilTwin-Lab-Test",
    "bssid": "AA:BB:CC:DD:EE:FF",
    "channel": 6,
    "frequency": 2437,
    "band": "2.4 GHz",
    "signal": -42.0,
    "security": "WPA2-PSK",
    "interface": "wlan1",
    "is_hidden": False,
}


class TargetProfileTests(unittest.TestCase):
    def test_builds_target_from_scan_network(self):
        target = build_target_profile_from_scan(
            VALID_NETWORK
        )

        self.assertEqual(
            target["ssid"],
            "EvilTwin-Lab-Test",
        )
        self.assertEqual(
            target["bssid"],
            "aa:bb:cc:dd:ee:ff",
        )
        self.assertEqual(target["channel"], 6)
        self.assertEqual(target["source"], "wifi_scan")

    def test_rejects_hidden_network(self):
        network = VALID_NETWORK.copy()
        network["ssid"] = "<Hidden>"
        network["is_hidden"] = True

        with self.assertRaises(TargetProfileError):
            build_target_profile_from_scan(network)

    def test_rejects_missing_bssid(self):
        network = VALID_NETWORK.copy()
        network["bssid"] = None

        with self.assertRaises(TargetProfileError):
            build_target_profile_from_scan(network)

    def test_rejects_missing_channel(self):
        network = VALID_NETWORK.copy()
        network["channel"] = None

        with self.assertRaises(TargetProfileError):
            build_target_profile_from_scan(network)


if __name__ == "__main__":
    unittest.main()