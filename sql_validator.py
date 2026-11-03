import sqlglot
from sqlglot import exp


class SQLValidationError(ValueError):
    pass


def validate_sql(sql):
    if not isinstance(sql, str) or not sql.strip():
        raise SQLValidationError("SQL query is empty.")

    try:
        statements = sqlglot.parse(sql, read="sqlite")
    except Exception as exc:
        raise SQLValidationError(f"SQL syntax error: {exc}") from exc

    statements = [
        statement for statement in statements
        if statement is not None
    ]

    if len(statements) != 1:
        raise SQLValidationError("Only one SQL statement is allowed.")

    tree = statements[0]

    # Allow SELECT queries only.
    if not isinstance(tree, exp.Select):
        raise SQLValidationError(
            "Only SELECT queries are allowed. "
            "Changes to data or schema are blocked."
        )

    # Block prohibited SQL operations.
    forbidden = (
        exp.Insert,
        exp.Update,
        exp.Delete,
        exp.Drop,
        exp.Alter,
        exp.Create,
        exp.Command,
    )

    if any(tree.find(kind) for kind in forbidden):
        raise SQLValidationError(
            "The query contains a prohibited SQL operation."
        )

    # Block access to SQLite internal tables.
    for table in tree.find_all(exp.Table):
        if table.name.lower().startswith("sqlite_"):
            raise SQLValidationError(
                "Access to SQLite internal tables is blocked."
            )

    # Block extension-loading functions.
    for func in tree.find_all(exp.Func):
        if func.sql_name().upper() == "LOAD_EXTENSION":
            raise SQLValidationError(
                "That SQL function is blocked."
            )

    # Return the validated SQL string.
    return tree.sql(dialect="sqlite")