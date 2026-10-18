@echo off
title CineMatch - Smart Movie and OTT Finder
echo =========================================================
echo   Starting CineMatch: Smart Movie and OTT Finder
echo =========================================================
echo Checking and installing dependencies...
python -m pip install -r requirements.txt
echo.
echo Launching CineMatch Web Application...
python -m streamlit run app.py
pause
