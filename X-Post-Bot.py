import tweepy
from datetime import datetime, timezone, timedelta
from app import guess_distribution, recent_elements
import os

current_directory = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(current_directory, 'images')

# Enter API tokens below
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGhmwwEAAAAAAPWUcJtWjU7LbBPFAJw2LF9FroU%3D1hcGjWrBUTPC222te3VrVZB5i4klkyRLU84ISCIM3jYO3WrDWz"
API_KEY = 'ICR2iSUBXaD8BRliJKwFENkd1'
API_SECRET_KEY = 'hWe7oWbb4zIobgkZmwBg7whx9psSBeg1UBNQyXMOS5MOjYjaRp'
ACCESS_TOKEN = '1464775758174380034-h0VPFO0Kou7Ys5VSEbSG2gq5f5kJWN'
ACCESS_TOKEN_SECRET = 'UCHPOmdRB5oGLdFJrmHU3rGSNSsOD7KU6zqCuiy9XdEMl'

# V1 Twitter API Authentication
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

# V2 Twitter API Authentication
client = tweepy.Client(
    consumer_key=API_KEY, consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN, access_token_secret=ACCESS_TOKEN_SECRET, wait_on_rate_limit=True,
)

pos = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]


def generate_distribution(date):
    distribution = guess_distribution[date]

    total_count = 0
    for i in range(1, 10):
        total_count += distribution[str(i)]

    formatted_distribution = ""

    for i in range(1, 9):
        count = distribution[str(i)]
        percentage = round(((count / total_count) * 100)) if total_count else 0
        formatted_distribution += f"{pos[i]} {'🟩' * min(5, max(1,  round((percentage / 100) * 5)))} {percentage}%\n"

    failed_count = distribution["9"]
    failed_percentage = round(
        ((failed_count / total_count) * 100)) if total_count else 0
    formatted_distribution += f"❌ {'🟩' * min(5, max(1,  round((failed_percentage / 100) * 5)))} {failed_percentage}%"

    return formatted_distribution


def post_tweet():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    yesterday_formatted = yesterday.strftime('%Y%m%d')


    mystery_element = recent_elements[yesterday_formatted]["name"]

    distribution_text = generate_distribution(yesterday_formatted)

    if mystery_element:
        # Construct the full file path for the image
        image_path = os.path.join(images_folder, f"{mystery_element}.jpg")

        # Compose the message
        message = f"Yesterday's #Elementle was {mystery_element} 🧪\n\n{distribution_text}\n\nhttps://elementlegame.com"

        try:
            # Upload the image and create the tweet
            media_id = api.media_upload(filename=image_path).media_id_string
            client.create_tweet(text=message, media_ids=[media_id])
            print("Tweet posted successfully!", flush=True)
        except Exception as e:
            print(f"Error posting tweet: {e}", flush=True)
    else:
        print("Could not load the mystery element.", flush=True)


post_tweet()
