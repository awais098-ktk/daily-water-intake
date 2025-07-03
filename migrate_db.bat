@echo off
echo Running database migration...
python migrate_db.py
if %ERRORLEVEL% EQU 0 (
    echo Migration completed successfully.
    echo You can now start the application with 'python run.py'
) else (
    echo Migration failed.
    echo Please check the error message above.
)
pause
