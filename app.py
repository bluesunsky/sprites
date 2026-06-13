from flask import Flask, render_template, request, jsonify
import json
import sqlite3

app = Flask(__name__)

SPRITES = [
    ("water", "rare"),
    ("earth", "rare"),
    ("fire", "rare"),
    ("duck", "rare"),
    ("ghost", "epic"),
    ("dream", "legendary"),
    ("demon", "epic"),
    ("punk", "legendary"),
    ("king", "legendary"),
    ("peanut", "mythic"),
    ("zero", "mythic"),
]

VARIANTES = [
    "",
    "gold",
    "gummy",
    "galaxy"
]

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/init")
def init():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS collection (
            key TEXT PRIMARY KEY,
            possede INTEGER
        )
    """)

    conn.commit()
    conn.close()
    return "DB OK"

@app.route("/")
def index():
    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT key, possede FROM collection")
    rows = {row["key"]: row["possede"] for row in c.fetchall()}

    sprites = []

    for sprite, rarity in SPRITES:
        variantes = []

        for variante in VARIANTES:

            key = f"{sprite}{'_' if variante else ''}{variante}"

            possede = rows.get(key, False)
            if not key.startswith('peanut_'):
              variantes.append({
                "sprite": sprite,
                "nom": variante,
                "key": key,
                "image": f"images/{key}.png",
                "possede": possede,
                "background": f"images/rarity_{rarity}.png",
              })

        sprites.append((sprite, variantes))

    return render_template("index.html", esprits=sprites)

@app.route("/toggle", methods=["POST"])
def toggle():
    data = request.get_json()
    key = data["key"]

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT possede FROM collection WHERE key=?", (key,))
    row = c.fetchone()

    if row is None:
        new_value = 1
        c.execute("INSERT INTO collection (key, possede) VALUES (?, ?)", (key, new_value))
    else:
        new_value = 0 if row["possede"] else 1
        c.execute("UPDATE collection SET possede=? WHERE key=?", (new_value, key))

    conn.commit()
    conn.close()

    return jsonify({"key": key, "value": new_value})

if __name__ == "__main__":
    app.run()