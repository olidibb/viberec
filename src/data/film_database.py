import sqlite3

connection = sqlite3.connect('../../data/raw/film_database.db')
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
        review_text TEXT,
        FOREIGN KEY (film_id) REFERENCES films (id)
        )
        """)

connection.commit()
connection.close()
