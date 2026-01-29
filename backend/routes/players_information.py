import os
from datetime import date

from flask import Blueprint, jsonify, request, send_from_directory
from models import PlayerInformation, PlayerGameStats
from rating import calculate_player_score

players_information_bp = Blueprint("players_information", __name__)


@players_information_bp.route("/list", methods=["GET"])
def get_players():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        salary_min = request.args.get("salary_min", 0, type=int)
        salary_max = request.args.get("salary_max", 60000000, type=int)
        teams = request.args.getlist("teams")

        query = PlayerInformation.query.filter(
            PlayerInformation.salary >= salary_min,
            PlayerInformation.salary <= salary_max,
        )
        if teams:
            query = query.filter(PlayerInformation.team_name.in_(teams))

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


@players_information_bp.route("/game-stats", methods=["GET"])
def get_player_game_stats():
    try:
        # 获取查询参数
        game_date = request.args.get("game_date")
        sort_by = request.args.get("sort_by", "score")
        sort_order = request.args.get("sort_order", "desc")
        
        if not game_date:
            return jsonify({"error": "game_date is required"}), 400
        
        # 转换日期格式
        try:
            game_date_obj = date.fromisoformat(game_date)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
        
        # 查询指定日期的球员统计数据
        stats = PlayerGameStats.query.filter(
            PlayerGameStats.game_date == game_date_obj
        ).all()
        
        # 计算每个球员的评分
        players_with_score = []
        for stat in stats:
            # 计算评分
            score = calculate_player_score(
                three_pointers=stat.threePointersMade,
                two_pointers=stat.twoPointersMade,
                free_throws=stat.freeThrowsMade,
                offensive_rebounds=stat.reboundsOffensive,
                defensive_rebounds=stat.reboundsDefensive,
                assists=stat.assists,
                steals=stat.steals,
                blocks=stat.blocks,
                field_goals_attempted=stat.threePointersAttempted + stat.twoPointersAttempted,
                field_goals_made=stat.threePointersMade + stat.twoPointersMade,
                free_throws_attempted=stat.freeThrowsAttempted,
                turnovers=stat.turnovers,
                personal_fouls=stat.foulsPersonal,
                team_won=stat.IS_WINNER,
                minutes_played=stat.minutes,
            )
            
            # 构建球员数据
            player_data = {
                "player_id": stat.personId,
                "team_name": stat.teamName,
                "minutes": stat.minutes,
                "three_pointers": stat.threePointersMade,
                "two_pointers": stat.twoPointersMade,
                "free_throws": stat.freeThrowsMade,
                "offensive_rebounds": stat.reboundsOffensive,
                "defensive_rebounds": stat.reboundsDefensive,
                "assists": stat.assists,
                "steals": stat.steals,
                "blocks": stat.blocks,
                "turnovers": stat.turnovers,
                "personal_fouls": stat.foulsPersonal,
                "team_won": stat.IS_WINNER,
                "score": score
            }
            players_with_score.append(player_data)
        
        # 排序
        if sort_by == "score":
            players_with_score.sort(
                key=lambda x: x["score"],
                reverse=(sort_order == "desc")
            )
        
        return jsonify({
            "players": players_with_score,
            "game_date": game_date,
            "total_players": len(players_with_score)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500