import os
from openai import OpenAI

MODEL = "openrouter/free"

def _client():
    key = os.getenv("OPENROUTER_API_KEY")

    if not key:
        raise RuntimeError("OPENROUTER_API_KEY is missing. Add it to your .env file.")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        timeout=20.0,
        max_retries=0,
        default_headers={
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "QueryMind"
        }
    )
    

def _chat(prompt, system, max_tokens=700):
    response = _client().chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": system},
                  {"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=max_tokens
    )
    return (response.choices[0].message.content or "").strip()

def generate_sql(question, schema):
    schema_text = "\n".join(
        f"{table['table']}: " + ", ".join(
            f"{col['name']} ({col['type']})" for col in table["columns"]
        ) for table in schema
    )
    result = _chat(
        f"Database schema:\n{schema_text}\n\nUser question: {question}\n\nReturn only one SQLite SELECT query. No markdown, no explanation. Never write or modify data.",
        "You translate natural-language analytics questions into safe SQLite SELECT queries. Use only the supplied tables and columns. Join tables using matching keys. Never return DML, DDL, PRAGMA, or multiple statements.",
        400
    )
    return result.replace("```sql", "").replace("```", "").strip().rstrip(";") + ";"

def explain_results(question, sql, columns, rows):
    try:
        preview = rows[:8]
        return _chat(
            f"User question: {question or 'Manual SQL query'}\nSQL: {sql}\nColumns: {columns}\nFirst rows: {preview}\nTotal rows returned: {len(rows)}\nExplain the result in plain, concise language. If there are no rows, say that no records matched. Do not invent facts.",
            "You explain database query results accurately. Only describe information present in the SQL and returned data. Keep the answer to 2-4 sentences.",
            250
        )
    except Exception:
        if not rows:
            return "The query ran successfully but returned no matching rows."
        return f"The query returned {len(rows)} row(s). Review the table below for the matching records."
