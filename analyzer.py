import re
from collections import defaultdict


POSITIVE_WORDS = {
    "amazing",
    "awesome",
    "great",
    "love",
    "hyped",
    "hype",
    "beautiful",
    "buy",
    "buying",
    "wanted",
    "want",
    "good",
    "excited",
    "popular",
    "sellout",
    "insane",
}


NEGATIVE_WORDS = {
    "bad",
    "hate",
    "ugly",
    "overpriced",
    "expensive",
    "trash",
    "awful",
    "disappointing",
    "skip",
    "pass",
    "boring",
}


PRODUCTS = [
    "Mega Evolution ETB",
    "Pokemon Center ETB",
    "Secret Lair",
    "Prismatic Evolutions",
    "Destined Rivals",
]


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9:’-]+", text.lower())


def get_sentiment(text):
    words = tokenize(text)

    positive = sum(word in POSITIVE_WORDS for word in words)
    negative = sum(word in NEGATIVE_WORDS for word in words)

    score = positive - negative

    if score > 0:
        label = "positive"
    elif score < 0:
        label = "negative"
    else:
        label = "neutral"

    return score, label


def find_products(text):
    text_lower = text.lower()

    found = []

    for product in PRODUCTS:
        if product.lower() in text_lower:
            found.append(product)

    return found


def analyze_posts(posts):

    results = defaultdict(lambda: {
        "mentions": 0,
        "positive": 0,
        "negative": 0,
        "neutral": 0,
    })

    for post in posts:

        title = post.get("title", "")
        body = post.get("body", "")

        text = title + " " + body

        products = find_products(text)

        if not products:
            continue

        score, sentiment = get_sentiment(text)

        for product in products:

            results[product]["mentions"] += 1
            results[product][sentiment] += 1

    return results


def print_report(results):

    print()
    print("=" * 50)
    print("          TCG REDDIT RADAR")
    print("=" * 50)

    if not results:
        print("No tracked products found.")
        return

    for product, data in results.items():

        mentions = data["mentions"]
        positive = data["positive"]
        negative = data["negative"]

        print()
        print(f"🔥 {product}")
        print(f"   Mentions: {mentions}")
        print(f"   Positive: {positive}")
        print(f"   Negative: {negative}")
        print(f"   Neutral:  {data['neutral']}")

        if positive > negative:
            print("   Signal:   🟢 Positive interest")
        elif negative > positive:
            print("   Signal:   🔴 Negative interest")
        else:
            print("   Signal:   🟡 Mixed interest")

    print()
    print("=" * 50)