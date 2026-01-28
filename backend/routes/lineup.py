from flask import Blueprint, jsonify, request
from models import Lineup, LineupPlayer, db
from utils import get_current_user_id

lineup_bp = Blueprint("lineup", __name__)


@lineup_bp.route("/create", methods=["POST"])
def create_lineup():
    """
    创建新阵容
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401
        data = request.get_json()

        if not data:
            return jsonify({"error": "请求数据为空"}), 400

        name = data.get("name")
        starting_players = data.get("starting_players", [])
        bench_players = data.get("bench_players", [])

        if not name:
            return jsonify({"error": "阵容名称不能为空"}), 400

        if not starting_players and not bench_players:
            return jsonify({"error": "阵容至少需要一名球员"}), 400

        # 计算总薪资
        total_salary = sum(p.get("salary", 0) for p in starting_players + bench_players)

        # 创建阵容
        new_lineup = Lineup(user_id=user_id, name=name, total_salary=total_salary)
        db.session.add(new_lineup)
        db.session.flush()  # 获取阵容ID

        # 添加首发球员
        for player in starting_players:
            lineup_player = LineupPlayer(
                lineup_id=new_lineup.id,
                player_id=player.get("player_id"),
                full_name=player.get("full_name"),
                team_name=player.get("team_name"),
                position=player.get("position"),
                salary=player.get("salary"),
                slot=player.get("slot"),
                is_starting=True,
            )
            db.session.add(lineup_player)

        # 添加替补球员
        for player in bench_players:
            lineup_player = LineupPlayer(
                lineup_id=new_lineup.id,
                player_id=player.get("player_id"),
                full_name=player.get("full_name"),
                team_name=player.get("team_name"),
                position=player.get("position"),
                salary=player.get("salary"),
                slot=None,
                is_starting=False,
            )
            db.session.add(lineup_player)

        db.session.commit()

        return jsonify({"message": "阵容创建成功", "lineup": new_lineup.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@lineup_bp.route("/list", methods=["GET"])
def get_user_lineups():
    """
    获取用户的所有阵容
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401

        lineups = (
            Lineup.query.filter_by(user_id=user_id)
            .order_by(Lineup.created_at.desc())
            .all()
        )

        return jsonify({"lineups": [lineup.to_dict() for lineup in lineups]}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lineup_bp.route("/<int:lineup_id>", methods=["GET"])
def get_lineup(lineup_id):
    """
    获取单个阵容详情
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401

        lineup = Lineup.query.filter_by(id=lineup_id, user_id=user_id).first()

        if not lineup:
            return jsonify({"error": "阵容不存在或无权限访问"}), 404

        return jsonify({"lineup": lineup.to_dict()}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@lineup_bp.route("/<int:lineup_id>", methods=["DELETE"])
def delete_lineup(lineup_id):
    """
    删除阵容
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401

        lineup = Lineup.query.filter_by(id=lineup_id, user_id=user_id).first()

        if not lineup:
            return jsonify({"error": "阵容不存在或无权限访问"}), 404

        db.session.delete(lineup)
        db.session.commit()

        return jsonify({"message": "阵容删除成功"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
