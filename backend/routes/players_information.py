from datetime import date

from flask import Blueprint, jsonify, request
from models import PlayerGameStats, PlayerInformation
from utils.pagination import paginated_response
from utils.rating import calculate_player_score

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
@paginated_response(items_key="players", default_per_page=10)
def get_player_game_stats():
    try:
        game_date = request.args.get("game_date")
        sort_by = request.args.get("sort_by", "score")
        sort_order = request.args.get("sort_order", "desc")

        if not game_date:
            return jsonify({"error": "game_date is required"}), 400

        try:
            game_date_obj = date.fromisoformat(game_date)
        except ValueError:
            return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400

        stats = PlayerGameStats.query.filter(
            PlayerGameStats.game_date == game_date_obj
        ).all()

        players_with_score = []
        for stat in stats:
            score = calculate_player_score(
                three_pointers=stat.threePointersMade,
                two_pointers=stat.twoPointersMade,
                free_throws=stat.freeThrowsMade,
                offensive_rebounds=stat.reboundsOffensive,
                defensive_rebounds=stat.reboundsDefensive,
                assists=stat.assists,
                steals=stat.steals,
                blocks=stat.blocks,
                field_goals_attempted=stat.threePointersAttempted
                + stat.twoPointersAttempted,
                field_goals_made=stat.threePointersMade + stat.twoPointersMade,
                free_throws_attempted=stat.freeThrowsAttempted,
                turnovers=stat.turnovers,
                personal_fouls=stat.foulsPersonal,
                team_won=stat.IS_WINNER,
                minutes_played=stat.minutes,
            )

            player_info = PlayerInformation.query.filter_by(
                player_id=stat.personId
            ).first()
            player_name = (
                player_info.full_name if player_info else f"Player {stat.personId}"
            )

            player_data = {
                "player_id": stat.personId,
                "player_name": player_name,
                "team_name": stat.teamName,
                "position": player_info.position if player_info else "",
                "salary": player_info.salary if player_info else 0,
                "minutes": stat.minutes,
                "three_pointers_made": stat.threePointersMade,
                "three_pointers_attempted": stat.threePointersAttempted,
                "two_pointers_made": stat.twoPointersMade,
                "two_pointers_attempted": stat.twoPointersAttempted,
                "free_throws_made": stat.freeThrowsMade,
                "free_throws_attempted": stat.freeThrowsAttempted,
                "offensive_rebounds": stat.reboundsOffensive,
                "defensive_rebounds": stat.reboundsDefensive,
                "assists": stat.assists,
                "steals": stat.steals,
                "blocks": stat.blocks,
                "turnovers": stat.turnovers,
                "personal_fouls": stat.foulsPersonal,
                "team_won": stat.IS_WINNER,
                "points": (
                    stat.threePointersMade * 3
                    + stat.twoPointersMade * 2
                    + stat.freeThrowsMade
                ),
                "score": score,  # TODO: 改名叫 rating
            }
            players_with_score.append(player_data)

        # TODO: 统一按照 score （rating）排序
        if sort_by == "score":
            players_with_score.sort(
                key=lambda x: x["score"], reverse=(sort_order == "desc")
            )
        elif sort_by == "points":
            players_with_score.sort(
                key=lambda x: x["points"], reverse=(sort_order == "desc")
            )

        return {"players": players_with_score, "game_date": game_date}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@players_information_bp.route("/player/<int:player_id>/game-stats", methods=["GET"])
def get_player_game_stats_by_id(player_id):
    try:
        # 查询指定球员的所有比赛统计数据
        stats = (
            PlayerGameStats.query.filter(PlayerGameStats.personId == player_id)
            .order_by(PlayerGameStats.game_date)
            .all()
        )

        # 计算每个比赛的评分
        game_stats = []
        for stat in stats:
            # 计算评分
            rating = calculate_player_score(
                three_pointers=stat.threePointersMade,
                two_pointers=stat.twoPointersMade,
                free_throws=stat.freeThrowsMade,
                offensive_rebounds=stat.reboundsOffensive,
                defensive_rebounds=stat.reboundsDefensive,
                assists=stat.assists,
                steals=stat.steals,
                blocks=stat.blocks,
                field_goals_attempted=stat.threePointersAttempted
                + stat.twoPointersAttempted,
                field_goals_made=stat.threePointersMade + stat.twoPointersMade,
                free_throws_attempted=stat.freeThrowsAttempted,
                turnovers=stat.turnovers,
                personal_fouls=stat.foulsPersonal,
                team_won=stat.IS_WINNER,
                minutes_played=stat.minutes,
            )

            # 构建比赛数据
            game_data = {
                "game_date": stat.game_date.isoformat() if stat.game_date else None,
                "score": rating,
            }
            game_stats.append(game_data)

        return jsonify({"player_id": player_id, "game_stats": game_stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@players_information_bp.route("/teams", methods=["GET"])
def get_teams():
    try:
        # 查询所有不重复的球队
        teams = (
            PlayerInformation.query.with_entities(PlayerInformation.team_name)
            .distinct()
            .all()
        )

        # 构建球队列表
        teams_list = []
        for i, team in enumerate(teams, 1):
            teams_list.append({"team_id": i, "team_name": team[0]})

        return jsonify({"teams": teams_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@players_information_bp.route("/team/<int:team_id>/players", methods=["GET"])
def get_team_players(team_id):
    try:
        # 查询所有球队
        teams = PlayerInformation.query.distinct(PlayerInformation.team_name).all()

        # 根据team_id获取对应的球队名称
        if team_id <= 0 or team_id > len(teams):
            return jsonify({"error": "Invalid team ID"}), 400

        team_name = teams[team_id - 1].team_name

        # 查询该球队的所有球员
        players = PlayerInformation.query.filter_by(team_name=team_name).all()

        # 构建球员列表
        players_list = [player.to_dict() for player in players]

        return jsonify({"players": players_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
