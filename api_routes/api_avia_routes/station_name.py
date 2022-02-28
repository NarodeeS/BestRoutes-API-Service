import requests


def get_airport_name_by_code(*args) -> dict:
    #  Get station names from aeroflot API
    api_endpoint = "https://www.aeroflot.ru/sb/booking/api/app/cities/v1"
    params = {
        "lang": "ru"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:97.0) Gecko/20100101 Firefox/97.0"
    }
    response = requests.get(url=api_endpoint, params=params, headers=headers)
    data = response.json()
    result = {}
    for arg in args:
        for city in data["data"]["cities"]:
            if city["code"] == arg:
                result[arg] = {
                    "name": city["name"],
                    "country": city["country_name"],
                    "code": arg
                }
            else:
                for airport in city["airports"]:
                    if airport["code"] == arg:
                        result[arg] = {
                            "name": f"{city['name']}({airport['name']})",
                            "country": city["country_name"],
                            "code": arg
                        }
    return result
