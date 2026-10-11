@echo off
setlocal
if exist "%~dp0runtime\pythonw.exe" (
  start "" "%~dp0runtime\pythonw.exe" -X utf8 "%~dp0app\server.py" %*
  exit /b
)
if defined ATOLYE_ROOT if exist "%ATOLYE_ROOT%\01_TASINABILIR\PythonMini\pythonw.exe" (
  start "" "%ATOLYE_ROOT%\01_TASINABILIR\PythonMini\pythonw.exe" -X utf8 "%~dp0app\server.py" --root "%ATOLYE_ROOT%"
  exit /b
)
python -X utf8 "%~dp0app\server.py" %*
if errorlevel 1 pause
