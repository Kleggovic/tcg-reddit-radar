import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from youtube_database import (
    create_youtube_tables,
    save_youtube_videos
)


# ============================================================
#               TCG RADAR - YOUTUBE COLLECTOR
# ============================================================
#
# JOB OF THIS FILE:
#
# 1. Read search settings from settings.json
# 2. Search YouTube
# 3. Get information about discovered videos
# 4. Remove duplicates
# 5. Save videos into tcg_radar.db
#
# IMPORTANT:
#
# Searching YouTube costs API search quota.
#
# This file should therefore only be run when we actually
# want to perform a fresh YouTube scan.
#
# Other parts of TCG Radar will read the saved videos from
# the database instead of searching YouTube again.
#
# ============================================================


# ============================================================
# PROJECT FILE LOCATIONS
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent

SETTINGS_FILE = PROJECT_FOLDER / "settings.json"
ENV_FILE = PROJECT_FOLDER / ".env"


# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv(ENV_FILE)

API_KEY = os.getenv("YOUTUBE_API_KEY")


# ============================================================
# YOUTUBE API ADDRESSES
# ============================================================

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_settings():

    """
    Loads your editable TCG Radar settings from:

        settings.json

    This includes:

    - games to monitor
    - YouTube search phrases
    - videos per search
    - videos shown in reports
    """

    if not SETTINGS_FILE.exists():

        print()
        print("ERROR: settings.json was not found.")
        print(f"Expected location: {SETTINGS_FILE}")
        print()

        raise SystemExit


    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            settings = json.load(file)


    except json.JSONDecodeError as error:

        print()
        print("ERROR: settings.json contains invalid JSON.")
        print()
        print(error)
        print()

        raise SystemExit


    return settings


# ============================================================
# CHECK API KEY
# ============================================================

def check_api_key():

    """
    Makes sure the YouTube API key was loaded from .env.
    """

    if not API_KEY:

        print()
        print("ERROR: YouTube API key not found.")
        print()
        print("Your .env file should contain:")
        print()
        print("YOUTUBE_API_KEY=your_key_here")
        print()

        raise SystemExit


# ============================================================
# SEARCH YOUTUBE
# ============================================================

def search_youtube(
    query,
    max_results=5
):

    """
    Searches YouTube for ONE search phrase.

    Example:

        Pokemon TCG market

    Returns a list of video IDs.

    IMPORTANT:

    Each call to this function uses YouTube search quota.
    """

    params = {

        # Basic video information
        "part": "snippet",

        # The actual search phrase
        "q": query,

        # We only want videos
        "type": "video",

        # Newest results first
        "order": "date",

        # Number of results
        "maxResults": max_results,

        # Our API key
        "key": API_KEY
    }


    response = requests.get(
        SEARCH_URL,
        params=params,
        timeout=20
    )


    # --------------------------------------------------------
    # HANDLE API ERRORS
    # --------------------------------------------------------

    if response.status_code != 200:

        print()
        print("=" * 70)
        print("YOUTUBE API ERROR")
        print("=" * 70)

        print(response.text)

        print("=" * 70)
        print()

        response.raise_for_status()


    data = response.json()


    # --------------------------------------------------------
    # EXTRACT VIDEO IDs
    # --------------------------------------------------------

    video_ids = []


    for item in data.get(
        "items",
        []
    ):

        video_id = (
            item
            .get("id", {})
            .get("videoId")
        )


        if video_id:

            video_ids.append(
                video_id
            )


    return video_ids


# ============================================================
# GET VIDEO DETAILS
# ============================================================

def get_video_details(
    video_ids
):

    """
    Gets more information for videos we found.

    We save:

    - title
    - description
    - channel
    - publication date
    - views
    - likes
    - comment count

    Views/likes are secondary information.

    Our main market analysis will eventually focus on:

    - video content
    - descriptions
    - comments
    - products
    - buying / selling opinions
    """


    if not video_ids:

        return []


    params = {

        "part": "snippet,statistics",

        "id": ",".join(
            video_ids
        ),

        "key": API_KEY
    }


    response = requests.get(
        VIDEOS_URL,
        params=params,
        timeout=20
    )


    if response.status_code != 200:

        print()
        print("=" * 70)
        print("YOUTUBE API ERROR")
        print("=" * 70)

        print(response.text)

        print("=" * 70)
        print()

        response.raise_for_status()


    data = response.json()


    videos = []


    for item in data.get(
        "items",
        []
    ):

        snippet = item.get(
            "snippet",
            {}
        )


        statistics = item.get(
            "statistics",
            {}
        )


        video = {

            "id":
                item.get(
                    "id",
                    ""
                ),

            "title":
                snippet.get(
                    "title",
                    ""
                ),

            "description":
                snippet.get(
                    "description",
                    ""
                ),

            "channel":
                snippet.get(
                    "channelTitle",
                    ""
                ),

            "published_at":
                snippet.get(
                    "publishedAt",
                    ""
                ),

            "views":
                int(
                    statistics.get(
                        "viewCount",
                        0
                    )
                ),

            "likes":
                int(
                    statistics.get(
                        "likeCount",
                        0
                    )
                ),

            "comments":
                int(
                    statistics.get(
                        "commentCount",
                        0
                    )
                )
        }


        videos.append(
            video
        )


    return videos


# ============================================================
# COLLECT ALL TCG VIDEOS
# ============================================================

def collect_all_tcg_videos(
    settings
):

    """
    Searches YouTube for every TCG and every search phrase
    listed inside settings.json.

    The result looks roughly like:

    {
        "Pokemon": [...videos...],
        "Magic": [...videos...],
        "Lorcana": [...videos...]
    }
    """


    games = settings.get(
        "games",
        {}
    )


    videos_per_search = settings.get(
        "videos_per_search",
        5
    )


    all_videos = {}


    # Prevent the same video from appearing several times
    seen_ids = set()


    # ========================================================
    # LOOP THROUGH GAMES
    # ========================================================

    for game, queries in games.items():

        print()
        print("=" * 60)

        print(
            f"Searching {game}"
        )

        print("=" * 60)


        all_videos[game] = []


        # ====================================================
        # LOOP THROUGH SEARCH PHRASES
        # ====================================================

        for query in queries:

            print(
                f"   → {query}"
            )


            # THIS is the expensive search call
            video_ids = search_youtube(
                query,
                videos_per_search
            )


            # Fetch additional information about
            # the videos we just discovered
            videos = get_video_details(
                video_ids
            )


            # =================================================
            # PROCESS RESULTS
            # =================================================

            for video in videos:


                # Skip duplicates
                if video["id"] in seen_ids:

                    continue


                seen_ids.add(
                    video["id"]
                )


                # Remember which TCG this video belongs to
                video["game"] = game


                # Remember which query discovered the video
                video["search_query"] = query


                all_videos[
                    game
                ].append(
                    video
                )


    return all_videos


# ============================================================
# SIMPLE REPORT
# ============================================================

def print_report(
    results,
    settings
):

    """
    Displays a quick overview of the videos we found.

    This is NOT the final market analysis report.

    It is mainly useful for checking whether the collector
    found sensible videos.
    """


    videos_shown = settings.get(
        "videos_shown_per_game",
        10
    )


    print()
    print()
    print("=" * 70)

    print(
        "                    TCG YOUTUBE SCAN"
    )

    print("=" * 70)


    for game, videos in results.items():

        print()
        print("#" * 70)

        print(
            game.upper()
        )

        print("#" * 70)


        if not videos:

            print(
                "No videos found."
            )

            continue


        # Temporary sorting.
        #
        # Views are NOT our actual TCG market signal.
        #
        # This is only useful for displaying some
        # potentially more relevant videos first.

        videos = sorted(
            videos,
            key=lambda video:
                video.get(
                    "views",
                    0
                ),
            reverse=True
        )


        for video in videos[
            :videos_shown
        ]:

            print()

            print(
                f"🎥 {video['title']}"
            )

            print(
                f"Channel:   "
                f"{video['channel']}"
            )

            print(
                f"Views:     "
                f"{video['views']:,}"
            )

            print(
                f"Comments:  "
                f"{video['comments']:,}"
            )

            print(
                f"Published: "
                f"{video['published_at']}"
            )

            print(
                f"Found via: "
                f"{video['search_query']}"
            )


    print()
    print("=" * 70)


# ============================================================
# RUN A FRESH YOUTUBE SCAN
# ============================================================

def run_youtube_scan():

    """
    This is the function our future tcgradar.py
    master program will call.

    FLOW:

        settings
            ↓
        YouTube search
            ↓
        collect videos
            ↓
        save to SQLite
            ↓
        return results

    IMPORTANT:

    Calling this function performs fresh YouTube searches.
    """


    print()
    print("=" * 70)

    print(
        "                 STARTING YOUTUBE SCAN"
    )

    print("=" * 70)


    # Make sure API key exists
    check_api_key()


    # Read settings.json
    settings = load_settings()


    # Make sure our YouTube database tables exist
    create_youtube_tables()


    number_of_games = len(
        settings.get(
            "games",
            {}
        )
    )


    print()

    print(
        f"Monitoring {number_of_games} TCGs."
    )


    # --------------------------------------------------------
    # SEARCH YOUTUBE ONCE
    # --------------------------------------------------------

    videos = collect_all_tcg_videos(
        settings
    )


    # --------------------------------------------------------
    # SAVE RESULTS
    # --------------------------------------------------------

    save_youtube_videos(
        videos
    )


    total_videos = sum(
        len(game_videos)
        for game_videos
        in videos.values()
    )


    print()
    print(
        f"Saved {total_videos} discovered videos "
        f"to tcg_radar.db."
    )


    return videos, settings


# ============================================================
# START PROGRAM DIRECTLY
# ============================================================

if __name__ == "__main__":

    videos, settings = run_youtube_scan()


    # Temporary discovery report
    print_report(
        videos,
        settings
    )


    print()
    print("=" * 70)

    print(
        "                  YOUTUBE SCAN COMPLETE"
    )

    print("=" * 70)
    print()