from collections import Counter

from youtube_database import get_saved_youtube_data


# ============================================================
#              TCG RADAR - YOUTUBE ANALYZER
# ============================================================
#
# IMPORTANT:
#
# This file DOES NOT contact YouTube.
# It DOES NOT perform searches.
# It DOES NOT download comments.
#
# It only analyzes information already stored in:
#
#       tcg_radar.db
#
# Therefore you can run this as often as you want
# without using YouTube search quota.
#
# ============================================================


# ============================================================
# MARKET KEYWORDS
# ============================================================
#
# You can add/remove phrases here later.
#
# Keep them lowercase.
#
# ============================================================

MARKET_KEYWORDS = {

    "buying": [
        "buying",
        "i bought",
        "i'm buying",
        "im buying",
        "preordered",
        "preorder",
        "ordered",
        "picked up",
        "grabbed",
        "getting one",
        "buy this",
        "must buy",
        "worth buying",
        "holding sealed"
    ],

    "hype": [
        "hype",
        "hyped",
        "excited",
        "insane",
        "crazy demand",
        "everyone wants",
        "going crazy",
        "very popular",
        "huge demand"
    ],

    "shortage": [
        "sold out",
        "selling out",
        "out of stock",
        "hard to find",
        "can't find",
        "cant find",
        "limited supply",
        "low supply",
        "shortage",
        "scarce",
        "underprinted"
    ],

    "restock": [
        "restock",
        "restocked",
        "back in stock",
        "available again"
    ],

    "overpriced": [
        "overpriced",
        "too expensive",
        "not worth",
        "way too much",
        "price is ridiculous",
        "too pricey"
    ],

    "undervalued": [
        "undervalued",
        "underpriced",
        "cheap right now",
        "good price",
        "great price",
        "good value",
        "great value",
        "bargain"
    ],

    "price_up": [
        "price will rise",
        "prices will rise",
        "price will go up",
        "prices will go up",
        "going up in price",
        "increase in value",
        "will increase"
    ],

    "price_down": [
        "price will drop",
        "prices will drop",
        "price will fall",
        "prices will fall",
        "going down",
        "will crash",
        "price crash",
        "prices crash"
    ],

    "skip": [
        "skip",
        "passing",
        "i'll pass",
        "ill pass",
        "not buying",
        "won't buy",
        "wont buy",
        "avoid",
        "stay away"
    ],

    "waiting": [
        "waiting",
        "i'll wait",
        "ill wait",
        "wait for",
        "waiting for a restock",
        "waiting for prices",
        "buy later"
    ]
}


# ============================================================
# ANALYZE TEXT
# ============================================================

def analyze_text(text):

    text = text.lower().strip()

    categories = []

    for category, keywords in MARKET_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                categories.append(category)
                break

    return categories


# ============================================================
# ANALYZE ONE VIDEO
# ============================================================

def analyze_video(video):

    creator_signals = Counter()
    community_signals = Counter()

    # Creator information we currently have:
    # title + description
    creator_text = (
        video.get("title", "")
        + " "
        + video.get("description", "")
    )

    for category in analyze_text(creator_text):
        creator_signals[category] += 1


    comments = video.get(
        "saved_comments",
        []
    )

    relevant_comments = 0


    for comment in comments:

        categories = analyze_text(
            comment.get("text", "")
        )

        if categories:
            relevant_comments += 1

        for category in categories:
            community_signals[category] += 1


    return {
        "title": video.get("title", ""),
        "channel": video.get("channel", ""),
        "comments_analyzed": len(comments),
        "relevant_comments": relevant_comments,
        "creator_signals": creator_signals,
        "community_signals": community_signals
    }


# ============================================================
# ANALYZE ONE TCG
# ============================================================

def analyze_game(videos):

    community_totals = Counter()
    creator_totals = Counter()

    total_comments = 0
    relevant_comments = 0


    for video in videos:

        result = analyze_video(video)

        total_comments += result["comments_analyzed"]
        relevant_comments += result["relevant_comments"]


        for category, count in result[
            "community_signals"
        ].items():

            community_totals[category] += count


        for category, count in result[
            "creator_signals"
        ].items():

            creator_totals[category] += count


    return {
        "videos_analyzed": len(videos),
        "comments_analyzed": total_comments,
        "relevant_comments": relevant_comments,
        "community_signals": community_totals,
        "creator_signals": creator_totals
    }


# ============================================================
# RADAR SCORE
# ============================================================

def calculate_signal(signals):

    positive = (
        signals["buying"] * 2
        + signals["hype"]
        + signals["shortage"] * 2
        + signals["undervalued"] * 2
        + signals["price_up"]
    )

    negative = (
        signals["overpriced"]
        + signals["price_down"] * 2
        + signals["skip"] * 2
        + signals["waiting"]
    )

    score = positive - negative


    if score >= 15:
        label = "🔥 STRONG POSITIVE"

    elif score >= 5:
        label = "📈 POSITIVE"

    elif score <= -10:
        label = "🔴 STRONG NEGATIVE"

    elif score <= -3:
        label = "📉 NEGATIVE"

    else:
        label = "🟡 MIXED / UNCLEAR"


    return score, label


# ============================================================
# ANALYZE SAVED DATABASE
# ============================================================

def analyze_database():

    youtube_data = get_saved_youtube_data()


    if not youtube_data:

        print()
        print("No saved YouTube data found.")
        print(
            "Run a fresh discovery scan after "
            "the YouTube search quota resets."
        )
        print()

        return {}


    results = {}


    for game, videos in youtube_data.items():

        results[game] = analyze_game(videos)


    return results


# ============================================================
# PRINT REPORT
# ============================================================

def print_market_report(results):

    print()
    print("=" * 70)
    print("              TCG RADAR MARKET INTELLIGENCE")
    print("=" * 70)


    for game, data in results.items():

        community = data["community_signals"]
        creators = data["creator_signals"]

        score, label = calculate_signal(
            community
        )


        print()
        print("#" * 70)
        print(game.upper())
        print("#" * 70)

        print(
            f"Videos analyzed:          "
            f"{data['videos_analyzed']}"
        )

        print(
            f"Comments analyzed:        "
            f"{data['comments_analyzed']}"
        )

        print(
            f"Market-relevant comments: "
            f"{data['relevant_comments']}"
        )


        print()
        print("COMMUNITY")
        print("-" * 35)

        print(f"Buying:       {community['buying']}")
        print(f"Hype:         {community['hype']}")
        print(f"Shortage:     {community['shortage']}")
        print(f"Restock:      {community['restock']}")
        print(f"Undervalued:  {community['undervalued']}")
        print(f"Overpriced:   {community['overpriced']}")
        print(f"Price up:     {community['price_up']}")
        print(f"Price down:   {community['price_down']}")
        print(f"Skip / avoid: {community['skip']}")
        print(f"Waiting:      {community['waiting']}")


        print()
        print("CREATOR TITLE / DESCRIPTION")
        print("-" * 35)

        print(f"Buying:      {creators['buying']}")
        print(f"Hype:        {creators['hype']}")
        print(f"Shortage:    {creators['shortage']}")
        print(f"Overpriced:  {creators['overpriced']}")
        print(f"Undervalued: {creators['undervalued']}")


        print()
        print(f"RADAR SCORE: {score}")
        print(f"RADAR:       {label}")


    print()
    print("=" * 70)


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    print()
    print("Analyzing saved YouTube information...")

    results = analyze_database()

    if results:
        print_market_report(results)

    print()
    print("Analysis finished.")