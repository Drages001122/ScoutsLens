from typing import Optional

from app.core.dependencies import get_db, get_pagination_params
from app.exceptions.base import ResourceNotFound, ValidationError
from app.schemas import ErrorResponse
from app.services.stats_service import StatsService
from app.utils.pagination import paginate_with_metadata
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/average-stats")
async def get_player_average_stats_leaderboard(
    sort_order: str = Query("desc", description="排序顺序"),
    sort_by: str = Query("rating", description="排序字段"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    try:
        players_with_score = StatsService.get_player_average_stats_leaderboard(
            db, sort_order=sort_order, sort_by=sort_by
        )

        return paginate_with_metadata(
            players_with_score,
            pagination["page"],
            pagination["per_page"],
            "players",
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
    sort_by: str = Query("rating", description="排序字段"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    try:
        players_with_score, game_date_result = StatsService.get_player_game_stats(
            db, game_date=game_date, sort_order=sort_order, sort_by=sort_by
        )

        return paginate_with_metadata(
            players_with_score,
            pagination["page"],
            pagination["per_page"],
            "players",
            game_date=game_date_result,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
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
        player_id_result, game_stats = StatsService.get_player_game_stats_by_id(
            db, player_id
        )
        return {"player_id": player_id_result, "game_stats": game_stats}
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
        average_stats = StatsService.get_player_average_stats(db, player_id)
        return average_stats
    except ResourceNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
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
        player_data, game_date_result = StatsService.get_value_for_money(db, game_date)
        return {"players": player_data, "game_date": game_date_result}
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
