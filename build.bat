:: File: build.bat
:: Maintainer: Vintage Warhawk
:: Last Edit: 2025-11-17
::
:: Description:
:: This batch script builds and starts the Discord bot Docker container on Windows.
:: It prompts the user for their Discord bot token, sets it as an environment variable,
:: and runs docker-compose to build and launch the container. Includes basic error handling.

@echo off

:: -----------------------------
:: Prompt for Discord Token
:: -----------------------------
:TOKEN_PROMPT
set /p DISCORD_TOKEN="Please enter your Discord Token: "
echo Using token: %DISCORD_TOKEN%

CHOICE /C YNE /M "Do you want to continue (Y), exit (N), or change token (E)?"

:: Handle user choice
IF ERRORLEVEL 3 GOTO TOKEN_PROMPT  :: E - Change token
IF ERRORLEVEL 2 GOTO EXIT_ACTION   :: N - Exit
IF ERRORLEVEL 1 GOTO CONTINUE_ACTION  :: Y - Continue

:: -----------------------------
:: Continue and build container
:: -----------------------------
:CONTINUE_ACTION
echo Creating Discord bot...
docker compose up -d --build
docker compose up -d --build

:: Check for errors in build or startup
IF ERRORLEVEL 1 (
    echo An error occurred while building or starting the container.
    pause
    goto EXIT_ACTION
)

echo Done. Press any key to exit.
pause
GOTO :EOF

:: -----------------------------
:: Exit action
:: -----------------------------
:EXIT_ACTION
echo Exiting.
exit /b

pause
