# 🛡️ GhostShield (Zero Edition)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=for-the-badge&logo=raspberrypi)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**GhostShield** is a lightweight, custom-built DNS Sinkhole and Network Traffic Monitor designed specifically for the **Raspberry Pi Zero**.

Unlike other solutions, GhostShield is built entirely in **Python** and utilizes an in-memory database to minimize SD card wear while providing a futuristic, cyberpunk-styled live dashboard.



## 🔥 Features

* **🚀 High Performance:** DNS resolution and blocking occur in RAM for maximum speed.
* **👁️ "The Eye" Dashboard:** A real-time web interface that visualizes network traffic and blocked threats.
* **🛑 Gravity Well:** Automatically loads over 150,000 known ad and tracking domains (via StevenBlack list).
* **🐍 Pure Python:** Built with `dnslib` and `Flask`. Modern, hackable, and lightweight.
* **📱 Responsive:** The interface looks great on desktop, mobile, and tablets.

## 🛠️ Installation & Setup

Follow these steps to get GhostShield running on your Raspberry Pi.

### 1. Download the Repository
Open your terminal on the Raspberry Pi and clone the project:

```bash
git clone https://github.com/YOUR-USERNAME/GhostShield.git
cd GhostShield


```
### 2. Run the Installer
```bash
chmod +x install.sh
./install.sh
```

### 3.Start the Shield
```bash
sudo python3 src/main.py
```

🖥️ Accessing the Dashboard
Once the script is running, you can access the interface to see live statistics.

1. Find your Pi's IP address (type hostname -I in the terminal).
2. Open a browser on any device in your network.
3. Navigate to: http://<YOUR-PI-IP> (e.g., http://192.168.1.50)


📡 Final Step: Router Configuration
For GhostShield to block ads on your phone, TV, and computer, you must configure your router to use the Raspberry Pi as its DNS server.

Log in to your router's admin panel (e.g., 192.168.0.1 or fritz.box).
Look for DNS Server settings (usually under Network or Internet > Account Information).
Set the Local / Primary DNS Server to the IP address of your Raspberry Pi.
Save settings and reconnect your devices to the WiFi.
Now, all traffic in your home flows through GhostShield! 🛡️

⚙️ Tech Stack
Language: Python 3
Web Framework: Flask
DNS Handling: dnslib
Frontend: HTML5, TailwindCSS, Chart.js

⚠️ Disclaimer
This project is a Proof of Concept (PoC) for educational purposes. While it effectively blocks ads, the developers are not responsible for any network issues that may arise.
