REGISTRY ?= docker.io/CHANGEME
SHA := $(shell git rev-parse --short HEAD 2>/dev/null || echo dev)
IMAGE := $(REGISTRY)/notes-app

build:
	docker build -t $(IMAGE):$(SHA) -t $(IMAGE):latest .
up:
	docker compose up -d --build
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build
push: build
	docker push $(IMAGE):$(SHA) && docker push $(IMAGE):latest
clean:
	docker compose down -v
