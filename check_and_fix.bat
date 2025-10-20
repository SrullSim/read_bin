@echo off
rem run_checks.bat - apply formatters and run static checks for the project

rem Use UTF-8 output
chcp 65001 >nul

rem find python executable (try python then py)
where python >nul 2>&1
if %ERRORLEVEL%==0 (
  set "PY=python"
) else (
  where py >nul 2>&1
  if %ERRORLEVEL%==0 (
    set "PY=py"
  ) else (
    echo Python not found on PATH. Install Python and required tools first.
    exit /b 1
  )
)

rem ensure script runs from repository root (location of this .bat)
cd /d "%~dp0"

set "EXITCODE=0"

echo.
echo === Running isort (auto-fix) ===
%PY% -m isort --profile black .
if %ERRORLEVEL% neq 0 (
  echo isort returned non-zero but continuing...
)

echo.
echo === Running black (auto-fix) ===
%PY% -m black .
if %ERRORLEVEL% neq 0 (
  echo black returned non-zero but continuing...
)

echo.
echo === Running mypy (type check) ===
%PY% -m mypy .
if %ERRORLEVEL% neq 0 (
  echo mypy reported issues.
  set "EXITCODE=1"
)

echo.
echo === Running pylint (lint) ===
rem adjust the targets below to match your packages/modules
%PY% -m pylint business_logic GUI file_handler map logger tests
if %ERRORLEVEL% neq 0 (
  echo pylint reported issues.
  set "EXITCODE=1"
)

echo.
if "%EXITCODE%"=="0" (
  echo All checks passed.
) else (
  echo Some checks failed. Exit code: %EXITCODE%
)

exit /b %EXITCODE%