"""Lógica compartida: escaneo, sesión Android TV y envío de teclas."""

from __future__ import annotations

import asyncio
import re
from collections.abc import Awaitable, Callable
from pathlib import Path

from androidtvremote2 import AndroidTVRemote, CannotConnect, ConnectionClosed, InvalidAuth
from zeroconf import (
    ServiceInfo,
    ServiceBrowser,
    Zeroconf,
    instance_name_from_service_info,
)

CONFIG_DIR = Path.home() / ".config" / "androidtv-remote"
CLIENT_NAME = "Python TV Remote"
CERTFILE = CONFIG_DIR / "client.pem"
KEYFILE = CONFIG_DIR / "client.key"


def _dns_unescape_instance_label(label: str) -> str:
    """Decodifica secuencias \\ooo (octal) usadas en nombres de instancia DNS-SD (p. ej. \\032 → espacio)."""

    def _sub(m: re.Match[str]) -> str:
        o = int(m.group(1), 8)
        return chr(o) if o <= 0x10FFFF else m.group(0)

    return re.sub(r"\\(\d{3})", _sub, label)


def _display_name_from_service(info: ServiceInfo, browser_name: str) -> str:
    """
    Nombre visible del televisor: el nombre de *instancia* mDNS (p. ej. bedroomtv), no info.server
    (suele ser algo como android-123.local., el hostname del servicio).
    """
    label: str | None = None
    try:
        label = instance_name_from_service_info(info)
    except Exception:
        label = None
    if not label:
        for marker in ("._androidtvremote2._tcp.local.", "._androidtvremote2._tcp."):
            if marker in browser_name:
                label = browser_name.split(marker)[0]
                break
    if label:
        return _dns_unescape_instance_label(label).strip()

    try:
        dp = info.decoded_properties
        if dp:
            for key in ("fn", "friendlyName", "name", "device_name", "nm"):
                v = dp.get(key)
                if v and str(v).strip():
                    return str(v).strip()
    except Exception:
        pass

    return (info.server or browser_name or "Android TV").rstrip(".")


class AndroidTVListener:
    def __init__(self) -> None:
        self.found: list[tuple[str, str]] = []

    def add_service(self, zeroconf, type_, name):
        info = zeroconf.get_service_info(type_, name)
        if info and info.addresses:
            ip = ".".join(map(str, info.addresses[0]))
            device_name = _display_name_from_service(info, name)
            self.found.append((device_name, ip))

    def update_service(self, zeroconf, type_, name):
        self.add_service(zeroconf, type_, name)

    def remove_service(self, zeroconf, type_, name):
        pass


async def scan_devices(timeout: float = 5) -> list[tuple[str, str]]:
    zeroconf = Zeroconf()
    listener = AndroidTVListener()
    ServiceBrowser(zeroconf, "_androidtvremote2._tcp.local.", listener)
    await asyncio.sleep(timeout)
    zeroconf.close()
    return list(listener.found)


async def ensure_paired(
    remote: AndroidTVRemote,
    get_pairing_code: Callable[[], Awaitable[str]],
) -> None:
    try:
        await remote.async_connect()
        return
    except InvalidAuth:
        pass
    await remote.async_start_pairing()
    code = (await get_pairing_code()).strip()
    await remote.async_finish_pairing(code)
    await remote.async_connect()


def send_key_safe(remote: AndroidTVRemote, key: str) -> None:
    try:
        remote.send_key_command(key)
    except ConnectionClosed:
        pass


class TVSession:
    """Una sesión con la TV; segura para usar desde FastAPI (asyncio.Lock)."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._remote: AndroidTVRemote | None = None
        self.pairing_pending = False

    @property
    def connected(self) -> bool:
        return self._remote is not None and not self.pairing_pending

    async def disconnect(self) -> None:
        async with self._lock:
            if self._remote:
                self._remote.disconnect()
                self._remote = None
            self.pairing_pending = False

    def _attach_callbacks(self, remote: AndroidTVRemote) -> None:
        def on_available(_available: bool) -> None:
            pass

        remote.add_is_available_updated_callback(on_available)
        remote.keep_reconnecting()

    async def connect(self, ip: str) -> str:
        """Devuelve 'connected' | 'pairing'. Lanza CannotConnect u otras excepciones."""
        async with self._lock:
            if self._remote:
                self._remote.disconnect()
                self._remote = None
            self.pairing_pending = False

            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            remote = AndroidTVRemote(
                CLIENT_NAME,
                str(CERTFILE),
                str(KEYFILE),
                ip.strip(),
            )
            await remote.async_generate_cert_if_missing()
            try:
                await remote.async_connect()
            except InvalidAuth:
                await remote.async_start_pairing()
                self._remote = remote
                self.pairing_pending = True
                return "pairing"

            self._remote = remote
            self._attach_callbacks(remote)
            return "connected"

    async def finish_pairing(self, code: str) -> None:
        async with self._lock:
            if not self._remote or not self.pairing_pending:
                raise ValueError("No hay emparejamiento pendiente")
            await self._remote.async_finish_pairing(code.strip())
            await self._remote.async_connect()
            self.pairing_pending = False
            self._attach_callbacks(self._remote)

    async def send_key(self, key: str) -> None:
        async with self._lock:
            if not self._remote or self.pairing_pending:
                raise RuntimeError("No conectado")
            send_key_safe(self._remote, key)
