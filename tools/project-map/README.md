# Project map generator

Builds `docs/project-map.pdf`: one card per file (what it does, why we need it, what it connects to) plus a full-page map of every file and import.

## Run it

From the repo root:

```bash
uv run --no-project --with reportlab==5.0.1 --with pypdf python -I tools/project-map/build.py
```

`uv` installs reportlab and pypdf into a temporary environment, so nothing is added to the project or the system Python.

## What updates by itself

- The **IMPORTS / USED BY** lines on every card, and every arrow on the map, come from the real `import` statements (`imports.py`).
- The cover's date and commit.

## What you update by hand

- **New file:** if a new `.ts`/`.tsx` file is imported somewhere, the build stops and names it. Add a box for it in `NODES` in `map_page.py` (pick a column and row), and a card in `content.py`.
- **Changed purpose:** the "what it does" / "why we need it" text lives in `content.py`.
- **HTTP calls and non-import links** (hooks → routes, config files) live in `EXTRA` in `map_page.py`.

## Files

| File | Job |
|---|---|
| `build.py` | Text pages (cover, big picture, walkthroughs, cards, notes), then merges in the map page |
| `map_page.py` | The 11×17 map: box positions and edge routing through the gaps between boxes |
| `content.py` | All the explanations |
| `imports.py` | Finds every internal import (`python3 tools/project-map/imports.py` lists them) |
