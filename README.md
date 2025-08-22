# tuya-light-fan-controller

Control Tuya-based light + fan combo devices locally using Python and tinytuya.

<img width="335" height="286" alt="image" src="https://github.com/user-attachments/assets/aaf5cbef-9e4c-4e2f-9ba1-46e31ff720dc" />


## Overview

This script relies on `tinytuya` to interface with your device via LAN. It supports:

- Turning the device on/off
- Selecting fan speeds
- Adjusting light brightness/color

## Prerequisites

- Python 3.6 or higher
- `tinytuya` library installed (`pip install tinytuya`)

You must know your device’s:
- Device ID
- IP address
- Local Key
- Protocol version (e.g., 3.3)

Obtain these via:
- `tinytuya` scan or wizard tool :contentReference[oaicite:3]{index=3}
- Monitoring DPS changes when controlling from the app :contentReference[oaicite:4]{index=4}

## Setup

1. Clone or copy this repository.
2. Install dependencies:
   ```bash
   pip install tinytuya
