@echo off
echo Opening SQLite shell for Water Tracker database...
echo.
echo Available commands:
echo   .tables                    - List all tables
echo   .schema table_name         - Show table structure
echo   SELECT * FROM table_name;  - View table data
echo   .quit                      - Exit
echo.
sqlite3 instance\water_tracker.db
