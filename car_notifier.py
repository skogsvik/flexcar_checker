import os
import pickle
import time
from contextlib import suppress as until

import requests

from flexcar import FlexCar

CACHE = os.environ.get('CAR_CHECKER_CACHE_PATH')
if not CACHE:
    CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.car_checker_cache')
MAILGUN_URL = f'https://api.mailgun.net/v3/{os.environ["MAILGUN_URL"]}/messages'


def send_email(subject, body):
    """
    Send email using Mailgun using settings from environment variables
    """
    requests.post(
        MAILGUN_URL,
        auth=('api', os.environ['MAILGUN_API_KEY']),
        data={
            'from': f'FlexCar Checker <{os.environ["MAILGUN_SENDER"]}>',
            'to': os.environ['MAILGUN_RECEIVERS'].split(' '),
            'subject': subject,
            'text': body
        }
    ).raise_for_status()


def email_error():
    """
    Grab the traceback of the current exception and send it as an email to the admin of the script
    """
    import traceback
    requests.post(
        MAILGUN_URL,
        auth=('api', os.environ['MAILGUN_API_KEY']),
        data={
            'from': f'FlexCar Checker <{os.environ["MAILGUN_SENDER"]}>',
            'to': os.environ['MAILGUN_SENDER'],
            'subject': 'Python Exception',
            'text': f'An exception occured:\n{traceback.format_exc()}'
        }
    ).raise_for_status()


def load_cache():
    try:
        with open(CACHE, 'br') as f:
            return pickle.load(f)
    except (IOError, EOFError):
        # File didn't exist or was not pickled
        return {}


def simplify_car(car):
    return (f'{car["make"]["name"]} {car["model"]["name"]}', car['colors'],)


def car_to_string(car, colors):
    return f'\t{car}: {", ".join(f"{color} ({count})" for color, count in colors.items())}'


def main(price=80, sleep=60):
    """
    Check for new cars in a loop, and send email if new cars pop up
    """
    flex_car = FlexCar('Atlanta')

    with until(KeyboardInterrupt):
        prev_notified_cars = load_cache()
        while True:
            available_cars = dict(map(simplify_car,
                                      flex_car.iter_available_inventory(priceWeekly=price)))

            new_cars = [car for car in available_cars if car not in prev_notified_cars]
            print(f'{len(new_cars)} new cars found, {len(available_cars)} total')
            if new_cars:
                new_cars_str = '\n'.join(car_to_string(car, available_cars[car])
                                         for car in new_cars)
                previous_cars_str = '\n'.join(car_to_string(car, colors)
                                              for car, colors in available_cars.items()
                                              if car not in new_cars)
                send_email('New cars available on FlexCar',
                           f'New cars are available:\n{new_cars_str}\n\n'
                           f'Previously notified cars:\n{previous_cars_str}')

            if prev_notified_cars != available_cars:
                with open(CACHE, 'bw') as f:
                    pickle.dump(available_cars, f)
                prev_notified_cars = available_cars

            time.sleep(sleep)


if __name__ == '__main__':
    try:
        main(80, 60)
    except:
        email_error()
        raise
