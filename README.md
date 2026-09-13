# GymTrac

GymTrac is a full-stack gym workout management web application built as a university project.

It helps gym-goers organize their weekly workout plans, browse a database of exercises, and manage their profile — all with user authentication and an admin panel for managing users and exercises.

## Features

- User authentication (sign up, login, logout) with JWT
- Role-based access control (User and Admin roles; designed to support a future Trainer role)
- User-specific workout plans (one active plan per user, seven weekdays)
- Exercise database with ~60–100 bodybuilding exercises across 10 muscle groups
- Calendar view of the user's weekly plan
- Theme switching (dark gym aesthetic / light theme)
- Admin panel for user and exercise management
- Async backend with FastAPI and SQLAlchemy (async SQLite)

## Technology Stack

### Backend

- Python 3.11
- FastAPI (async web framework)
- SQLAlchemy 2.x with async support (`AsyncSession`)
- SQLite + aiosqlite (async driver)
- Pydantic v2 (request/response validation, settings)
- PyJWT + passlib[bcrypt] (JWT authentication, password hashing)

### Frontend

- React 18
- Vite (build tool + dev server)
- React Router v6 (client-side routing)
- React Context (auth + theme state)
- Plain CSS with CSS custom properties (theming)

## Project Structure

```
GymTrac/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry, lifespan, CORS
│   │   ├── config.py            # Pydantic settings (env vars)
│   │   ├── database.py          # AsyncEngine, session factory, Base
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── exercise.py
│   │   │   └── workout.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── workout.py
│   │   │   └── exercise.py
│   │   ├── routers/             # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── workout.py
│   │   │   ├── exercises.py
│   │   │   └── admin.py
│   │   ├── services/            # Business logic helpers
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   └── seed.py
│   │   └── dependencies.py      # Auth dependencies (get_current_user, require_role)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── main.jsx             # React entry point
│   │   ├── App.jsx              # Router + layout + theme
│   │   ├── api/                 # HTTP client + query helpers
│   │   ├── context/             # AuthContext, ThemeContext
│   │   ├── components/          # Shared UI components
│   │   ├── pages/               # Route page components
│   │   └── styles/              # Global CSS + themes
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── .gitignore
├── .env.example
└── README.md
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
JWT_SECRET_KEY=<random-secret>
JWT_EXPIRATION_MINUTES=1440
DATABASE_URL=sqlite+aiosqlite:///./data/gym_trac.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<secure-password>
```

See `.env.example` for full documentation.

## Database Setup

The database is SQLite (async via aiosqlite). The database file is created automatically on first run in `backend/data/gym_trac.db`.

No manual database setup is required — tables are created on application startup via SQLAlchemy `Base.metadata.create_all`.

## Admin Initialization

The first administrator is created automatically on first startup via `backend/app/services/seed.py`. The seed script reads `ADMIN_USERNAME` and `ADMIN_PASSWORD` from the environment and creates an admin user if one does not already exist. This is idempotent — running the app multiple times will not create duplicate admins.

There is no public admin signup endpoint.

## How to Run Backend

From the `backend/` directory:

```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload (development)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API docs are available at `http://127.0.0.1:8000/docs`.

## How to Run Frontend

From the `frontend/` directory:

```bash
# Install dependencies
npm install

# Run dev server
npm run dev
```

The frontend is available at `http://localhost:5173`.

## Git Workflow

The repository uses the following branches:

- `main` — always deployable; merged from feature branches
- `feature/auth` — authentication (backend + frontend)
- `feature/dashboard` — dashboard page
- `feature/workout` — workout plan CRUD
- `feature/calendar` — calendar page
- `feature/exercises` — exercise database + exercises page
- `feature/admin` — admin panel
- `feature/settings` — settings + theme

Work is done on feature branches branching off `main`. Each feature is merged back to `main` with a merge commit. Feature branches are preserved (not deleted) unless explicitly asked.

Example:

```bash
git checkout main
git checkout -b feature/auth
# ... work ...
git checkout main
git merge feature/auth
```

## Future Expansion Ideas

- Add a Trainer role with plan assignment capabilities
- Add workout logging (sets, reps, weight)
- Add progress charts and personal records
- Add exercise images or video links
- Replace localStorage JWT with httpOnly cookies
- Add Alembic for database migrations
- Add unit/integration tests (pytest + httpx)

## License

This is a university project — see your course guidelines for licensing.
