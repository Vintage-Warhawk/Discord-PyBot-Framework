@echo off

:TOKEN_PROMPT
set /p DISCORD_TOKEN="Please enter your Discord Token: "
echo Using token: %DISCORD_TOKEN%
CHOICE /C YNE /M "Do you want to continue (Y), exit (N), or change token (E)?"

IF ERRORLEVEL 3 GOTO TOKEN_PROMPT
IF ERRORLEVEL 2 GOTO EXIT_ACTION
IF ERRORLEVEL 1 GOTO CONTINUE_ACTION

:CONTINUE_ACTION
echo Creating Discord bot...
docker compose up -d --build
docker compose up -d --build

IF ERRORLEVEL 1 (
    echo An error occurred while building or starting the container.
    pause
    goto EXIT_ACTION
)

echo Done. Press any key to exit.
pause
GOTO :EOF

:EXIT_ACTION
echo Exiting.
exit /b

pause