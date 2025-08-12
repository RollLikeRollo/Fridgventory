# Fridgventory
Simple self-hosted Django app for managing a kitchen inventory with desired vs current quantities, tags, and locations. Generates shopping list as text and image. No auth.

## Quick start with Docker (Recommended)

Requirements: Docker and Docker Compose

```bash
# Clone the repository
git clone <repository-url>
cd Fridgventory

# Start the application
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

Visit `http://localhost:8000/`.

To stop the application: `docker-compose down`

Optional: Create a superuser to access `/admin/`:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Manual setup

Requirements: Python 3.11+, pip

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Visit `http://localhost:8000/`.

Optional: `python manage.py createsuperuser` to access `/admin/`.

## Plugins

Plugins live under `plugins/` and must expose an `on_ready()` callable in `plugin.py`.

Example plugin seeds locations: `plugins/examples/room_tags/plugin.py`.
