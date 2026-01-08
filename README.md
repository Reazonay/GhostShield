# 🛡️ GhostShield (Zero Edition)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi-red?style=for-the-badge&logo=raspberrypi)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**GhostShield** ist ein moderner, leichtgewichtiger DNS-Adblocker und Netzwerk-Monitor, der speziell für die begrenzte Hardware des **Raspberry Pi Zero** entwickelt wurde.

Anders als herkömmliche Lösungen setzt GhostShield komplett auf **Python** (statt PHP) und nutzt eine In-Memory-Datenbank für maximale Performance.

## 🔥 Features

* **🚀 High Performance:** DNS-Auflösung und Blocking passieren im Arbeitsspeicher (RAM). Schont die SD-Karte.
* **👁️ "The Eye" Dashboard:** Ein Live-Interface im Cyberpunk-Stil, das Netzwerkverkehr in Echtzeit visualisiert.
* **🛑 Gravity Well:** Lädt automatisch über 150.000 bekannte Werbe- und Tracking-Domains (StevenBlack List).
* **🐍 100% Python:** Backend basiert auf `dnslib` und `Flask`. Modern und anpassbar.
* **📱 Responsive:** Das Dashboard funktioniert perfekt auf Desktop und Mobile.

## 📸 Screenshots

*(Hier kannst du später einen Screenshot von deinem Dashboard einfügen)*

## 🛠️ Installation

GhostShield ist darauf ausgelegt, auf einem frischen Raspberry Pi OS (Lite) zu laufen.

### 1. Repository klonen
```bash
git clone [https://github.com/DEIN-USERNAME/GhostShield.git](https://github.com/DEIN-USERNAME/GhostShield.git)
cd GhostShield
