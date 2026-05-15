# contracts — Claude Code Guide

## Project Overview
**contractility** — a Flask web app automating race support contract management and sponsorship tracking for the Steeplechase Running Club (FSRC). Replaces manual Google Sheets workflows.

## Tech Stack
- **Backend**: Python 3.12, Flask 3.0, SQLAlchemy 1.4, Alembic (migrations)
- **Database**: MySQL 8.0 (via PyMySQL driver)
- **Frontend**: Jinja2 templates, WTForms, Flask-Assets/webassets
- **Auth**: Flask-Security-Too, Flask-Principal
- **Document Gen**: python-docx, html2docx
- **External APIs**: RunSignUp (race data), Google Workspace/Sheets API
- **Mail**: Flask-Mail + msmtp
- **Infrastructure**: Docker, Docker Compose, Nginx, Gunicorn, phpMyAdmin, crond
- **Internal lib**: loutilities (custom utilities, version 3.11+)

## Project Structure
```
contracts/
├── app/src/contracts/    # Core Flask app package
│   ├── __init__.py       # create_app() factory
│   ├── dbmodel.py        # SQLAlchemy models
│   ├── contractmanager.py # Contract generation logic
│   ├── views/
│   │   ├── admin/        # Admin route handlers
│   │   ├── frontend/     # Public route handlers
│   │   └── userrole/     # User role management
│   ├── templates/        # Jinja2 HTML templates
│   └── static/           # CSS, JS, images
├── app/src/scripts/      # Flask CLI commands
├── app/src/migrations/   # Alembic migration files
├── config/               # App config, DB secrets, mail config
├── web/                  # Nginx container
├── docs/                 # Sphinx documentation
└── test/                 # pytest test suite
```

## Running the App
```bash
# Development (from project root)
docker compose up

# Services started:
# - MySQL (internal)
# - Flask/Gunicorn (internal port 5000)
# - Nginx reverse proxy (port 8003 via APP_PORT)
# - phpMyAdmin (at /phpmyadmin)
# - crond for scheduled tasks
```

## Database Migrations
```bash
flask db upgrade      # apply migrations
flask db migrate      # generate new migration
```

### Static JS Assets

JS assets are **not** served from the repo's `app/src/rrwebapp/static/js/` directory. That path is shadowed by a Docker volume mount defined in `docker-compose.yml`:

```yaml
- ${JS_COMMON_HOST}:/app/${APP_NAME}/static/js:ro
```

`JS_COMMON_HOST` is set in `.env`:
```
JS_COMMON_HOST="C:\Users\lking\Documents\Lou's Software\operational\js-common"
```

This shared `js-common` directory contains all versioned JS bundles (jQuery, DataTables, yadcf, etc.) used across multiple apps. Editing files under `static/js/` in the repo has no effect on the running container — changes must be placed in `js-common`.

The yadcf development repo lives at `C:\Users\lking\Documents\Lou's Software\projects\yadcf\yadcf\`. After editing yadcf there, the built file must be copied into `js-common` under the appropriate versioned directory (e.g., `js/yadcf-<version>/`) for it to be picked up by the app.

## Testing
```bash
pytest test/
```

## Key Entry Points
- `app/src/app_server.py` — production WSGI entry (gunicorn)
- `app/src/app.py` — Flask CLI entry
- `app/src/contracts/__init__.py` — `create_app()` factory
- `app/src/dbupgrade_and_run.sh` — container startup script

## Key Configuration
- `config/contracts.cfg` — main app config (email addresses, API keys, timing thresholds)
- `config/users.cfg` — user auth config
- `.env` — environment variables (APP_PORT, FLASK_DEBUG, DB/service versions, COMPOSE_FILE)
- `config/db/` — DB password secrets (mounted as Docker secrets)

## External Services
- **RunSignUp**: race registration data (RSU_KEY, RSU_SECRET in config)
- **Google Workspace**: service account JSON for Sheets API access
- **msmtp**: outbound mail relay

## Deployment
Uses Fabric (`fabfile.py`) for remote deployment via docker compose pull + up.

## MySQL SSL / Driver Note

**Problem:** MySQL 8.0+ in Docker with Alpine-based app containers causes `MySQLdb.OperationalError: (2026, 'TLS/SSL error: Certificate verification failure')`. Alpine uses MariaDB Connector/C (not libmysqlclient), which defaults to SSL with cert verification. MySQL 8.0 auto-generates self-signed certs. Server-side workarounds (`--skip-ssl`) are unreliable in 8.0.40+.

**Fix:** Use **PyMySQL** instead of mysqlclient. PyMySQL is pure Python, does not use MariaDB Connector/C, and does not attempt SSL by default.

Three files to change:

1. **`app/requirements.txt`** — remove `mysqlclient==x.x.x` and add `PyMySQL==1.1.3`. Also remove `typed_ast` if present — it does not build on Python 3.12 and is no longer needed (its functionality is in the standard `ast` module).

2. **`app/src/<appname>/settings.py`** — change URI scheme in `RealDb.__init__`:
   ```python
   # before
   db_uri = f'mysql://{dbuser}:{password}@{dbserver}/{dbname}'
   # after
   db_uri = f'mysql+pymysql://{dbuser}:{password}@{dbserver}/{dbname}'
   ```
   Same change for `usersdb_uri` if present.

3. **`app/Dockerfile`** — remove the C build scaffolding for mysqlclient (PyMySQL needs no compilation):
   ```dockerfile
   # remove these lines:
   RUN apk add --no-cache mariadb-connector-c-dev \
       && apk add --no-cache --virtual .build-deps build-base mariadb-dev \
       && pip install -r requirements.txt \
       && rm -rf .cache/pip \
       && apk del .build-deps
   # replace with:
   RUN pip install -r requirements.txt \
       && rm -rf .cache/pip
   ```
   Keep `apk add --no-cache mysql-client` — the startup script and cron backup jobs use the `mariadb`/`mariadb-dump` CLI.

4. **`app/client.my.cnf`** — must exist with `ssl = false` to suppress SSL for CLI tools (`mariadb`, `mariadb-dump`). The Dockerfile copies it to `/home/appuser/.my.cnf`:
   ```ini
   # see https://stackoverflow.com/a/78683658
   [client]
   ssl = false
   ```
   And in the Dockerfile:
   ```dockerfile
   COPY client.my.cnf /home/appuser/.my.cnf
   ```
