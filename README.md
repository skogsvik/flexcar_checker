# Python client for FlexCar
Basic python package for looking up available cars in your city on Flexcar.com

## Requirements
* Python 3.8+
* [Pipenv](https://github.com/pypa/pipenv)

## Installation
1. Clone the repository using: `git clone`
1. Install python environment: `pipenv install`

### setup `.env`
To use the `car_notifier.py` script and send out a notifying email using [mailgun](https://www.mailgun.com) the following envionment variables need to be set:
* `MAILGUN_URL`
* `MAILGUN_API_KEY`
* `MAILGUN_SENDER`
* `MAILGUN_RECEIVERS`: comma separated list of recipients
