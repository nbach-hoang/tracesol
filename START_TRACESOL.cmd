@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Start-TraceSol.ps1"
if errorlevel 1 pause
