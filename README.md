# Baker Tilly Liberia - Timesheet Management System

A professional timesheet management application built for Baker Tilly Liberia to track employee hours, manage projects/clients, and streamline the approval workflow.

## Features

- **Authentication & Authorization** – Role-based access (Admin, Manager, Staff)
- **Timesheet Entry** – Daily time tracking with project/client assignment
- **Approval Workflow** – Submit → Review → Approve/Reject cycle
- **Project & Client Management** – CRUD operations for projects and clients
- **Dashboard & Reporting** – Overview of hours, utilization, and billing
- **User Management** – Admin panel for managing staff accounts

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask, SQLAlchemy, Flask-Login |
| Frontend | React 18, TypeScript, Tailwind CSS |
| Database | SQLite (development), PostgreSQL (production) |
| Testing | pytest (backend), Jest + React Testing Library (frontend) |

## Project Structure

```
Baker-Tilly-Audit/
├── backend/
│   ├── app/
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoint blueprints
│   │   ├── services/      # Business logic layer
│   │   └── utils/         # Helpers and utilities
│   ├── tests/
│   │   ├── unit/          # Unit tests
│   │   └── integration/   # Integration tests
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── src/
│   │   ├── components/    # Reusable UI components
│   │   ├── pages/         # Page-level components
│   │   ├── services/      # API client services
│   │   └── utils/         # Frontend utilities
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

The API server starts at `http://localhost:5000`.

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

The frontend dev server starts at `http://localhost:3000`.

### Running Tests

**Backend:**
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

**Frontend:**
```bash
cd frontend
npm test -- --coverage
```

## Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@bakertilly.com.lr | admin123 |

## License

Proprietary – Baker Tilly Liberia © 2024
