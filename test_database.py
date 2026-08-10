from database import create_database, save_posts, get_all_posts
from collector import collect_sample_posts


create_database()

posts = collect_sample_posts()

save_posts(posts)

saved_posts = get_all_posts()

print(f"Database contains {len(saved_posts)} posts.")