import tweepy
import json
import time
import random
import pytz
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Timezone setup
TIMEZONE = pytz.UTC


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

# Set up Chrome options for Selenium
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
driver = webdriver.Chrome(options=chrome_options)


def get_mystery_element():
    try:
        driver.get("https://elementlegame.com/")
        print("On site", flush=True)

        # Wait until the page has loaded completely
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )

        # Access the localStorage item
        mystery_element = driver.execute_script(
            'return window.localStorage.getItem("mysteryElement");'
        )
        print("Got element:", mystery_element, flush=True)

        return mystery_element

    except Exception as e:
        print(f"Error retrieving mystery element: {e}", flush=True)
        return None


def save_mystery_element():
    print("Running save_mystery_element function", flush=True)

    mystery_element = get_mystery_element()

    if mystery_element:
        # Specify the full path to the file
        file_path = "/home/Haokai/Elementle-Post-Bot/X-Bot-Elementle/mystery_element.txt"

        with open(file_path, "w") as file:
            file.write(mystery_element)
        print("Saved mystery element for the day", flush=True)
    else:
        print("Could not retrieve the mystery element.", flush=True)


def load_previous_mystery_element():
    try:
        # Specify the full path to the file
        file_path = "/home/Haokai/Elementle-Post-Bot/X-Bot-Elementle/mystery_element.txt"

        with open(file_path, "r") as file:
            data = json.load(file)  # Load JSON from file

        # Access the value with the key "name" if it exists
        return data.get('name')

    except FileNotFoundError:
        print("File not found.", flush=True)
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON.", flush=True)
        return None
    except Exception as e:
        print(f"Error loading mystery element: {e}", flush=True)
        return None



def generate_random_distribution():
    bins = [1] * 9
    remaining = 91
    weights = [0.1, 0.3, 1.5, 1.5, 1.5, 1.5, 1.5, 1.5, 0.6]

    for _ in range(remaining):
        selected_bin = random.choices(range(9), weights=weights, k=1)[0]
        bins[selected_bin] += 1

    formatted_distribution = f"""
    1️⃣  {'🟩' * max(1, bins[0] // 5)} {bins[0]}%
    2️⃣  {'🟩' * max(1, bins[1] // 5)} {bins[1]}%
    3️⃣  {'🟩' * max(1, bins[2] // 5)} {bins[2]}%
    4️⃣  {'🟩' * max(1, bins[3] // 5)} {bins[3]}%
    5️⃣  {'🟩' * max(1, bins[4] // 5)} {bins[4]}%
    6️⃣  {'🟩' * max(1, bins[5] // 5)} {bins[5]}%
    7️⃣  {'🟩' * max(1, bins[6] // 5)} {bins[6]}%
    8️⃣  {'🟩' * max(1, bins[7] // 5)} {bins[7]}%
    ❌  {'🟩' * max(1, bins[8] // 5)} {bins[8]}%
    """

    return formatted_distribution


def post_tweet():
    mystery_element = load_previous_mystery_element()
    today = datetime.now(TIMEZONE)
    yesterday = today - timedelta(days=1)
    yesterday_formatted = yesterday.strftime('%Y-%m-%d')

    distribution_text = generate_random_distribution()

    if mystery_element:
        # Construct the full file path for the image
        image_path = f"/home/Haokai/Elementle-Post-Bot/X-Bot-Elementle/{mystery_element}.jpg"

        # Compose the message
        message = f"Yesterday's #Elementle was {mystery_element} 🧪\n\n{distribution_text}\n\nhttps://elementlegame.com\nDate: {yesterday_formatted}"

        try:
            # Upload the image and create the tweet
            media_id = api.media_upload(filename=image_path).media_id_string
            client.create_tweet(text=message, media_ids=[media_id])
            print("Tweet posted successfully!", flush=True)
        except Exception as e:
            print(f"Error posting tweet: {e}", flush=True)
    else:
        print("Could not load the mystery element.", flush=True)



while True:
    now = datetime.now(TIMEZONE)
    if now.hour == 23 and now.minute == 58:
        save_mystery_element()
        time.sleep(120)
    elif now.hour == 10 and now.minute == 0:
        post_tweet()
        time.sleep(120)
    else:
        time.sleep(30)
