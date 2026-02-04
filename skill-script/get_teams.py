import os
import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库连接配置
db_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "database",
    "scoutslens.db",
)
engine = create_engine(f"sqlite:///{db_path}", echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# 定义 PlayerInformation 模型
class PlayerInformation(Base):
    __tablename__ = "player_information"
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    position = Column(String(10), nullable=False)
    salary = Column(Integer, nullable=False)


def get_all_teams():
    """获取所有NBA球队的英文名列表"""
    try:
        teams = session.query(PlayerInformation.team_name).distinct().all()
        return [team[0] for team in teams]
    except Exception as e:
        print(f"Error getting teams: {e}")
        return []


if __name__ == "__main__":
    teams = get_all_teams()
    print("Teams:", teams)
