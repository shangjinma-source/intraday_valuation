@echo off
cd /d E:\Git\valuation_grid
call .venv\Scripts\activate.bat
python cron_job.py
echo %date% %time% >> cron_log.txt
