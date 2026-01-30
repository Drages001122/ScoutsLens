import time
from datetime import datetime

from flask import Blueprint, jsonify, request
from models import Lineup, LineupPlayer, User, db
from routes.rule import SALARY_CAP
from utils.jwt import get_current_user_id
from utils.rule import PlayerCountRule, SalaryRule

lineup_bp = Blueprint("lineup", __name__)


def verify_lineup(starting_players: list, bench_players: list):
    salary_rule = SalaryRule(SALARY_CAP)
    player_count_rule = PlayerCountRule(5, 7)

    valid, err_msg = True, ""

    if not salary_rule.verify(starting_players, bench_players):
        err_msg = "阵容薪资超过限制"
        valid = False
    if not player_count_rule.verify(starting_players, bench_players):
        err_msg = "球员数量不符合规则"
        valid = False

    return valid, err_msg


def calculate_total_salary(starting_players: list, bench_players: list):
    return sum(p.get("salary", 0) for p in starting_players + bench_players)


@lineup_bp.route("/create", methods=["POST"])
def create_lineup():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401
        data = request.get_json()

        if not data:
            return jsonify({"error": "请求数据为空"}), 400

        name = data.get("name")
        date_str = data.get("date")
        starting_players = data.get("starting_players", [])
        bench_players = data.get("bench_players", [])

        # 当前不要求用户提供阵容名, name 一定为空
        if not name:
            timestamp = int(time.time())
            name = f"阵容_{date_str}_{timestamp}"

        if not date_str:
            return jsonify({"error": "比赛日期不能为空"}), 400

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "日期格式不正确，请使用 YYYY-MM-DD 格式"}), 400

        if not starting_players and not bench_players:
            return jsonify({"error": "阵容至少需要一名球员"}), 400

        valid, err_msg = verify_lineup(starting_players, bench_players)
        if not valid:
            return jsonify({"error": err_msg}), 400

        new_lineup = Lineup(
            user_id=user_id,
            name=name,
            date=date,
            total_salary=calculate_total_salary(starting_players, bench_players),
        )
        db.session.add(new_lineup)
        db.session.flush()

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


@lineup_bp.route("/by-date", methods=["GET"])
def get_lineups_by_date():
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({"error": "未授权，请先登录"}), 401

        date_str = request.args.get("date")
        if not date_str:
            return jsonify({"error": "日期参数不能为空"}), 400

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "日期格式不正确，请使用 YYYY-MM-DD 格式"}), 400

        lineups = (
            Lineup.query.filter_by(date=date).order_by(Lineup.created_at.desc()).all()
        )

        result = []
        for lineup in lineups:
            lineup_dict = lineup.to_dict()
            user = User.query.get(lineup.user_id)
            if user:
                lineup_dict["username"] = user.username
            else:
                lineup_dict["username"] = "未知用户"
            result.append(lineup_dict)

        return jsonify({"lineups": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
