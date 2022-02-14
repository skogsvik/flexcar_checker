import requests

URL = 'https://www.flexcar.com/subscription-web/api/inventory/v1'


def clean_response(response, *_, **__):
    response.raise_for_status()
    if not response.json().get('success'):
        raise ValueError(f'Failed request: {response:r}')


class FlexCar():
    sesion = None
    location_id = None

    def __init__(self, city='Atlanta'):
        self.session = requests.Session()
        self.session.headers = {'Accept': 'application/json, text/plain, */*',
                                'Accept-Language': 'en-US,en;q=0.5',
                                'Accept-Encoding': 'gzip, deflate, br',
                                'DNT': '1',
                                'Connection': 'keep-alive',
                                'Cache-Control': 'max-age=0',
                                'cache-control': 'no-cache'}
        self.session.hooks['response'].append(clean_response)
        self.location_id = self.get_location(city)

    def get(self, *args, **kwargs):
        return self.session.get(*args, **kwargs).json()['data']

    def get_location(self, city):
        response = self.get(f'{URL}/markets')
        for location in response:
            if location['name'].lower() == city.lower():
                return location['id']
        raise ValueError(
            f'{city} not found among cities: {", ".join(loc["name"] for loc in response)}')

    def iter_available_inventory(self, **filters):
        filters.setdefault('marketId', self.location_id)
        response = self.get(f'{URL}/inventories', params={
            'filters[]': [f'{key}|=|{value}' for key, value in filters.items()],
            'page': '1',
            'pageSize': '900'
        })
        yield from (car for car in response if car['colors'])


if __name__ == '__main__':
    flex_car = FlexCar('Atlanta')
    print(len(list(flex_car.iter_available_inventory(priceWeekly=80))))

