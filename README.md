# ElderCare

Recruitment / customer portal for elder care services.

- **Backend**: FastAPI + SQLAlchemy + SQLite, JWT auth
- **Frontend**: React (Vite) login / register / blank home page

## Structure

```
app/
├─ api/             # routers/views — thin, no business logic here
├─ core/            # settings, security helpers, database
├─ models/          # ORM models
├─ schemas/         # Pydantic schemas
└─ services/        # business logic
tests/              # unit tests, mirrors app structure
frontend/           # React.js SPA
docs/               # diagrams, API contract
.env.example, README.md, requirements.txt
```

## Roles

| role | value | description |
|------|-------|-------------|
| Recruiter | 1 | Recruiter |
| Customer  | 2 | Customer |

## Backend setup

```bash
python -m venv .venv
.\.venv\Scripts\activate          # Windows
pip install -r requirements.txt
Copy-Item .env.example .env       # then edit SECRET_KEY
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Auth endpoints

| Method | Path                 | Description              |
|--------|----------------------|--------------------------|
| POST   | `/api/auth/register` | Create account + token   |
| POST   | `/api/auth/login`    | Email/password login     |

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — login and register pages connect to the backend on `http://localhost:8000`. After login you land on the (blank) home page.

## Tests

```bash
pip install pytest httpx
pytest
```
