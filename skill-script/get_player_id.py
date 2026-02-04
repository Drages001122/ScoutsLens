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

def get_player_id(team_name, player_name):
    """根据球队名和球员名获取球员的player_id"""
    try:
        player = session.query(PlayerInformation).filter_by(
            team_name=team_name,
            full_name=player_name
        ).first()
        if player:
            return player.player_id
        return None
    except Exception as e:
        print(f"Error getting player id: {e}")
        return None

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python get_player_id.py <team_name> <player_name>")
        sys.exit(1)
    
    team_name = sys.argv[1]
    player_name = sys.argv[2]
    player_id = get_player_id(team_name, player_name)
    if player_id:
        print(f"Player ID: {player_id}")
    else:
        print("Player not found")