@echo off

call venv\Scripts\activate

start "Backend Server" cmd /k "cd backend && uvicorn app.main:app --reload"

start "Frontend Server" cmd /k "cd frontend && npm run dev"