@echo off
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0ExtractApprovers.ps1"
pause