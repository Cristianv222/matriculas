# Sistema de MatrÃ­culas en LÃ­nea
## Escuela Fiscomisional San Francisco de Quito

### Stack TecnolÃ³gico
- **Backend:** Django 4.2
- **Base de datos:** PostgreSQL 15
- **Contenedores:** Docker + Docker Compose
- **Frontend:** Bootstrap 5

### MÃ³dulos del sistema
| MÃ³dulo | DescripciÃ³n |
|--------|-------------|
| core | Base compartida y utilidades |
| usuarios | AutenticaciÃ³n y roles |
| estudiantes | Ficha del estudiante |
| periodos | AÃ±os lectivos y paralelos |
| matriculas | Flujo principal de matrÃ­cula |
| documentos | GestiÃ³n de requisitos documentales |
| 
otificaciones | ComunicaciÃ³n con representantes |
| eportes | EstadÃ­sticas y exportaciÃ³n |

### Inicio rÃ¡pido

`ash
# 1. Clonar y configurar
cp .env.example .env
# Editar .env con tus datos

# 2. Construir e iniciar
docker-compose build
docker-compose up -d

# 3. Migrar base de datos
docker-compose exec web python manage.py migrate

# 4. Crear superusuario
docker-compose exec web python manage.py createsuperuser

# 5. Acceder
# http://localhost:8000
# http://localhost:8000/admin
`

### Roles del sistema
- **Administrador:** Acceso total al sistema
- **Secretaria:** GestiÃ³n de matrÃ­culas y documentos
- **Representante:** Portal de solicitud de matrÃ­cula
- **Docente:** Consulta de listas de estudiantes
