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

# 查询所有不同的球队名
def get_all_teams():
    teams = session.query(PlayerInformation.team_name).distinct().all()
    team_list = [team[0] for team in teams]
    return team_list

if __name__ == '__main__':
    teams = get_all_teams()
    print("所有球队名:")
    for team in teams:
        print(team)
