<div align="center">

# Self-hosted Android TV Remote

**Control your Google TV / Android TV from any browser on your Wi‑Fi — no cloud, no vendor account.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[Features](#features) · [Screenshots](#screenshots) · [Quick start](#quick-start) · [API](#http-api) · [Contributing](#contributing)

</div>

---

Run a tiny **FastAPI** server on your Mac, PC, or Raspberry Pi. Your phone opens a **mobile-first web UI** to discover TVs, pair once, and send keys (power, D‑pad, volume, media). Prefer a **desktop window** or **terminal**? Those are included too.

Uses the official **Android TV Remote v2** protocol via [`androidtvremote2`](https://pypi.org/project/androidtvremote2/) — the same family of APIs the Google TV app uses on the local network.

---

## Screenshots

<p align="center">
  <img src="assets/screenshots/screenshot-connect.png" alt="Discover and connect to TVs on your network" width="320" />
  &nbsp;&nbsp;
  <img src="assets/screenshots/screenshot-remote.png" alt="Virtual remote — D-pad, volume, media keys" width="320" />
</p>

<p align="center">
  <em>Left: discover devices by name (mDNS). Right: full remote in the browser — self-hosted on your LAN.</em>
</p>

> **Note:** Screenshots are illustrative mockups of the UI style. Your real device list and layout match the live app.

---

## Why self-hosted?

| | |
|---|---|
| **Privacy** | Traffic stays on your LAN. No third-party server sees when you change channels. |
| **Reliability** | Works when the internet is down, as long as Wi‑Fi and the TV are up. |
| **Hackable** | REST API, plain Python — script it, theme it, or wrap it in your own stack. |

---

## Features

- **Discovery** — finds TVs advertising `_androidtvremote2._tcp`; shows **friendly instance names** (e.g. `bedroomtv`), not just hostnames
- **Pairing** — one-time 6-character hex code on the TV; client cert stored in `~/.config/androidtv-remote/`
- **Reconnect** — handles dropped sessions (idle timeouts) with automatic reconnect
- **Three interfaces** — **web** (default), **Tk** desktop (`--tk`), **CLI** (`--cli`)
- **LAN-ready** — listens on `0.0.0.0` so phones and tablets can connect via `http://<your-pc-ip>:8765`
- **Web UI** — **Vue 3** + **Vite** + **Tailwind CSS** (`frontend/`), built into `static/dist/` for FastAPI to serve

---

## Quick start

**Requirements:** Python **3.12+**, **Node.js 20+** (for building the web UI), same Wi‑Fi as the TV, [uv](https://github.com/astral-sh/uv) recommended.

```bash
git clone https://github.com/YOUR_USERNAME/androidtv.git
cd androidtv
cd frontend && npm install && npm run build && cd ..
uv sync
uv run python main.py
```

If `static/dist/` is missing, the server returns `503` with build instructions. After changing Vue/Tailwind code, run `npm run build` in `frontend/` again (or use `npm run dev` for local UI development — see below).

The terminal prints a URL like `http://192.168.x.x:8765`. Open it on your **phone** (same network).

| Mode | Command |
|------|---------|
| **Web + API** (default) | `uv run python main.py` |
| **Desktop (Tk)** | `uv run python main.py --tk` |
| **Terminal** | `uv run python main.py --cli` |

Optional: `ANDROIDTV_PORT=9000 uv run python main.py` to change the port.

### Web UI development

```bash
cd frontend
npm install
npm run dev   # Vite on http://127.0.0.1:5173 — proxy API to your FastAPI or run backend separately
```

For a full-stack flow, run `uv run python main.py` in one terminal and `npm run dev` in another; configure Vite `server.proxy` if you want `/api` forwarded to the Python backend (optional). For production, always `npm run build` so `static/dist/` is up to date.

---

## Pairing & data on disk

First connection may show a code on the TV. The app stores:

```
~/.config/androidtv-remote/client.pem
~/.config/androidtv-remote/client.key
```

Treat these like credentials for your remote identity.

---

## HTTP API

Handy for Home Assistant, shortcuts, or your own scripts — same process as the web UI.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI |
| `GET` | `/api/status` | `{ connected, pairing }` |
| `POST` | `/api/scan` | List `{ name, ip }` for ~5s |
| `POST` | `/api/connect` | Body `{ "ip": "..." }` → `{ state: "connected" \| "pairing" }` |
| `POST` | `/api/pair` | Body `{ "code": "xxxxxx" }` (hex) |
| `POST` | `/api/key` | Body `{ "key": "POWER" }` — see keys below |

**Example keys:** `POWER`, `HOME`, `BACK`, `MENU`, `MUTE`, `VOLUME_UP`, `VOLUME_DOWN`, `DPAD_UP`, `DPAD_DOWN`, `DPAD_LEFT`, `DPAD_RIGHT`, `DPAD_CENTER`, `MEDIA_PLAY_PAUSE`, … (full set follows Android `RemoteKeyCode` in `androidtvremote2`).

---

## Project layout

```
.
├── main.py              # Entry: web (default) | --tk | --cli
├── web.py               # FastAPI + routes; serves static/dist/index.html
├── tv_core.py           # Session, scan, pairing, keys
├── frontend/            # Vue 3 + Vite + Tailwind (npm run build → ../static/dist)
├── static/dist/         # Vite build output (generated)
├── assets/screenshots/  # README images
├── pyproject.toml
├── LICENSE              # MIT
└── CONTRIBUTING.md
```

---

## Security

- **No authentication by default** — anyone on your LAN who reaches the port can use the API. Do **not** port-forward this to the public internet without TLS, auth, or VPN.
- Control traffic to the TV uses the **device’s TLS remote protocol**; your browser only talks to **your** FastAPI instance.

---

## Contributing

We welcome issues and pull requests. Please read **[CONTRIBUTING.md](CONTRIBUTING.md)** before submitting a PR.

**Ideas:** UI themes, i18n, optional API token, Docker image, systemd unit examples.

---

## Credits

- [androidtvremote2](https://pypi.org/project/androidtvremote2/) — protocol implementation  
- [zeroconf](https://pypi.org/project/zeroconf/) — mDNS discovery  
- [FastAPI](https://fastapi.tiangolo.com/) & [Uvicorn](https://www.uvicorn.org/) — web stack  

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).
