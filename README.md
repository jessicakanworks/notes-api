# notes-api

A small **Flask + PostgreSQL + Redis** notes API packaged for production: a hardened multi-stage Dockerfile, a Compose stack for local and server use, and a Makefile that builds and publishes the image to a registry.

## What's here
| File | Purpose |
|---|---|
| `app/` | Flask API (`/notes` CRUD, `/healthz`), Redis cache for GET, PostgreSQL storage |
| `Dockerfile` | multi-stage, non-root user, pinned base, healthcheck, small final image |
| `docker-compose.yml` | app + postgres + redis with volumes, healthchecks, env file |
| `docker-compose.dev.yml` | bind-mount + hot reload for development |
| `.dockerignore` | keeps secrets and junk out of the build context |
| `Makefile` | build / run / push shortcuts |

## Run it
```bash
cp .env.example .env
docker compose up -d --build
curl -s localhost:8000/healthz
curl -s -X POST localhost:8000/notes -H 'content-type: application/json' -d '{"title":"first","body":"hello"}'
curl -s localhost:8000/notes
```

## Push to a registry
```bash
docker login                                    # Docker Hub
make push REGISTRY=docker.io/<username>          # tags :latest and :<git sha>
# or a private registry
make push REGISTRY=registry.example.com/team
```

## Things I made sure of
- Multi-stage build: build deps in one stage, copy only the virtualenv into a slim runtime image (≈ 60 MB vs 1 GB).
- Runs as UID 10001, read-only filesystem compatible, `HEALTHCHECK` wired to `/healthz`.
- Config only through environment variables (12-factor); secrets never baked into the image.
- Named volumes for data so `docker compose down` does not lose the database.
