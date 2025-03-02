.PHONY: run run-docker build-docker run-docker-compose

# Menjalankan aplikasi Flask secara langsung
run:
	FLASK_APP=main.py FLASK_ENV=development flask run

# Membangun image Docker
build-docker:
	docker build -t jira-automation .

# Menjalankan container Docker secara langsung
run-docker:
	docker run -p 8000:8000 --env-file .env jira-automation

# Menjalankan aplikasi dengan Docker Compose
run-docker-compose:
	docker-compose up -d

stop-docker-compose:
	docker-compose down