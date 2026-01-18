import pandas as pd
from nba_api.stats.endpoints import leaguegamelog, boxscoresummaryv2, boxscoretraditionalv2
from nba_api.stats.library.parameters import SeasonAll
from datetime import datetime

# 设置日期
TARGET_DATE = '2026-01-02'

def get_games_by_date(date):
    """获取指定日期的所有NBA比赛"""
    # 转换日期格式
    game_date = datetime.strptime(date, '%Y-%m-%d')
    season_year = game_date.year
    
    # 确定赛季（NBA赛季跨年度，例如2025-26赛季）
    if game_date.month >= 10:
        season = f"{season_year}-{str(season_year+1)[-2:]}"
    else:
        season = f"{season_year-1}-{str(season_year)[-2:]}"
    
    print(f"查询赛季: {season}")
    
    # 获取当天所有比赛
    try:
        # 尝试使用不同的方法获取比赛数据
        from nba_api.stats.endpoints import scoreboardv2
        
        # 转换为MM/DD/YYYY格式
        game_date_str = game_date.strftime('%m/%d/%Y')
        month, day, year = game_date_str.split('/')
        
        # 使用ScoreboardV2获取比赛数据
        scoreboard = scoreboardv2.ScoreboardV2(
            game_date=game_date_str,
            league_id='00'
        )
        
        # 获取比赛列表
        games_df = scoreboard.get_data_frames()[0]
        game_ids = games_df['GAME_ID'].tolist()
        
        print(f"找到 {len(game_ids)} 场比赛")
        return game_ids
    except Exception as e:
        print(f"获取比赛数据失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_player_stats(game_id):
    """获取指定比赛的球员数据"""
    try:
        # 使用新的API端点
        from nba_api.stats.endpoints import boxscoretraditionalv3, boxscoresummaryv3
        
        # 获取比赛传统数据
        boxscore = boxscoretraditionalv3.BoxScoreTraditionalV3(game_id=game_id)
        player_stats = boxscore.get_data_frames()[0]
        
        # 获取比赛基本信息
        summary = boxscoresummaryv3.BoxScoreSummaryV3(game_id=game_id)
        
        # 检查所有可用的数据帧
        data_frames = summary.get_data_frames()
        print(f"Number of data frames: {len(data_frames)}")
        
        # 尝试从不同的数据帧获取球队信息
        home_team = "Unknown"
        away_team = "Unknown"
        home_score = 0
        away_score = 0
        
        # 从球员数据中获取唯一的球队
        teams_in_game = player_stats['teamTricode'].unique()
        print(f"Teams in game: {teams_in_game}")
        
        # 计算每个球队的总得分
        team_scores = {}
        for team in teams_in_game:
            team_players = player_stats[player_stats['teamTricode'] == team]
            team_score = team_players['points'].sum()
            team_scores[team] = team_score
        
        print(f"Team scores: {team_scores}")
        
        # 确定主客队和得分
        if len(teams_in_game) == 2:
            team1, team2 = teams_in_game
            score1, score2 = team_scores[team1], team_scores[team2]
            
            # 简单分配主客队（实际API可能有其他方式确定）
            home_team = player_stats[player_stats['teamTricode'] == team1]['teamName'].iloc[0]
            away_team = player_stats[player_stats['teamTricode'] == team2]['teamName'].iloc[0]
            home_score = score1
            away_score = score2
        
        # 添加比赛信息到球员数据
        player_stats['GAME_DATE'] = TARGET_DATE
        player_stats['HOME_TEAM'] = home_team
        player_stats['AWAY_TEAM'] = away_team
        player_stats['HOME_SCORE'] = home_score
        player_stats['AWAY_SCORE'] = away_score
        
        # 计算比赛胜负
        def is_winner(row):
            team = row['teamTricode']
            team_score = team_scores.get(team, 0)
            # 比较得分确定胜负
            if len(team_scores) == 2:
                other_team = [t for t in team_scores if t != team][0]
                other_score = team_scores[other_team]
                return team_score > other_score
            return False
        
        player_stats['IS_WINNER'] = player_stats.apply(is_winner, axis=1)
        
        # 计算两分数据（总投篮 - 三分投篮）
        player_stats['twoPointersMade'] = player_stats['fieldGoalsMade'] - player_stats['threePointersMade']
        player_stats['twoPointersAttempted'] = player_stats['fieldGoalsAttempted'] - player_stats['threePointersAttempted']
        
        return player_stats
    except Exception as e:
        print(f"获取球员数据失败 (Game ID: {game_id}): {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print(f"查询 {TARGET_DATE} NBA比赛结果和球员数据...")
    
    # 获取指定日期的所有比赛
    game_ids = get_games_by_date(TARGET_DATE)
    
    if not game_ids:
        print("未找到比赛数据")
        return
    
    # 收集所有球员数据
    all_player_stats = []
    
    for game_id in game_ids:
        print(f"处理比赛: {game_id}")
        player_stats = get_player_stats(game_id)
        if player_stats is not None:
            all_player_stats.append(player_stats)
    
    if not all_player_stats:
        print("未获取到球员数据")
        return
    
    # 合并所有球员数据
    combined_stats = pd.concat(all_player_stats, ignore_index=True)
    
    # 选择并重命名字段以符合要求
    required_fields = {
        'personId': '球员id',
        'teamName': '球队名',
        'minutes': '上场时间',
        'threePointersMade': '三分命中数',
        'threePointersAttempted': '三分出手数',
        'twoPointersMade': '两分命中数',
        'twoPointersAttempted': '两分出手数',
        'freeThrowsMade': '罚球命中数',
        'freeThrowsAttempted': '罚球出手数',
        'reboundsOffensive': '进攻篮板',
        'reboundsDefensive': '防守篮板',
        'assists': '助攻',
        'steals': '抢断',
        'blocks': '盖帽',
        'turnovers': '失误',
        'foulsPersonal': '犯规',
        'IS_WINNER': '本场比赛是否获胜'
    }
    
    # 确保所有必要的列都存在
    for col in required_fields.keys():
        if col not in combined_stats.columns:
            combined_stats[col] = 0
    
    # 选择并重命名字段
    formatted_stats = combined_stats[list(required_fields.keys())].rename(columns=required_fields)
    
    # 导出为CSV文件
    import os
    # 确保输出目录存在
    output_dir = 'player_stats_data'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = f'{output_dir}/nba_player_stats_{TARGET_DATE.replace("-", "_")}.csv'
    formatted_stats.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n数据导出完成！")
    print(f"文件保存为: {output_file}")
    print(f"总记录数: {len(formatted_stats)}")
    print(f"涉及比赛数: {len(game_ids)}")
    print(f"导出字段数: {len(formatted_stats.columns)}")
    print(f"字段列表: {list(formatted_stats.columns)}")

if __name__ == "__main__":
    main()
