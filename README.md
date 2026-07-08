# Evil Twin Lab

Educational Raspberry Pi project to learn Python, Linux, networking and wireless security through a modular laboratory.

## Overview

Evil Twin Lab is a personal cybersecurity learning project focused on building a modular wireless security laboratory using a Raspberry Pi and an anthenna.

The goal of this project is not only to create a functional lab, but to understand how each component works internally: Python modules, Linux networking, process automation, logging, web dashboards, APIs and wireless security concepts.

This project is intended only for personal networks, controlled environments and authorized security testing.

## Goals

- Learn Python by building a real project.
- Understand Linux networking and wireless interfaces.
- Build a modular and maintainable codebase.
- Create both a CLI interface and a local web dashboard.
- Implement structured logging.
- Expose internal state through an API.
- Document each development phase.
- Practice Git and GitHub with clean commits.

## Project Structure

evil-twin-lab/
│
├── cli/                # Terminal interface
├── config/             # Configuration files and settings
├── core/               # Core logic of the application
├── docs/               # Technical documentation and learning notes
├── logs/               # Runtime logs
├── captures/           # Generated captures and lab output files
├── tests/              # Automated tests
├── web/                # Local web dashboard
│
├── .gitignore
├── LICENSE
├── main.py             # Application entry point
├── README.md
└── requirements.txt

## Hardware

- Raspberry Pi 5
- Realtek RTL8812AU USB WiFi adapter
- Ethernet connection for stable remote access

## Current WiFi Adapter

Realtek RTL8812AU 802.11a/b/g/n/ac 2T2R USB WLAN Adapter
USB ID: 0bda:8812

This adapter will be used during the lab to study wireless interfaces, monitor mode, access point creation and Linux networking behavior.