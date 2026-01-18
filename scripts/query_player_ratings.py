import os
import sys
import pandas as pd
from datetime import datetime

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.scoring import calculate_per

def get_player_id_by_name(player_name):
    """根据球员名获取球员ID"""
    try:
        player_info_df = pd.read_csv("data/player_information.csv", encoding="utf-8-sig")
        # 转换球员名为小写进行模糊匹配
        player_info_df['full_name_lower'] = player_info_df['full_name'].str.lower()
        player_name_lower = player_name.lower()
        
        # 查找匹配的球员
        matched_players = player_info_df[player_info_df['full_name_lower'].str.contains(player_name_lower)]
        
        if matched_players.empty:
            return None, "未找到匹配的球员"
        elif len(matched_players) > 1:
            print("找到多个匹配的球员:")
            for idx, row in matched_players.iterrows():
                print(f"{idx + 1}. {row['full_name']}")
            choice = input("请选择球员编号: ")
            try:
                selected_idx = int(choice) - 1
                if 0 <= selected_idx < len(matched_players):
                    selected_player = matched_players.iloc[selected_idx]
                    return selected_player['player_id'], selected_player['full_name']
                else:
                    return None, "无效的选择"
            except ValueError:
                return None, "无效的输入"
        else:
            selected_player = matched_players.iloc[0]
            return selected_player['player_id'], selected_player['full_name']
    except Exception as e:
        return None, f"读取球员信息文件失败: {e}"

def get_player_ratings(player_id, player_name):
    """获取球员所有比赛的评分"""
    data_dir = "player_stats_data"
    all_files = []
    
    # 收集所有数据文件
    for file_name in os.listdir(data_dir):
        if file_name.endswith(".csv") and not file_name.startswith("all_player_stats_"):
            all_files.append(os.path.join(data_dir, file_name))
    
    if not all_files:
        print("未找到任何数据文件")
        return []
    
    print(f"找到 {len(all_files)} 个数据文件")
    
    # 收集球员数据
    player_games = []
    
    for file_path in all_files:
        try:
            df = pd.read_csv(file_path, encoding="utf-8-sig")
            # 提取日期
            date_str = os.path.basename(file_path).replace("nba_player_stats_", "").replace(".csv", "").replace("_", "-")
            
            # 筛选该球员的数据
            player_data = df[df["球员id"] == player_id]
            
            if not player_data.empty:
                for _, row in player_data.iterrows():
                    # 计算评分
                    rating = calculate_per(row)
                    
                    # 提取比赛信息
                    game_info = {
                        "date": date_str,
                        "team": row.get("球队名", "未知"),
                        "minutes": row.get("上场时间", "0"),
                        "rating": round(rating, 2),
                        "win": row.get("本场比赛是否获胜", False)
                    }
                    player_games.append(game_info)
            
        except Exception as e:
            print(f"读取文件 {file_path} 失败: {e}")
    
    # 按日期排序
    player_games.sort(key=lambda x: x["date"])
    
    return player_games

def main():
    print("NBA球员评分查询系统")
    print("=" * 50)
    
    # 获取用户输入的球员名
    player_name = input("请输入球员名: ")
    
    if not player_name:
        print("请输入有效的球员名")
        return
    
    # 获取球员ID
    player_id, actual_name = get_player_id_by_name(player_name)
    
    if player_id is None:
        print(f"错误: {actual_name}")
        return
    
    print(f"\n查询球员: {actual_name} (ID: {player_id})")
    print("正在获取所有比赛评分...")
    
    # 获取球员评分
    player_games = get_player_ratings(player_id, actual_name)
    
    if not player_games:
        print("未找到该球员的比赛数据")
        return
    
    print(f"\n找到 {len(player_games)} 场比赛的数据")
    print("=" * 80)
    print(f"{'日期':<12} {'球队':<15} {'上场时间':<10} {'评分':<8} {'胜负'}")
    print("=" * 80)
    
    total_rating = 0
    for game in player_games:
        win_status = "获胜" if game["win"] else "落败"
        print(f"{game['date']:<12} {game['team']:<15} {game['minutes']:<10} {game['rating']:<8} {win_status}")
        total_rating += game["rating"]
    
    print("=" * 80)
    avg_rating = total_rating / len(player_games) if player_games else 0
    print(f"平均评分: {round(avg_rating, 2)}")
    print(f"最高评分: {max(game['rating'] for game in player_games)}")
    print(f"最低评分: {min(game['rating'] for game in player_games)}")

if __name__ == "__main__":
    main()
