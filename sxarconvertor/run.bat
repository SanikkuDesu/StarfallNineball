@echo off
title ZIP to SXAR Converter

if "%~1"=="" (
    echo Please drag and drop a ZIP file onto this batch file.
    pause
    exit /b 1
)

echo Converting: %~nx1
echo.

python "%~dp0zip_to_sxar.py" "%~1"

if errorlevel 1 (
    echo.
    echo Conversion failed!
    pause
) else (
    echo.
    echo Conversion successful!
    timeout /t 3
)