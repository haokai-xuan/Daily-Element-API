from flask import Flask, jsonify, request
import datetime
import random
from pytz import timezone
from flask_cors import CORS
import json
import os

from elements import elements


app = Flask(__name__)
CORS(app)

current_directory = os.path.dirname(os.path.abspath(__file__))
recent_elements_path = os.path.join(current_directory, 'recent_elements.json')
guess_distribution_path = os.path.join(
    current_directory, 'guess_distribution.json')

# We will run this slightly before new day to ensure smoothness, hence the timedelta


def get_most_recent_date():
    most_recent_zone = timezone('Pacific/Kiritimati')
    now = datetime.datetime.now(most_recent_zone)

    next_day = now + datetime.timedelta(days=1)

    return next_day.strftime('%Y%m%d')  # ISO format (YYYYMMDD)


# Elements
def save_recent_elements():
    with open(recent_elements_path, 'w') as file:
        json.dump(recent_elements, file, indent=4)


def load_recent_elements():
    try:
        with open(recent_elements_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# {date: element}
recent_elements = load_recent_elements()


def update_recent_elements():
    global recent_elements
    current_date = get_most_recent_date()

    print(f"Updated {current_date}")

    if current_date in recent_elements:
        return

    seed = int(current_date)
    random.seed(seed)

    mystery_element = random.choice(elements)
    mystery_element_name = mystery_element['name']

    recent_elements_names = [element['name'] for element in recent_elements.values()]

    # Ensure no repeats within an 80-day time frame
    while mystery_element_name in recent_elements_names:
        seed -= 100000
        random.seed(seed)
        mystery_element = random.choice(elements)
        mystery_element_name = mystery_element['name']

    recent_elements[current_date] = mystery_element

    if len(recent_elements) > 80:
        oldest_date = min(recent_elements.keys())
        del recent_elements[oldest_date]

    save_recent_elements()


# Guess distribution
def load_guess_distribution():
    try:
        with open(guess_distribution_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_guess_distribution():
    with open(guess_distribution_path, 'w') as file:
        json.dump(guess_distribution, file)


# {"date": {Str: Num, Str: Num}}
guess_distribution = load_guess_distribution()


@app.route('/guess_distribution', methods=['POST', 'GET'])
def distribution():
    global guess_distribution
    guess_distribution = load_guess_distribution()  # all keys become string

    if request.method == 'POST':
        data = request.get_json()
        local_date = data['localDate']
        guesses = data['guesses']

        if local_date not in guess_distribution:
            guess_distribution[local_date] = {str(i): 0 for i in range(1, 9)}
            guess_distribution[local_date]["9"] = 0  # Num of failed attempts

        guess_distribution[local_date][str(guesses)] += 1

        if len(guess_distribution) > 3:
            oldest_date = min(guess_distribution.keys())
            del guess_distribution[oldest_date]

        save_guess_distribution()

        return jsonify(guess_distribution)

    elif request.method == 'GET':
        return jsonify(guess_distribution)


# Home
@app.route('/', methods=['GET'])
def home():
    global recent_elements
    recent_elements = load_recent_elements()
    return jsonify(recent_elements)


if __name__ == '__main__':
    app.run()
