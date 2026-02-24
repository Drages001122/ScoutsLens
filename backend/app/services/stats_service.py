from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional, Tuple

from app.models import PlayerGameStats, PlayerInformation
from sqlalchemy.orm import Session


def calculate_player_score(
    three_pointers: int,
    two_pointers: int,
    free_throws: int,
    offensive_rebounds: int,
    defensive_rebounds: int,
    assists: int,
    steals: int,
    blocks: int,
    field_goals_attempted: int,
    field_goals_made: int,
    free_throws_attempted: int,
    turnovers: int,
    personal_fouls: int,
    team_won: bool,
    minutes_played: int,
) -> float:
    """
    计算球员评分

    Args:
        three_pointers: 三分球命中数
        two_pointers: 两分球命中数
        free_throws: 罚球命中数
        offensive_rebounds: 进攻篮板
        defensive_rebounds: 防守篮板
        assists: 助攻
        steals: 抢断
        blocks: 盖帽
        field_goals_attempted: 投篮出手数
        field_goals_made: 投篮命中数
        free_throws_attempted: 罚球出手数
        turnovers: 失误
        personal_fouls: 犯规
        team_won: 是否赢球
        minutes_played: 出场时间

    Returns:
        球员评分
    """
    score = (
        (three_pointers * 1.5)
        + two_pointers
        + (free_throws * 0.5)
        + offensive_rebounds
        + (defensive_rebounds * 0.7)
        + assists
        + (steals * 1.2)
        + (blocks * 1.2)
        - ((field_goals_attempted - field_goals_made) * 0.7)
        - ((free_throws_attempted - free_throws) * 0.4)
        - (turnovers * 1.2)
        - (personal_fouls * 0.4)
    )
    if minutes_played > 0:
        if team_won:
            score += 2
        else:
            score -= 2
    return score


class StatsService:
    """统计服务"""

    @staticmethod
    def get_player_average_stats_leaderboard(
        db: Session,
        sort_order: str = "desc",
        sort_by: str = "rating",
    ) -> List[Dict]:
        """
        获取球员平均数据排行榜

        Args:
            db: 数据库会话
            sort_order: 排序顺序

        Returns:
            球员排行榜列表
        """
        stats = db.query(PlayerGameStats).all()

        player_stats = defaultdict(list)
        for stat in stats:
            player_stats[stat.personId].append(stat)

        players_with_score = []
        for player_id, stat_list in player_stats.items():
            total_games = len(stat_list)

            total_minutes = sum(stat.minutes for stat in stat_list)
            total_three_pointers_made = sum(
                stat.threePointersMade for stat in stat_list
            )
            total_three_pointers_attempted = sum(
                stat.threePointersAttempted for stat in stat_list
            )
            total_two_pointers_made = sum(stat.twoPointersMade for stat in stat_list)
            total_two_pointers_attempted = sum(
                stat.twoPointersAttempted for stat in stat_list
            )
            total_free_throws_made = sum(stat.freeThrowsMade for stat in stat_list)
            total_free_throws_attempted = sum(
                stat.freeThrowsAttempted for stat in stat_list
            )
            total_offensive_rebounds = sum(stat.reboundsOffensive for stat in stat_list)
            total_defensive_rebounds = sum(stat.reboundsDefensive for stat in stat_list)
            total_assists = sum(stat.assists for stat in stat_list)
            total_steals = sum(stat.steals for stat in stat_list)
            total_blocks = sum(stat.blocks for stat in stat_list)
            total_turnovers = sum(stat.turnovers for stat in stat_list)
            total_personal_fouls = sum(stat.foulsPersonal for stat in stat_list)
            total_points = sum(
                stat.threePointersMade * 3
                + stat.twoPointersMade * 2
                + stat.freeThrowsMade
                for stat in stat_list
            )

            avg_minutes = total_minutes / total_games
            avg_three_pointers_made = total_three_pointers_made / total_games
            avg_three_pointers_attempted = total_three_pointers_attempted / total_games
            avg_two_pointers_made = total_two_pointers_made / total_games
            avg_two_pointers_attempted = total_two_pointers_attempted / total_games
            avg_free_throws_made = total_free_throws_made / total_games
            avg_free_throws_attempted = total_free_throws_attempted / total_games
            avg_offensive_rebounds = total_offensive_rebounds / total_games
            avg_defensive_rebounds = total_defensive_rebounds / total_games
            avg_assists = total_assists / total_games
            avg_steals = total_steals / total_games
            avg_blocks = total_blocks / total_games
            avg_turnovers = total_turnovers / total_games
            avg_personal_fouls = total_personal_fouls / total_games
            avg_points = total_points / total_games

            avg_score = calculate_player_score(
                three_pointers=avg_three_pointers_made,
                two_pointers=avg_two_pointers_made,
                free_throws=avg_free_throws_made,
                offensive_rebounds=avg_offensive_rebounds,
                defensive_rebounds=avg_defensive_rebounds,
                assists=avg_assists,
                steals=avg_steals,
                blocks=avg_blocks,
                field_goals_attempted=avg_three_pointers_attempted
                + avg_two_pointers_attempted,
                field_goals_made=avg_three_pointers_made + avg_two_pointers_made,
                free_throws_attempted=avg_free_throws_attempted,
                turnovers=avg_turnovers,
                personal_fouls=avg_personal_fouls,
                team_won=True,
                minutes_played=avg_minutes,
            )

            player_info = (
                db.query(PlayerInformation).filter_by(player_id=player_id).first()
            )
            player_name = (
                player_info.full_name if player_info else f"Player {player_id}"
            )

            three_point_percentage = (
                (avg_three_pointers_made / avg_three_pointers_attempted * 100)
                if avg_three_pointers_attempted > 0
                else 0
            )
            two_point_percentage = (
                (avg_two_pointers_made / avg_two_pointers_attempted * 100)
                if avg_two_pointers_attempted > 0
                else 0
            )
            free_throw_percentage = (
                (avg_free_throws_made / avg_free_throws_attempted * 100)
                if avg_free_throws_attempted > 0
                else 0
            )

            player_data = {
                "player_id": player_id,
                "player_name": player_name,
                "team_name": stat_list[0].teamName if stat_list else "",
                "position": player_info.position if player_info else "",
                "salary": player_info.salary if player_info else 0,
                "minutes": avg_minutes,
                "three_pointers_made": avg_three_pointers_made,
                "three_pointers_attempted": avg_three_pointers_attempted,
                "three_pointers_percentage": three_point_percentage,
                "two_pointers_made": avg_two_pointers_made,
                "two_pointers_attempted": avg_two_pointers_attempted,
                "two_pointers_percentage": two_point_percentage,
                "free_throws_made": avg_free_throws_made,
                "free_throws_attempted": avg_free_throws_attempted,
                "free_throws_percentage": free_throw_percentage,
                "offensive_rebounds": avg_offensive_rebounds,
                "defensive_rebounds": avg_defensive_rebounds,
                "assists": avg_assists,
                "steals": avg_steals,
                "blocks": avg_blocks,
                "turnovers": avg_turnovers,
                "personal_fouls": avg_personal_fouls,
                "team_won": True,
                "points": avg_points,
                "rating": avg_score,
                "games_played": total_games,
            }
            players_with_score.append(player_data)

        valid_sort_fields = {
            "salary", "minutes", "points", "offensive_rebounds", "defensive_rebounds",
            "assists", "steals", "blocks", "turnovers", "personal_fouls", "games_played",
            "three_pointers_made", "three_pointers_attempted", "three_pointers_percentage",
            "two_pointers_made", "two_pointers_attempted", "two_pointers_percentage",
            "free_throws_made", "free_throws_attempted", "free_throws_percentage",
            "rating"
        }
        sort_field = sort_by if sort_by in valid_sort_fields else "rating"
        players_with_score.sort(
            key=lambda x: x[sort_field], reverse=(sort_order == "desc")
        )
        return players_with_score

    @staticmethod
    def get_player_game_stats(
        db: Session,
        game_date: str,
        sort_order: str = "desc",
        sort_by: str = "rating",
    ) -> Tuple[List[Dict], str]:
        """
        获取指定日期的球员比赛数据

        Args:
            db: 数据库会话
            game_date: 比赛日期
            sort_order: 排序顺序

        Returns:
            (球员数据列表, 日期字符串)

        Raises:
            ValidationError: 日期格式无效
        """
        try:
            game_date_obj = date.fromisoformat(game_date)
        except ValueError:
            from app.exceptions.base import ValidationError

            raise ValidationError("Invalid date format, use YYYY-MM-DD")

        stats = (
            db.query(PlayerGameStats)
            .filter(PlayerGameStats.game_date == game_date_obj)
            .all()
        )

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

            player_info = (
                db.query(PlayerInformation).filter_by(player_id=stat.personId).first()
            )
            player_name = (
                player_info.full_name if player_info else f"Player {stat.personId}"
            )

            three_point_percentage = (
                (stat.threePointersMade / stat.threePointersAttempted * 100)
                if stat.threePointersAttempted > 0
                else 0
            )
            two_point_percentage = (
                (stat.twoPointersMade / stat.twoPointersAttempted * 100)
                if stat.twoPointersAttempted > 0
                else 0
            )
            free_throw_percentage = (
                (stat.freeThrowsMade / stat.freeThrowsAttempted * 100)
                if stat.freeThrowsAttempted > 0
                else 0
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
                "three_pointers_percentage": three_point_percentage,
                "two_pointers_made": stat.twoPointersMade,
                "two_pointers_attempted": stat.twoPointersAttempted,
                "two_pointers_percentage": two_point_percentage,
                "free_throws_made": stat.freeThrowsMade,
                "free_throws_attempted": stat.freeThrowsAttempted,
                "free_throws_percentage": free_throw_percentage,
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

        valid_sort_fields = {
            "salary", "minutes", "points", "offensive_rebounds", "defensive_rebounds",
            "assists", "steals", "blocks", "turnovers", "personal_fouls",
            "three_pointers_made", "three_pointers_attempted", "three_pointers_percentage",
            "two_pointers_made", "two_pointers_attempted", "two_pointers_percentage",
            "free_throws_made", "free_throws_attempted", "free_throws_percentage",
            "rating"
        }
        sort_field = sort_by if sort_by in valid_sort_fields else "rating"
        players_with_score.sort(
            key=lambda x: x[sort_field], reverse=(sort_order == "desc")
        )
        return players_with_score, game_date

    @staticmethod
    def get_player_game_stats_by_id(
        db: Session,
        player_id: int,
    ) -> Tuple[int, List[Dict]]:
        """
        获取指定球员的比赛数据

        Args:
            db: 数据库会话
            player_id: 球员ID

        Returns:
            (球员ID, 比赛数据列表)
        """
        stats = (
            db.query(PlayerGameStats)
            .filter(PlayerGameStats.personId == player_id)
            .order_by(PlayerGameStats.game_date)
            .all()
        )

        game_stats = []
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
                field_goals_attempted=stat.threePointersAttempted
                + stat.twoPointersAttempted,
                field_goals_made=stat.threePointersMade + stat.twoPointersMade,
                free_throws_attempted=stat.freeThrowsAttempted,
                turnovers=stat.turnovers,
                personal_fouls=stat.foulsPersonal,
                team_won=stat.IS_WINNER,
                minutes_played=stat.minutes,
            )

            game_data = {
                "game_date": stat.game_date.isoformat() if stat.game_date else None,
                "rating": rating,
            }
            game_stats.append(game_data)

        return player_id, game_stats

    @staticmethod
    def get_player_average_stats(
        db: Session,
        player_id: int,
    ) -> Dict:
        """
        获取指定球员的平均数据

        Args:
            db: 数据库会话
            player_id: 球员ID

        Returns:
            平均数据字典

        Raises:
            ResourceNotFound: 球员数据不存在
        """
        stats = (
            db.query(PlayerGameStats)
            .filter(PlayerGameStats.personId == player_id)
            .all()
        )
        if not stats:
            from app.exceptions.base import ResourceNotFound

            raise ResourceNotFound("No stats found for this player")

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
        total_three_pointers_attempted = sum(
            stat.threePointersAttempted for stat in stats
        )
        total_two_pointers_made = sum(stat.twoPointersMade for stat in stats)
        total_two_pointers_attempted = sum(stat.twoPointersAttempted for stat in stats)
        total_free_throws_made = sum(stat.freeThrowsMade for stat in stats)
        total_free_throws_attempted = sum(stat.freeThrowsAttempted for stat in stats)

        field_goals_made = total_three_pointers_made + total_two_pointers_made
        field_goals_attempted = (
            total_three_pointers_attempted + total_two_pointers_attempted
        )
        field_goal_percentage = (
            (field_goals_made / field_goals_attempted * 100)
            if field_goals_attempted > 0
            else 0
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

        return average_stats

    @staticmethod
    def get_value_for_money(
        db: Session,
        game_date: Optional[str] = None,
    ) -> Tuple[List[Dict], Optional[str]]:
        """
        获取性价比球员列表

        Args:
            db: 数据库会话
            game_date: 比赛日期

        Returns:
            (球员列表, 游戏日期)

        Raises:
            ValidationError: 日期格式无效
        """
        players = db.query(PlayerInformation).all()
        player_data = []

        for player in players:
            if game_date:
                try:
                    game_date_obj = date.fromisoformat(game_date)
                except ValueError:
                    from app.exceptions.base import ValidationError

                    raise ValidationError("Invalid date format, use YYYY-MM-DD")

                stat = (
                    db.query(PlayerGameStats)
                    .filter(
                        PlayerGameStats.personId == player.player_id,
                        PlayerGameStats.game_date == game_date_obj,
                    )
                    .first()
                )

                if stat:
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

                    player_data.append(
                        {
                            "player_id": player.player_id,
                            "player_name": player.full_name,
                            "team_name": player.team_name,
                            "position": player.position,
                            "salary": player.salary,
                            "average_rating": rating,
                        }
                    )
            else:
                stats = (
                    db.query(PlayerGameStats)
                    .filter(PlayerGameStats.personId == player.player_id)
                    .all()
                )

                if stats:
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
                            field_goals_attempted=stat.threePointersAttempted
                            + stat.twoPointersAttempted,
                            field_goals_made=stat.threePointersMade
                            + stat.twoPointersMade,
                            free_throws_attempted=stat.freeThrowsAttempted,
                            turnovers=stat.turnovers,
                            personal_fouls=stat.foulsPersonal,
                            team_won=stat.IS_WINNER,
                            minutes_played=stat.minutes,
                        )
                        total_rating += rating

                    average_rating = total_rating / len(stats)

                    player_data.append(
                        {
                            "player_id": player.player_id,
                            "player_name": player.full_name,
                            "team_name": player.team_name,
                            "position": player.position,
                            "salary": player.salary,
                            "average_rating": average_rating,
                        }
                    )

        if player_data:
            player_data.sort(key=lambda x: x["salary"], reverse=True)
            for i, player in enumerate(player_data):
                player["salary_rank"] = i + 1

            player_data.sort(key=lambda x: x["average_rating"], reverse=True)
            for i, player in enumerate(player_data):
                player["rating_rank"] = i + 1

            player_data.sort(key=lambda x: x["salary"])

        return player_data, game_date
