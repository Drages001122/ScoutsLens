from typing import Optional

from app.core.dependencies import get_db, login_required
from app.exceptions.base import ResourceNotFound, ValidationError
from app.schemas import ErrorResponse, LineupCreate
from app.services.lineup_service import LineupService
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.post(
    "/create",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def create_lineup(
    data: LineupCreate,
    user_id: int = Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        name = data.name
        date_str = data.date
        starting_players = [p.model_dump() for p in data.starting_players]
        bench_players = [p.model_dump() for p in data.bench_players]

        new_lineup = LineupService.create_lineup(
            db,
            user_id=user_id,
            name=name,
            date_str=date_str,
            starting_players=starting_players,
            bench_players=bench_players,
        )

        return {"message": "阵容创建成功", "lineup": new_lineup.to_dict()}

    except ValidationError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/by-date",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_lineups_by_date(
    date: str = Query(..., description="日期"),
    current_user_id: int = Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        lineups = LineupService.get_lineups_by_date(db, date, current_user_id)
        return {"lineups": lineups}
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
    "/best",
    response_model=dict,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_best_lineup_endpoint(
    date: Optional[str] = None,
    user_id: int = Depends(login_required),
    db: Session = Depends(get_db),
):
    try:
        formatted_lineup = LineupService.get_best_lineup(db, date)
        return {"message": "获取今日最佳阵容成功", "best_lineup": formatted_lineup}
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
