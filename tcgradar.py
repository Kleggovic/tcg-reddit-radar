from collector import collect_sample_posts
from database import create_database, save_posts, get_all_posts
from analyzer import analyze_posts, print_report
from trends import calculate_trends, print_trends


def main():

    print()
    print("=" * 55)
    print("              STARTING TCG RADAR")
    print("=" * 55)

    print("\n[1/4] Opening database...")
    create_database()

    print("[2/4] Collecting new data...")
    new_posts = collect_sample_posts()

    print(f"      Found {len(new_posts)} posts.")

    print("[3/4] Saving data...")
    save_posts(new_posts)

    posts = get_all_posts()

    print(f"      Database contains {len(posts)} posts.")

    print("[4/4] Analyzing data...")

    results = analyze_posts(posts)
    print_report(results)

    trends = calculate_trends(posts)
    print_trends(trends)

    print()
    print("=" * 55)
    print("              TCG RADAR FINISHED")
    print("=" * 55)
    print()


if __name__ == "__main__":
    main()