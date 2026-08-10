from collections import Counter
from datetime import datetime, timedelta, timezone


def get_post_date(post):
    """
    Convert the stored timestamp into a Python datetime.
    """

    return datetime.fromisoformat(
        post["created_at"].replace("Z", "+00:00")
    )


def count_mentions(posts, hours):

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    counts = Counter()

    for post in posts:

        post_date = get_post_date(post)

        if post_date >= cutoff:

            text = (
                post.get("title", "")
                + " "
                + post.get("body", "")
            ).lower()

            products = [
                "Mega Evolution ETB",
                "Pokemon Center ETB",
                "Secret Lair",
                "Prismatic Evolutions",
                "Destined Rivals",
            ]

            for product in products:

                if product.lower() in text:
                    counts[product] += 1

    return counts


def calculate_trends(posts):

    current = count_mentions(posts, 24)
    previous = count_mentions(posts, 48)

    trends = []

    for product in current:

        current_count = current[product]

        previous_count = (
            previous[product] - current_count
        )

        if previous_count <= 0:

            if current_count > 0:
                change = 100
            else:
                change = 0

        else:

            change = (
                (current_count - previous_count)
                / previous_count
            ) * 100

        trends.append({
            "product": product,
            "current_mentions": current_count,
            "previous_mentions": previous_count,
            "change_percent": round(change)
        })

    trends.sort(
        key=lambda x: x["change_percent"],
        reverse=True
    )

    return trends


def print_trends(trends):

    print()
    print("=" * 55)
    print("              TCG TREND RADAR")
    print("=" * 55)

    if not trends:

        print("\nNo trends detected.")

        return

    for trend in trends:

        change = trend["change_percent"]

        if change >= 100:

            signal = "🔥 EXPLODING"

        elif change >= 50:

            signal = "🟢 RISING"

        elif change > 0:

            signal = "🟡 GROWING"

        else:

            signal = "🔴 FALLING"

        print()
        print(f"{signal}  {trend['product']}")

        print(
            f"   Current mentions: "
            f"{trend['current_mentions']}"
        )

        print(
            f"   Previous mentions: "
            f"{trend['previous_mentions']}"
        )

        print(
            f"   Change: "
            f"{change}%"
        )

    print()
    print("=" * 55)