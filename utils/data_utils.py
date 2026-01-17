import pandas as pd
import streamlit as st
from nba_api.stats.endpoints import leaguegamefinder, playergamelogs
from nba_api.stats.library.parameters import SeasonNullable, SeasonTypeNullable
from utils.constants import POSITION_TRANSLATION, TEAM_TRANSLATION, TEAM_ID_MAP

# 加载球员数据
def load_players_data():
    try:
        df = pd.read_csv("球员信息.csv")
        # 处理空值，将 NaN 转换为字符串
        df['team_name'] = df['team_name'].fillna('未知')
        df['team_abbr'] = df['team_abbr'].fillna('')
        
        # 翻译球队名称为中文
        df['team_name'] = df['team_name'].apply(lambda x: TEAM_TRANSLATION.get(x, x))
        
        # 翻译位置为中文
        def translate_position(position_str):
            positions = position_str.split('-')
            translated_positions = [POSITION_TRANSLATION.get(pos, pos) for pos in positions]
            return '-'.join(translated_positions)
        
        df['position'] = df['position'].apply(translate_position)
        
        # 处理多位置球员
        df['positions'] = df['position'].str.split('-')
        df['all_positions'] = df['position'].apply(lambda x: x.split('-'))
        return df
    except Exception as e:
        st.error(f"加载球员数据失败: {e}")
        return pd.DataFrame()

# 计算薪资总额
def calculate_total_salary(players):
    if players.empty:
        return 0
    return sum(players['salary'])

# 获取球队ID
def get_team_id(team_name):
    # 反向查找球队ID
    return TEAM_ID_MAP.get(team_name, None)

# 查询指定日期的比赛
def get_games_by_date(date_str):
    try:
        gamefinder = leaguegamefinder.LeagueGameFinder(
            date_from_nullable=date_str,
            date_to_nullable=date_str,
            season_nullable=SeasonNullable.default,
            season_type_nullable=SeasonTypeNullable.regular_season
        )
        games = gamefinder.get_data_frames()[0]
        return games
    except Exception as e:
        st.error(f"查询比赛失败: {e}")
        return pd.DataFrame()

# 查询球员在指定日期的比赛数据
def get_player_game_stats(player_id, date_str):
    try:
        gamelogs = playergamelogs.PlayerGameLogs(
            player_id_nullable=player_id,
            date_from_nullable=date_str,
            date_to_nullable=date_str,
            season_nullable=SeasonNullable.default,
            season_type_nullable=SeasonTypeNullable.regular_season
        )
        stats = gamelogs.get_data_frames()[0]
        return stats
    except Exception as e:
        st.error(f"查询球员数据失败: {e}")
        return pd.DataFrame()
