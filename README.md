# Mini Calendar

A local calendar app built with FastAPI and React, preloaded with all 104 FIFA World Cup 2026 matches.

## Stack

- **Backend** — FastAPI, SQLAlchemy, SQLite
- **Frontend** — React, TypeScript, Vite, FullCalendar
- **Data** — FIFA public API via `fetch_matches.py`

## Getting started

### Backend

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Runs on `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:3000`.

## Import World Cup matches

The repo includes `games.json` with Brazil's group stage games. To fetch all 104 matches:

```bash
python fetch_matches.py --all   # fetch all teams
python fetch_matches.py --country ARG  # fetch a specific country
```

Then POST them to the running API:

```bash
python import_games.py
```

## Features

- Create, edit, delete, and cancel events
- Click any day to create an event
- Dark / light theme toggle (remembers your preference)
- REST API at `/api/events`
