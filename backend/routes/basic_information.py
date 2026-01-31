from flask import Blueprint, jsonify, request
from models import PlayerInformation
from utils.pagination import paginated_response

basic_information_bp = Blueprint("basic_information", __name__)


@basic_information_bp.route("/list-players", methods=["GET"])
@paginated_response(items_key="players", default_per_page=10)
def get_players():
    try:
        salary_min = request.args.get("salary_min", 0, type=int)
        salary_max = request.args.get("salary_max", 60000000, type=int)
        teams = request.args.getlist("teams")

        query = PlayerInformation.query.filter(
            PlayerInformation.salary >= salary_min,
            PlayerInformation.salary <= salary_max,
        )
        if teams:
            query = query.filter(PlayerInformation.team_name.in_(teams))

        players = query.order_by(PlayerInformation.salary.desc()).all()
        players_list = [player.to_dict() for player in players]

        return {"players": players_list}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@basic_information_bp.route("/teams", methods=["GET"])
def get_teams():
    try:
        teams = (
            PlayerInformation.query.with_entities(PlayerInformation.team_name)
            .distinct()
            .all()
        )
        teams_list = []
        for i, team in enumerate(teams, 1):
            teams_list.append({"team_id": i, "team_name": team[0]})
        return jsonify({"teams": teams_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@basic_information_bp.route("/team/<int:team_id>/players", methods=["GET"])
def get_team_players(team_id):
    try:
        teams = (
            PlayerInformation.query.with_entities(PlayerInformation.team_name)
            .distinct()
            .all()
        )
        if team_id <= 0 or team_id > len(teams):
            return jsonify({"error": "Invalid team ID"}), 400
        team_name = teams[team_id - 1].team_name
        players = PlayerInformation.query.filter_by(team_name=team_name).all()
        players_list = [player.to_dict() for player in players]
        return jsonify({"players": players_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
