from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from config import get_db
from models import ErrorResponse, PlayerInformation
from utils.pagination import get_pagination_params, paginate

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
        query = db.query(PlayerInformation).filter(
            PlayerInformation.salary >= salary_min,
            PlayerInformation.salary <= salary_max,
        )
        if teams:
            query = query.filter(PlayerInformation.team_name.in_(teams))

        players = query.order_by(PlayerInformation.salary.desc()).all()
        players_list = [player.to_dict() for player in players]

        return paginate(
            players_list, pagination["page"], pagination["per_page"], "players"
        )
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
        teams = db.query(PlayerInformation.team_name).distinct().all()
        teams_list = []
        for i, team in enumerate(teams, 1):
            teams_list.append({"team_id": i, "team_name": team[0]})
        return {"teams": teams_list}
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
        teams = db.query(PlayerInformation.team_name).distinct().all()
        if team_id <= 0 or team_id > len(teams):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid team ID",
            )
        team_name = teams[team_id - 1].team_name
        players = db.query(PlayerInformation).filter_by(team_name=team_name).all()
        players_list = [player.to_dict() for player in players]
        return {"players": players_list}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
