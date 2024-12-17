from flask import Flask, jsonify
import datetime
import random
from pytz import timezone
from flask_cors import CORS

from elements import elements


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://elementlegame.com"}})

recent_elements = {"20241216": {"name": 'Antimony', "atomicNumber": 51, "family": 'Metalloid',
     "hint": 'Used in flame retardants and batteries.', "symbol": 'Sb'}}  # {date: element}


def get_most_recent_date():
    most_recent_zone = timezone('Pacific/Kiritimati')
    now = datetime.datetime.now(most_recent_zone)
    print(now)
    return now.strftime('%Y%m%d')  # ISO format (YYYYMMDD)


def update_recent_elements():
    current_date = get_most_recent_date()

    if current_date in recent_elements:
        return

    seed = int(current_date)
    random.seed(seed)

    mystery_element = random.choice(elements)

    # Ensure no repeats within an 80-day time frame
    while mystery_element in recent_elements.values():
        seed -= 100000
        random.seed(seed)
        mystery_element = random.choice(elements)

    recent_elements[current_date] = mystery_element

    if len(recent_elements) > 80:
        oldest_date = min(recent_elements.keys())
        del recent_elements[oldest_date]


@app.route('/')
def home():
    update_recent_elements()

    return jsonify(recent_elements)


if __name__ == '__main__':
    app.run()
