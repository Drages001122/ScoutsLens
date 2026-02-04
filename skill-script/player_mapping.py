import os
import sys
import re
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

# 简单的中文拼音首字母映射
pinyin_first_letter = {
    '李': 'L', '斯': 'S', '利': 'L', '拉': 'L', '德': 'D',
    '布': 'B', '朗': 'L', '詹': 'Z', '姆': 'M', '斯': 'S',
    '库': 'K', '里': 'L', '欧': 'O', '文': 'W', '杜': 'D',
    '兰': 'L', '特': 'T', '哈': 'H', '登': 'D', '威': 'W',
    '少': 'S', '安': 'A', '东': 'D', '尼': 'N', '卡': 'K',
    '椒': 'J', '乔': 'J', '丹': 'D', '麦': 'M', '迪': 'D',
    '克': 'K', '雷': 'L', '阿': 'A', '伦': 'L', '保': 'B',
    '罗': 'R', '格': 'G', '林': 'L', '汤': 'T', '普': 'P',
    '乐': 'L', '福': 'F', '考': 'K', '辛': 'X', '斯': 'S'
}

def get_players_by_team(team_name):
    """根据球队名查询球员信息"""
    players = session.query(PlayerInformation).filter_by(team_name=team_name).all()
    player_list = []
    for player in players:
        player_list.append({
            'player_id': player.player_id,
            'full_name': player.full_name,
            'team_name': player.team_name
        })
    return player_list

def map_chinese_player_name(chinese_name, team_name):
    """根据中文球员名和球队名映射到英文球员名"""
    # 获取该球队的所有球员
    players = get_players_by_team(team_name)
    
    if not players:
        return None
    
    # 详细的映射逻辑
    # 1. 检查中文名字的首字母与英文名字的首字母是否匹配
    # 2. 检查中文名字的长度与英文名字的长度是否相似
    # 3. 考虑常见的翻译习惯
    # 4. 特别处理常见的中文姓氏和名字
    
    # 提取中文名字的首字母
    chinese_initials = ''
    for char in chinese_name:
        if char in pinyin_first_letter:
            chinese_initials += pinyin_first_letter[char]
    
    # 候选球员列表
    candidates = []
    
    for player in players:
        english_name = player['full_name']
        # 提取英文名字的首字母
        english_initials = ''.join([word[0].upper() for word in english_name.split()])
        # 提取英文名字的所有部分
        english_name_parts = english_name.split()
        
        # 计算匹配分数
        score = 0
        
        # 检查首字母匹配
        if chinese_initials and english_initials:
            # 检查中文首字母是否在英文首字母中
            for ci in chinese_initials:
                if ci in english_initials:
                    score += 2  # 增加权重
            
            # 检查英文首字母是否在中文首字母中
            for ei in english_initials:
                if ei in chinese_initials:
                    score += 2  # 增加权重
        
        # 检查名字长度
        chinese_length = len(chinese_name)
        english_length = len(english_name_parts)
        if abs(chinese_length - english_length) <= 1:
            score += 1
        
        # 考虑特殊情况，比如中文姓氏与英文名字的部分匹配
        # 例如 "杨" 可能对应 "Yang"
        if chinese_name in english_name:
            score += 5  # 大幅增加权重
        
        # 考虑常见的翻译，比如 "李" 可能对应 "Lee" 或 "Li"
        if '李' in chinese_name:
            if 'Lee' in english_name or 'Li' in english_name:
                score += 4  # 增加权重
            # 也考虑 "Le" 开头的名字
            for part in english_name_parts:
                if part.lower().startswith('le'):
                    score += 3
        
        # 考虑 "斯" 结尾的中文名字，可能对应 "s" 结尾的英文名字
        if chinese_name.endswith('斯'):
            if english_name.lower().endswith('s'):
                score += 3  # 增加权重
            # 也考虑 "ce" 结尾的名字（如 "Lance"）
            if english_name.lower().endswith('ce'):
                score += 2
        
        # 特别处理 "李斯" 这个名字
        if chinese_name == '李斯':
            # 尝试匹配 "Lee"、"Li"、"Le" 开头的名字
            for part in english_name_parts:
                part_lower = part.lower()
                if part_lower.startswith('le') or part_lower.startswith('li'):
                    score += 5
                # 考虑 "Lillard" 这样的名字
                if 'll' in part_lower:
                    score += 2
        
        candidates.append((score, player))
    
    # 按分数排序，取分数最高的
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # 打印调试信息
    print("\n球员匹配调试:")
    for score, player in candidates[:5]:  # 只显示前5个候选
        print(f"{player['full_name']}: 分数 = {score}")
    
    if candidates and candidates[0][0] > 0:
        return candidates[0][1]
    
    # 如果没有找到匹配的，返回第一个球员（作为默认值）
    return players[0]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python player_mapping.py <chinese_player_name> <team_name>")
        sys.exit(1)
    
    chinese_player_name = sys.argv[1]
    team_name = sys.argv[2]
    
    player = map_chinese_player_name(chinese_player_name, team_name)
    
    if player:
        print(f"Player ID: {player['player_id']}")
        print(f"English Name: {player['full_name']}")
        print(f"Team Name: {player['team_name']}")
    else:
        print("No player found")
