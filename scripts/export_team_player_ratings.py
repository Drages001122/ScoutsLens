import os
import sys
import pandas as pd
from datetime import datetime

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.scoring import calculate_per
from utils.constants import TEAM_TRANSLATION

def get_team_name_mapping():
    """获取球队名映射（双向）"""
    # 创建双向映射
    team_mapping = {}
    # 英文到中文
    for en_name, zh_name in TEAM_TRANSLATION.items():
        team_mapping[en_name.lower()] = en_name
        team_mapping[zh_name] = en_name
    return team_mapping

def get_player_info():
    """获取球员ID到名字和薪资的映射"""
    try:
        player_info_df = pd.read_csv("data/player_information.csv", encoding="utf-8-sig")
        # 确保薪资是数字类型
        player_info_df["salary"] = pd.to_numeric(player_info_df["salary"], errors='coerce').fillna(0).astype(int)
        player_id_to_name = dict(zip(player_info_df["player_id"], player_info_df["full_name"]))
        player_id_to_salary = dict(zip(player_info_df["player_id"], player_info_df["salary"]))
        return player_id_to_name, player_id_to_salary
    except Exception as e:
        print(f"读取球员信息文件失败: {e}")
        return {}, {}

def get_team_players_ratings(team_name):
    """获取指定球队所有球员的评分统计"""
    data_dir = "player_stats_data"
    all_files = []
    
    # 收集所有数据文件
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".csv") and not file_name.startswith("all_player_stats_"):
            all_files.append(os.path.join(data_dir, file_name))
    
    if not all_files:
        print("未找到任何数据文件")
        return {}
    
    print(f"找到 {len(all_files)} 个数据文件")
    
    # 获取球队名映射
    team_mapping = get_team_name_mapping()
    # 标准化球队名
    normalized_team = team_mapping.get(team_name.lower()) or team_mapping.get(team_name)
    
    if not normalized_team:
        print(f"未找到球队: {team_name}")
        return {}
    
    print(f"标准化球队名: {normalized_team}")
    
    # 获取球员ID到名字和薪资的映射
    player_id_to_name, player_id_to_salary = get_player_info()
    
    # 收集球员数据
    player_ratings = {}
    
    for file_path in all_files:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            
            # 筛选该球队的数据
            team_data = df[df["球队名"] == normalized_team]
            
            if not team_data.empty:
                for _, row in team_data.iterrows():
                    player_id = row["球员id"]
                    # 计算评分
                    rating = calculate_per(row)
                    
                    if player_id not in player_ratings:
                        player_ratings[player_id] = []
                    
                    player_ratings[player_id].append(rating)
            
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
    
    # 计算每个球员的统计数据
    player_stats = []
    for player_id, ratings in player_ratings.items():
        player_name = player_id_to_name.get(player_id, f"未知球员({player_id})")
        salary = player_id_to_salary.get(player_id, 0)
        if ratings:
            player_stats.append({
                "player_id": player_id,
                "player_name": player_name,
                "salary": salary,
                "games_played": len(ratings),
                "avg_rating": round(sum(ratings) / len(ratings), 2),
                "highest_rating": round(max(ratings), 2),
                "lowest_rating": round(min(ratings), 2)
            })
    
    # 按平均评分排序
    player_stats.sort(key=lambda x: x["avg_rating"], reverse=True)
    
    return player_stats

def export_to_csv(player_stats, team_name):
    """导出数据到CSV文件"""
    if not player_stats:
        print("没有数据可导出")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(player_stats)
    
    # 重命名字段
    df = df.rename(columns={
        "player_id": "球员ID",
        "player_name": "球员名",
        "salary": "薪资",
        "games_played": "出场次数",
        "avg_rating": "平均评分",
        "highest_rating": "最高评分",
        "lowest_rating": "最低评分"
    })
    
    # 构建输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"player_stats_data/{team_name}_player_ratings_{timestamp}.csv"
    
    # 导出
    try:
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n数据导出完成！")
        print(f"文件保存为: {output_file}")
        print(f"导出球员数: {len(df)}")
        return output_file
    except Exception as e:
        print(f"导出文件失败: {e}")
        return None

def main():
    print("NBA球队球员评分统计系统")
    print("=" * 50)
    
    # 获取用户输入的球队名
    team_name = input("请输入球队名（支持中英文）: ")
    
    if not team_name:
        print("请输入有效的球队名")
        return
    
    print(f"\n查询球队: {team_name}")
    print("正在获取球员评分数据...")
    
    # 获取球员评分
    player_stats = get_team_players_ratings(team_name)
    
    if not player_stats:
        print("未找到该球队的球员数据")
        return
    
    print(f"\n找到 {len(player_stats)} 名球员的数据")
    print("=" * 100)
    print(f"{'球员名':<25} {'薪资':<12} {'出场次数':<10} {'平均评分':<10} {'最高评分':<10} {'最低评分'}")
    print("=" * 100)
    
    for player in player_stats:
        # 格式化薪资，添加千位分隔符
        formatted_salary = f"${player['salary']:,}"
        print(f"{player['player_name']:<25} {formatted_salary:<12} {player['games_played']:<10} {player['avg_rating']:<10} {player['highest_rating']:<10} {player['lowest_rating']}")
    
    print("=" * 100)
    
    # 导出数据
    export_to_csv(player_stats, team_name)

if __name__ == "__main__":
    main()
