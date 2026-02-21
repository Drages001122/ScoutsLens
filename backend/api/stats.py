from collections import defaultdict
from datetime import date
from typing import Optional

from config import get_db
from fastapi import APIRouter, Depends, HTTPException, Query, status
from models import ErrorResponse, PlayerGameStats, PlayerInformation
from sqlalchemy.orm import Session
from utils.pagination import get_pagination_params, paginate
from utils.rating import calculate_player_score

router = APIRouter()


@router.get("/average-stats")
async def get_player_average_stats_leaderboard(
    sort_order: str = Query("desc", description="排序顺序"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    try:
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

            player_data = {
                "player_id": player_id,
                "player_name": player_name,
                "team_name": stat_list[0].teamName if stat_list else "",
                "position": player_info.position if player_info else "",
                "salary": player_info.salary if player_info else 0,
                "minutes": avg_minutes,
                "three_pointers_made": avg_three_pointers_made,
                "three_pointers_attempted": avg_three_pointers_attempted,
                "two_pointers_made": avg_two_pointers_made,
                "two_pointers_attempted": avg_two_pointers_attempted,
                "free_throws_made": avg_free_throws_made,
                "free_throws_attempted": avg_free_throws_attempted,
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

        players_with_score.sort(
            key=lambda x: x["rating"], reverse=(sort_order == "desc")
        )

        return paginate(
            players_with_score, pagination["page"], pagination["per_page"], "players"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/game-stats")
async def get_player_game_stats(
    game_date: str = Query(..., description="比赛日期"),
    sort_order: str = Query("desc", description="排序顺序"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    try:
        if not game_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="game_date is required",
            )

        try:
            game_date_obj = date.fromisoformat(game_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format, use YYYY-MM-DD",
            )

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

        result = paginate(
            players_with_score, pagination["page"], pagination["per_page"], "players"
        )
        result["game_date"] = game_date
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/player/{player_id}/game-stats",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
)
async def get_player_game_stats_by_id(player_id: int, db: Session = Depends(get_db)):
    try:
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

        return {"player_id": player_id, "game_stats": game_stats}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/player/{player_id}/average-stats",
    response_model=dict,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_player_average_stats(player_id: int, db: Session = Depends(get_db)):
    try:
        stats = (
            db.query(PlayerGameStats)
            .filter(PlayerGameStats.personId == player_id)
            .all()
        )
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No stats found for this player",
            )
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/value-for-money",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_value_for_money(
    game_date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    try:
        players = db.query(PlayerInformation).all()
        player_data = []

        for player in players:
            if game_date:
                try:
                    game_date_obj = date.fromisoformat(game_date)
                except ValueError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid date format, use YYYY-MM-DD",
                    )

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

        return {"players": player_data, "game_date": game_date}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
