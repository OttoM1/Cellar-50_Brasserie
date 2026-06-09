import os, sqlite3, datetime, json, random, string, uuid
from contextlib import contextmanager
from flask import (
    Flask, render_template, request, jsonify,
    session, redirect, url_for, send_from_directory
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(ROOT, "backend", "wine_cellar.db")


server = Flask(
    __name__,
    template_folder=os.path.join(ROOT, "scaffold"),
    static_folder=os.path.join(ROOT, "static"),
)
server.secret_key = os.environ.get("CELLAR50_SECRET", "dev-only-change-in-production")


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



def init_db():
    with get_db() as conn:
        c = conn.cursor()

        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code TEXT UNIQUE,
                event_name TEXT,
                host_name TEXT,
                wine_list_json TEXT,
                created_at TEXT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS tastings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room_code TEXT, user_id TEXT, user_name TEXT,
                wine_name TEXT, date TEXT,
                color TEXT, scent TEXT, flavour TEXT, aftertaste TEXT,
                acidity INTEGER, tannin INTEGER,
                country TEXT, region TEXT, grape TEXT,
                year INTEGER, price INTEGER, score FLOAT
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS wines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, region TEXT, year INTEGER, type TEXT, tags TEXT
            )
        """)

        c.execute("SELECT count(*) FROM wines")
        if c.fetchone()[0] == 0:
            seed_data = [
                ("Château Margaux", "Bordeaux", 2015, "Red", "Oaky,Leather"),
                ("Château d'Issan", "Margaux, Bordeaux", 2022, "Red", "Tobacco, Silk"),
                ("Harlan Estate", "Oakville, Napa Valley", 2021, "Red", "Blackberry, Earthy"),
                ("Ciacci Piccolomini d'Aragona", "Brunello di Montalcino", 2020, "Red", "Licorice, Cocoa"),
                ("Beaulieu Vineyard Georges de Latour", "Napa Valley", 2021, "Red", "Dark Fruit, Polished"),
                ("Château Giscours", "Margaux, Bordeaux", 2022, "Red", "Graphite, Dark Berries"),
                ("Cloudy Bay", "Marlborough", 2022, "White", "Citrus, Grass"),
                ("Dog Point", "Marlborough", 2023, "White", "Citrus, Smoke, Melon"),
                ("Astrolabe", "Marlborough", 2025, "White", "Lime, Green Pepper"),
                ("Clos Henri", "Marlborough", 2025, "White", "Grapefruit, Mineral"),
                ("Simon Family Estate 'Golden Ore'", "Rutherford, Napa", 2022, "White", "Electric, Vibrant"),
                ("Markus Huber Berg EL", "Traisental, Austria", 2024, "White", "Pepper, Lime, Zesty"),
                ("Louis Roederer Brut Nature Rosé", "Champagne, France", 2018, "Sparkling", "Dry, Strawberry, Citrus"),
                ("Nyetimber Blanc de Blancs", "West Sussex, England", 2016, "Sparkling", "Brioche, Lemon Curd"),
                ("Veuve Monsigny", "Champagne, France", "NV", "Sparkling", "Crisp, Apple, Floral"),
                ("Philipponnat Blanc de Noirs", "Champagne, France", 2019, "Sparkling", "Black Cherry, Hazelnut"),
                ("De Margerie Grand Cru Brut", "Bouzy, Champagne", "NV", "Sparkling", "Red Fruit, Delicate"),
                ("Château d'Esclans 'Rock Angel'", "Provence, France", 2024, "Rosé", "Honey, Almond, Mineral"),
                ("M de Minuty", "Côtes de Provence, France", 2024, "Rosé", "Peach, Orange"),
                ("Sancerre 'Le Rabault'", "Loire Valley, France", 2024, "Rosé", "Floral, Spicy"),
                ("Saracina Vineyards Rosé", "Mendocino, California", 2024, "Rosé", "Grapefruit, Intense Saline"),
                ("Pikasi Barbera Rosé", "Vipava Valley, Slovenia", 2024, "Rosé", "Mixed Berries, Juicy"),
            ]
            c.executemany(
                "INSERT INTO wines (name, region, year, type, tags) VALUES (?,?,?,?,?)",
                seed_data,
            )


def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase, k=4))


def require_session(*keys):
    for key in keys:
        if key not in session: return False
    return True



# static assets
@server.route("/components.css")
def serve_css():
    return send_from_directory(ROOT, "components.css", mimetype="text/css")

@server.route("/interface.js")
def serve_js():
    return send_from_directory(ROOT, "interface.js", mimetype="application/javascript")


@server.route("/")
def home():
    return render_template("home.html", active_page="home")

@server.route("/cheatsheet")
def cheatsheet():
    return render_template("cheatsheet.html", active_page="cheatsheet")

@server.route("/basics")
def basics():
    session.clear()
    return render_template("basics.html", active_page="basics")



@server.route("/create_event", methods=["POST"])
def create_event():
    data = request.get_json(force=True)

    if not data.get("eventName") or not data.get("hostName"):
        return jsonify({"status": "error", "message": "Missing event or host name"}), 400
    if not data.get("wines"):
        return jsonify({"status": "error", "message": "Add at least one wine"}), 400

    room_code = generate_room_code()
    user_id = str(uuid.uuid4())

    with get_db() as conn:
        conn.execute(
            "INSERT INTO events (room_code, event_name, host_name, wine_list_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (room_code, data["eventName"], data["hostName"], json.dumps(data["wines"]), str(datetime.date.today())),
        )

    session.update({
        "room_code": room_code, "user_id": user_id,
        "user_name": data["hostName"], "is_host": True,
    })
    return jsonify({"status": "success", "room_code": room_code})


@server.route("/join_event", methods=["POST"])
def join_event():
    data = request.get_json(force=True)
    room_code = (data.get("roomCode") or "").upper().strip()
    guest_name = (data.get("guestName") or "").strip()

    if not room_code or not guest_name:
        return jsonify({"status": "error", "message": "Name and room code required"}), 400

    with get_db() as conn:
        event = conn.execute("SELECT * FROM events WHERE room_code = ?", (room_code,)).fetchone()

    if not event:
        return jsonify({"status": "error", "message": "Room not found"}), 404

    session.update({
        "room_code": room_code,
        "user_id": str(uuid.uuid4()),
        "user_name": guest_name,
        "is_host": False,
    })
    return jsonify({"status": "success"})



@server.route("/tasting")
def tasting():
    if not require_session("room_code", "user_id"):
        return redirect(url_for("basics"))

    with get_db() as conn:
        event = conn.execute(
            "SELECT wine_list_json, event_name FROM events WHERE room_code = ?",
            (session["room_code"],),
        ).fetchone()

        if not event: return redirect(url_for("basics"))

        wine_list = json.loads(event["wine_list_json"])
        count = conn.execute(
            "SELECT count(*) FROM tastings WHERE room_code = ? AND user_id = ?",
            (session["room_code"], session["user_id"]),
        ).fetchone()[0]

    if count < len(wine_list):
        return render_template("tasting.html",
            active_page="tasting",
            current_wine=wine_list[count],
            current_index=count + 1,
            total_wines=len(wine_list),
            event_name=event["event_name"],
            room_code=session["room_code"],
        )

    return redirect(url_for("summary"))


@server.route("/summary")
def summary():
    if not require_session("room_code"):
        return redirect(url_for("cellar"))

    room_code = session["room_code"]

    with get_db() as conn:
        event_info = conn.execute(
            "SELECT event_name, host_name FROM events WHERE room_code = ?",
            (room_code,),
        ).fetchone()

        stats = conn.execute("""
            SELECT wine_name, COUNT(id) as rating_count,
                   ROUND(AVG(score) * 20, 1) as avg_score,
                   ROUND(AVG(acidity), 1) as avg_acidity,
                   ROUND(AVG(tannin), 1) as avg_tannin
            FROM tastings WHERE room_code = ?
            GROUP BY wine_name ORDER BY id ASC
        """, (room_code,)).fetchall()

    return render_template("summary.html",
        event=event_info, stats=stats,
        room_code=room_code, active_page="tasting",
    )


@server.route("/save_tasting", methods=["POST"])
def save_tasting():
    if not require_session("room_code", "user_id"):
        return jsonify({"status": "error", "message": "Not in a tasting session"}), 401

    data = request.get_json(force=True)
    score = data.get("score")

    if score is None or not (1 <= float(score) <= 5):
        return jsonify({"status": "error", "message": "Score must be 1–5"}), 400

    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO tastings
                (room_code, user_id, user_name, wine_name, date,
                 color, scent, flavour, aftertaste, acidity, tannin,
                 country, region, grape, year, price, score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session["room_code"], session["user_id"], session.get("user_name"),
                data.get("wineName"), datetime.date.today().strftime("%b %d, %Y"),
                data.get("color"), data.get("scent"), data.get("flavour"), data.get("aftertaste"),
                data.get("acidity"), data.get("tannin"),
                data.get("country"), data.get("region"), data.get("grape"),
                data.get("year"), data.get("price"), float(score),
            ))
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@server.route("/cellar")
def cellar():
    user_id = session.get("user_id")

    with get_db() as conn:
        if user_id:
            tastings = conn.execute(
                "SELECT * FROM tastings WHERE user_id = ? ORDER BY id DESC", (user_id,)
            ).fetchall()
            stats = conn.execute("""
                SELECT wine_name, grape, COUNT(id) as rating_count,
                       AVG(score) as avg_score, AVG(year) as avg_year, AVG(price) as avg_price
                FROM tastings
                WHERE wine_name IN (SELECT DISTINCT wine_name FROM tastings WHERE user_id = ?)
                GROUP BY wine_name ORDER BY avg_score DESC
            """, (user_id,)).fetchall()
        else:
            tastings = conn.execute("SELECT * FROM tastings ORDER BY id DESC LIMIT 10").fetchall()
            stats = []

    return render_template("cellar.html", tastings=tastings, stats=stats, active_page="cellar")


@server.route("/discover")
def discover():
    wine_type = request.args.get("type", "")
    query = request.args.get("q", "").strip()

    sql = "SELECT * FROM wines WHERE 1=1"
    params = []

    if wine_type:
        sql += " AND type = ?"
        params.append(wine_type)

    if query:
        sql += " AND (name LIKE ? OR region LIKE ? OR tags LIKE ?)"
        like = f"%{query}%"
        params.extend([like, like, like])

    sql += " ORDER BY type, name"

    with get_db() as conn:
        wines = conn.execute(sql, params).fetchall()

    return render_template("discover.html",
        wines=wines, active_page="discover",
        filter_type=wine_type, search_q=query,
    )



if __name__ == "__main__":
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    init_db()
    server.run(debug=True, port=int(os.environ.get("PORT", 5000)))
