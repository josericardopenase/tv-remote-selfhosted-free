import asyncio
import os
import sys
import threading
from collections.abc import Callable
from tkinter import (
    BOTH,
    DISABLED,
    END,
    LEFT,
    NSEW,
    W,
    Button,
    Entry,
    Frame,
    Label,
    Listbox,
    StringVar,
    Text,
    Tk,
    messagebox,
    simpledialog,
)

from androidtvremote2 import CannotConnect

from tv_core import (
    AndroidTVRemote,
    CERTFILE,
    CLIENT_NAME,
    CONFIG_DIR,
    KEYFILE,
    ensure_paired,
    scan_devices,
    send_key_safe,
)

# Tema tipo mando físico (oscuro, acentos metálicos)
BG = "#141418"
PANEL = "#1e1e24"
BTN = "#2a2a32"
BTN_ACTIVE = "#3d3d48"
ACCENT = "#c9a227"
TEXT_MUTED = "#8a8a96"
BTN_DPAD = "#25252d"


def _style_round_button(
    parent: Frame,
    text: str,
    command: Callable[[], None],
    *,
    width: int = 8,
    bg: str = BTN,
    active_bg: str = BTN_ACTIVE,
    fg: str = "#e8e8ed",
    font_: tuple[str, int, str] | None = None,
) -> Button:
    f = font_ or ("Helvetica Neue", 11, "bold")
    b = Button(
        parent,
        text=text,
        command=command,
        width=width,
        bg=bg,
        activebackground=active_bg,
        activeforeground=fg,
        fg=fg,
        font=f,
        relief="flat",
        bd=0,
        highlightthickness=0,
        cursor="hand2",
        padx=8,
        pady=10,
    )
    return b


class TkRemoteApp:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.title("Mando Android TV")
        self.root.configure(bg=BG)
        self.root.minsize(320, 520)
        self.root.geometry("380x620")

        self._async_loop: asyncio.AbstractEventLoop | None = None
        self._async_thread: threading.Thread | None = None
        self._remote: AndroidTVRemote | None = None
        self._cmd_queue: asyncio.Queue[str] | None = None
        self._shutdown = threading.Event()

        self._ip_var = StringVar(value=sys.argv[1] if len(sys.argv) >= 2 else "")
        self._status_var = StringVar(value="Introduce IP o busca dispositivos.")

        self._build_connect_frame()
        self._build_remote_frame()

        self.connect_frame.pack(fill=BOTH, expand=True)
        self.remote_frame.pack_forget()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        if len(sys.argv) >= 2:
            self.root.after(400, self._connect)

    def _build_connect_frame(self) -> None:
        self.connect_frame = Frame(self.root, bg=BG, padx=24, pady=20)

        Label(
            self.connect_frame,
            text="Android TV",
            bg=BG,
            fg="#f0f0f5",
            font=("Helvetica Neue", 22, "bold"),
        ).pack(anchor=W, pady=(0, 4))
        Label(
            self.connect_frame,
            text="Conexión",
            bg=BG,
            fg=TEXT_MUTED,
            font=("Helvetica Neue", 12),
        ).pack(anchor=W, pady=(0, 16))

        row = Frame(self.connect_frame, bg=BG)
        row.pack(fill=BOTH, pady=4)
        Label(row, text="IP", bg=BG, fg=TEXT_MUTED, width=4, anchor=W).pack(side=LEFT)
        ip_entry = Entry(
            row,
            textvariable=self._ip_var,
            width=24,
            bg=PANEL,
            fg="#eee",
            insertbackground="#fff",
            relief="flat",
            font=("Menlo", 12),
        )
        ip_entry.pack(side=LEFT, fill=BOTH, expand=True, ipady=6, padx=(8, 0))

        btn_row = Frame(self.connect_frame, bg=BG)
        btn_row.pack(fill=BOTH, pady=16)
        _style_round_button(btn_row, "Buscar en red", self._scan, width=14).pack(side=LEFT, padx=(0, 8))
        self._btn_connect = _style_round_button(
            btn_row, "Conectar", self._connect, width=14, bg=ACCENT, active_bg="#ddb52e"
        )
        self._btn_connect.pack(side=LEFT)

        self._scan_list = Listbox(
            self.connect_frame,
            height=5,
            bg=PANEL,
            fg="#ddd",
            selectbackground=ACCENT,
            selectforeground="#111",
            relief="flat",
            highlightthickness=0,
            font=("Menlo", 11),
        )
        self._scan_list.pack(fill=BOTH, expand=True, pady=8)
        self._scan_list.bind("<<ListboxSelect>>", self._on_list_select)

        self._log = Text(
            self.connect_frame,
            height=5,
            bg=PANEL,
            fg=TEXT_MUTED,
            relief="flat",
            font=("Menlo", 10),
            state=DISABLED,
        )
        self._log.pack(fill=BOTH, pady=8)

        Label(self.connect_frame, textvariable=self._status_var, bg=BG, fg=ACCENT, wraplength=320).pack(
            anchor=W
        )

    def _on_list_select(self, _event=None) -> None:
        sel = self._scan_list.curselection()
        if not sel:
            return
        line = self._scan_list.get(sel[0])
        if " — " in line:
            self._ip_var.set(line.split(" — ")[-1].strip())

    def _log_line(self, msg: str) -> None:
        self._log.configure(state="normal")
        self._log.insert(END, msg + "\n")
        self._log.see(END)
        self._log.configure(state=DISABLED)

    def _scan(self) -> None:
        self._status_var.set("Escaneando…")
        self._log_line("Buscando _androidtvremote2…")

        def work() -> None:
            async def run() -> None:
                found = await scan_devices(5)
                self.root.after(0, lambda: self._scan_done(found))

            asyncio.run(run())

        threading.Thread(target=work, daemon=True).start()

    def _scan_done(self, found: list[tuple[str, str]]) -> None:
        self._scan_list.delete(0, END)
        for name, ip in found:
            self._scan_list.insert(END, f"{name} — {ip}")
        if not found:
            self._status_var.set("No se encontró ningún dispositivo.")
            self._log_line("Prueba con la IP manualmente.")
        else:
            self._status_var.set(f"{len(found)} dispositivo(s). Selecciona uno o pulsa Conectar.")
            self._log_line("Lista actualizada.")

    def _pairing_code_dialog(self) -> str:
        return (
            simpledialog.askstring(
                "Emparejamiento",
                "Código de 6 caracteres hex que muestra la TV:",
                parent=self.root,
            )
            or ""
        )

    def _connect(self) -> None:
        if self._async_thread is not None and self._async_thread.is_alive():
            return
        ip = self._ip_var.get().strip()
        if not ip:
            messagebox.showwarning("IP", "Introduce una IP o elige un dispositivo de la lista.", parent=self.root)
            return
        self._status_var.set("Conectando…")
        self._log_line(f"Conectando a {ip}…")
        self._btn_connect.configure(state=DISABLED)

        def run_session() -> None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._async_loop = loop

            async def pairing_wrapper() -> str:
                return await asyncio.to_thread(self._pairing_code_dialog)

            async def session_inner() -> None:
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                remote = AndroidTVRemote(
                    CLIENT_NAME,
                    str(CERTFILE),
                    str(KEYFILE),
                    ip,
                )
                self._remote = remote
                self._cmd_queue = asyncio.Queue()

                def on_avail(available: bool) -> None:
                    if not available:
                        self.root.after(0, lambda: self._status_var.set("Reconectando…"))

                try:
                    await remote.async_generate_cert_if_missing()
                    await ensure_paired(remote, pairing_wrapper)

                    remote.add_is_available_updated_callback(on_avail)
                    remote.keep_reconnecting()

                    self.root.after(0, self._show_remote_ui)

                    while not self._shutdown.is_set():
                        try:
                            key = await asyncio.wait_for(self._cmd_queue.get(), timeout=0.5)
                        except TimeoutError:
                            continue
                        send_key_safe(remote, key)
                except CannotConnect as e:
                    self.root.after(
                        0,
                        lambda m=str(e): messagebox.showerror("Conexión", m, parent=self.root),
                    )
                except Exception as e:
                    self.root.after(
                        0,
                        lambda m=str(e): messagebox.showerror("Error", m, parent=self.root),
                    )
                finally:
                    remote.disconnect()
                    self._remote = None
                    self.root.after(0, lambda: self._btn_connect.configure(state="normal"))

            loop.run_until_complete(session_inner())

        self._async_thread = threading.Thread(target=run_session, daemon=True)
        self._async_thread.start()

    def _show_remote_ui(self) -> None:
        self._status_var.set("Conectado")
        self.connect_frame.pack_forget()
        self.remote_frame.pack(fill=BOTH, expand=True)

    def _enqueue_key(self, key: str) -> None:
        if self._async_loop is None or self._cmd_queue is None:
            return

        def put() -> None:
            if self._cmd_queue is not None:
                self._cmd_queue.put_nowait(key)

        self._async_loop.call_soon_threadsafe(put)

    def _build_remote_frame(self) -> None:
        self.remote_frame = Frame(self.root, bg=BG, padx=20, pady=16)

        top = Frame(self.remote_frame, bg=BG)
        top.pack(fill=BOTH)
        _style_round_button(top, "⏻", lambda: self._enqueue_key("POWER"), width=4, bg="#4a1518", active_bg="#6a2024").pack(
            side=LEFT, padx=(0, 6)
        )
        _style_round_button(top, "⌂", lambda: self._enqueue_key("HOME"), width=4).pack(side=LEFT, padx=6)
        _style_round_button(top, "↩", lambda: self._enqueue_key("BACK"), width=4).pack(side=LEFT, padx=6)

        vol = Frame(self.remote_frame, bg=BG)
        vol.pack(pady=12)
        _style_round_button(vol, "Vol +", lambda: self._enqueue_key("VOLUME_UP"), width=10).pack(pady=2)
        _style_round_button(vol, "Vol −", lambda: self._enqueue_key("VOLUME_DOWN"), width=10).pack(pady=2)

        mid = Frame(self.remote_frame, bg=BG)
        mid.pack(pady=8)
        _style_round_button(mid, "Mudo", lambda: self._enqueue_key("MUTE"), width=8).pack(side=LEFT, padx=4)
        _style_round_button(mid, "Menú", lambda: self._enqueue_key("MENU"), width=8).pack(side=LEFT, padx=4)

        Label(self.remote_frame, text="Navegación", bg=BG, fg=TEXT_MUTED, font=("Helvetica Neue", 10)).pack(
            pady=(8, 4)
        )

        dpad = Frame(self.remote_frame, bg=BG)
        dpad.pack()
        dpad.grid_columnconfigure(0, weight=1)
        dpad.grid_columnconfigure(1, weight=1)
        dpad.grid_columnconfigure(2, weight=1)

        def dbtn(txt: str, key: str, r: int, c: int, cs: int = 1) -> None:
            b = _style_round_button(dpad, txt, lambda k=key: self._enqueue_key(k), width=6, bg=BTN_DPAD)
            b.grid(row=r, column=c, columnspan=cs, padx=4, pady=4, sticky=NSEW)

        dbtn("▲", "DPAD_UP", 0, 1)
        dbtn("◀", "DPAD_LEFT", 1, 0)
        dbtn("OK", "DPAD_CENTER", 1, 1)
        dbtn("▶", "DPAD_RIGHT", 1, 2)
        dbtn("▼", "DPAD_DOWN", 2, 1)

        Label(self.remote_frame, text="Reproducción", bg=BG, fg=TEXT_MUTED, font=("Helvetica Neue", 10)).pack(
            pady=(16, 4)
        )
        play_row = Frame(self.remote_frame, bg=BG)
        play_row.pack()
        for txt, key in (
            ("⏮", "MEDIA_REWIND"),
            ("⏯", "MEDIA_PLAY_PAUSE"),
            ("⏭", "MEDIA_FAST_FORWARD"),
        ):
            _style_round_button(play_row, txt, lambda k=key: self._enqueue_key(k), width=5).pack(
                side=LEFT, padx=4
            )

        Label(
            self.remote_frame,
            text="Cierra la ventana para salir.",
            bg=BG,
            fg=TEXT_MUTED,
            font=("Helvetica Neue", 9),
        ).pack(pady=16)

    def _on_close(self) -> None:
        self._shutdown.set()
        if self._remote:
            try:
                self._remote.disconnect()
            except Exception:
                pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main_cli() -> None:
    async def _main() -> None:
        if len(sys.argv) >= 2:
            ip = sys.argv[1].strip()
            print(f"Usando IP: {ip}")
        else:
            found = await scan_devices()
            if not found:
                print("❌ No se encontraron dispositivos.")
                return
            for i, (name, ip_) in enumerate(found):
                print(f"[{i}] {name} - {ip_}")
            choice = int(input("\nSelecciona un dispositivo: "))
            ip = found[choice][1]

        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        remote = AndroidTVRemote(CLIENT_NAME, str(CERTFILE), str(KEYFILE), ip)

        async def get_code() -> str:
            return (await asyncio.to_thread(input, "Código (6 hex): ")).strip()

        def on_available(available: bool) -> None:
            if not available:
                print("⚠️ Conexión perdida; reconectando…")

        try:
            await remote.async_generate_cert_if_missing()
            await ensure_paired(remote, get_code)
            remote.add_is_available_updated_callback(on_available)
            remote.keep_reconnecting()
            print("✅ Conectado. Comandos: power, volup, voldown, home, back, exit\n")
            while True:
                cmd = (await asyncio.to_thread(input, "👉 Comando: ")).strip().lower()
                if cmd == "power":
                    send_key_safe(remote, "POWER")
                elif cmd == "volup":
                    send_key_safe(remote, "VOLUME_UP")
                elif cmd == "voldown":
                    send_key_safe(remote, "VOLUME_DOWN")
                elif cmd == "home":
                    send_key_safe(remote, "HOME")
                elif cmd == "back":
                    send_key_safe(remote, "BACK")
                elif cmd == "exit":
                    break
                else:
                    print("❓ Comando no reconocido")
        except CannotConnect as e:
            print(f"❌ No se pudo conectar: {e}")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            remote.disconnect()

    asyncio.run(_main())


if __name__ == "__main__":
    if "--cli" in sys.argv:
        sys.argv = [a for a in sys.argv if a != "--cli"]
        main_cli()
    elif "--tk" in sys.argv:
        sys.argv = [a for a in sys.argv if a != "--tk"]
        TkRemoteApp().run()
    else:
        import uvicorn

        port = int(os.environ.get("ANDROIDTV_PORT", "8765"))
        uvicorn.run(
            "web:app",
            host="0.0.0.0",
            port=port,
            reload=False,
        )
