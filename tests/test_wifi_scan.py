import unittest

from core.wifi_scan import parse_iw_scan_output


IW_SCAN_SAMPLE = """\
BSS 38:16:5a:28:72:b9(on wlan1)
\tfreq: 2412.0
\tsignal: -65.00 dBm
\tcapability: ESS Privacy (0x0011)
\tDS Parameter set: channel 1
\tRSN:
\t\tAuthentication suites: PSK
\tSSID: DIGIFIBRA-PLUS-hU5S
BSS 3a:16:5a:48:72:b9(on wlan1)
\tfreq: 5200.0
\tsignal: -45.00 dBm
\tcapability: ESS Privacy (0x0011)
\tRSN:
\t\tAuthentication suites: SAE
\tSSID:
BSS 20:11:22:33:44:55(on wlan1)
\tfreq: 5180.0
\tsignal: -72.00 dBm
\tcapability: ESS (0x0001)
\tDS Parameter set: channel 36
\tSSID: Guest network
BSS 38:16:5a:28:72:b9(on wlan1)
\tfreq: 2412.0
\tsignal: -85.00 dBm
\tSSID: Duplicate should be ignored
"""


class ParseIwScanOutputTests(unittest.TestCase):
    def setUp(self):
        self.networks = parse_iw_scan_output(IW_SCAN_SAMPLE)

    def test_parses_network_fields_and_sorts_by_signal(self):
        self.assertEqual([network["bssid"] for network in self.networks], [
            "3a:16:5a:48:72:b9",
            "38:16:5a:28:72:b9",
            "20:11:22:33:44:55",
        ])

        wpa2_network = self.networks[1]
        self.assertEqual(wpa2_network["ssid"], "DIGIFIBRA-PLUS-hU5S")
        self.assertEqual(wpa2_network["interface"], "wlan1")
        self.assertEqual(wpa2_network["frequency"], 2412)
        self.assertEqual(wpa2_network["channel"], 1)
        self.assertEqual(wpa2_network["band"], "2.4 GHz")
        self.assertEqual(wpa2_network["security"], "WPA2-PSK")

    def test_detects_wpa3_hidden_ssid_and_inferred_channel(self):
        hidden_network = self.networks[0]
        self.assertEqual(hidden_network["ssid"], "<Hidden>")
        self.assertTrue(hidden_network["is_hidden"])
        self.assertEqual(hidden_network["security"], "WPA3-SAE")
        self.assertEqual(hidden_network["channel"], 40)
        self.assertEqual(hidden_network["band"], "5 GHz")

    def test_detects_open_network_and_removes_duplicate_bssid(self):
        open_network = self.networks[2]
        self.assertEqual(open_network["security"], "Open")
        self.assertFalse(open_network["is_hidden"])
        self.assertEqual(len(self.networks), 3)


if __name__ == "__main__":
    unittest.main()
