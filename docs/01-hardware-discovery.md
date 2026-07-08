# Hardware Discovery

## Lab hardware

- Raspberry Pi 5
- External WiFi adapter: Realtek RTL8812AU
- USB ID: `0bda:8812`

## Network interfaces

Command used:

ip link

Detected interfaces:

wlan0 → internal Raspberry Pi WiFi
wlan1 → external Realtek RTL8812AU USB WiFi adapter

Wireless capabilities

Command used:

iw list | grep -A 30 "Supported interface modes"

Relevant supported modes:

managed
AP
monitor
Conclusion

The external WiFi adapter is correctly detected as wlan1.

Current validation status:

- USB detection: OK
- Linux network interface: OK
- Wireless interface detection: OK
- Monitor mode support: OK
- AP mode support: OK

This means the adapter should be suitable for the first stages of the wireless lab, including monitor mode testing and access point creation with hostapd.