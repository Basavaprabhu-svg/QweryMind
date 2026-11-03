import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from database import init_db, get_schema, run_readonly_query, get_history, save_history
from ai_service import generate_sql, explain_results
from sql_validator import validate_sql, SQLValidationError
import traceback

load_dotenv()
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

init_db()

@app.get("/")
def index():
    return render_template("index.html")

@app.get("/api/schema")
def schema():
    return jsonify(get_schema())

@app.get("/api/history")
def history():
    return jsonify(get_history())

@app.post("/api/validate")
def validate():
    data = request.get_json(silent=True) or {}
    try:
        sql = validate_sql(data.get("sql", ""))
        return jsonify({"valid": True, "sql": sql, "message": "Safe SELECT query."})
    except SQLValidationError as exc:
        return jsonify({"valid": False, "error": str(exc)}), 400

@app.post("/api/execute")
def execute():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()
    sql = data.get("sql", "")
    try:
        safe_sql = validate_sql(sql)
        columns, rows = run_readonly_query(safe_sql)
        explanation = explain_results(question, safe_sql, columns, rows)
        save_history(question or "Manual SQL query", safe_sql, len(rows), "success")
        return jsonify({"sql": safe_sql, "columns": columns, "rows": rows,
                        "row_count": len(rows), "explanation": explanation})
    except (SQLValidationError, ValueError) as exc:
        save_history(question or "Manual SQL query", str(sql), 0, "blocked")
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": f"Query failed: {exc}"}), 400

@app.post("/api/query")
def query():
    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Enter a question first."}), 400

    # Block obvious requests to modify or delete data before calling the AI.
    destructive_words = (
        r"\b(delete|remove|erase|drop|truncate|update|insert|"
        r"alter|destroy|modify)\b"
    )

    if re.search(destructive_words, question, re.IGNORECASE):
        return jsonify({
            "error": (
                "QueryMind is read-only. Requests to delete or modify "
                "data are blocked. Try asking to view or filter records instead."
            )
        }), 400

    try:
        sql = generate_sql(question, get_schema())
        safe_sql = validate_sql(sql)
        columns, rows = run_readonly_query(safe_sql)
        explanation = explain_results(question, safe_sql, columns, rows)

        save_history(question, safe_sql, len(rows), "success")

        return jsonify({
            "sql": safe_sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "explanation": explanation
        })

    except (SQLValidationError, ValueError) as exc:
        save_history(question, "", 0, "blocked")
        return jsonify({"error": str(exc)}), 400

    except Exception as exc:
        print("QUERY ERROR:", repr(exc))
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 502

if __name__ == "__main__":
    app.run(debug=True)
