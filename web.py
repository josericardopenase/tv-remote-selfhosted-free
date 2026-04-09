"""Servidor web FastAPI: API REST + interfaz estática para el mando."""

from __future__ import annotations

import contextlib
import os
import socket
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from androidtvremote2 import CannotConnect, InvalidAuth

from tv_core import TVSession, scan_devices

STATIC_DIR = Path(__file__).resolve().parent / "static"

session = TVSession()


def _local_ipv4() -> str:
    """IP en la LAN para mostrar la URL (no es el bind del servidor)."""
    for dest in (("8.8.8.8", 80), ("1.1.1.1", 80)):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(1.0)
            s.connect(dest)
            ip = s.getsockname()[0]
            s.close()
            return ip
        except OSError:
            continue
    return "127.0.0.1"


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    port = int(os.environ.get("ANDROIDTV_PORT", "8765"))
    lan = _local_ipv4()
    print(
        "\n  Android TV — accesible en tu red local (Wi‑Fi)\n"
        f"  Abre en el móvil: http://{lan}:{port}\n"
        f"  (El servidor escucha en 0.0.0.0:{port} para aceptar conexiones de otros equipos.)\n",
        flush=True,
    )
    yield
    await session.disconnect()


app = FastAPI(title="Android TV Remote", lifespan=lifespan)


class ConnectBody(BaseModel):
    ip: str = Field(..., min_length=1)


class PairBody(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)


class KeyBody(BaseModel):
    key: str = Field(..., min_length=1)


@app.get("/", response_class=HTMLResponse)
async def index():
    index_path = STATIC_DIR / "index.html"
    if index_path.is_file():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    return HTMLResponse("<p>Missing static/index.html</p>", status_code=500)


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/favicon.ico")
async def favicon():
    return Response(status_code=204)


@app.get("/api/status")
async def api_status():
    return {
        "connected": session.connected,
        "pairing": session.pairing_pending,
    }


@app.post("/api/scan")
async def api_scan():
    try:
        found = await scan_devices(5)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {
        "devices": [{"name": n, "ip": ip} for n, ip in found],
    }


@app.post("/api/connect")
async def api_connect(body: ConnectBody):
    try:
        state = await session.connect(body.ip)
    except CannotConnect as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    return {"state": state}


@app.post("/api/pair")
async def api_pair(body: PairBody):
    try:
        await session.finish_pairing(body.code)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except InvalidAuth as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return {"ok": True}


@app.post("/api/key")
async def api_key(body: KeyBody):
    try:
        await session.send_key(body.key)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return {"ok": True}
