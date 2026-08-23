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

Seed the curated demo inventory and provision the first admin account from trusted local commands:

```powershell
python -m app.seed
python -m app.bootstrap_admin
```

Public registration always creates a standard user. This avoids a user elevating their own access in production.

Use those administrator credentials from the new **Administrator sign in** link on the login screen. The administrator dashboard can add, edit, restock, and delete vehicles, and its **Users** tab can manage customer roles, verification status, and accounts. Inventory changes are stored in the shared database, so they appear for customer accounts on their next inventory request.

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Visit `http://localhost:5173` (or the port shown in terminal).

For PostgreSQL, start the provided local container with `docker compose up -d`, then set `DATABASE_URL` to `postgresql+psycopg://apex:change-me-before-deploying@localhost:5432/apex_motors`. The required driver and Alembic migration tooling are included in `requirements.txt`. Run `alembic upgrade head` from `backend` before production startup.

## Deployment

### Frontend (Vercel)

The frontend is configured for Vercel deployment. To deploy:

1. Push your repository to GitHub
2. Import the project in Vercel
3. Set the `VITE_API_URL` environment variable to your deployed backend URL
4. Deploy

### Backend (Vercel)

The backend includes a `vercel.json` configuration for deployment. To deploy:

1. Push your repository to GitHub
2. Import the backend directory as a separate Vercel project
3. Set environment variables:
   - `DATABASE_URL`: PostgreSQL connection string (recommended for production)
   - `JWT_SECRET`: Secure random string for token signing
4. Deploy

Note: For production, use PostgreSQL instead of SQLite for better performance and reliability.

## Test report

```powershell
cd backend
python -m pytest
```

The suite covers registration/login, duplicate accounts, public role escalation prevention, authorization, vehicle CRUD, search filters, restocking, purchasing, and zero-stock rejection. Frontend tests validate disabled purchases and administrator controls.

## TDD approach

Work is organised around small feature slices: write an executable expectation, run it to see it fail, implement only what makes it pass, then refactor. Future commits should retain this narrative—especially for authentication, inventory behaviour, and authorization.

## My AI Usage

I used multiple AI tools throughout this project to accelerate development while maintaining code quality and architectural integrity.

### Tools Used

- **Cascade (Cognition)**: Primary AI assistant used for debugging, code implementation, and troubleshooting. Used extensively for:
  - Diagnosing and fixing CORS configuration issues between frontend and backend
  - Creating environment configuration files (.env) for both frontend and backend
  - Implementing backend API endpoints and database models
  - Writing and debugging test cases
  - Managing development server processes
  - Analyzing project structure and identifying missing components

- **ChatGPT**: Used for initial project planning, architecture decisions, and understanding the TDD Kata requirements. Helped clarify the assignment scope and choose the technology stack (FastAPI + React).

- **Codex**: Used for scaffolding initial boilerplate code, generating test case templates, and implementing repetitive UI components.

### How AI Impacted My Workflow

AI tools significantly accelerated the development process by:
- Reducing time spent on boilerplate code and repetitive tasks
- Providing immediate debugging assistance when encountering runtime errors
- Suggesting best practices for API design and security implementation
- Helping maintain TDD discipline by generating test cases before implementation

However, all architectural decisions, security implementations, and core business logic remained under my direct control. AI-generated code was thoroughly reviewed, tested, and adapted to fit the project's specific requirements and coding standards.

### AI Co-authorship

Commits where AI tools were used include the appropriate co-authorship trailers following the format:
```
Co-authored-by: AI Tool Name <ai@users.noreply.github.com>
```

This ensures transparency about AI usage while maintaining accountability for the codebase.

## Required deliverables

- `PROMPTS.md` preserves the available raw chat/prompt record.
- Run the test command above before submission and add its terminal output or CI link to the submission.
- Capture final UI screenshots once test accounts/data are populated.
- Publish the repository and optionally deploy the frontend and API separately.
