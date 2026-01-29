@echo off
setlocal enabledelayedexpansion

:: ========================================================
::  R6 Siege Match Stats Analyzer - Interface Web
:: ========================================================

:: Changer vers le repertoire du script
cd /d "%~dp0"

title R6 Siege Match Stats Analyzer

:: Verification de Python 3.12
py -3.12 --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3.12
    echo [OK] Utilisation de Python 3.12
    goto :check_flask
)

:: Fallback sur python par defaut
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Installez Python depuis https://www.python.org/downloads/
    echo OU executez install_requirements.bat
    echo.
    pause
    exit /b 1
)
set PYTHON_CMD=python

:check_flask

:: Verification de Flask
%PYTHON_CMD% -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Flask n'est pas installe. Installation en cours...
    echo.
    %PYTHON_CMD% -m pip install flask
    echo.
)

:: Verification de pandas et openpyxl
%PYTHON_CMD% -c "import pandas; import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installation des dependances...
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt
    echo.
)

cls
echo ========================================================
echo  R6 Siege Match Stats Analyzer - Interface Web
echo ========================================================
echo.
echo  L'interface web va s'ouvrir dans votre navigateur
echo.
echo  URL: http://localhost:5000
echo.
echo  Appuyez sur Ctrl+C pour arreter le serveur
echo ========================================================
echo.
echo Demarrage du serveur...
echo.

:: Attendre 2 secondes puis ouvrir le navigateur
start /B timeout /t 2 /nobreak >nul && start http://localhost:5000

:: Lancer l'application Flask
%PYTHON_CMD% web\app.py

pause
