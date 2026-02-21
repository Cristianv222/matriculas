@echo off
echo ========================================
echo  SFQ MATRICULAS - Inicio rapido
echo ========================================
echo.

IF NOT EXIST .env (
    echo [!] Copiando .env de ejemplo...
    copy .env.example .env
    echo [!] Por favor edita el archivo .env antes de continuar
    pause
    exit
)

echo [1] Construyendo contenedores...
docker-compose build

echo [2] Iniciando servicios...
docker-compose up -d

echo [3] Esperando a que la DB este lista...
timeout /t 8 /nobreak > NUL

echo [4] Aplicando migraciones...
docker-compose exec web python manage.py migrate

echo.
echo ========================================
echo  SISTEMA LISTO
echo  URL: http://localhost:8000
echo  Admin: http://localhost:8000/admin
echo ========================================
echo.
pause
