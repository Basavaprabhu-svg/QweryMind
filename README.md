# QueryMind — AI-Powered Voice-to-SQL Assistant

QueryMind lets a user ask a question in plain English or by voice, generates SQLite SQL using OpenRouter, validates the SQL, executes it against a sample database, and explains the returned results.

## Features
- Voice input through the browser Speech Recognition API (browser/permission dependent)
- Natural-language-to-SQL generation
- SQL editor and manual query execution
- SQLGlot validation: one `SELECT` statement only
- SQLite read-only connection and `query_only` safeguard
- Results table and CSV download
- AI-generated plain-language explanation
- Database schema explorer and recent query history
- Sample EMPLOYEE, CUSTOMER, and SALES data, relationships, and indexes

## Setup (Python 3.10+ recommended)
1. Open this folder in VS Code.
2. Create and activate a virtual environment:
   - Windows: `py -m venv .venv`
   - Windows PowerShell: `.venv\\Scripts\\Activate.ps1`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`, then paste your OpenRouter API key into `.env`.
5. Run: `python app.py`
6. Open `http://127.0.0.1:5000` in a browser.

Do not share your API key or commit `.env` to GitHub.

## Try these questions
- Show all employees in Engineering.
- What is the average salary by department?
- Which employees earn more than 70000?
- Show total sales by customer.
- Which customers have total sales greater than 10000?
- Show the top three sales by amount.
- How many employees are in each department?

## Important safety note
The backend accepts one parsed SELECT statement only, blocks known write/schema operations, and executes against a read-only SQLite connection. This is a student demo, not a hardened production security boundary. Keep the database limited to trusted sample data.

## Main files
- `app.py`: Flask routes and request flow
- `ai_service.py`: OpenRouter SQL generation and result explanation
- `sql_validator.py`: SQL parsing and safety checks
- `database.py`: schema, read-only execution, and history
- `database.sql`: tables, relationships, indexes, and sample data
- `templates/index.html`, `static/style.css`, `static/script.js`: interface
