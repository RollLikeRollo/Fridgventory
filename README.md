# Fridgventory
Simple self-hosted Django app for managing a kitchen inventory with desired vs current quantities, tags, and locations. Generates shopping list as text and image. No auth.

## Quick start

Requirements: Python 3.11+, pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install "Django>=5,<6" "Pillow>=10,<11"
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/`.

Optional: `python manage.py createsuperuser` to access `/admin/`.

## Plugins

Plugins live under `plugins/` and must expose an `on_ready()` callable in `plugin.py`.

Example plugin seeds locations: `plugins/examples/room_tags/plugin.py`.
