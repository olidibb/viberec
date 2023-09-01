import sqlite3

DB_LOCATION = '../../data/raw/film_database.db'

connection = sqlite3.connect(DB_LOCATION)
cursor = connection.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS films (
        id INTEGER PRIMARY KEY,
        title TEXT,
        director TEXT,
        genre TEXT,
        themes TEXT,
        year INTEGER
        )
        """)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY,
        film_id INTEGER,
        user TEXT,
        rating FLOAT,
        review_text TEXT,
        FOREIGN KEY (film_id) REFERENCES films (id)
        )
        """)

connection.commit()
connection.close()
