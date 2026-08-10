import sqlite3
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
#                TCG RADAR - YOUTUBE DATABASE
# ============================================================
#
# Stores:
#
# - discovered YouTube videos
# - collected YouTube comments
#
# This lets us search YouTube ONCE and reuse the data
# without spending more search quota.
#
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_NAME = PROJECT_FOLDER / "tcg_radar.db"


# ============================================================
# CREATE TABLES
# ============================================================

def create_youtube_tables():

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    # --------------------------------------------------------
    # SAVED VIDEOS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_videos (

            video_id TEXT PRIMARY KEY,

            game TEXT,

            title TEXT,

            description TEXT,

            channel TEXT,

            published_at TEXT,

            views INTEGER,

            likes INTEGER,

            comment_count INTEGER,

            search_query TEXT,

            first_seen TEXT,

            last_seen TEXT
        )
    """)


    # --------------------------------------------------------
    # SAVED COMMENTS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS youtube_comments (

            comment_id TEXT PRIMARY KEY,

            video_id TEXT,

            text TEXT,

            likes INTEGER,

            published_at TEXT,

            collected_at TEXT
        )
    """)

    connection.commit()
    connection.close()


# ============================================================
# SAVE VIDEOS
# ============================================================

def save_youtube_videos(videos_by_game):

    create_youtube_tables()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    now = datetime.now(
        timezone.utc
    ).isoformat()


    for game, videos in videos_by_game.items():

        for video in videos:

            cursor.execute("""
                INSERT INTO youtube_videos (

                    video_id,
                    game,
                    title,
                    description,
                    channel,
                    published_at,
                    views,
                    likes,
                    comment_count,
                    search_query,
                    first_seen,
                    last_seen

                )

                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(video_id)
                DO UPDATE SET

                    game = excluded.game,
                    title = excluded.title,
                    description = excluded.description,
                    channel = excluded.channel,
                    published_at = excluded.published_at,
                    views = excluded.views,
                    likes = excluded.likes,
                    comment_count = excluded.comment_count,
                    search_query = excluded.search_query,
                    last_seen = excluded.last_seen

            """, (

                video.get("id", ""),
                game,
                video.get("title", ""),
                video.get("description", ""),
                video.get("channel", ""),
                video.get("published_at", ""),
                video.get("views", 0),
                video.get("likes", 0),
                video.get("comments", 0),
                video.get("search_query", ""),
                now,
                now
            ))

    connection.commit()
    connection.close()


# ============================================================
# LOAD SAVED VIDEOS
# ============================================================

def get_saved_youtube_videos():

    create_youtube_tables()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            video_id,
            game,
            title,
            description,
            channel,
            published_at,
            views,
            likes,
            comment_count,
            search_query

        FROM youtube_videos

        ORDER BY published_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()


    videos_by_game = {}


    for row in rows:

        game = row[1]

        if game not in videos_by_game:

            videos_by_game[game] = []


        videos_by_game[game].append({

            "id": row[0],

            "game": row[1],

            "title": row[2],

            "description": row[3],

            "channel": row[4],

            "published_at": row[5],

            "views": row[6],

            "likes": row[7],

            "comments": row[8],

            "search_query": row[9]
        })


    return videos_by_game


# ============================================================
# SAVE COMMENTS
# ============================================================

def save_youtube_comments(
    video_id,
    comments
):

    create_youtube_tables()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    collected_at = datetime.now(
        timezone.utc
    ).isoformat()


    for comment in comments:

        cursor.execute("""
            INSERT INTO youtube_comments (

                comment_id,
                video_id,
                text,
                likes,
                published_at,
                collected_at

            )

            VALUES (?, ?, ?, ?, ?, ?)

            ON CONFLICT(comment_id)
            DO UPDATE SET

                text = excluded.text,
                likes = excluded.likes,
                collected_at = excluded.collected_at

        """, (

            comment.get("id", ""),
            video_id,
            comment.get("text", ""),
            comment.get("likes", 0),
            comment.get("published_at", ""),
            collected_at
        ))

    connection.commit()
    connection.close()


# ============================================================
# LOAD COMMENTS FOR ONE VIDEO
# ============================================================

def get_saved_youtube_comments(
    video_id
):

    create_youtube_tables()

    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT

            comment_id,
            text,
            likes,
            published_at

        FROM youtube_comments

        WHERE video_id = ?

        ORDER BY likes DESC

    """, (
        video_id,
    ))

    rows = cursor.fetchall()

    connection.close()


    comments = []


    for row in rows:

        comments.append({

            "id": row[0],

            "text": row[1],

            "likes": row[2],

            "published_at": row[3]
        })


    return comments


# ============================================================
# LOAD VIDEOS + THEIR SAVED COMMENTS
# ============================================================

def get_saved_youtube_data():

    videos_by_game = get_saved_youtube_videos()


    for game, videos in videos_by_game.items():

        for video in videos:

            video["saved_comments"] = (
                get_saved_youtube_comments(
                    video["id"]
                )
            )


    return videos_by_game