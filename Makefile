# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
#  COMANDOS DE DESARROLLO - SFQ MATRICULAS
#  Usar con: make <comando>
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

.PHONY: build up down restart logs shell migrate makemigrations collectstatic createsuperuser

# Construir e iniciar contenedores
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart web

# Ver logs
logs:
	docker-compose logs -f web

# Entrar al contenedor
shell:
	docker-compose exec web python manage.py shell

# Base de datos
migrate:
	docker-compose exec web python manage.py migrate

makemigrations:
	docker-compose exec web python manage.py makemigrations

# Archivos estÃ¡ticos
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput

# Crear superusuario
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Cargar datos iniciales
loaddata:
	docker-compose exec web python manage.py loaddata fixtures/initial_data.json
