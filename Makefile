lint:
	ruff format .
	ruff check --fix .

build:
	docker build -t rssku/spanish-tg-bot:latest .

up:
	docker-compose up -d

down:
	docker-compose down

push:
	docker push rssku/spanish-tg-bot:latest

pull:
	docker pull rssku/spanish-tg-bot:latest

up_tdb:
	docker run -d -p "5431:5432" --rm --name tdb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tdb postgres

down_tdb:
	docker stop tdb