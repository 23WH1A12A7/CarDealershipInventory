# Apex Motors — Car Dealership Inventory System

A full-stack dealership inventory platform built for the TDD Kata. It combines a refined, responsive React experience with a secure FastAPI REST API, persistent database support, role-based access control, and automated tests.

## Highlights

- JWT-based registration and login with Argon2 password hashing
- User and administrator roles, with protected inventory operations
- Search by make, model, category, and price range
- Stock-safe purchasing: inventory cannot become negative
- Admin vehicle create, update, delete, and restock APIs
- File-backed SQLite for immediate local use; PostgreSQL-ready configuration for deployment
- Modern React + Tailwind SPA with responsive, accessible controls

## Technology

| Layer | Choice |
| --- | --- |
| Frontend | React, Vite, Tailwind CSS, Lucide |
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Authentication | JWT, pwdlib/Argon2 |
| Database | SQLite locally; PostgreSQL in production |
| Tests | Pytest, FastAPI TestClient |

## Run locally

### Backend

```powershell
cd backend
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --port 8000
```

The API documentation is available at `http://localhost:8000/docs`.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`.

For PostgreSQL, start the provided local container with `docker compose up -d`, install a PostgreSQL driver such as `psycopg`, then set `DATABASE_URL` to `postgresql+psycopg://apex:change-me-before-deploying@localhost:5432/apex_motors`.

## Test report

```powershell
cd backend
python -m pytest
```

The initial test suite covers registration and login, invalid credentials, protected vehicle creation and search, purchase stock decrementation, and zero-stock rejection.

## TDD approach

Work is organised around small feature slices: write an executable expectation, run it to see it fail, implement only what makes it pass, then refactor. Future commits should retain this narrative—especially for authentication, inventory behaviour, and authorization.

## My AI Usage

I used ChatGPT and Codex as development assistants. ChatGPT was used to clarify the assignment requirements, choose the architecture, and plan the TDD workflow. Codex was used to scaffold source files, create initial test cases, implement API/UI code, troubleshoot dependency setup, and visually verify the local interface.

AI output was reviewed, adapted, and tested as part of the development process. It accelerated repetitive setup and offered design alternatives, while engineering decisions—such as the architecture, security boundaries, test cases, and final implementation—remained deliberate and reviewable. AI-assisted commits should include the required co-author trailer, for example: `Co-authored-by: Codex <codex@openai.com>`.

## Required deliverables

- `PROMPTS.md` preserves the available raw chat/prompt record.
- Run the test command above before submission and add its terminal output or CI link to the submission.
- Capture final UI screenshots once test accounts/data are populated.
- Publish the repository and optionally deploy the frontend and API separately.

