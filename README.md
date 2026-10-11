# Veterinary Management SQL Studio — SQLite Edition

A local React + Vite frontend, FastAPI backend, and SQLite database. No Oracle/database server required.

## Requirements
- Python 3.10+
- Node.js LTS (npm included)

## Windows / VS Code setup

### Terminal 1 — backend
```powershell
cd backend
py -m venv .venv
# If activation is blocked: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Keep this terminal running.

### Terminal 2 — frontend
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open the Vite URL shown (usually http://127.0.0.1:5173).

## Useful URLs
- Website: http://127.0.0.1:5173
- API health: http://127.0.0.1:8000/api/health
- Database row counts: http://127.0.0.1:8000/api/db-status
- API docs: http://127.0.0.1:8000/docs

On first backend startup, `backend/veterinary.db` is created and seeded with sample records. Seed data is inserted only if the Owners table is empty. Delete the database file only if you intentionally want to reset all data.

## Tables and seed data
- `VMS26_Owners`: 6 owners
- `VMS26_Pets`: 8 pets
- `VMS26_Veterinarians`: 4 vets
- `VMS26_Appointments`: 8 appointments
- `VMS26_Treatments`: 3 treatments
- `VMS26_Payments`: 6 payments

Run one SQLite statement at a time. Supported statements include SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, DROP and PRAGMA. SQLite syntax differs from Oracle syntax. Successful DML changes are committed. This project is for local learning; don't expose the SQL editor publicly without authentication and tighter access controls.
