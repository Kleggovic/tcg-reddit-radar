import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from youtube_collector import load_settings

from youtube_database import (
    create_youtube_tables,
    get_saved_youtube_videos,
    save_youtube_comments
)


# ============================================================
#              TCG RADAR - YOUTUBE COMMENTS
# ============================================================
#
# IMPORTANT:
#
# THIS FILE DOES NOT SEARCH YOUTUBE.
#
# It reads videos that youtube_collector.py already saved
# inside tcg_radar.db.
#
# Then it downloads comments for those saved videos.
#
#
# Correct flow:
#
# YouTube Search
#      ↓
# youtube_collector.py
#      ↓
# DATABASE
#      ↓
# youtube_comments.py
#
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent
ENV_FILE = PROJECT_FOLDER / ".env"


load_dotenv(ENV_FILE)

API_KEY = os.getenv(
    "YOUTUBE_API_KEY"
)


COMMENTS_URL = (
    "https://www.googleapis.com/youtube/v3/commentThreads"
)


# ============================================================
# CHECK API KEY
# ============================================================

def check_api_key():

    if not API_KEY:

        print()
        print(
            "ERROR: YouTube API key not found."
        )

        print(
            "Check your .env file."
        )

        print()

        raise SystemExit


# ============================================================
# GET COMMENTS FROM ONE VIDEO
# ============================================================

def get_video_comments(
    video_id,
    max_comments=50
):

    """
    Downloads public top-level comments.

    This does NOT perform a YouTube search.

    It already knows exactly which video ID to access.
    """


    comments = []

    next_page_token = None


    while len(comments) < max_comments:

        remaining = (
            max_comments
            - len(comments)
        )


        params = {

            "part": "snippet",

            "videoId": video_id,

            "maxResults":
                min(
                    remaining,
                    100
                ),

            # Start with the most relevant comments
            "order": "relevance",

            "textFormat": "plainText",

            "key": API_KEY
        }


        if next_page_token:

            params[
                "pageToken"
            ] = next_page_token


        response = requests.get(
            COMMENTS_URL,
            params=params,
            timeout=20
        )


        # ----------------------------------------------------
        # HANDLE ERRORS WITHOUT CRASHING WHOLE RADAR
        # ----------------------------------------------------

        if response.status_code != 200:

            print()

            print(
                f"Could not collect comments "
                f"for video {video_id}."
            )


            try:

                error_data = (
                    response
                    .json()
                    .get(
                        "error",
                        {}
                    )
                )

                print(
                    error_data.get(
                        "message",
                        "Unknown YouTube error"
                    )
                )


            except Exception:

                print(
                    response.text
                )


            return comments


        data = response.json()


        # ----------------------------------------------------
        # PROCESS COMMENTS
        # ----------------------------------------------------

        for item in data.get(
            "items",
            []
        ):

            top_comment = (
                item
                .get("snippet", {})
                .get(
                    "topLevelComment",
                    {}
                )
            )


            snippet = top_comment.get(
                "snippet",
                {}
            )


            comment_id = top_comment.get(
                "id",
                ""
            )


            # If YouTube somehow doesn't give us an ID,
            # skip that comment because our database needs one.
            if not comment_id:

                continue


            comments.append({

                "id":
                    comment_id,

                "text":
                    snippet.get(
                        "textDisplay",
                        ""
                    ),

                "likes":
                    snippet.get(
                        "likeCount",
                        0
                    ),

                "published_at":
                    snippet.get(
                        "publishedAt",
                        ""
                    )
            })


            if len(comments) >= max_comments:

                break


        next_page_token = data.get(
            "nextPageToken"
        )


        # No more pages
        if not next_page_token:

            break


    return comments


# ============================================================
# COLLECT COMMENTS FROM SAVED VIDEOS
# ============================================================

def collect_comments_from_database(
    settings
):

    """
    Reads saved videos from SQLite.

    It does NOT run youtube_collector.py
    and does NOT perform any search requests.
    """


    create_youtube_tables()


    videos_by_game = (
        get_saved_youtube_videos()
    )


    if not videos_by_game:

        print()
        print(
            "No saved YouTube videos found."
        )

        print()
        print(
            "After your search quota resets, run:"
        )

        print()
        print(
            "python youtube_collector.py"
        )

        print()
        print(
            "Then run this comment collector."
        )

        print()

        return {}


    videos_to_analyze = settings.get(
        "videos_to_analyze_per_game",
        5
    )


    comments_per_video = settings.get(
        "comments_per_video",
        50
    )


    results = {}


    # ========================================================
    # EACH TCG
    # ========================================================

    for game, videos in videos_by_game.items():

        print()
        print("=" * 65)

        print(
            f"Collecting comments: {game}"
        )

        print("=" * 65)


        results[
            game
        ] = []


        # ----------------------------------------------------
        # CHOOSE NEWEST VIDEOS
        # ----------------------------------------------------
        #
        # We are deliberately NOT choosing videos based
        # mainly on views.
        #
        # You care about current market intelligence,
        # so recent videos are more useful.
        #

        videos = sorted(

            videos,

            key=lambda video:
                video.get(
                    "published_at",
                    ""
                ),

            reverse=True
        )


        selected_videos = videos[
            :videos_to_analyze
        ]


        # ----------------------------------------------------
        # COLLECT COMMENTS
        # ----------------------------------------------------

        for video in selected_videos:

            print()

            print(
                f"🎥 {video['title']}"
            )


            comments = get_video_comments(

                video["id"],

                comments_per_video
            )


            # Save comments permanently
            save_youtube_comments(

                video["id"],

                comments
            )


            print(
                f"   Saved comments: "
                f"{len(comments)}"
            )


            video_copy = dict(
                video
            )


            video_copy[
                "saved_comments"
            ] = comments


            results[
                game
            ].append(
                video_copy
            )


    return results


# ============================================================
# RUN COMMENT COLLECTION
# ============================================================

def run_comment_collection():

    check_api_key()

    settings = load_settings()


    print()
    print("=" * 70)

    print(
        "            STARTING YOUTUBE COMMENT COLLECTION"
    )

    print("=" * 70)


    results = collect_comments_from_database(
        settings
    )


    total_comments = 0


    for game, videos in results.items():

        for video in videos:

            total_comments += len(
                video.get(
                    "saved_comments",
                    []
                )
            )


    print()
    print("=" * 70)

    print(
        f"Saved {total_comments} comments."
    )

    print(
        "No YouTube search was performed."
    )

    print("=" * 70)
    print()


    return results


# ============================================================
# START DIRECTLY
# ============================================================

if __name__ == "__main__":

    run_comment_collection()