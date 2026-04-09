# Contributing

Thanks for helping improve this project. Here is how we work.

## Getting started

1. **Fork** the repository and create a **branch** from `main`.
2. Use **Python 3.12+** and install with `uv sync` (or `pip install -e ".[dev]"` if we add extras later).
3. Run the **web app** locally: `uv run python main.py` and test on your LAN with a real Android TV when possible.

## Pull requests

- Keep changes **focused** (one feature or fix per PR).
- Match **existing style**: type hints where it helps, no unnecessary refactors.
- If you change user-facing behaviour, update **README.md** (or this file) when relevant.
- Add a short **description** of what changed and **why** in the PR body.

## Code style

- Prefer **clear names** over clever one-liners.
- **Async** code stays in `tv_core.py` / `web.py`; Tk stays in `main.py` unless we split modules further.
- Avoid new heavy dependencies unless there is a strong reason.

## Reporting issues

Include when you can:

- OS and Python version  
- How you run the app (`main.py` default, `--tk`, `--cli`)  
- TV model / Android TV build (approximate)  
- What you expected vs what happened  
- Relevant logs from the terminal  

## Security

If you find a **security issue**, please report it privately to the maintainers instead of opening a public issue first.
