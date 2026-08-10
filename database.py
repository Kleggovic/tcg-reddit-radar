import sqlite3


DATABASE_NAME = "tcg_radar.db"


def create_database():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def save_posts(posts):

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    for post in posts:

        cursor.execute("""
            INSERT OR IGNORE INTO posts
            (id, subreddit, title, body, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            post["id"],
            post["subreddit"],
            post["title"],
            post["body"],
            post["created_at"]
        ))

    connection.commit()
    connection.close()


def get_all_posts():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, subreddit, title, body, created_at
        FROM posts
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    posts = []

    for row in rows:

        posts.append({
            "id": row[0],
            "subreddit": row[1],
            "title": row[2],
            "body": row[3],
            "created_at": row[4]
        })

    return posts