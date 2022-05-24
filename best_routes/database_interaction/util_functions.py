import requests
from flask import request, Response, make_response, jsonify
from .database import db_session
from best_routes.exceptions import NoSuchCityException
from .user_dao import get_user_by_id
from .token_dao import get_tokens_by_user_id
from .models import User


def check_login(token: str) -> bool:
    user_id = int(token.split(":")[0])
    user_tokens = get_tokens_by_user_id(user_id)
    for user_token in user_tokens:
        if user_token.value == token:
            return True
    return False


def get_current_user() -> User:
    user_token = request.headers.get("Token")
    if user_token is None:
        raise KeyError()
    user_id = int(user_token.split(":")[0])
    user = get_user_by_id(user_id)
    return user


def check_service_belonging(user_id: int, service_id: int) -> bool:
    if user_id is not None:
        services = get_user_by_id(user_id).services
        for service in services:
            if service.id == service_id:
                return True
    return False


def process_item(collection: list, item_id: int) -> Response:
    for item in collection:
        if item.id == item_id:
            if request.method == "GET":
                return make_response(jsonify(status="OK", result=item.to_json()), 200)
            elif request.method == "DELETE":
                delete_item(item)
                return make_response(jsonify(status="OK", message="Deleted successfully"), 200)
    return make_response(jsonify(status="error", message="No such item"), 404)


def get_city_id(code: str, direction: str) -> int:
    api_endpoint = "https://avia.tutu.ru/suggest/city/v5/"
    params = {
        "name": code,
        "direction": direction
    }
    response = requests.get(url=api_endpoint, params=params)
    data = response.json()
    if isinstance(data, list):
        for offer in data:
            if offer["code"] == code:
                return int(offer["id"])
        raise NoSuchCityException(code)


def check_station_existence(station_code: str, direction: str) -> bool:
    try:
        get_city_id(station_code, direction)
        return True
    except NoSuchCityException:
        return False


def delete_item(item) -> None:
    db_session.delete(item)
    db_session.commit()
