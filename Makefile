lint:
	ruff format .
	ruff check --fix .

up:
	docker-compose up -d

down:
	docker-compose down
