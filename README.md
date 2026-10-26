# 🚀 InfinityFree Autonomous Account & Hosting Agent

[![GitHub Auto-Sync](https://img.shields.io/badge/GitHub-Auto--Sync-brightgreen.svg)](https://github.com/thakoralpesh3/infinityfree)
[![Managed Domains](https://img.shields.io/badge/InfinityFree-6%20Domains-00ffcc.svg)](DOMAINS.md)
[![Hosted APKs](https://img.shields.io/badge/Hosted%20APKs-17%20Releases-blue.svg)](DOMAINS.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous AI Agent designed to manage **InfinityFree** web hosting accounts, organize and automate custom domains & subdomains, package and deploy Android APK download portals with embedded QR codes, and maintain real-time bidirectional synchronization with GitHub and Google Antigravity conversations.

---

## 🌐 Live Hosted Domains & APK Work Catalog

All active domains, projects, and hosted APK releases are tracked in real-time in **[DOMAINS.md](DOMAINS.md)**.

| Domain / Subdomain | Associated Project | Target Device | Hosted APKs | Live Matrix |
| :--- | :--- | :--- | :--- | :--- |
| **[anime4all.epizy.com](http://anime4all.epizy.com)** | [Web2APK Anime Streaming App](https://github.com/thakoralpesh3/web-to-apk-autonomous-agent) | Universal, TV, Mobile | 3 Releases | [View Details](DOMAINS.md#-anime4allepizycom---web2apk-anime-streaming-app) |
| **[cinemamoviebox.epizy.com](http://cinemamoviebox.epizy.com)** | [Cinema MovieBox Media Center](https://github.com/thakoralpesh3/web-to-apk-autonomous-agent) | Universal, TV, Mobile | 4 Releases | [View Details](DOMAINS.md#-cinemamovieboxepizycom---cinema-moviebox-media-center) |
| **[tvmouse.epizy.com](http://tvmouse.epizy.com)** | [TV Mouse Navigation Suite](https://github.com/thakoralpesh3/apk-tv-converter-agent) | Android TV / Fire TV | 1 Release | [View Details](DOMAINS.md#-tvmouseepizycom---tv-mouse-navigation--leanback-suite) |
| **[openworld.epizy.com](http://openworld.epizy.com)** | [Openworld4All Suite](https://github.com/thakoralpesh3/web-to-apk-autonomous-agent) | Universal, TV, Mobile | 5 Releases | [View Details](DOMAINS.md#-openworldepizycom---openworld4all-suite) |
| **[cyberarcade.epizy.com](http://cyberarcade.epizy.com)** | [Cyber Arcade Gaming Suite](https://github.com/thakoralpesh3/web-to-apk-autonomous-agent) | Universal | 1 Release | [View Details](DOMAINS.md#-cyberarcadeepizycom---cyber-arcade-gaming-suite) |
| **[retrostream.epizy.com](http://retrostream.epizy.com)** | [RetroStream Media](https://github.com/thakoralpesh3/web-to-apk-autonomous-agent) | Universal, TV, Mobile | 3 Releases | [View Details](DOMAINS.md#-retrostreamepizycom---retrostream-media) |

---

## 🌟 Core Features

- ⚡ **Automated InfinityFree FTP Management**: Full connection lifecycle to `ftpupload.net:21`, recursive directory creation, upload progress tracking, and MIME-type configuration via automated `.htaccess`.
- 📱 **Zero-Config APK Landing Pages**: Auto-generates responsive, dark-mode download portals with inline base64 QR codes for instant smartphone & Android TV camera scanning.
- 🔍 **Intelligent Local APK Discovery**: Automatically indexes APK builds from `/home/alpesh/Web2APK_Output` and `/home/alpesh/APK_TV_Converter_Output` and correlates them with domains.
- 🩺 **Domain Health & DNS Watchdog**: Regularly pings domains for DNS resolution, HTTP/HTTPS response codes, and verified APK download URL reachability.
- 🔄 **Conversation & Code GitHub Auto-Sync**: Automatically formats live Antigravity transcripts (`transcript.jsonl` -> `conversation/CONVERSATION.md`), captures artifacts, and pushes commits to GitHub.

---

## 🛠️ Architecture Overview

```
infinityfree/
├── agent/                         # Core InfinityFree Agent Engine
│   ├── __init__.py
│   ├── config.py                  # Environment & credentials loader
│   ├── catalog.py                 # domains.json manager
│   ├── apk_scanner.py             # Local APK indexer & analyzer
│   ├── ftp_client.py              # ftpupload.net FTPS/FTP engine
│   ├── portal_builder.py          # HTML5 + QR code download portal generator
│   ├── health_checker.py          # HTTP, DNS & link validator
│   ├── markdown_generator.py      # DOMAINS.md generator
│   └── cli.py                     # CLI entrypoint
├── config/
│   └── domains.json               # Domain-to-project & APK mapping
├── sync/                          # Auto-Sync to GitHub
│   ├── sync_daemon.py             # Continuous watcher & pusher
│   └── infinityfree-sync.service  # Systemd user service
├── conversation/                  # Synced Antigravity conversation transcripts
├── artifacts/                     # Synced planning & walkthrough artifacts
├── infinityfree_agent.sh          # Quick CLI runner
├── sync_to_github.sh              # One-shot sync helper
├── DOMAINS.md                     # GitHub showcase matrix
└── requirements.txt
```

---

## 🚀 Quick Start & CLI Usage

### 1. Configure Credentials
Copy `.env.example` to `.env` and fill in your InfinityFree hosting credentials (available in the InfinityFree Client Area):
```bash
cp .env.example .env
nano .env
```
Key variables:
- `IF_FTP_HOST=ftpupload.net`
- `IF_FTP_USER=epiz_xxxxxxxx`
- `IF_FTP_PASS=your_vpanel_password`

### 2. View Agent Status
```bash
./infinityfree_agent.sh status
```

### 3. List Registered Domains & Work
```bash
./infinityfree_agent.sh list-domains
```

### 4. Scan & Auto-Link Local APKs
```bash
./infinityfree_agent.sh scan-apks --link
```

### 5. Add a New Domain or Subdomain
```bash
./infinityfree_agent.sh add-domain myapp.epizy.com \
  --project "My New App" \
  --repo "thakoralpesh3/web-to-apk-autonomous-agent" \
  --description "Download portal for My New App"
```

### 6. Build Local Landing Portal
```bash
./infinityfree_agent.sh build-portal anime4all.epizy.com
```

### 7. Run Live Health Check
```bash
./infinityfree_agent.sh health-check --sync
```

### 8. Deploy to InfinityFree Host
Uploads `.htaccess`, generated landing page, and APK files directly to InfinityFree:
```bash
./infinityfree_agent.sh deploy anime4all.epizy.com --upload-apks
```

---

## 🔄 Automatic GitHub Sync

To perform an immediate one-shot synchronization of your codebase, artifacts, and conversation:
```bash
./sync_to_github.sh
```

To run the sync daemon in the background or enable systemd service:
```bash
python3 sync/sync_daemon.py --interval 30
```
Or install as a systemd user service:
```bash
mkdir -p ~/.config/systemd/user
cp sync/infinityfree-sync.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now infinityfree-sync.service
```
