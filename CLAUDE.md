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
pytest
```
Run from the repo root; `pytest.ini` puts `app/src` on `sys.path` so `contracts`/`running` import normally. `test/conftest.py` sets `APP_NAME` (normally supplied by Docker Compose's `.env`) since `contracts/__init__.py` reads it at import time — needed for `contracts` to import outside the container at all.

Most of `contracts.runsignup.RunSignUp`'s methods are tested via `monkeypatch`-ing `_rsuget`/`_rsupost` (or `session.post`) rather than hitting the real API — see `test/test_runsignup.py` for the pattern. Tests that only need a `RSU_*`-config'd Flask app (e.g. `test/test_helpers.py`) build a bare `Flask(__name__)` rather than going through the full `create_app()`.

**`test_basic.py::test_login` still errors at setup — root cause is a `create_app()` ordering issue, not a missing config value.** `settings.Testing` used to be missing `EXCEPTION_EMAIL`/`APP_LOUTILITY`/the three `SECURITY_EMAIL_SUBJECT_*` keys (all now filled in, matching what real deployments get from `config/users.cfg`/`config/contracts.cfg`) and `SQLALCHEMY_BINDS['users']` (added, since `loutilities.user.model`'s `Application`/`User`/`Role` live on a separate `users` bind in production — see `RealDb` in `settings.py`). Filling those got `create_app(Testing)` past its config-lookup failures, but it still fails: `create_app()` unconditionally queries the `Application` table (for `g.loutility`) *while creating the app*, but the `app`/`dbapp` fixtures in `conftest.py` only call `db.create_all()` *after* `create_app()` returns — so that query always hits a table that doesn't exist yet. Properly fixing this means restructuring `create_app()` (e.g. deferring the `g.loutility` lookup) or `dbapp`'s fixture ordering, which is a behavior change to production startup code — left alone here, same as the pre-existing gap this replaces.

Because of that, DB-backed tests that don't need routing/security/full app setup (`test_utils.py`, `test_trends.py`, `test_dbmodel.py`) use a separate `bare_dbapp`/`bareapp` fixture pair in `conftest.py` instead of `app`/`dbapp` — a bare `Flask('contracts')` with just `contracts.dbmodel.db` bound (plus the `users` bind, since some models share it) and `db.create_all()` run directly, no `create_app()` involved. Same pattern as rrwebapp's `test/conftest.py` (there it's to dodge `celery.py`'s container-only config reads; here it's to dodge the `Application`-table-ordering issue above) — reach for `bare_dbapp` for any new model/free-function-level test that touches `contracts.dbmodel` query methods.

`contracts/request.py` (`annotatescripts`/`addscripts`/`crossdomain`) has no callers anywhere in the app — confirmed dead code, not worth testing. Its module-level `@current_app.after_request` also means merely importing it requires an app context already pushed, which would make tests unusually awkward for something nothing exercises.

`contractmanager._evaluate()`'s callable-leaf detection (`if not hasattr(subtree, '__dict__')`) only actually invokes callables that themselves lack a `__dict__` — e.g. a `__slots__`-based class implementing `__call__`. An ordinary function, lambda, or bound method *has* a `__dict__` (even if empty), so `_evaluate` treats it as a nested object to recurse into instead of a leaf to call, and it comes back unmodified. See `test_contractmanager.py::test_evaluate_does_not_call_ordinary_functions_or_lambdas` — surfaced while adding coverage, left as-is (matches production usage, which passes SQLAlchemy model instances as mergefields and never relies on function/lambda leaves).

**Gotcha (fixed once, watch for regression):** `test/conftest.py` used to import from `racesupportcontracts` (the app's pre-rename package name) instead of `contracts` — this failed at conftest *collection* time, so it silently broke every test in `test/`, not just the ones using the `app`/`dbapp` fixtures. If `pytest` suddenly reports zero tests collected or a conftest ImportError, check this first.

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
- **RunSignUp**: race registration data (RSU_KEY, RSU_SECRET, RSU_API_REG_TOKEN, RSU_API_REG_SECRET in config)
- **Google Workspace**: service account JSON for Sheets API access
- **msmtp**: outbound mail relay

### RunSignUp Client (`app/src/contracts/runsignup.py`)

`contracts.runsignup.RunSignUp` subclasses `running.runsignup.RunSignupBase` (from the `runtilities` PyPI package, `github.com/louking/running` — now a real dependency in `requirements.txt`). The base class owns all the shared plumbing: `__init__`/`open`/`close`, session setup, `client_credentials`, and `_rsuget`/`_rsugetcsv`. contracts' subclass adds only what `running`'s own `RunSignUp` doesn't need: `getcoupons`/`setcoupon` (coupon management for contract billing, POST-based) and `getraceparticipants`/`getremovedparticipants`, plus a local `_rsupost` since `RunSignupBase` only implements GET. This mirrors `members`' `helpers.make_runsignup_client()`, which builds `running.runsignup.RunSignUp` directly — contracts still needs its own subclass rather than using `running`'s `RunSignUp` as-is because of the coupon/POST and participant methods.

This inheritance only became safe once `running.runsignup_fluent.RunSignupFluent` (which needs `universalclient`/`rauth`) was split out of `running/runsignup.py` into its own module — before that, importing `running.runsignup` at all would have dragged in those extra dependencies. Don't reintroduce that coupling.

**Gotcha:** `running.runsignup` imports `loutilities.csvwt` at module level (for the unrelated `members2csv()` helper), which in turn imports `openpyxl` unconditionally — so `openpyxl` had to be added to `requirements.txt` even though contracts never calls anything CSV/Excel-related here. If this trips again after a `running`/`loutilities` bump, it's this transitive import, not a real new feature dependency.

**Instantiation is centralized**: use `helpers.make_runsignup_client(**kwargs)` rather than constructing `RunSignUp(...)` directly — it reads `RSU_KEY`/`RSU_SECRET`/`RSU_API_REG_TOKEN`/`RSU_API_REG_SECRET` from `current_app.config` once. Same pattern as `members`' `helpers.make_runsignup_client()`.

Endpoints are on `api.runsignup.com/rest/...` (migrated Aug 2025 from the legacy `runsignup.com/rest/...`), and the client sends the `rsu_api_reg` token/`X-RSU-API-REG-SECRET` header required by all API callers starting 2027-01-01 per https://info.runsignup.com/2026/07/17/new-api-registration-requirements/ (existing `api_key`/`api_secret` still required alongside it). The legacy email/password Login API path has been removed — it was unused dead code (confirmed both call sites only ever passed `key=`/`secret=`).

## Deployment
Uses Fabric (`fabfile.py`) for remote deployment via docker compose pull + up.

## Production Infrastructure

The production server runs **Caddy** as the HTTPS reverse proxy. Caddy terminates TLS and forwards traffic to the Docker container on port 8003 (`APP_PORT`). The Caddyfile lives on the production server (not in this repo) and covers all loutilities apps.

### Caddy HTTP/3 / QUIC Issue

Caddy enables HTTP/3 (QUIC) by default. This can cause intermittent `net::ERR_QUIC_PROTOCOL_ERROR 200 (OK)` in Chrome, where the page returns 200 but renders blank — the QUIC connection drops mid-stream. The Flask app is not at fault; it's a Caddy transport issue that shows up with larger responses.

**Fix:** add `protocols h1 h2` to the global `servers` block in the Caddyfile to disable HTTP/3 across all sites:

```
{
    servers {
        protocols h1 h2
        # ... rest of existing servers block
    }
}
```

After editing, reload Caddy: `caddy reload` or `systemctl reload caddy`.

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
