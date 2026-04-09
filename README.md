<div align="center">

# Self-hosted Android TV Remote

## **TOTALLY FUCKING FREE · NO ADS · NO TRACKING · NO SUBSCRIPTION · NO SIGN‑UP**

*No login walls. No “watch an ad to unlock volume.” No data sold to ad networks. It runs on **your** Wi‑Fi and doesn’t nag you.*

*Estoy harto de aplicaciones de TV remote que no paran de sacarte anuncios — por eso existe esto.*

**Control your Google TV / Android TV from any browser on your Wi‑Fi — no cloud, no vendor account.**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

[Docker Hub (1 command)](#docker-hub-quick-run) · [Features](#features) · [How it works](#how-it-works) · [Screenshots](#screenshots) · [Not a programmer?](#not-a-programmer) · [Quick start](#quick-start) · [Docker](#docker) · [API](#http-api) · [Contributing](#contributing)

</div>

---

**Install with Docker** (recommended): pull **`pepe12341234/tv-remove-selfhosted:latest`** from Docker Hub — see [Not a programmer?](#not-a-programmer) or [Docker](#docker). No clone required.

Run a tiny **FastAPI** server on your Mac, PC, or Raspberry Pi. Your phone opens a **mobile-first web UI** to discover TVs, pair once, and send keys (power, D‑pad, volume, media). Prefer a **desktop window** or **terminal**? Those are included when you run from source (below).

Uses the official **Android TV Remote v2** protocol via [`androidtvremote2`](https://pypi.org/project/androidtvremote2/) — the same family of APIs the Google TV app uses on the local network.

---

<div align="center">

### Docker Hub — one command

No Git, no Python, no project folder — only Docker:

```bash
docker pull pepe12341234/tv-remove-selfhosted:latest && \
docker run -d --name androidtv-remote --restart unless-stopped \
  -p 8765:8765 -e ANDROIDTV_PORT=8765 \
  -v androidtv-config:/root/.config/androidtv-remote \
  pepe12341234/tv-remove-selfhosted:latest
```

On your **phone**, open **`http://<YOUR-LAN-IP>:8765`** (same Wi‑Fi as the PC). **Linux / Raspberry Pi** with host networking: [full commands](#not-a-programmer).

*Image: [`pepe12341234/tv-remove-selfhosted:latest`](https://hub.docker.com/r/pepe12341234/tv-remove-selfhosted)*

</div>

---

## How it works

**One** small computer on your network runs the app (a **Raspberry Pi**, an old laptop, a NAS, or your desktop). It **hosts the web page** and the **API**. **Many** phones or tablets can open the same URL at once — each browser loads the UI from that machine; the server is the single place that pairs with the TV and sends remote keys.

```mermaid
flowchart TB
  subgraph lan["Your home Wi‑Fi LAN"]
    subgraph clients["Phones & tablets — any browser"]
      M1["📱"]
      M2["📱"]
      M3["📱"]
    end
    subgraph server["Home server — Pi, PC, Mac, Docker…"]
      S["FastAPI + Uvicorn\n• serves web UI\n• REST /api"]
    end
    TV["📺 Android TV / Google TV"]
  end

  M1 -->|"http://server-ip:8765"| S
  M2 -->|"http://server-ip:8765"| S
  M3 -->|"http://server-ip:8765"| S
  S -->|"Remote v2 — TLS, pairing, keys"| TV
```

Nothing goes through the public internet for control: traffic stays between **clients ↔ your server** and **server ↔ TV** on the LAN.

---

## Screenshots

<div align="center">

<img src="assets/screenshots/screenshot-connect.png" alt="Discover and connect to TVs on your network" width="320" />
&nbsp;&nbsp;
<img src="assets/screenshots/screenshot-remote.png" alt="Virtual remote — D-pad, volume, media keys" width="320" />

*Left: discover devices by name (mDNS). Right: full remote in the browser — self-hosted on your LAN.*

</div>

> **Note:** Screenshots are illustrative mockups of the UI style. Your real device list and layout match the live app.

---

## Why self-hosted?

| | |
| --- | --- |
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
- **Docker** — pre-built **[`pepe12341234/tv-remove-selfhosted:latest`](https://hub.docker.com/r/pepe12341234/tv-remove-selfhosted)** on Docker Hub; multi-stage Dockerfile builds the UI with Node and runs **FastAPI + Uvicorn** on Python slim (**no** Tkinter / `main.py` in the container)

---

## Not a programmer?

You **do not** need Git, Python, or Node — only **Docker** and the **pre-built image** on [Docker Hub](https://hub.docker.com/r/pepe12341234/tv-remove-selfhosted). The first `docker pull` downloads the app; **`docker run`** starts it. Pairing data is kept in a Docker volume so it survives restarts.

### What you need

- **Docker** — [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac / Windows) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux / Raspberry Pi)
- A PC that stays on while you use the remote, and the **TV on the same Wi‑Fi** as that PC
- A few minutes the first time (`docker pull` can be large)

### Install — pull the image and run it

Open **Terminal** (Mac / Linux) or **PowerShell** (Windows). **Mac or Windows:** use the **`-p`** form (Docker Desktop does not support host networking).

**Mac / Windows (Docker Desktop)**

```bash
docker pull pepe12341234/tv-remove-selfhosted:latest

docker run -d --name androidtv-remote --restart unless-stopped \
  -p 8765:8765 \
  -e ANDROIDTV_PORT=8765 \
  -v androidtv-config:/root/.config/androidtv-remote \
  pepe12341234/tv-remove-selfhosted:latest
```

**Linux (recommended — same network stack as the PC, better TV discovery)**

```bash
docker pull pepe12341234/tv-remove-selfhosted:latest

docker run -d --name androidtv-remote --restart unless-stopped \
  --network host \
  -e ANDROIDTV_PORT=8765 \
  -v androidtv-config:/root/.config/androidtv-remote \
  pepe12341234/tv-remove-selfhosted:latest
```

If `androidtv-remote` already exists from a previous try: `docker rm -f androidtv-remote` and run the `docker run` again.

### Use your phone as the remote

1. Find the PC’s **LAN IP** (same Wi‑Fi as the TV).
2. On the phone’s browser: **`http://<THAT-IP>:8765`** (example: `http://192.168.1.42:8765`). On the **Linux server itself**, you can use **`http://127.0.0.1:8765`** or **`http://localhost:8765`**.
3. Pick your TV from the list, or **Connect by IP** if the list is empty.
4. If the TV shows a **pairing** code, enter the **6 hex characters** in the app.

### Stop, start, or remove

```bash
docker stop androidtv-remote    # stop
docker start androidtv-remote   # start again
docker rm -f androidtv-remote # remove container (volume keeps pairing — add -v androidtv-config to delete it)
```

### Another port (Mac / Windows)

Use the **same number** for `-p` and `-e` (example **9000**):

```bash
docker run -d --name androidtv-remote --restart unless-stopped \
  -p 9000:9000 -e ANDROIDTV_PORT=9000 \
  -v androidtv-config:/root/.config/androidtv-remote \
  pepe12341234/tv-remove-selfhosted:latest
```

On **Linux** with `--network host`, only **`-e ANDROIDTV_PORT=9000`** matters; open **`http://<IP>:9000`**.

### If the TV list is empty

Common with **bridge** networking. Tap **Connect by IP** and enter the TV’s IP from **Android TV → Settings → Network**.

### ¿No eres programador? (español)

No necesitas **Git**, **Python** ni descargar el código: solo **Docker** y la imagen **`pepe12341234/tv-remove-selfhosted:latest`**.

1. Instala **Docker** ([Docker Desktop](https://www.docker.com/products/docker-desktop/) en Mac/Windows, o Docker en Linux / Raspberry Pi).
2. Abre una **terminal** y ejecuta **`docker pull`** y luego **`docker run`** como arriba: en **Mac o Windows** el bloque con **`-p 8765:8765`**; en **Linux** el bloque con **`--network host`**.
3. En el **móvil** (misma Wi‑Fi), abre **`http://IP-DE-TU-PC:8765`**.
4. Elige la TV o **Conectar por IP**. Si pide **emparejamiento**, el código **hex de 6 caracteres** en la TV.
5. Para **parar**: `docker stop androidtv-remote`. Para **volver a arrancar**: `docker start androidtv-remote`.

---

## Quick start

**From source** — for the **Docker Hub image**, use [Not a programmer?](#not-a-programmer) instead.

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

---

## Docker

### Install from Docker Hub (recommended)

Use the public image — **no clone, no build**:

[`pepe12341234/tv-remove-selfhosted:latest`](https://hub.docker.com/r/pepe12341234/tv-remove-selfhosted)

Full **`docker pull` / `docker run`** commands (Mac, Windows, Linux, stop/start) are in **[Not a programmer?](#not-a-programmer)**.

### Build from source (optional)

Clone the repo if you want to **change code** or **build your own image**:

```bash
git clone https://github.com/YOUR_USERNAME/androidtv.git
cd androidtv
```

**Compose** (builds the image locally):

```bash
docker compose up --build
```

**Linux:** `docker-compose.yml` uses **`network_mode: host`** — same network as the PC (better mDNS). **Docker Desktop (Mac / Windows):** host mode is unavailable; use:

```bash
docker compose -f docker-compose.bridge.yml up --build
```

Change port (Linux host network):

```bash
ANDROIDTV_PORT=9000 docker compose up --build
```

**Build / run the image manually (no Compose)**

```bash
docker build -t androidtv-remote .
docker run -d --name androidtv-remote --restart unless-stopped \
  -p 8765:8765 -e ANDROIDTV_PORT=8765 \
  -v androidtv-config:/root/.config/androidtv-remote \
  androidtv-remote
```

### Dockerfile layout

The **Dockerfile** is **multi-stage**:

| Stage | Image | What it does |
|-------|--------|----------------|
| **frontend** | `node:20-alpine` | `npm ci`, copies `frontend/`, runs `npm run build` → `static/dist` |
| **runtime** | `python:3.12-slim-bookworm` | Installs **FastAPI**, **Uvicorn**, **androidtvremote2**, **zeroconf** with `pip`; copies only **`web.py`**, **`tv_core.py`**, and the built **`static/dist/`** |

`main.py` is **not** copied into the image: it imports **Tkinter**, which is not used in the container. The process is started with **Uvicorn**:

```text
python -m uvicorn web:app --host 0.0.0.0 --port ${ANDROIDTV_PORT:-8765}
```

### Discovery & networking

- **Different network than the TV?** Discovery uses **mDNS** (multicast) on the local LAN. If the TV is on another **subnet**, **VLAN**, **guest Wi‑Fi**, or a **different router**, the list is often **empty** — not because Docker is “on another internet”, but because **multicast does not cross** those boundaries the way you expect. **Connect by IP** can still work if your PC can **route** to the TV’s IP and nothing blocks the remote port (firewall).
- **Linux + default `docker-compose.yml`:** **`network_mode: host`** puts the app on the **same network stack as the PC**, so discovery usually matches a non‑Docker run.
- **Bridge** (`docker-compose.bridge.yml`, or `docker run -p …`): **mDNS** from inside the container often **misses** TVs. Use **Connect by IP** in the web UI.

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

**Docker:** the same paths exist **inside the container** under **`/root/.config/androidtv-remote`**. Use **`-v androidtv-config:/root/.config/androidtv-remote`** (see [Docker Hub install](#not-a-programmer)) or the Compose files — the named volume keeps pairing across container recreates.

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
├── Dockerfile           # Multi-stage: Node 20 → build UI; Python 3.12 slim → uvicorn web:app
├── docker-compose.yml   # Linux: host network (same LAN as PC) + volume for pairing certs
├── docker-compose.bridge.yml  # Mac/Windows Docker Desktop: published port + bridge
├── static/dist/         # Vite build output (local `npm run build`, or produced in Docker)
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

**Ideas:** UI themes, i18n, optional API token, pre-built images on a registry, systemd unit examples.

---

## Credits

- [androidtvremote2](https://pypi.org/project/androidtvremote2/) — protocol implementation
- [zeroconf](https://pypi.org/project/zeroconf/) — mDNS discovery
- [FastAPI](https://fastapi.tiangolo.com/) & [Uvicorn](https://www.uvicorn.org/) — web stack

---

## License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE).
