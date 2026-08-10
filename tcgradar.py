import sqlite3
from pathlib import Path

from youtube_collector import run_youtube_scan
from youtube_comments import run_comment_collection
from youtube_analyzer import (
    analyze_database,
    print_market_report
)

from youtube_database import create_youtube_tables


# ============================================================
#                     TCG RADAR
# ============================================================
#
# This is now the MAIN PROGRAM.
#
# Normally you only run:
#
#       python tcgradar.py
#
# From here you can:
#
# - check the database
# - perform a fresh YouTube scan
# - collect comments
# - analyze saved information
# - run the entire daily pipeline
#
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_FOLDER / "tcg_radar.db"


# ============================================================
# DATABASE STATUS
# ============================================================

def show_database_status():

    """
    Shows how much YouTube information is currently saved.

    This uses ZERO API quota.
    """

    create_youtube_tables()

    connection = sqlite3.connect(DATABASE_FILE)

    cursor = connection.cursor()


    cursor.execute("""
        SELECT COUNT(*)
        FROM youtube_videos
    """)

    video_count = cursor.fetchone()[0]


    cursor.execute("""
        SELECT COUNT(*)
        FROM youtube_comments
    """)

    comment_count = cursor.fetchone()[0]


    cursor.execute("""
        SELECT game, COUNT(*)
        FROM youtube_videos
        GROUP BY game
        ORDER BY COUNT(*) DESC
    """)

    games = cursor.fetchall()


    connection.close()


    print()
    print("=" * 60)
    print("                 DATABASE STATUS")
    print("=" * 60)

    print()
    print(f"Saved YouTube videos:   {video_count}")
    print(f"Saved YouTube comments: {comment_count}")


    if games:

        print()
        print("Videos by TCG:")
        print("-" * 30)

        for game, count in games:

            print(
                f"{game:<25} {count}"
            )


    if video_count == 0:

        print()
        print(
            "No YouTube discovery data has been saved yet."
        )

        print(
            "A fresh YouTube scan will be required "
            "after your search quota resets."
        )


    print()
    print("=" * 60)


# ============================================================
# ANALYZE SAVED INFORMATION
# ============================================================

def run_saved_analysis():

    """
    Reads ONLY the local database.

    ZERO YouTube API calls.
    ZERO search quota.
    """

    print()
    print("Analyzing saved market information...")


    results = analyze_database()


    if results:

        print_market_report(
            results
        )


# ============================================================
# FRESH YOUTUBE SEARCH
# ============================================================

def fresh_youtube_scan():

    """
    Searches YouTube for new videos.

    WARNING:
    This uses the limited YouTube search quota.
    """

    print()
    print("=" * 60)
    print("WARNING")
    print("=" * 60)

    print()
    print(
        "A fresh scan uses your limited "
        "YouTube Search API quota."
    )

    print()

    confirmation = input(
        "Run fresh YouTube search? (y/n): "
    ).lower().strip()


    if confirmation != "y":

        print()
        print("Fresh scan cancelled.")

        return


    run_youtube_scan()


# ============================================================
# UPDATE COMMENTS
# ============================================================

def update_comments():

    """
    Downloads comments for videos already discovered.

    This contacts YouTube, but DOES NOT perform
    expensive YouTube search requests.
    """

    run_comment_collection()


# ============================================================
# FULL DAILY PIPELINE
# ============================================================

def run_full_daily_scan():

    """
    Intended eventual daily workflow:

    1. Search YouTube once
    2. Save videos
    3. Download comments
    4. Analyze everything
    5. Print market intelligence
    """

    print()
    print("=" * 60)
    print("               FULL DAILY TCG SCAN")
    print("=" * 60)

    print()
    print(
        "This WILL use YouTube search quota."
    )

    print()

    confirmation = input(
        "Start full daily scan? (y/n): "
    ).lower().strip()


    if confirmation != "y":

        print()
        print("Daily scan cancelled.")

        return


    # --------------------------------------------------------
    # STEP 1 - DISCOVER VIDEOS
    # --------------------------------------------------------

    print()
    print("[1/3] Searching YouTube...")

    run_youtube_scan()


    # --------------------------------------------------------
    # STEP 2 - GET COMMENTS
    # --------------------------------------------------------

    print()
    print("[2/3] Collecting comments...")

    run_comment_collection()


    # --------------------------------------------------------
    # STEP 3 - ANALYZE
    # --------------------------------------------------------

    print()
    print("[3/3] Analyzing market discussion...")


    results = analyze_database()


    if results:

        print_market_report(
            results
        )


    print()
    print("=" * 60)

    print(
        "             DAILY TCG SCAN FINISHED"
    )

    print("=" * 60)


# ============================================================
# MAIN MENU
# ============================================================

def show_menu():

    print()
    print()
    print("=" * 60)
    print("                     TCG RADAR")
    print("=" * 60)

    print()
    print("1 - Database status")
    print("2 - Analyze saved market data")
    print("3 - Update YouTube comments")
    print("4 - Fresh YouTube discovery scan")
    print("5 - Full daily scan")

    print()
    print("0 - Exit")

    print()
    print("-" * 60)

    print(
        "NOTE: Options 4 and 5 use limited "
        "YouTube search quota."
    )

    print(
        "Options 1 and 2 use no API quota."
    )

    print("-" * 60)


# ============================================================
# START TCG RADAR
# ============================================================

def main():

    # Make sure database exists
    create_youtube_tables()


    while True:

        show_menu()


        choice = input(
            "\nChoose an option: "
        ).strip()


        # ----------------------------------------------------
        # DATABASE STATUS
        # ----------------------------------------------------

        if choice == "1":

            show_database_status()


        # ----------------------------------------------------
        # ANALYZE DATABASE
        # ----------------------------------------------------

        elif choice == "2":

            run_saved_analysis()


        # ----------------------------------------------------
        # COMMENTS
        # ----------------------------------------------------

        elif choice == "3":

            update_comments()


        # ----------------------------------------------------
        # FRESH SEARCH
        # ----------------------------------------------------

        elif choice == "4":

            fresh_youtube_scan()


        # ----------------------------------------------------
        # FULL PIPELINE
        # ----------------------------------------------------

        elif choice == "5":

            run_full_daily_scan()


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        elif choice == "0":

            print()
            print("TCG Radar closed.")
            print()

            break


        # ----------------------------------------------------
        # INVALID INPUT
        # ----------------------------------------------------

        else:

            print()
            print(
                "Invalid option. "
                "Choose 0, 1, 2, 3, 4 or 5."
            )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()