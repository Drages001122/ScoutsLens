import pandas as pd
import streamlit as st
from utils.constants import TEAM_TRANSLATION, POSITION_TRANSLATION


def load_players_data():
    """加载球员数据并进行预处理"""
    try:
        df = pd.read_csv("data/player_information.csv")
        # 处理空值，将 NaN 转换为字符串
        df["team_name"] = df["team_name"].fillna("未知")
        df["team_abbr"] = df["team_abbr"].fillna("")

        # 翻译球队名称为中文
        df["team_name"] = df["team_name"].apply(lambda x: TEAM_TRANSLATION.get(x, x))

        # 翻译位置为中文
        def translate_position(position_str):
            positions = position_str.split("-")
            translated_positions = [
                POSITION_TRANSLATION.get(pos, pos) for pos in positions
            ]
            return "-".join(translated_positions)

        df["position"] = df["position"].apply(translate_position)

        # 处理多位置球员
        df["positions"] = df["position"].str.split("-")
        df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
        return df
    except Exception as e:
        st.error(f"加载球员数据失败: {e}")
        return pd.DataFrame()


def filter_players(df, selected_positions, selected_teams, salary_range, selected_player_ids):
    """根据过滤条件筛选球员"""
    filtered_df = df.copy()

    # 排除已经在阵容中的球员
    if selected_player_ids is not None and not filtered_df.empty and "player_id" in filtered_df.columns:
        # 检查是否为空，同时处理列表和NumPy数组
        try:
            # 尝试使用len()检查（适用于列表）
            is_empty = len(selected_player_ids) == 0
        except TypeError:
            # 处理NumPy数组的情况
            is_empty = selected_player_ids.size == 0
        
        if not is_empty:
            filtered_df = filtered_df[
                ~filtered_df["player_id"].isin(selected_player_ids)
            ]

    # 位置过滤
    if selected_positions and not filtered_df.empty and "all_positions" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["all_positions"].apply(
                lambda x: any(pos in x for pos in selected_positions)
            )
        ]

    # 球队过滤
    if selected_teams and not filtered_df.empty and "team_name" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["team_name"].isin(selected_teams)]

    # 薪资范围过滤
    if not filtered_df.empty and "salary" in filtered_df.columns:
        filtered_df = filtered_df[
            (filtered_df["salary"] >= salary_range[0])
            & (filtered_df["salary"] <= salary_range[1])
        ]

    return filtered_df


def sort_players(df, sort_by, sort_order):
    """根据排序条件对球员进行排序"""
    if df.empty or sort_by not in df.columns:
        return df
    ascending = sort_order == "升序"
    return df.sort_values(by=sort_by, ascending=ascending)


def get_paged_players(df, page, page_size):
    """获取分页后的球员数据"""
    if page <= 0:
        return df
    if page_size <= 0:
        return pd.DataFrame()
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]


def calculate_total_salary(players):
    """计算球员总薪资"""
    if players.empty:
        return 0
    return sum(players["salary"])


def format_salary(salary):
    """格式化薪资显示"""
    if pd.isna(salary):
        return "$0"
    try:
        return f"${int(salary):,}"
    except:
        return "$0"