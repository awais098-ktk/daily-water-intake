@echo off
echo Running database recreation...
python recreate_db.py
if %ERRORLEVEL% EQU 0 (
    echo Database recreation completed successfully.
    echo You can now start the application with 'python run.py'
) else (
    echo Database recreation failed.
    echo Please check the error message above.
)
pause
