@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..\..") do set BACKEND_DIR=%%~fI
set COMPOSE_FILE=%BACKEND_DIR%\testing\docker-compose.test.yml

cd /d "%BACKEND_DIR%"

docker compose -f "%COMPOSE_FILE%" up --build --abort-on-container-exit --exit-code-from tests
set TEST_EXIT=%ERRORLEVEL%

docker compose -f "%COMPOSE_FILE%" down -v --remove-orphans >nul 2>nul

exit /b %TEST_EXIT%

