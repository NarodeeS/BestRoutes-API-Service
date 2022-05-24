from flask import Blueprint, make_response, request, jsonify
from best_routes.middleware import exception_handler
from best_routes.transport_utils.avia_routes import get_avia_routes, get_avia_trips

base_blueprint = Blueprint("base_blueprint", __name__)


@base_blueprint.route("/routes/avia", methods=["GET", "POST"])
@exception_handler
def routes_avia():
    return make_response(jsonify(result=get_avia_routes(request.args), status="OK"), 200)


@base_blueprint.route("/routes/avia/trips", methods=["GET", "POST"])
@exception_handler
def routes_avia_trip():
    return make_response(jsonify(result=get_avia_trips(request.args), status="OK"), 200)
