import sqlite3

DB_NAME = "label_history.db"
def get_chart_data():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT score FROM history")
    rows = cursor.fetchall()

    conn.close()

    excellent = 0
    good = 0
    average = 0
    poor = 0

    for row in rows:
        score = row[0]

        if score >= 90:
            excellent += 1
        elif score >= 75:
            good += 1
        elif score >= 50:
            average += 1
        else:
            poor += 1

    return {
        "excellent": excellent,
        "good": good,
        "average": average,
        "poor": poor
    }

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        score INTEGER,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_result(filename, score, date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO history(filename, score, date) VALUES (?, ?, ?)",
        (filename, score, date)
    )

    conn.commit()
    conn.close()


def get_history():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, filename, score, date
    FROM history
    ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_dashboard_stats():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM history")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(score) FROM history")
    avg = cursor.fetchone()[0]

    cursor.execute("SELECT MAX(score) FROM history")
    highest = cursor.fetchone()[0]

    cursor.execute("SELECT MIN(score) FROM history")
    lowest = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "average": round(avg, 1) if avg else 0,
        "highest": highest if highest else 0,
        "lowest": lowest if lowest else 0
    }


def search_history(keyword):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, filename, score, date
    FROM history
    WHERE filename LIKE ?
    ORDER BY id DESC
    """, ('%' + keyword + '%',))

    rows = cursor.fetchall()

    conn.close()

    return rows


def delete_history(record_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM history WHERE id = ?",
        (record_id,)
    )

    conn.commit()
    conn.close()