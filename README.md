# Constellation-Travel

My personal travel agent.

## Backend Prerequisites

- Python 3.12+
- Create and activate a virtual environment:

  ```bash
  python -m venv .venv
  source .venv/bin/activate
  ```

- Install dependencies: `pip install -r agent/requirements.txt`

## Frontend Prerequisites

- Node.js 18+
- Install dependencies: `cd frontend && npm install`

## Environment Variables

The agent relies on the following variables, which must be set in your
shell (or a `.env` file) before running tests or the agent itself:

- `RAPIDAPI_KIWI_KEY` – RapidAPI key for Kiwi flight search
- `AMADEUS_API_KEY` – Amadeus API key
- `AMADEUS_API_SECRET` – Amadeus API secret

Example setup:

```bash
export RAPIDAPI_KIWI_KEY=your_rapidapi_key
export AMADEUS_API_KEY=your_amadeus_key
export AMADEUS_API_SECRET=your_amadeus_secret
```

## Useful Commands

Run tests:

```bash
pytest
```

Run the travel agent:

```bash
python agent/travel_deal_agent.py --config config/request.json
```

Run the development server:

```bash
cd frontend
npm run dev
```
