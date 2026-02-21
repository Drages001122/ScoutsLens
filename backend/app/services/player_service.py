from typing import Dict, List, Optional

from app.models import PlayerInformation
from sqlalchemy.orm import Session


class PlayerService:
    """球员服务"""

    @staticmethod
    def get_players(
        db: Session,
        salary_min: int = 0,
        salary_max: int = 60000000,
        teams: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        获取球员列表

        Args:
            db: 数据库会话
            salary_min: 最低薪资
            salary_max: 最高薪资
            teams: 球队列表

        Returns:
            球员列表
        """
        query = db.query(PlayerInformation).filter(
            PlayerInformation.salary >= salary_min,
            PlayerInformation.salary <= salary_max,
        )

        if teams:
            query = query.filter(PlayerInformation.team_name.in_(teams))

        players = query.order_by(PlayerInformation.salary.desc()).all()
        return [player.to_dict() for player in players]

    @staticmethod
    def get_teams(db: Session) -> List[Dict]:
        """
        获取球队列表

        Args:
            db: 数据库会话

        Returns:
            球队列表
        """
        teams = db.query(PlayerInformation.team_name).distinct().all()
        teams_list = []
        for i, team in enumerate(teams, 1):
            teams_list.append({"team_id": i, "team_name": team[0]})
        return teams_list

    @staticmethod
    def get_team_players(db: Session, team_id: int) -> List[Dict]:
        """
        获取指定球队的球员

        Args:
            db: 数据库会话
            team_id: 球队ID

        Returns:
            球员列表

        Raises:
            ValidationError: 无效的球队ID
        """
        teams = db.query(PlayerInformation.team_name).distinct().all()
        if team_id <= 0 or team_id > len(teams):
            from app.exceptions.base import ValidationError

            raise ValidationError("Invalid team ID")

        team_name = teams[team_id - 1][0]
        players = db.query(PlayerInformation).filter_by(team_name=team_name).all()
        return [player.to_dict() for player in players]

    @staticmethod
    def get_player_by_id(db: Session, player_id: int) -> Optional[PlayerInformation]:
        """
        通过ID获取球员

        Args:
            db: 数据库会话
            player_id: 球员ID

        Returns:
            球员对象，不存在返回None
        """
        return db.query(PlayerInformation).filter_by(player_id=player_id).first()
