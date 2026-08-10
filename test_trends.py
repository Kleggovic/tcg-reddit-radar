from database import get_all_posts
from trends import calculate_trends, print_trends


posts = get_all_posts()

trends = calculate_trends(posts)

print_trends(trends)