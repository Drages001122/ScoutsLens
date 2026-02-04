import os
import sys
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 数据库连接配置
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'scoutslens.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# 定义 PlayerInformation 模型
class PlayerInformation(Base):
    __tablename__ = 'player_information'
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, nullable=False)
    full_name = Column(String(255), nullable=False)
    team_name = Column(String(255), nullable=False)
    position = Column(String(10), nullable=False)
    salary = Column(Integer, nullable=False)

def get_players_by_team(team_name):
    """根据球队名获取该球队的所有球员列表"""
    try:
        players = session.query(PlayerInformation).filter_by(team_name=team_name).all()
        return [player.full_name for player in players]
    except Exception as e:
        print(f"Error getting players: {e}")
        return []

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python get_players.py <team_name>")
        sys.exit(1)
    
    team_name = sys.argv[1]
    players = get_players_by_team(team_name)
    print(f"Players in {team_name}:", players)