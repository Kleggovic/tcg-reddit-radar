import json
from datetime import datetime, timezone


def collect_sample_posts():

    now = datetime.now(timezone.utc).isoformat()

    posts = [
        {
            "id": "post1",
            "subreddit": "PokemonTCG",
            "title": "Mega Evolution ETB looks amazing",
            "body": "I love the artwork and I am definitely buying two.",
            "created_at": now
        },
        {
            "id": "post2",
            "subreddit": "PokemonTCG",
            "title": "Will the Mega Evolution ETB sell out?",
            "body": "Everyone seems hyped for this release.",
            "created_at": now
        },
        {
            "id": "post3",
            "subreddit": "PokemonInvesting",
            "title": "Prismatic Evolutions is expensive",
            "body": "I wanted another box but I might skip it at these prices.",
            "created_at": now
        },
        {
            "id": "post4",
            "subreddit": "mtgfinance",
            "title": "Secret Lair discussion",
            "body": "This Secret Lair is overpriced. I am going to pass.",
            "created_at": now
        }
    ]

    return posts


if __name__ == "__main__":

    posts = collect_sample_posts()

    with open("sample_data.json", "w", encoding="utf-8") as file:
        json.dump(posts, file, indent=4)

    print(f"Collected {len(posts)} posts.")