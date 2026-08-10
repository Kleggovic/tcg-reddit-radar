import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from youtube_database import get_saved_youtube_data
from youtube_analyzer import analyze_text


# ============================================================
#              TCG RADAR - PRODUCT ANALYZER
# ============================================================
#
# PURPOSE:
#
# Instead of only saying:
#
#   Pokemon = positive
#
# we eventually want:
#
#   Mega Evolution ETB
#   Buying: 14
#   Shortage: 6
#   Overpriced: 2
#   Signal: POSITIVE
#
# This file makes ZERO YouTube API calls.
# It only analyzes data already stored in tcg_radar.db.
#
# ============================================================


PROJECT_FOLDER = Path(__file__).resolve().parent
SETTINGS_FILE = PROJECT_FOLDER / "settings.json"


# ============================================================
# GENERIC WORDS TO IGNORE
# ============================================================

GENERIC_WORDS = {
    "pokemon",
    "pokémon",
    "tcg",
    "magic",
    "mtg",
    "lorcana",
    "yugioh",
    "cards",
    "card",
    "game",
    "new",
    "release",
    "market",
    "price",
    "prices",
    "worth",
    "buy",
    "opening",
    "pack",
    "packs",
    "video",
    "news",
    "the",
    "this",
    "that",
    "and",
    "or",
    "for",
    "with",
    "from",
    "about",
    "what",
    "why",
    "how",
    "is",
    "are",
    "was",
    "will",
    "you",
    "your",
    "our",
    "we",
    "of",
    "to",
    "in",
    "on"
}


# ============================================================
# LOAD SETTINGS
# ============================================================

def load_product_settings():

    if not SETTINGS_FILE.exists():
        return {}

    with open(
        SETTINGS_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        return json.load(file)


# ============================================================
# CLEAN TITLE INTO WORDS
# ============================================================

def clean_words(text):

    return re.findall(
        r"[a-zA-Z0-9À-ÿ'-]+",
        text.lower()
    )


# ============================================================
# FIND POSSIBLE PRODUCT / TOPIC PHRASES
# ============================================================

def extract_candidate_phrases(title):

    words = clean_words(title)

    candidates = set()

    # Look for phrases containing 2-4 words
    for size in range(2, 5):

        for start in range(
            len(words) - size + 1
        ):

            phrase_words = words[
                start:start + size
            ]

            meaningful = [
                word
                for word in phrase_words
                if word not in GENERIC_WORDS
            ]

            # Require at least two meaningful words
            if len(meaningful) < 2:
                continue

            phrase = " ".join(
                phrase_words
            )

            candidates.add(phrase)

    return candidates


# ============================================================
# DISCOVER RECURRING TOPICS
# ============================================================

def discover_topics(
    videos,
    minimum_videos=2
):

    """
    A phrase must appear in at least two different
    video titles before we consider it interesting.
    """

    phrase_videos = defaultdict(set)

    for video in videos:

        video_id = video.get("id", "")
        title = video.get("title", "")

        for phrase in extract_candidate_phrases(title):

            phrase_videos[
                phrase
            ].add(video_id)

    topics = set()

    for phrase, video_ids in phrase_videos.items():

        if len(video_ids) >= minimum_videos:
            topics.add(phrase)

    return topics


# ============================================================
# MANUALLY TRACKED PRODUCTS
# ============================================================

def get_tracked_products(
    settings,
    game
):

    """
    Optional section in settings.json:

    "tracked_products": {
        "Pokemon": [
            "Mega Evolution ETB",
            "Prismatic Evolutions"
        ]
    }
    """

    tracked = settings.get(
        "tracked_products",
        {}
    )

    return tracked.get(
        game,
        []
    )


# ============================================================
# DOES TEXT MENTION PRODUCT?
# ============================================================

def mentions_product(
    text,
    product
):

    return (
        product.lower()
        in text.lower()
    )


# ============================================================
# ANALYZE ONE PRODUCT
# ============================================================

def analyze_product(
    product,
    videos
):

    signals = Counter()

    video_mentions = 0
    comment_mentions = 0

    example_videos = []

    for video in videos:

        title = video.get(
            "title",
            ""
        )

        description = video.get(
            "description",
            ""
        )

        creator_text = (
            title
            + " "
            + description
        )

        # ---------------------------------------------
        # CREATOR MENTION
        # ---------------------------------------------

        if mentions_product(
            creator_text,
            product
        ):

            video_mentions += 1

            if len(example_videos) < 3:
                example_videos.append(title)

            for category in analyze_text(
                creator_text
            ):

                signals[category] += 1


        # ---------------------------------------------
        # COMMENT MENTIONS
        # ---------------------------------------------

        for comment in video.get(
            "saved_comments",
            []
        ):

            comment_text = comment.get(
                "text",
                ""
            )

            if not mentions_product(
                comment_text,
                product
            ):
                continue

            comment_mentions += 1

            for category in analyze_text(
                comment_text
            ):

                signals[category] += 1


    return {
        "product": product,
        "video_mentions": video_mentions,
        "comment_mentions": comment_mentions,
        "signals": signals,
        "examples": example_videos
    }


# ============================================================
# PRODUCT SCORE
# ============================================================

def calculate_product_score(result):

    signals = result["signals"]

    positive = (
        signals["buying"] * 3
        + signals["hype"]
        + signals["shortage"] * 3
        + signals["undervalued"] * 2
        + signals["price_up"] * 2
    )

    negative = (
        signals["overpriced"] * 2
        + signals["price_down"] * 2
        + signals["skip"] * 3
        + signals["waiting"]
    )

    # Independent videos discussing something
    # are useful attention evidence.
    attention = (
        result["video_mentions"] * 2
    )

    return (
        positive
        - negative
        + attention
    )


# ============================================================
# LABEL SCORE
# ============================================================

def product_label(score):

    if score >= 20:
        return "🔥 STRONG POSITIVE"

    if score >= 8:
        return "📈 POSITIVE"

    if score <= -15:
        return "🔴 STRONG NEGATIVE"

    if score <= -5:
        return "📉 NEGATIVE"

    return "🟡 WATCH"


# ============================================================
# ANALYZE PRODUCTS FOR ONE GAME
# ============================================================

def analyze_game_products(
    game,
    videos,
    settings
):

    products = discover_topics(
        videos
    )

    # Add anything you manually want tracked
    for product in get_tracked_products(
        settings,
        game
    ):

        products.add(
            product.lower()
        )

    results = []

    for product in products:

        result = analyze_product(
            product,
            videos
        )

        if (
            result["video_mentions"] == 0
            and result["comment_mentions"] == 0
        ):
            continue

        score = calculate_product_score(
            result
        )

        result["score"] = score
        result["label"] = product_label(
            score
        )

        results.append(result)

    results.sort(
        key=lambda item: (
            item["video_mentions"]
            + item["comment_mentions"],
            item["score"]
        ),
        reverse=True
    )

    return results


# ============================================================
# ANALYZE ALL SAVED DATA
# ============================================================

def analyze_all_products():

    settings = load_product_settings()

    youtube_data = (
        get_saved_youtube_data()
    )

    if not youtube_data:

        print()
        print(
            "No saved YouTube videos found yet."
        )
        print()

        return {}

    results = {}

    for game, videos in youtube_data.items():

        results[game] = (
            analyze_game_products(
                game,
                videos,
                settings
            )
        )

    return results


# ============================================================
# PRINT PRODUCT REPORT
# ============================================================

def print_product_report(results):

    print()
    print("=" * 72)
    print(
        "              TCG RADAR - PRODUCT INTELLIGENCE"
    )
    print("=" * 72)

    for game, products in results.items():

        print()
        print("#" * 72)
        print(game.upper())
        print("#" * 72)

        if not products:

            print(
                "No repeated product/topic signals detected."
            )

            continue

        # Only show the top 10 topics
        for item in products[:10]:

            signals = item["signals"]

            print()
            print(
                f"🔥 {item['product'].title()}"
            )

            print(
                f"Videos mentioning:   "
                f"{item['video_mentions']}"
            )

            print(
                f"Comments mentioning: "
                f"{item['comment_mentions']}"
            )

            print()
            print(
                f"Buying:      "
                f"{signals['buying']}"
            )

            print(
                f"Hype:        "
                f"{signals['hype']}"
            )

            print(
                f"Shortage:    "
                f"{signals['shortage']}"
            )

            print(
                f"Restock:     "
                f"{signals['restock']}"
            )

            print(
                f"Undervalued: "
                f"{signals['undervalued']}"
            )

            print(
                f"Overpriced:  "
                f"{signals['overpriced']}"
            )

            print(
                f"Price up:    "
                f"{signals['price_up']}"
            )

            print(
                f"Price down:  "
                f"{signals['price_down']}"
            )

            print(
                f"Skip:        "
                f"{signals['skip']}"
            )

            print()
            print(
                f"Radar score: {item['score']}"
            )

            print(
                f"Signal:      {item['label']}"
            )

            if item["examples"]:

                print()
                print("Example videos:")

                for title in item["examples"]:
                    print(
                        f"  • {title}"
                    )

    print()
    print("=" * 72)


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    results = analyze_all_products()

    if results:
        print_product_report(results)