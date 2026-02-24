import time
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.core.logger import logger
from app.models import Lineup, LineupPlayer, User
from app.services.optimization_service import get_best_lineup
from sqlalchemy.orm import Session


class Rule(ABC):
    """规则基类"""

    def __init__(self, description: str):
        self.description = description

    @abstractmethod
    def verify(self, starting_players: list, bench_players: list) -> bool:
        pass


class SalaryRule(Rule):
    """薪资规则"""

    def __init__(self, max_salary: int):
        super().__init__("薪资限制")
        self.max_salary = max_salary

    def verify(self, starting_players: list, bench_players: list) -> bool:
        total_salary = sum(p.get("salary", 0) for p in starting_players + bench_players)
        return total_salary <= self.max_salary


class PlayerCountRule(Rule):
    """球员数量规则"""

    def __init__(self, starting_player_count: int, bench_player_count: int):
        super().__init__("球员数量限制")
        self.starting_player_count = starting_player_count
        self.bench_player_count = bench_player_count

    def verify(self, starting_players: list, bench_players: list) -> bool:
        starting_players = len(starting_players)
        bench_players = len(bench_players)
        return (
            self.starting_player_count == starting_players
            and self.bench_player_count == bench_players
        )


SALARY_CAP = 187895000


class LineupService:
    """阵容服务"""

    @staticmethod
    def verify_lineup(starting_players: list, bench_players: list) -> Tuple[bool, str]:
        """
        验证阵容

        Args:
            starting_players: 首发球员列表
            bench_players: 替补球员列表

        Returns:
            (是否有效, 错误消息)
        """
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

    @staticmethod
    def calculate_total_salary(starting_players: list, bench_players: list) -> int:
        """
        计算总薪资

        Args:
            starting_players: 首发球员列表
            bench_players: 替补球员列表

        Returns:
            总薪资
        """
        return sum(p.get("salary", 0) for p in starting_players + bench_players)

    @staticmethod
    def create_lineup(
        db: Session,
        user_id: int,
        name: Optional[str],
        date_str: str,
        starting_players: list,
        bench_players: list,
    ) -> Lineup:
        """
        创建阵容

        Args:
            db: 数据库会话
            user_id: 用户ID
            name: 阵容名称
            date_str: 日期字符串
            starting_players: 首发球员
            bench_players: 替补球员

        Returns:
            阵容对象

        Raises:
            ValidationError: 参数验证失败
        """
        if not name:
            timestamp = int(time.time())
            name = f"阵容_{date_str}_{timestamp}"

        if not date_str:
            from app.exceptions.base import ValidationError

            raise ValidationError("比赛日期不能为空")

        try:
            lineup_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            from app.exceptions.base import ValidationError

            raise ValidationError("日期格式不正确，请使用 YYYY-MM-DD 格式")

        if not starting_players and not bench_players:
            from app.exceptions.base import ValidationError

            raise ValidationError("阵容至少需要一名球员")

        valid, err_msg = LineupService.verify_lineup(starting_players, bench_players)
        if not valid:
            from app.exceptions.base import ValidationError

            raise ValidationError(err_msg)

        new_lineup = Lineup(
            user_id=user_id,
            name=name,
            date=lineup_date,
            total_salary=LineupService.calculate_total_salary(
                starting_players, bench_players
            ),
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
        logger.info(f"阵容创建成功: lineup_id={new_lineup.id}, user_id={user_id}")
        return new_lineup

    @staticmethod
    def can_view_lineup(
        lineup_user_id: int, current_user_id: int, lineup_date: date
    ) -> bool:
        """
        判断是否可以查看阵容

        Args:
            lineup_user_id: 阵容所属用户ID
            current_user_id: 当前用户ID
            lineup_date: 阵容日期

        Returns:
            是否可以查看
        """
        if lineup_user_id == current_user_id:
            return True
        now = datetime.utcnow() + timedelta(hours=8)
        today = now.date()
        if lineup_date < today:
            return True
        elif lineup_date == today and now.hour >= 7:
            return True
        return False

    @staticmethod
    def get_lineups_by_date(
        db: Session,
        date: str,
        current_user_id: int,
    ) -> List[Dict]:
        """
        获取指定日期的阵容列表

        Args:
            db: 数据库会话
            date: 日期字符串
            current_user_id: 当前用户ID

        Returns:
            阵容列表

        Raises:
            ValidationError: 日期格式无效
        """
        if not date:
            from app.exceptions.base import ValidationError

            raise ValidationError("日期参数不能为空")

        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            from app.exceptions.base import ValidationError

            raise ValidationError("日期格式不正确，请使用 YYYY-MM-DD 格式")

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

            if LineupService.can_view_lineup(
                lineup.user_id, current_user_id, lineup.date
            ):
                lineup_dict["can_view"] = True
            else:
                lineup_dict["can_view"] = False
                lineup_dict["players"] = []
            result.append(lineup_dict)

        return result

    @staticmethod
    def get_best_lineup(
        db: Session,
        date: Optional[str],
    ) -> Dict:
        """
        获取最佳阵容

        Args:
            db: 数据库会话
            date: 日期

        Returns:
            最佳阵容数据

        Raises:
            ResourceNotFound: 无法计算最佳阵容
        """
        now = datetime.utcnow() + timedelta(hours=8)
        target_date = date if date else now.date().strftime("%Y-%m-%d")
        best_lineup_data = get_best_lineup(target_date)

        if not best_lineup_data:
            from app.exceptions.base import ResourceNotFound

            raise ResourceNotFound(
                f"无法计算{target_date}最佳阵容，可能是因为当日没有比赛或数据不足"
            )

        formatted_lineup = {
            "id": 0,
            "user_id": 0,
            "name": f"{target_date}最佳阵容",
            "date": target_date,
            "total_salary": best_lineup_data["total_salary"],
            "created_at": now.isoformat(),
            "players": [],
            "total_rating": best_lineup_data["total_rating"],
        }

        from app.models import PlayerInformation

        for slot, player in best_lineup_data["starters"].items():
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

        for player in best_lineup_data["bench"]:
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

        return formatted_lineup
