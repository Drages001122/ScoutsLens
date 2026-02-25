from typing import List, Optional

from app.core.dependencies import get_db, get_pagination_params
from app.exceptions.base import ValidationError
from app.schemas import ErrorResponse
from app.services.player_service import PlayerService
from app.utils.pagination import paginate
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/list-players")
async def get_players(
    salary_min: int = Query(0, ge=0, description="最低薪资"),
    salary_max: int = Query(60000000, ge=0, description="最高薪资"),
    teams: Optional[List[str]] = Query(None, description="球队列表"),
    pagination: dict = Depends(get_pagination_params),
    db: Session = Depends(get_db),
):
    try:
        players = PlayerService.get_players(
            db, salary_min=salary_min, salary_max=salary_max, teams=teams
        )

        return paginate(players, pagination["page"], pagination["per_page"], "players")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/teams",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
)
async def get_teams(db: Session = Depends(get_db)):
    try:
        teams = PlayerService.get_teams(db)
        return {"teams": teams}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/team/{team_id}/players",
    response_model=dict,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_team_players(team_id: int, db: Session = Depends(get_db)):
    try:
        players = PlayerService.get_team_players(db, team_id)
        return {"players": players}
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
