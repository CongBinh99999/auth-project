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
docker compose up -d
```

The API is at http://localhost:8000, Swagger UI at http://localhost:8000/docs.
PostgreSQL is published on **5433** rather than 5432, so it does not collide with a
Postgres already installed on the host.

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

- **No migration tool.** `database/schema.sql` is the only definition, so schema
  changes have to be applied by hand everywhere.
- **`X-Forwarded-For` is not handled.** `request.client.host` is taken as the
  client IP, so behind a reverse proxy every request shares one address and the
  per-IP limits on login and registration stop discriminating.
- **Tests share the configured database** and leave data behind; they are not safe
  to run in parallel.
- **No `/reset-password` page.** The password reset email links to a frontend
  route that does not exist yet; the endpoint works for any client holding the token.
- **Access tokens survive revocation** until they expire, at most
  `ACCESS_TOKEN_EXPIRE_MINUTES`. Only refresh tokens are revoked immediately.
