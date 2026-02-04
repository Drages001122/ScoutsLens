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

# 球队中文名到英文名的映射
TEAM_CHINESE_TO_ENGLISH = {
    '湖人队': 'Lakers',
    '勇士队': 'Warriors',
    '火箭队': 'Rockets',
    '雄鹿队': 'Bucks',
    '凯尔特人队': 'Celtics',
    '篮网队': 'Nets',
    '掘金队': 'Nuggets',
    '快船队': 'Clippers',
    '热火队': 'Heat',
    '猛龙队': 'Raptors',
    '爵士队': 'Jazz',
    '步行者队': 'Pacers',
    '活塞队': 'Pistons',
    '公牛队': 'Bulls',
    '魔术队': 'Magic',
    '黄蜂队': 'Hornets',
    '奇才队': 'Wizards',
    '尼克斯队': 'Knicks',
    '76人队': '76ers',
    '开拓者队': 'Trail Blazers',
    '国王队': 'Kings',
    '太阳队': 'Suns',
    '灰熊队': 'Grizzlies',
    '鹈鹕队': 'Pelicans',
    '老鹰队': 'Hawks',
    '骑士队': 'Cavaliers',
    '马刺队': 'Spurs',
    '雷霆队': 'Thunder',
    '森林狼队': 'Timberwolves',
    '独行侠队': 'Mavericks'
}

def get_all_teams():
    """获取所有NBA球队的英文名列表"""
    try:
        teams = session.query(PlayerInformation.team_name).distinct().all()
        return [team[0] for team in teams]
    except Exception as e:
        print(f"Error getting teams: {e}")
        return []

def get_players_by_team(team_name):
    """根据球队名获取该球队的所有球员列表"""
    try:
        players = session.query(PlayerInformation).filter_by(team_name=team_name).all()
        return [player.full_name for player in players]
    except Exception as e:
        print(f"Error getting players: {e}")
        return []

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

def match_team_chinese_to_english(chinese_team_name):
    """将中文球队名匹配到英文球队名"""
    # 直接映射
    if chinese_team_name in TEAM_CHINESE_TO_ENGLISH:
        return TEAM_CHINESE_TO_ENGLISH[chinese_team_name]
    
    # 模糊匹配
    for key, value in TEAM_CHINESE_TO_ENGLISH.items():
        if chinese_team_name in key or key in chinese_team_name:
            return value
    
    return None

def match_player_name(input_player_name, player_list):
    """将用户输入的球员名匹配到准确的球员英文名"""
    # 标准化输入
    input_normalized = input_player_name.strip().lower()
    
    # 精确匹配
    for player_name in player_list:
        if player_name.lower() == input_normalized:
            return player_name
    
    # 模糊匹配
    for player_name in player_list:
        if input_normalized in player_name.lower() or player_name.lower() in input_normalized:
            return player_name
    
    # 部分匹配
    for player_name in player_list:
        input_parts = input_normalized.split()
        player_parts = player_name.lower().split()
        # 检查是否有共同的部分
        common_parts = set(input_parts) & set(player_parts)
        if common_parts:
            return player_name
    
    return None

def query_player(chinese_team_name, player_english_name):
    """查询NBA球员信息的主函数"""
    try:
        # 1. 获取所有球队列表
        teams = get_all_teams()
        if not teams:
            return {"error": "无法获取球队列表"}
        
        # 2. 匹配中文球队名到英文球队名
        english_team_name = match_team_chinese_to_english(chinese_team_name)
        if not english_team_name:
            return {"error": f"无法匹配球队: {chinese_team_name}"}
        
        # 3. 获取该球队的所有球员列表
        players = get_players_by_team(english_team_name)
        if not players:
            return {"error": f"无法获取球队 {english_team_name} 的球员列表"}
        
        # 4. 匹配球员英文名
        matched_player_name = match_player_name(player_english_name, players)
        if not matched_player_name:
            return {"error": f"无法在球队 {english_team_name} 中找到球员: {player_english_name}"}
        
        # 5. 获取球员的player_id
        player_id = get_player_id(english_team_name, matched_player_name)
        if player_id is None:
            return {"error": f"无法获取球员 {matched_player_name} 的ID"}
        
        # 6. 返回结果
        return {
            "player_id": player_id,
            "team_name": english_team_name,
            "player_name": matched_player_name
        }
        
    except Exception as e:
        return {"error": f"查询失败: {str(e)}"}

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python nba_player_query.py <chinese_team_name> <player_english_name>")
        sys.exit(1)
    
    chinese_team_name = sys.argv[1]
    player_english_name = sys.argv[2]
    
    result = query_player(chinese_team_name, player_english_name)
    
    if "error" in result:
        print(f"错误: {result['error']}")
    else:
        print(f"Player ID: {result['player_id']}")
        print(f"Team Name: {result['team_name']}")
        print(f"Player Name: {result['player_name']}")
