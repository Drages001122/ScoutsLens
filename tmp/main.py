import os
import sys
import re

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入必要的模块
from tmp.team_mapping import get_english_team_name
from tmp.player_mapping import map_chinese_player_name

def parse_input(user_input):
    """解析用户输入，提取中文球队名和球员名"""
    # 常见的输入格式："球队名的球员名"
    pattern = r'(.*?)的(.*)'
    match = re.match(pattern, user_input)
    if match:
        team_name = match.group(1)
        player_name = match.group(2)
        return team_name, player_name
    else:
        # 尝试其他格式
        # 例如："球队名 球员名"
        parts = user_input.split()
        if len(parts) >= 2:
            team_name = parts[0]
            player_name = ' '.join(parts[1:])
            return team_name, player_name
    return None, None

def main(user_input):
    """主函数，处理用户输入并输出结果"""
    print(f"用户输入: {user_input}")
    
    # 解析输入
    chinese_team_name, chinese_player_name = parse_input(user_input)
    
    if not chinese_team_name or not chinese_player_name:
        print("输入格式错误，请使用类似'开拓者队的李斯'的格式")
        return
    
    print(f"解析结果: 球队 - {chinese_team_name}, 球员 - {chinese_player_name}")
    
    # 映射中文球队名到英文球队名
    english_team_name = get_english_team_name(chinese_team_name)
    
    if not english_team_name:
        print(f"无法找到对应的英文球队名: {chinese_team_name}")
        return
    
    print(f"球队名映射: {chinese_team_name} -> {english_team_name}")
    
    # 映射中文球员名到英文球员名和player_id
    player_info = map_chinese_player_name(chinese_player_name, english_team_name)
    
    if not player_info:
        print(f"无法找到对应的球员信息: {chinese_player_name} (球队: {english_team_name})")
        return
    
    # 输出结果
    print("\n查询结果:")
    print(f"Player ID: {player_info['player_id']}")
    print(f"英文名: {player_info['full_name']}")
    print(f"球队名: {player_info['team_name']}")

if __name__ == '__main__':
    # 测试示例输入
    if len(sys.argv) > 1:
        user_input = ' '.join(sys.argv[1:])
    else:
        # 默认测试示例
        user_input = '开拓者队的李斯'
    
    main(user_input)
