import sqlite3
from pathlib import Path

from youtube_collector import run_youtube_scan
from youtube_comments import run_comment_collection

from youtube_analyzer import (
    analyze_database,
    print_market_report
)

from product_analyzer import (
    analyze_all_products,
    print_product_report
)

from youtube_database import create_youtube_tables


# ============================================================
#                         TCG RADAR
# ============================================================
#
# MAIN PROGRAM
#
# Normally you only need to run:
#
#       python tcgradar.py
#
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent
DATABASE_FILE = PROJECT_FOLDER / "tcg_radar.db"


# ============================================================
# DATABASE STATUS
# ============================================================

def show_database_status():

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
            print(f"{game:<25} {count}")

    print()
    print("=" * 60)


# ============================================================
# GENERAL MARKET ANALYSIS
# ============================================================

def run_market_analysis():

    print()
    print("Analyzing overall TCG market discussion...")

    results = analyze_database()

    if results:
        print_market_report(results)


# ============================================================
# PRODUCT ANALYSIS
# ============================================================

def run_product_analysis():

    print()
    print("Analyzing individual products and topics...")

    results = analyze_all_products()

    if results:
        print_product_report(results)


# ============================================================
# UPDATE COMMENTS
# ============================================================

def update_comments():

    run_comment_collection()


# ============================================================
# FRESH YOUTUBE DISCOVERY
# ============================================================

def fresh_youtube_scan():

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
# FULL DAILY PIPELINE
# ============================================================

def run_full_daily_scan():

    print()
    print("=" * 60)
    print("               FULL DAILY TCG SCAN")
    print("=" * 60)

    print()
    print(
        "This performs a fresh YouTube search "
        "and therefore uses search quota."
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
    # STEP 1
    # Discover current YouTube videos
    # --------------------------------------------------------

    print()
    print("[1/4] Discovering new YouTube videos...")

    run_youtube_scan()


    # --------------------------------------------------------
    # STEP 2
    # Collect comments for saved videos
    # --------------------------------------------------------

    print()
    print("[2/4] Collecting community comments...")

    run_comment_collection()


    # --------------------------------------------------------
    # STEP 3
    # Analyze broad market discussion
    # --------------------------------------------------------

    print()
    print("[3/4] Analyzing market sentiment...")

    market_results = analyze_database()

    if market_results:

        print_market_report(
            market_results
        )


    # --------------------------------------------------------
    # STEP 4
    # Analyze individual products/topics
    # --------------------------------------------------------

    print()
    print("[4/4] Analyzing individual products...")

    product_results = analyze_all_products()

    if product_results:

        print_product_report(
            product_results
        )


    print()
    print("=" * 60)
    print("             DAILY TCG SCAN FINISHED")
    print("=" * 60)
    print()


# ============================================================
# MENU
# ============================================================

def show_menu():

    print()
    print("=" * 60)
    print("                     TCG RADAR")
    print("=" * 60)

    print()
    print("1 - Database status")
    print("2 - Overall market analysis")
    print("3 - Product / topic analysis")
    print("4 - Update YouTube comments")
    print("5 - Fresh YouTube discovery scan")
    print("6 - Full daily scan")

    print()
    print("0 - Exit")

    print()
    print("-" * 60)

    print("1, 2 and 3 = local / no API calls")
    print("4 = YouTube comments, but no search")
    print("5 and 6 = use limited YouTube search quota")

    print("-" * 60)


# ============================================================
# START PROGRAM
# ============================================================

def main():

    create_youtube_tables()

    while True:

        show_menu()

        choice = input(
            "\nChoose an option: "
        ).strip()


        if choice == "1":

            show_database_status()


        elif choice == "2":

            run_market_analysis()


        elif choice == "3":

            run_product_analysis()


        elif choice == "4":

            update_comments()


        elif choice == "5":

            fresh_youtube_scan()


        elif choice == "6":

            run_full_daily_scan()


        elif choice == "0":

            print()
            print("TCG Radar closed.")
            print()

            break


        else:

            print()
            print(
                "Invalid option. "
                "Choose 0-6."
            )


if __name__ == "__main__":

    main()