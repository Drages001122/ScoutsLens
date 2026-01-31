from datetime import date

from flask import Blueprint, jsonify, request
from models import PlayerGameStats, PlayerInformation
from utils.pagination import paginated_response
from utils.rating import calculate_player_score

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/game-stats", methods=["GET"])
@paginated_response(items_key="players", default_per_page=10)
def get_player_game_stats():
    try:
        game_date = request.args.get("game_date")
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
                "rating": score,
            }
            players_with_score.append(player_data)

        players_with_score.sort(
            key=lambda x: x["rating"], reverse=(sort_order == "desc")
        )

        return {"players": players_with_score, "game_date": game_date}
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/player/<int:player_id>/game-stats", methods=["GET"])
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
                "rating": rating,
            }
            game_stats.append(game_data)

        return jsonify({"player_id": player_id, "game_stats": game_stats})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/player/<int:player_id>/average-stats", methods=["GET"])
def get_player_average_stats(player_id):
    try:
        stats = PlayerGameStats.query.filter(PlayerGameStats.personId == player_id).all()
        if not stats:
            return jsonify({"error": "No stats found for this player"}), 404
        total_games = len(stats)

        total_minutes = sum(stat.minutes for stat in stats)
        total_points = sum(
            stat.threePointersMade * 3 + stat.twoPointersMade * 2 + stat.freeThrowsMade
            for stat in stats
        )
        total_rebounds = sum(
            stat.reboundsOffensive + stat.reboundsDefensive for stat in stats
        )
        total_assists = sum(stat.assists for stat in stats)
        total_steals = sum(stat.steals for stat in stats)
        total_blocks = sum(stat.blocks for stat in stats)
        total_turnovers = sum(stat.turnovers for stat in stats)
        total_three_pointers_made = sum(stat.threePointersMade for stat in stats)
        total_three_pointers_attempted = sum(stat.threePointersAttempted for stat in stats)
        total_two_pointers_made = sum(stat.twoPointersMade for stat in stats)
        total_two_pointers_attempted = sum(stat.twoPointersAttempted for stat in stats)
        total_free_throws_made = sum(stat.freeThrowsMade for stat in stats)
        total_free_throws_attempted = sum(stat.freeThrowsAttempted for stat in stats)

        field_goals_made = total_three_pointers_made + total_two_pointers_made
        field_goals_attempted = total_three_pointers_attempted + total_two_pointers_attempted
        field_goal_percentage = (
            (field_goals_made / field_goals_attempted * 100) if field_goals_attempted > 0 else 0
        )
        three_point_percentage = (
            (total_three_pointers_made / total_three_pointers_attempted * 100)
            if total_three_pointers_attempted > 0
            else 0
        )
        free_throw_percentage = (
            (total_free_throws_made / total_free_throws_attempted * 100)
            if total_free_throws_attempted > 0
            else 0
        )

        average_stats = {
            "player_id": player_id,
            "games_played": total_games,
            "minutes_per_game": round(total_minutes / total_games, 1),
            "points_per_game": round(total_points / total_games, 1),
            "rebounds_per_game": round(total_rebounds / total_games, 1),
            "assists_per_game": round(total_assists / total_games, 1),
            "steals_per_game": round(total_steals / total_games, 1),
            "blocks_per_game": round(total_blocks / total_games, 1),
            "turnovers_per_game": round(total_turnovers / total_games, 1),
            "field_goal_percentage": round(field_goal_percentage, 1),
            "three_point_percentage": round(three_point_percentage, 1),
            "free_throw_percentage": round(free_throw_percentage, 1),
        }

        return jsonify(average_stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/value-for-money", methods=["GET"])
def get_value_for_money():
    try:
        # 获取所有球员信息
        players = PlayerInformation.query.all()
        player_data = []

        for player in players:
            # 获取该球员的所有比赛统计
            stats = PlayerGameStats.query.filter(PlayerGameStats.personId == player.player_id).all()
            
            if stats:
                # 计算该球员的平均评分
                total_rating = 0
                for stat in stats:
                    rating = calculate_player_score(
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
                    total_rating += rating
                
                average_rating = total_rating / len(stats)
                
                player_data.append({
                    "player_id": player.player_id,
                    "player_name": player.full_name,
                    "team_name": player.team_name,
                    "position": player.position,
                    "salary": player.salary,
                    "average_rating": average_rating
                })

        return jsonify({"players": player_data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
