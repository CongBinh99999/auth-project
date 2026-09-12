# AuthProject

Async authentication service built on FastAPI and PostgreSQL. Email verification,
refresh token rotation with theft detection, password reset, device tracking and
role-based access control, plus a browser console for exercising the flows by hand.

Written in English because every commit, pull request and code comment in the
repository's history is in English.

## Quick start

Two supported paths. Docker needs nothing installed but Docker; the local path
needs [uv](https://docs.astral.sh/uv/) and a running PostgreSQL 14+.

### Docker Compose

```bash
cp .env.example .env      # optional, compose has working defaults
docker compose up -d --build
```

`--build` is not optional after the first run. The image copies `app/` at build
time, so `docker compose up -d` on its own happily restarts the previous image
and serves whatever code it was built from — with no warning that it is stale.

Three services come up: the API at http://localhost:8000 (Swagger UI at
`/docs`), the dev console at http://localhost:5173, and PostgreSQL.

PostgreSQL is published on **5433** rather than 5432, so it does not collide with a
Postgres already installed on the host. The console must be on 5173 — that is one
of the two origins `CORS_ORIGINS` allows.

`database/schema.sql` runs automatically the first time the database volume is
created. It is **not** re-run afterwards — changing the schema means
`docker compose down -v` and starting again, or applying the change by hand.

### Local

```bash
uv sync
createdb auth_db
psql -d auth_db -f database/schema.sql
cp .env.example .env      # then edit DATABASE_URL
uv run uvicorn app.main:app --reload
```

## Configuration

Settings are read from environment variables and `.env` by
[`app/config/settings.py`](app/config/settings.py). Names must match exactly:
pydantic-settings is configured with `extra="ignore"`, so a misspelled key is
dropped without a warning and the default silently applies.

| Variable | Default | Notes |
|---|---|---|
| `APP_ENV` | `development` | Anything other than `development` enforces the `JWT_SECRET` rules below |
| `DATABASE_URL` | — | Must use the `postgresql+asyncpg://` driver |
| `JWT_SECRET` | `SECRET_KEY` | Placeholder. Outside development the app refuses to start unless this is changed and at least 32 characters |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | |
| `SMTP_USERNAME` / `SMTP_PASSWORD` | empty | Empty means nothing is sent. Register still returns 201 and the token is still created — nobody receives it |
| `SMTP_TIMEOUT` | `10` | Without it a hung SMTP server would block a worker indefinitely |
| `CORS_ORIGINS` | `:3000`, `:5173` | The dev console runs on 5173 |

Generate a real secret with `openssl rand -hex 32`.

## Client IP and proxies

Login and registration are rate-limited per IP, so the address the app records
matters. uvicorn parses `X-Forwarded-For` and rewrites `request.client.host`, but
only when the connection's peer is listed in `FORWARDED_ALLOW_IPS` — which
defaults to `127.0.0.1`. Measured behaviour:

| Setup | `X-Forwarded-For` sent | IP recorded |
|---|---|---|
| uvicorn on localhost, request from 127.0.0.1 | `203.0.113.77` | `203.0.113.77` — trusted |
| `docker compose`, request through the gateway | `1.2.3.4` | `192.168.65.1` — header ignored |
| `docker compose`, no header | — | `192.168.65.1` |

The default is safe: a client cannot forge its own address unless it is already
on the loopback interface. The cost is the third row — behind Docker's NAT, and
behind any reverse proxy that is not on `127.0.0.1`, every client collapses into
one address and the per-IP thresholds stop separating users.

Behind a real proxy, set `FORWARDED_ALLOW_IPS` to that proxy's address so the
forwarded header is trusted from it and only it:

```yaml
environment:
  FORWARDED_ALLOW_IPS: "10.0.0.5"   # the proxy, never "*"
```

`"*"` trusts the header from anyone and makes the limits trivially bypassable.

## API

29 routes under `/api/v1`, plus `/health`. Full schema at `/docs`.

| Group | Routes |
|---|---|
| Auth | `POST /auth/register`, `/login`, `/refresh`, `/logout`, `/logout-all` |
| Email | `GET` and `POST /auth/verify-email`, `POST /auth/resend-verification` |
| Password | `POST /auth/forgot-password`, `POST /auth/reset-password` |
| Users | `GET` and `PATCH /users/me`, `PATCH /users/me/password` |
| Devices | `GET /devices/`, `DELETE /devices/`, and per-device get, update, delete, trust, untrust |
| Roles | CRUD on `/roles/` plus permission assignment — admin only |

`GET /auth/verify-email?token=...` is the URL that goes out in the email. The
`POST` variant exists for a client that already holds the token.

`GET /reset-password` is served at the root, outside `/api/v1`, because that is
where the password reset email links. It is a static form that posts to
`POST /api/v1/auth/reset-password`; the token stays in the query string and is
read by the page's own JavaScript, never interpolated into the HTML.

`/logout` and `/logout-all` read the access token from the `Authorization`
header, not the request body. `/logout` takes `refresh_token` in the body because
a header cannot carry it.

## Tests

```bash
uv run pytest            # 82 tests, no server needed
uv run ruff check app tests
```

The suite drives the app through `ASGITransport` in-process, so nothing has to be
started first. A reachable PostgreSQL is still required — the tests use the
database from `DATABASE_URL` and leave their rows behind.

SMTP is stubbed in `tests/conftest.py`. Without that stub, real credentials in
`.env` would make every run send mail: background tasks execute inside the test
process under `ASGITransport`, so "background" does not mean "after the test".

CI runs the same two commands against a `postgres:18` service container on every
pull request.

## Dev console

A React app under [`dev/`](dev/) for running the flows by hand and executing six
security scenarios (refresh token used as an access token, single-use
verification token, brute-force blocking, and so on) with one click each.

`docker compose up` already serves it on http://localhost:5173 as static files
behind nginx — no Node needed. To edit the console itself, run it with hot reload
instead:

```bash
cd dev && npm install && npm run dev
```

Port 5173 is required rather than convenient — it is one of the two origins
`CORS_ORIGINS` allows, and `file://` sends `Origin: null` and is refused. See
[`dev/README.md`](dev/README.md).

## Layout

```
app/api/v1/        route handlers, one module per resource
app/services/      business logic and orchestration
app/repositories/  database access, one per table
app/models/        SQLModel tables
app/schemas/       pydantic request and response models
app/core/          security primitives, exceptions, DI dependencies
database/          schema.sql — tables, triggers, indexes, seed roles
dev/               React console
```

Routes talk to services, services talk to repositories. No route touches a
repository directly.

## Known limitations

- **Blocking a device is advisory, not a barrier.** The device identity is a
  hash of the `User-Agent`, which the client chooses. Blocking revokes the token
  families bound to that device, so a live session on it dies immediately — but
  anyone holding the password can log in again under a different `User-Agent` and
  will be recorded as a new, unblocked device. Stopping that needs a device
  identifier the client cannot set.

- **No migration tool.** `database/schema.sql` is the only definition, so schema
  changes have to be applied by hand everywhere.
- **Per-IP limits need a deployment that exposes the real client IP.** See
  "Client IP and proxies" below. Under `docker compose` every request arrives from
  the Docker gateway, so the per-IP limits on login and registration apply to all
  users combined rather than per user.
- **Tests share the configured database** and leave data behind; they are not safe
  to run in parallel.
- **Access tokens survive revocation** until they expire, at most
  `ACCESS_TOKEN_EXPIRE_MINUTES`. Only refresh tokens are revoked immediately.
