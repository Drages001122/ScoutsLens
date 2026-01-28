from flask import Blueprint, jsonify, request
from models import PlayerInformation

players_information_bp = Blueprint("players_information", __name__)


@players_information_bp.route("/api/players_information", methods=["GET"])
def get_players():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        total = PlayerInformation.query.count()
        players = PlayerInformation.query.order_by(PlayerInformation.id).paginate(
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
