import tweepy
from datetime import datetime, timezone, timedelta
from app import guess_distribution, recent_elements
import os
import math

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


def calculate_squares(guesses, max_squares):
    max_guess = max(guesses)
    squares = [max(1, math.ceil((guess / max_guess) * max_squares))
               for guess in guesses]
    return squares


def generate_distribution(date):
    if date not in guess_distribution:
        return "\n".join([f"{pos[i]} {'🟩'} 0%" for i in range(1, 9)]) + f"\n❌ {'🟩'} 0%"

    distribution = guess_distribution[date]

    total_count = 0
    for i in range(1, 10):
        total_count += distribution[str(i)]

    total_count = total_count if total_count != 0 else 1

    formatted_distribution = ""

    guesses = list(distribution.values())

    squares = calculate_squares(guesses, 5)

    for i in range(1, 10):
        if i == 9:
            formatted_distribution += f"❌ {'🟩' * squares[i - 1]} {round((guesses[i - 1] / total_count) * 100)}%"
        else:
            formatted_distribution += f"{pos[i]} {'🟩' * squares[i - 1]} {round((guesses[i - 1] / total_count) * 100)}%\n"

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
