lint:
	ruff format .
	ruff check --fix .

build:
	docker build -t spanish_bot:latest .

up:
	docker-compose up -d

down:
	docker-compose down

up_tdb:
	docker run -d -p "5431:5432" --rm --name tdb -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=tdb postgres

down_tdb:
	docker stop tdb