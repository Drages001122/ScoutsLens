import os

from flask import Blueprint, jsonify, request, send_from_directory
from models import PlayerInformation

players_information_bp = Blueprint("players_information", __name__)


@players_information_bp.route("/list", methods=["GET"])
def get_players():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        salary_min = request.args.get("salary_min", 0, type=int)
        salary_max = request.args.get("salary_max", 60000000, type=int)

        query = PlayerInformation.query.filter(
            PlayerInformation.salary >= salary_min,
            PlayerInformation.salary <= salary_max,
        )

        total = query.count()
        players = query.order_by(PlayerInformation.salary.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        players_list = [player.to_dict() for player in players.items]
        total_pages = players.pages
        return jsonify(
            {
                "players": players_list,
                "pagination": {
                    "current_page": page,
                    "per_page": per_page,
                    "total_items": total,
                    "total_pages": total_pages,
                },
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@players_information_bp.route("/avatar/<int:player_id>", methods=["GET"])
def get_player_avatar(player_id):
    try:
        avatars_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "database",
            "player_avatars",
        )
        avatar_file = f"{player_id}.png"
        avatar_path = os.path.join(avatars_dir, avatar_file)
        if os.path.exists(avatar_path):
            return send_from_directory(avatars_dir, avatar_file)
        else:
            # Return 404 if avatar not found
            return jsonify({"error": "Avatar not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
