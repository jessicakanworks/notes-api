import json, os
from flask import Flask, jsonify, request
import psycopg, redis

app = Flask(__name__)
DB_URL = os.environ["DATABASE_URL"]
cache = redis.Redis.from_url(os.environ.get("REDIS_URL", "redis://redis:6379/0"))

def db():
    return psycopg.connect(DB_URL, autocommit=True)

def init_db():
    with db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS notes (id SERIAL PRIMARY KEY, title TEXT NOT NULL, body TEXT, created_at TIMESTAMPTZ DEFAULT now())")

@app.get("/healthz")
def healthz():
    try:
        with db() as conn: conn.execute("SELECT 1")
        cache.ping()
        return jsonify(status="ok")
    except Exception as e:
        return jsonify(status="degraded", error=str(e)), 503

@app.get("/notes")
def list_notes():
    cached = cache.get("notes:all")
    if cached:
        return app.response_class(cached, mimetype="application/json")
    with db() as conn:
        rows = conn.execute("SELECT id, title, body, created_at FROM notes ORDER BY id DESC").fetchall()
    data = json.dumps([{"id": r[0], "title": r[1], "body": r[2], "created_at": r[3].isoformat()} for r in rows])
    cache.set("notes:all", data, ex=30)
    return app.response_class(data, mimetype="application/json")

@app.post("/notes")
def create_note():
    payload = request.get_json(force=True)
    with db() as conn:
        row = conn.execute("INSERT INTO notes (title, body) VALUES (%s, %s) RETURNING id", (payload["title"], payload.get("body", ""))).fetchone()
    cache.delete("notes:all")
    return jsonify(id=row[0]), 201

@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    with db() as conn:
        conn.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    cache.delete("notes:all")
    return "", 204

init_db()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
