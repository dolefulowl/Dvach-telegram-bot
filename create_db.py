import sqlite3

db = sqlite3.connect("server.db")
sql = db.cursor()


sql.execute("""CREATE TABLE IF NOT EXISTS users (
    id INT,
    ChosenBoard TEXT,
    current_thread INT DEFAULT 0
)""")
db.commit()


sql.execute("""CREATE TABLE IF NOT EXISTS boards (
    board TEXT,
    thread_url TEXT,
    photo_url TEXT,
    message TEXT)""")
db.commit()
