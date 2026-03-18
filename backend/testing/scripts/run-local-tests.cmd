@echo off
setlocal

set SCRIPT_DIR=%~dp0
for %%I in ("%SCRIPT_DIR%..\..") do set BACKEND_DIR=%%~fI

cd /d "%BACKEND_DIR%"

if "%TEST_DATABASE_URL%"=="" set TEST_DATABASE_URL=sqlite:///./tests/.tmp/test.db

set PYTHON_BIN=python
if exist ".venv\Scripts\python.exe" set PYTHON_BIN=.venv\Scripts\python.exe
if exist ".venv\bin\python" set PYTHON_BIN=.venv\bin\python

"%PYTHON_BIN%" -m pytest -m "not integration" %*

endlocal
