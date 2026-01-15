IMAGE=fintext-harvester:latest
CONTAINER=fintext-harvester
.PHONY: build up down logs sh run-once
build: ; docker compose build
up: ; docker compose up -d
down: ; docker compose down
logs: ; docker logs -f $(CONTAINER)
sh: ; docker exec -it $(CONTAINER) bash
run-once:
\tdocker run --rm --name harvester-once \\
\t  --env-file .env \\
\t  -v $$PWD/data:/app/data -v $$PWD/logs:/app/logs -v $$PWD/config:/app/config:ro \\
\t  $(IMAGE) /usr/bin/env bash -lc "python /app/scripts/run_all.py && ls -lah /app/data/bronze"
