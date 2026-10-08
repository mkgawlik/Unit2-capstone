import os
import re
import sqlite3
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from google import genai
from google.genai import types


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
DATABASE_PATHS = [
    BASE_DIR / "data" / "database.sqlite",
    BASE_DIR / "data" / "documents" / "database.sqlite",
    BASE_DIR / "database.sqlite",
]

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing from your .env file.")

client = genai.Client(api_key=API_KEY)


def find_database() -> Path:
    for path in DATABASE_PATHS:
        if path.is_file():
            return path

    raise FileNotFoundError(
        "database.sqlite was not found in the expected project folders."
    )


def get_schema(database_path: Path) -> str:
    with sqlite3.connect(database_path) as connection:
        tables = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()

        schema = []

        for (table_name,) in tables:
            columns = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

            column_names = ", ".join(
                column[1] for column in columns
            )

            schema.append(
                f"- {table_name}({column_names})"
            )

        return "\n".join(schema)


def ask_gemini(prompt: str, max_tokens: int) -> tuple[str, Any]:
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=max_tokens,
        ),
    )

    return response.text.strip(), response.usage_metadata


def usage_value(usage: Any, field: str) -> int:
    return int(getattr(usage, field, 0) or 0)


def clean_sql(text: str) -> str:
    sql = text.strip()

    fenced_sql = re.search(
        r"```(?:sql)?\s*(.*?)```",
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )

    if fenced_sql:
        sql = fenced_sql.group(1).strip()

    first_sql_word = re.search(
        r"\b(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE,
    )

    if first_sql_word:
        sql = sql[first_sql_word.start():]

    return sql.rstrip(";").strip()


def validate_sql(query: str) -> dict:
    sql = clean_sql(query)

    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        return {
            "valid": False,
            "reason": "Only SELECT or WITH queries are permitted.",
        }

    if ";" in sql:
        return {
            "valid": False,
            "reason": "Only one SQL statement is permitted.",
        }

    blocked_words = [
        "ALTER",
        "ATTACH",
        "CREATE",
        "DELETE",
        "DROP",
        "INSERT",
        "PRAGMA",
        "REPLACE",
        "TRUNCATE",
        "UPDATE",
        "VACUUM",
    ]

    for word in blocked_words:
        if re.search(rf"\b{word}\b", sql, re.IGNORECASE):
            return {
                "valid": False,
                "reason": f"Blocked keyword: {word}",
            }

    return {"valid": True, "reason": "OK"}


def generate_sql(query: str, schema: str) -> dict:
    prompt = f"""
You are a SQLite query generator.

Actual database schema:
{schema}

User question:
{query}

Generate one read-only SQLite query.

Requirements:
- Use only the exact table and column names shown in the schema.
- Use SQLite-compatible syntax.
- For monthly revenue trends, group revenue by month.
- For customer churn rate, calculate the rate from the actual churn fields.
- For Q4 regional performance, filter for Q4 and compare regions.
- Return only SQL beginning with SELECT or WITH.
- Do not return Markdown or explanations.
""".strip()

    text, usage = ask_gemini(prompt, 300)

    return {
        "sql": clean_sql(text),
        "input_tokens": usage_value(
            usage,
            "prompt_token_count",
        ),
        "output_tokens": usage_value(
            usage,
            "candidates_token_count",
        ),
    }


def interpret_results(
    query: str,
    sql: str,
    columns: list[str],
    rows: list[tuple],
) -> dict:
    prompt = f"""
The user asked: {query}

SQL query:
{sql}

Query results:
Columns: {columns}
Rows: {rows[:20]}

Provide a clear, concise answer using only these results.
Do not invent facts or repeat the SQL query.
""".strip()

    text, usage = ask_gemini(prompt, 500)

    return {
        "answer": text,
        "input_tokens": usage_value(
            usage,
            "prompt_token_count",
        ),
        "output_tokens": usage_value(
            usage,
            "candidates_token_count",
        ),
    }


def run(query: str) -> dict:
    database_path = find_database()
    schema = get_schema(database_path)

    sql_result = generate_sql(query, schema)
    sql = sql_result["sql"]
    validation = validate_sql(sql)

    if not validation["valid"]:
        return {
            "answer": f"Query blocked: {validation['reason']}",
            "sql": sql,
            "rows": [],
            "validation": "FAILED",
            "input_tokens": sql_result["input_tokens"],
            "output_tokens": sql_result["output_tokens"],
        }

    try:
        with sqlite3.connect(database_path) as connection:
            cursor = connection.execute(sql)
            columns = [
                description[0]
                for description in cursor.description or []
            ]
            rows = cursor.fetchmany(100)

        interpretation = interpret_results(
            query,
            sql,
            columns,
            rows,
        )

        return {
            "answer": interpretation["answer"],
            "sql": sql,
            "columns": columns,
            "rows": rows,
            "validation": "PASSED",
            "input_tokens": (
                sql_result["input_tokens"]
                + interpretation["input_tokens"]
            ),
            "output_tokens": (
                sql_result["output_tokens"]
                + interpretation["output_tokens"]
            ),
        }

    except Exception as error:
        return {
            "answer": f"Query execution failed: {error}",
            "sql": sql,
            "columns": [],
            "rows": [],
            "validation": "ERROR",
            "input_tokens": sql_result["input_tokens"],
            "output_tokens": sql_result["output_tokens"],
        }


if __name__ == "__main__":
    question = " ".join(sys.argv[1:]).strip()

    if not question:
        question = input("Enter your question: ").strip()

    result = run(question)

    print("\nAnswer:")
    print(result["answer"])
    print("\nSQL:")
    print(result["sql"])
    print(f"\nValidation: {result['validation']}")
