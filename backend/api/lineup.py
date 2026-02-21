import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.rule import SALARY_CAP
from config import get_db
from models import (
    ErrorResponse,
    Lineup,
    LineupCreate,
    LineupPlayer,
    PlayerInformation,
    User,
)
from utils.best_lineup import get_best_lineup
from utils.permission import login_required
from utils.rule import PlayerCountRule, SalaryRule

router = APIRouter()


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
        starting_players = [p.dict() for p in data.starting_players]
        bench_players = [p.dict() for p in data.bench_players]

        if not name:
            timestamp = int(time.time())
            name = f"阵容_{date_str}_{timestamp}"

        if not date_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="比赛日期不能为空",
            )

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式不正确，请使用 YYYY-MM-DD 格式",
            )

        if not starting_players and not bench_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="阵容至少需要一名球员",
            )

        valid, err_msg = verify_lineup(starting_players, bench_players)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg,
            )

        new_lineup = Lineup(
            user_id=user_id,
            name=name,
            date=date,
            total_salary=calculate_total_salary(starting_players, bench_players),
        )
        db.add(new_lineup)
        db.flush()

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
            db.add(lineup_player)

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
            db.add(lineup_player)

        db.commit()
        db.refresh(new_lineup)

        return {"message": "阵容创建成功", "lineup": new_lineup.to_dict()}

    except HTTPException:
        db.rollback()
        raise
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
    def can_view_lineup(lineup_user_id, current_user_id, lineup_date):
        if lineup_user_id == current_user_id:
            return True
        now = datetime.utcnow() + timedelta(hours=8)
        today = now.date()
        if lineup_date < today:
            return True
        elif lineup_date == today and now.hour >= 7:
            return True
        return False

    try:
        if not date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期参数不能为空",
            )
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="日期格式不正确，请使用 YYYY-MM-DD 格式",
            )
        lineups = (
            db.query(Lineup)
            .filter_by(date=date_obj)
            .order_by(Lineup.created_at.desc())
            .all()
        )
        result = []
        for lineup in lineups:
            lineup_dict = lineup.to_dict()
            user = db.query(User).get(lineup.user_id)
            if user:
                lineup_dict["username"] = user.username
            else:
                lineup_dict["username"] = "未知用户"
            if can_view_lineup(lineup.user_id, current_user_id, lineup.date):
                lineup_dict["can_view"] = True
            else:
                lineup_dict["can_view"] = False
                lineup_dict["players"] = []
            result.append(lineup_dict)
        return {"lineups": result}
    except HTTPException:
        raise
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
        now = datetime.utcnow() + timedelta(hours=8)
        target_date = date if date else now.date().strftime("%Y-%m-%d")
        best_lineup = get_best_lineup(target_date)
        if not best_lineup:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"无法计算{target_date}最佳阵容，可能是因为当日没有比赛或数据不足",
            )
        formatted_lineup = {
            "id": 0,
            "user_id": 0,
            "name": f"{target_date}最佳阵容",
            "date": target_date,
            "total_salary": best_lineup["total_salary"],
            "created_at": now.isoformat(),
            "players": [],
            "total_rating": best_lineup["total_rating"],
        }

        for slot, player in best_lineup["starters"].items():
            player_info = (
                db.query(PlayerInformation).filter_by(player_id=player["id"]).first()
            )
            team_name = player_info.team_name if player_info else ""
            formatted_lineup["players"].append(
                {
                    "id": 0,
                    "lineup_id": 0,
                    "player_id": player["id"],
                    "full_name": player["name"],
                    "team_name": team_name,
                    "position": player["position"],
                    "salary": player["salary"],
                    "slot": slot,
                    "is_starting": True,
                    "rating": player["rating"],
                }
            )

        for player in best_lineup["bench"]:
            player_info = (
                db.query(PlayerInformation).filter_by(player_id=player["id"]).first()
            )
            team_name = player_info.team_name if player_info else ""
            formatted_lineup["players"].append(
                {
                    "id": 0,
                    "lineup_id": 0,
                    "player_id": player["id"],
                    "full_name": player["name"],
                    "team_name": team_name,
                    "position": player["position"],
                    "salary": player["salary"],
                    "slot": None,
                    "is_starting": False,
                    "rating": player["rating"],
                }
            )

        return {"message": "获取今日最佳阵容成功", "best_lineup": formatted_lineup}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
