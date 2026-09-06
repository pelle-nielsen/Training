@echo off
REM Runs the daily paper-trading check. Registered as a Windows Scheduled Task
REM (see README's "Automation" section). Logs everything to data\paper_trade_log.csv
REM plus this script's own stdout/stderr redirected to data\scheduled_run.log.

cd /d "%~dp0.."
call .venv\Scripts\activate.bat
python scripts\run_paper_trade.py --ticker AAPL --qty 5 --live >> data\scheduled_run.log 2>&1
