import os
import subprocess
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import streamlit as st

# 导入拆分的模块
from utils.constants import SALARY_LIMIT
from utils.data_utils import calculate_total_salary, load_players_data
from utils.lineup_utils import check_lineup_requirements

# 设置页面标题和布局
st.set_page_config(
    page_title="Scout's Lens", layout="wide", initial_sidebar_state="expanded"
)


# 辅助函数：将值转换为数字，处理"none"和NaN情况
def to_numeric(value, default=0):
    if value is None:
        return default
    if isinstance(value, str):
        if value.strip().lower() == "none":
            return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

# 计算PER评分的函数
def calculate_per(row):
    # PER=3P+(2P×0.8)+(FT×0.5)+ORB+(DRB×0.7)+AST+STL+BLK−(FGA−FG)×0.7−(FTA−FT)×0.4−TOV−PF×0.4
    three_pointers_made = to_numeric(row.get("三分命中数", 0))
    two_pointers_made = to_numeric(row.get("两分命中数", 0))
    free_throws_made = to_numeric(row.get("罚球命中数", 0))
    offensive_rebounds = to_numeric(row.get("进攻篮板", 0))
    defensive_rebounds = to_numeric(row.get("防守篮板", 0))
    assists = to_numeric(row.get("助攻", 0))
    steals = to_numeric(row.get("抢断", 0))
    blocks = to_numeric(row.get("盖帽", 0))

    # 计算投篮和罚球的未命中数
    field_goals_attempted = to_numeric(row.get("两分出手数", 0)) + to_numeric(row.get("三分出手数", 0))
    field_goals_made = two_pointers_made + three_pointers_made
    field_goals_missed = field_goals_attempted - field_goals_made

    free_throws_attempted = to_numeric(row.get("罚球出手数", 0))
    free_throws_missed = free_throws_attempted - free_throws_made

    turnovers = to_numeric(row.get("失误", 0))
    personal_fouls = to_numeric(row.get("犯规", 0))

    # 计算PER
    try:
        per = (
            three_pointers_made
            + (two_pointers_made * 0.8)
            + (free_throws_made * 0.5)
            + offensive_rebounds
            + (defensive_rebounds * 0.7)
            + assists
            + steals
            + blocks
            - (field_goals_missed * 0.7)
            - (free_throws_missed * 0.4)
            - turnovers
            - (personal_fouls * 0.4)
        )
        # 确保per是一个有效的数字
        if pd.isna(per):
            per = 0
    except:
        per = 0

    # 检查是否有上场时间且球队获胜/落败
    playing_time = row.get("上场时间", "")
    # 同时检查"获胜"和"本场比赛是否获胜"字段，确保在不同场景下都能正确获取获胜状态
    game_won = row.get("获胜", row.get("本场比赛是否获胜", False))

    # 处理game_won的值，确保它是布尔类型
    if isinstance(game_won, str):
        game_won_str = game_won.strip().lower()
        if game_won_str == "true" or game_won_str == "1" or game_won_str == "是":
            game_won = True
        else:
            game_won = False
    elif not isinstance(game_won, bool):
        try:
            game_won = bool(game_won)
        except:
            game_won = False

    # 只有当有上场时间且上场时间不为None、不为空字符串、不为NaN时才考虑胜负加成
    has_playing_time = False
    if playing_time is not None:
        if isinstance(playing_time, str):
            has_playing_time = playing_time.strip() != ""
        else:
            # 处理数值类型（如NaN）
            has_playing_time = not pd.isna(playing_time)

    if has_playing_time:
        if game_won:
            per += 2
        else:
            per -= 2

    return per

# 主应用
def main():
    # 初始化会话状态
    if "selected_players" not in st.session_state:
        st.session_state.selected_players = pd.DataFrame()
    if "starters" not in st.session_state:
        st.session_state.starters = pd.DataFrame()
    if "bench" not in st.session_state:
        st.session_state.bench = pd.DataFrame()
    if "current_page" not in st.session_state:
        st.session_state.current_page = "main"
    if "active_section" not in st.session_state:
        st.session_state.active_section = "阵容选择"

    # 侧边栏：板块切换
    st.sidebar.title("🏀 Scout's Lens")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("阵容选择", key="btn_lineup", use_container_width=True):
            st.session_state.active_section = "阵容选择"
    with col2:
        if st.button("排行榜", key="btn_ranking", use_container_width=True):
            st.session_state.active_section = "排行榜"
    
    # 第二行按钮
    col3, col4 = st.sidebar.columns(2)
    with col3:
        if st.button("查看结果", key="btn_view_results", use_container_width=True):
            st.session_state.active_section = "查看结果"
    with col4:
        # 空列，保持布局平衡
        pass
    
    st.sidebar.markdown("---")

    # 加载数据
    df = load_players_data()
    if df.empty and st.session_state.active_section == "阵容选择":
        return

    # 主页面
    if st.session_state.current_page == "main":
        if st.session_state.active_section == "阵容选择":
            st.title("🏀 阵容选择")

            # 侧边栏：过滤和排序选项
            st.sidebar.header("🔍 过滤和排序")

            # 位置过滤
            positions = ["后卫", "前锋", "中锋"]
            selected_positions = st.sidebar.multiselect("位置", positions, default=[])

            # 球队过滤
            teams = sorted(df["team_name"].unique())
            selected_teams = st.sidebar.multiselect("球队", teams, default=[])

            # 薪资范围过滤
            min_salary, max_salary = int(df["salary"].min()), int(df["salary"].max())
            salary_range = st.sidebar.slider(
                "薪资范围 ($)",
                min_salary,
                max_salary,
                (min_salary, max_salary),
                step=1000000,
            )

            # 排序选项
            sort_by = st.sidebar.selectbox(
                "排序依据", ["salary", "player_id", "full_name", "team_name"], index=0
            )

            sort_order = st.sidebar.radio("排序顺序", ["降序", "升序"], index=0)

            # 侧边栏：阵容信息
            st.sidebar.header("📊 阵容信息")

            # 显示总薪资
            total_salary = calculate_total_salary(st.session_state.selected_players)

            # 计算剩余可支配薪资
            remaining_salary = SALARY_LIMIT - total_salary

            st.sidebar.write(f"总薪资: ${total_salary:,.0f}")
            st.sidebar.write(f"薪资上限: ${SALARY_LIMIT:,.0f}")
            st.sidebar.write(f"剩余可支配薪资: ${remaining_salary:,.0f}")

            # 检查薪资是否超过上限
            if total_salary > SALARY_LIMIT:
                st.sidebar.error("⚠️ 薪资总额超过上限!")
            else:
                st.sidebar.success("✅ 薪资总额在限制范围内")

            # 显示已选择球员数量
            st.sidebar.write(f"已选择球员: {len(st.session_state.selected_players)}/12")

            # 重置阵容按钮
            if st.sidebar.button("🔄 重置阵容"):
                st.session_state.selected_players = pd.DataFrame()
                st.session_state.starters = pd.DataFrame()
                st.session_state.bench = pd.DataFrame()
                # 强制重新运行以更新界面
                st.rerun()

            # 应用过滤
            filtered_df = df.copy()

            # 排除已经在阵容中的球员
            if not st.session_state.selected_players.empty:
                selected_player_ids = st.session_state.selected_players[
                    "player_id"
                ].values
                filtered_df = filtered_df[
                    ~filtered_df["player_id"].isin(selected_player_ids)
                ]

            if selected_positions:
                filtered_df = filtered_df[
                    filtered_df["all_positions"].apply(
                        lambda x: any(pos in x for pos in selected_positions)
                    )
                ]

            if selected_teams:
                filtered_df = filtered_df[filtered_df["team_name"].isin(selected_teams)]

            filtered_df = filtered_df[
                (filtered_df["salary"] >= salary_range[0])
                & (filtered_df["salary"] <= salary_range[1])
            ]

            # 应用排序
            ascending = sort_order == "升序"
            filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)

            # 主界面布局
            st.header("📋 球员列表")

            # 显示过滤后的球员数量
            st.write(f"找到 {len(filtered_df)} 名球员")

            # 分页控件
            page_size = st.selectbox(
                "每页显示数量", options=[10, 15, 20, 50, 100], index=1
            )
            total_pages = (len(filtered_df) + page_size - 1) // page_size

            # 页码选择
            if total_pages > 1:
                page = st.number_input(
                    "页码", min_value=1, max_value=total_pages, value=1
                )
            else:
                page = 1

            # 计算当前页的球员范围
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            current_page_players = filtered_df.iloc[start_idx:end_idx]

            # 显示当前页信息
            st.write(f"显示第 {page} 页，共 {total_pages} 页")

            # 创建可选择的数据框
            for i, player in current_page_players.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                with col1:
                    st.write(player["full_name"])
                with col2:
                    st.write(player["position"])
                with col3:
                    st.write(player["team_name"])
                with col4:
                    st.write(f"${player['salary']:,.0f}")
                with col5:
                    if st.button("添加", key=f"add_{player['player_id']}"):
                        # 检查是否已经在阵容中
                        if not st.session_state.selected_players.empty:
                            if (
                                player["player_id"]
                                in st.session_state.selected_players["player_id"].values
                            ):
                                continue
                        # 添加球员
                        new_player = filtered_df[
                            filtered_df["player_id"] == player["player_id"]
                        ]
                        st.session_state.selected_players = pd.concat(
                            [st.session_state.selected_players, new_player]
                        )
                        # 同时添加到替补阵容
                        st.session_state.bench = pd.concat(
                            [st.session_state.bench, new_player]
                        )
                        # 强制重新运行以更新界面
                        st.rerun()

            # 显示当前阵容
            st.header("🏆 当前阵容")

            lineup_col1, lineup_col2 = st.columns(2)

            with lineup_col1:
                st.subheader("首发阵容")
                if not st.session_state.starters.empty:
                    # 显示首发球员列表，带有管理按钮
                    for i, player in st.session_state.starters.iterrows():
                        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                        with col1:
                            st.write(player["full_name"])
                        with col2:
                            st.write(player["position"])
                        with col3:
                            st.write(player["team_name"])
                        with col4:
                            st.write(f"${player['salary']:,.0f}")
                        with col5:
                            if st.button(
                                "→替补", key=f"to_bench_{player['player_id']}"
                            ):
                                # 从首发阵容移除
                                st.session_state.starters = st.session_state.starters[
                                    st.session_state.starters["player_id"]
                                    != player["player_id"]
                                ]
                                st.session_state.starters = (
                                    st.session_state.starters.reset_index(drop=True)
                                )
                                # 从selected_players中获取球员数据
                                player_data = st.session_state.selected_players[
                                    st.session_state.selected_players["player_id"]
                                    == player["player_id"]
                                ]
                                # 添加到替补阵容
                                st.session_state.bench = pd.concat(
                                    [st.session_state.bench, player_data]
                                )
                                st.session_state.bench = (
                                    st.session_state.bench.reset_index(drop=True)
                                )
                                # 强制重新运行以更新界面
                                st.rerun()
                else:
                    st.info("尚未选择首发球员")

            with lineup_col2:
                st.subheader("替补阵容")
                if not st.session_state.bench.empty:
                    # 显示替补球员列表，带有管理按钮
                    for i, player in st.session_state.bench.iterrows():
                        col1, col2, col3, col4, col5, col6 = st.columns(
                            [3, 2, 2, 2, 1, 1]
                        )
                        with col1:
                            st.write(player["full_name"])
                        with col2:
                            st.write(player["position"])
                        with col3:
                            st.write(player["team_name"])
                        with col4:
                            st.write(f"${player['salary']:,.0f}")
                        with col5:
                            if st.button(
                                "→首发", key=f"to_starter_{player['player_id']}"
                            ):
                                # 检查首发阵容是否已满
                                if len(st.session_state.starters) >= 5:
                                    pass
                                else:
                                    # 从替补阵容移除
                                    st.session_state.bench = st.session_state.bench[
                                        st.session_state.bench["player_id"]
                                        != player["player_id"]
                                    ]
                                    st.session_state.bench = (
                                        st.session_state.bench.reset_index(drop=True)
                                    )
                                    # 从selected_players中获取球员数据
                                    player_data = st.session_state.selected_players[
                                        st.session_state.selected_players["player_id"]
                                        == player["player_id"]
                                    ]
                                    # 添加到首发阵容
                                    st.session_state.starters = pd.concat(
                                        [st.session_state.starters, player_data]
                                    )
                                    st.session_state.starters = (
                                        st.session_state.starters.reset_index(drop=True)
                                    )
                                    # 强制重新运行以更新界面
                                    st.rerun()
                        with col6:
                            if st.button("移除", key=f"remove_{player['player_id']}"):
                                # 从替补阵容移除
                                st.session_state.bench = st.session_state.bench[
                                    st.session_state.bench["player_id"]
                                    != player["player_id"]
                                ]
                                # 从选中球员中移除
                                st.session_state.selected_players = (
                                    st.session_state.selected_players[
                                        st.session_state.selected_players["player_id"]
                                        != player["player_id"]
                                    ]
                                )
                                # 如果在首发阵容中，也从首发阵容移除
                                if not st.session_state.starters.empty:
                                    st.session_state.starters = (
                                        st.session_state.starters[
                                            st.session_state.starters["player_id"]
                                            != player["player_id"]
                                        ]
                                    )
                                # 强制重新运行以更新界面
                                st.rerun()
                else:
                    st.info("尚未选择替补球员")

            # 导出功能
            st.header("📤 导出阵容")

            if not st.session_state.selected_players.empty:
                # 检查各项限制条件
                starters_count = len(st.session_state.starters)
                bench_count = len(st.session_state.bench)
                total_players = starters_count + bench_count

                # 检查首发人数
                starters_valid = starters_count == 5
                # 检查替补人数
                bench_valid = bench_count == 7
                # 检查首发位置要求
                positions_valid = check_lineup_requirements(st.session_state.starters)
                # 检查薪资要求
                salary_valid = total_salary <= SALARY_LIMIT

                # 检查阵容是否完全符合要求
                valid_lineup = (
                    starters_valid and bench_valid and positions_valid and salary_valid
                )

                # 显示阵容限制条件
                with st.container():
                    st.subheader("📋 阵容限制条件")
                    st.markdown("---")

                    # 创建四列布局，每列一个限制条件
                    cols = st.columns(1)

                    # 首发阵容检查
                    with st.expander("1. 首发阵容", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：首发必须有5名球员")
                        with col_right:
                            if starters_valid:
                                st.success(f"✅ {starters_count}/5")
                            else:
                                st.error(f"❌ {starters_count}/5")

                    # 替补阵容检查
                    with st.expander("2. 替补阵容", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：替补必须有7名球员")
                        with col_right:
                            if bench_valid:
                                st.success(f"✅ {bench_count}/7")
                            else:
                                st.error(f"❌ {bench_count}/7")

                    # 首发位置要求检查
                    with st.expander("3. 首发位置要求", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：首发必须满足2后卫2前锋1中锋的位置要求")
                        with col_right:
                            if positions_valid:
                                st.success("✅ 符合要求")
                            else:
                                st.error("❌ 不符合要求")

                    # 薪资要求检查
                    with st.expander("4. 薪资要求", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write(f"要求：总薪资不超过 ${SALARY_LIMIT:,.0f}")
                        with col_right:
                            if salary_valid:
                                st.success(f"✅ ${total_salary:,.0f}")
                            else:
                                st.error(f"❌ ${total_salary:,.0f}")

                    st.markdown("---")

                # 显示阵容状态
                with st.container():
                    if valid_lineup:
                        st.success("🎉 所有限制条件都已满足，可以导出阵容！")

                        # 添加日期选择器
                        export_date = st.date_input(
                            "选择导出日期",
                            value=datetime.now(),
                            min_value=datetime(2020, 1, 1),
                        )

                        # 准备导出数据
                        export_data = {
                            "导出时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "总薪资": total_salary,
                            "薪资上限": SALARY_LIMIT,
                            "已选择球员数": total_players,
                            "首发阵容": (
                                st.session_state.starters[
                                    ["full_name", "position", "team_name", "salary"]
                                ].to_dict("records")
                                if not st.session_state.starters.empty
                                else []
                            ),
                            "替补阵容": (
                                st.session_state.bench[
                                    ["full_name", "position", "team_name", "salary"]
                                ].to_dict("records")
                                if not st.session_state.bench.empty
                                else []
                            ),
                        }

                        # 转换为DataFrame格式以便导出
                        export_df = pd.DataFrame()

                        # 添加首发
                        if not st.session_state.starters.empty:
                            starters_df = st.session_state.starters[
                                [
                                    "player_id",
                                    "full_name",
                                    "position",
                                    "team_name",
                                    "salary",
                                ]
                            ].copy()
                            starters_df["角色"] = "首发"
                            export_df = pd.concat([export_df, starters_df])

                        # 添加替补
                        if not st.session_state.bench.empty:
                            bench_df = st.session_state.bench[
                                [
                                    "player_id",
                                    "full_name",
                                    "position",
                                    "team_name",
                                    "salary",
                                ]
                            ].copy()
                            bench_df["角色"] = "替补"
                            export_df = pd.concat([export_df, bench_df])

                        # 导出为CSV
                        csv = export_df.to_csv(index=False, encoding="utf-8-sig")

                        # 美化导出按钮
                        st.markdown("---")
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.download_button(
                                label="📥 导出阵容为CSV文件",
                                data=csv,
                                file_name=f"scouts_lens_lineup_{export_date.strftime('%Y%m%d')}.csv",
                                mime="text/csv",
                                use_container_width=True,
                            )
                    else:
                        st.error("❌ 请满足以上限制条件问题后再尝试导出。")
                        st.info("💡 提示：点击上方的展开面板查看具体的限制条件详情")
            else:
                st.info("请先选择球员组成阵容")
        elif st.session_state.active_section == "查看结果":
            st.title("🏀 查看结果")
            
            # 文件上传
            uploaded_file = st.file_uploader("上传阵容CSV文件", type="csv")
            
            if uploaded_file is not None:
                # 读取上传的文件
                lineup_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
                
                # 显示导入的球员数据
                st.header("📋 导入的球员数据")
                st.dataframe(lineup_df, use_container_width=True, hide_index=True)
                
                # 计算用户得分
                st.header("📊 得分计算")
                
                # 读取球员信息文件
                player_info_df = pd.read_csv(
                    "d:\PycharmProjects\ScoutsLens\player_information.csv",
                    encoding="utf-8-sig",
                )
                # 确保薪资是数字类型
                player_info_df["salary"] = pd.to_numeric(player_info_df["salary"], errors='coerce').fillna(0).astype(int)
                
                # 计算总薪资
                total_salary = lineup_df["salary"].sum()
                st.write(f"总薪资: ${total_salary:,.0f}")
                
                # 计算球员数量
                total_players = len(lineup_df)
                st.write(f"球员数量: {total_players}")
                
                # 计算首发和替补数量
                starters_count = len(lineup_df[lineup_df["角色"] == "首发"])
                bench_count = len(lineup_df[lineup_df["角色"] == "替补"])
                st.write(f"首发数量: {starters_count}")
                st.write(f"替补数量: {bench_count}")
                
                # 尝试读取最新的比赛统计数据
                st.subheader("📈 球员详细数据")
                
                # 查找最新的比赛统计CSV文件
                stats_files = [f for f in os.listdir('player_stats_data') if f.startswith('nba_player_stats_') and f.endswith('.csv')]
                
                if stats_files:
                    # 按文件名排序，获取最新的文件
                    stats_files.sort(reverse=True)
                    latest_stats_file = stats_files[0]
                    
                    # 读取比赛统计数据
                    stats_df = pd.read_csv(os.path.join('player_stats_data', latest_stats_file), encoding="utf-8-sig")
                    
                    # 合并阵容数据和统计数据
                    merged_df = pd.merge(
                        lineup_df,
                        stats_df,
                        left_on="player_id",
                        right_on="球员id",
                        how="left"
                    )
                    
                    # 添加评分列
                    merged_df["评分"] = merged_df.apply(calculate_per, axis=1)
                    
                    # 计算得分
                    def calculate_score(row):
                        three_pointers = to_numeric(row.get("三分命中数", 0))
                        two_pointers = to_numeric(row.get("两分命中数", 0))
                        free_throws = to_numeric(row.get("罚球命中数", 0))
                        return 3 * three_pointers + 2 * two_pointers + 1 * free_throws
                    
                    merged_df["得分"] = merged_df.apply(calculate_score, axis=1)
                    
                    # 计算篮板
                    def calculate_rebounds(row):
                        offensive = to_numeric(row.get("进攻篮板", 0))
                        defensive = to_numeric(row.get("防守篮板", 0))
                        return offensive + defensive
                    
                    merged_df["篮板"] = merged_df.apply(calculate_rebounds, axis=1)
                    
                    # 调整字段顺序，与排行榜保持一致
                    desired_cols = [
                        "full_name", "team_name", "position", "salary", "评分",
                        "上场时间", "得分", "助攻", "篮板", "抢断", "盖帽",
                        "失误", "犯规", "三分命中数", "三分出手数", "两分命中数",
                        "两分出手数", "罚球命中数", "罚球出手数", "本场比赛是否获胜", "角色"
                    ]
                    
                    # 确保所有列都存在
                    existing_cols = [
                        col for col in desired_cols if col in merged_df.columns
                    ]
                    
                    # 构建最终数据框
                    display_df = merged_df[existing_cols].copy()
                    
                    # 重命名列，与排行榜保持一致
                    display_df = display_df.rename(columns={
                        "full_name": "球员名",
                        "team_name": "球队名",
                        "position": "位置",
                        "salary": "薪资",
                        "本场比赛是否获胜": "获胜"
                    })
                    
                    # 计算所有球员的评分总和（区分首发和替补）
                    # 对于首发球员，评分乘以2；对于替补球员，直接使用评分
                    total_rating = 0
                    for _, row in display_df.iterrows():
                        rating = to_numeric(row.get("评分", 0))
                        if row["角色"] == "首发":
                            total_rating += rating * 2
                        else:  # 替补
                            total_rating += rating
                    st.write(f"总评分: {total_rating:.2f}")
                    
                    # 显示详细的得分计算
                    st.subheader("📈 球员详细数据")
                    
                    # 格式化薪资
                    def format_salary(salary):
                        if pd.isna(salary):
                            return "$0"
                        try:
                            return f"${int(salary):,}"
                        except:
                            return "$0"
                    
                    display_df["薪资"] = display_df["薪资"].apply(format_salary)
                    
                    # 显示带有评分的球员列表
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=600,
                        column_config={
                            "评分": st.column_config.NumberColumn(
                                "评分",
                                format="%.1f"
                            )
                        },
                        hide_index=True
                    )
                else:
                    st.warning("未找到比赛统计数据，请先在排行榜中获取数据")
                    
                    # 如果没有统计数据，使用薪资计算预估得分
                    # 计算总得分（区分首发和替补）
                    # 对于首发球员，预估得分乘以2；对于替补球员，直接使用预估得分
                    total_score = 0
                    for _, row in lineup_df.iterrows():
                        salary = to_numeric(row.get("salary", 0))
                        player_score = salary * 0.01
                        if row["角色"] == "首发":
                            total_score += player_score * 2
                        else:  # 替补
                            total_score += player_score
                    st.write(f"预估得分: {total_score:.2f}")
                    
                    # 显示详细的得分计算
                    st.subheader("📈 得分明细")
                    
                    # 添加球员得分列
                    lineup_df["预估得分"] = lineup_df["salary"] * 0.01
                    
                    # 显示带有得分的球员列表
                    st.dataframe(
                        lineup_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "salary": st.column_config.NumberColumn(
                                "薪资",
                                format="$%d"
                            ),
                            "预估得分": st.column_config.NumberColumn(
                                "预估得分",
                                format="%.2f"
                            )
                        }
                    )
        elif st.session_state.active_section == "排行榜":
            st.title("🏀 球员排行榜")

            # 日期选择器
            default_date = datetime.now() - timedelta(days=1)
            selected_date = st.date_input(
                "选择比赛日期",
                value=default_date,
                min_value=datetime(2020, 1, 1),
                max_value=datetime.now(),
            )

            # 将北京时间转换为美国时间（减一天）
            api_date = selected_date - timedelta(days=1)
            # 转换为字符串格式
            target_date_str = api_date.strftime("%Y-%m-%d")

            # 运行nba_game_stats.py脚本获取数据
            if st.button("获取数据"):
                # 显示用户选择的原始日期
                user_date_str = selected_date.strftime("%Y-%m-%d")
                with st.spinner(f"正在获取 {user_date_str} 的比赛数据..."):
                    try:
                        # 构建命令
                        script_path = (
                            "d:\\PycharmProjects\\ScoutsLens\\nba_game_stats.py"
                        )
                        command = f"python {script_path}"

                        # 修改脚本中的TARGET_DATE
                        with open(script_path, "r", encoding="utf-8") as f:
                            script_content = f.read()

                        # 更新TARGET_DATE
                        import re

                        # 使用正则表达式更安全地替换TARGET_DATE
                        new_script_content = re.sub(
                            r"TARGET_DATE = '.*'",
                            f"TARGET_DATE = '{target_date_str}'",
                            script_content,
                        )

                        # 写回文件
                        with open(script_path, "w", encoding="utf-8") as f:
                            f.write(new_script_content)

                        # 运行脚本
                        result = subprocess.run(
                            command,
                            shell=True,
                            capture_output=True,
                            text=True,
                            cwd="d:\PycharmProjects\ScoutsLens",
                        )

                        # 不显示运行结果，只在有错误时记录

                        # 检查是否生成了CSV文件
                        csv_file = (
                            f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
                        )
                        if os.path.exists(csv_file):
                            # 导入常量
                            from utils.constants import TEAM_TRANSLATION, POSITION_TRANSLATION

                            # 读取球员信息文件，创建id到名字、位置、薪资的映射
                            player_info_df = pd.read_csv(
                                "d:\PycharmProjects\ScoutsLens\player_information.csv",
                                encoding="utf-8-sig",
                            )
                            # 确保薪资是数字类型
                            player_info_df["salary"] = pd.to_numeric(player_info_df["salary"], errors='coerce').fillna(0).astype(int)
                            player_id_to_name = dict(
                                zip(
                                    player_info_df["player_id"],
                                    player_info_df["full_name"],
                                )
                            )
                            player_id_to_position = dict(
                                zip(
                                    player_info_df["player_id"],
                                    player_info_df["position"],
                                )
                            )
                            player_id_to_salary = dict(
                                zip(
                                    player_info_df["player_id"],
                                    player_info_df["salary"],
                                )
                            )

                            # 使用常量中的球队名到中文名的映射
                            team_name_mapping = TEAM_TRANSLATION

                            # 读取数据
                            player_stats_df = pd.read_csv(
                                csv_file, encoding="utf-8-sig"
                            )

                            # 将球员id替换为球员名
                            player_stats_df["球员名"] = player_stats_df["球员id"].map(
                                player_id_to_name
                            )

                            # 添加位置和薪资字段
                            player_stats_df["位置"] = player_stats_df["球员id"].map(
                                player_id_to_position
                            )
                            player_stats_df["薪资"] = player_stats_df["球员id"].map(
                                player_id_to_salary
                            )
                            
                            # 确保薪资是数字类型
                            player_stats_df["薪资"] = pd.to_numeric(player_stats_df["薪资"], errors='coerce').fillna(0).astype(int)
                            
                            # 将位置转换为中文
                            def translate_position(pos):
                                if pd.isna(pos):
                                    return pos
                                # 处理复合位置，如"Guard-Forward"
                                translated_parts = []
                                for part in str(pos).split('-'):
                                    translated_parts.append(POSITION_TRANSLATION.get(part.strip(), part.strip()))
                                return '-'.join(translated_parts)
                            
                            player_stats_df["位置"] = player_stats_df["位置"].apply(translate_position)

                            # 将球队名替换为中文名
                            player_stats_df["球队名"] = player_stats_df["球队名"].map(
                                team_name_mapping
                            )

                            # 移除原始球员id列
                            player_stats_df = player_stats_df.drop("球员id", axis=1)

                            # 重新排列列，将球员名放在第一位
                            cols = ["球员名"] + [
                                col
                                for col in player_stats_df.columns
                                if col != "球员名"
                            ]
                            player_stats_df = player_stats_df[cols]

                            # 计算得分
                            player_stats_df["得分"] = (
                                3 * player_stats_df["三分命中数"]
                                + 2 * player_stats_df["两分命中数"]
                                + 1 * player_stats_df["罚球命中数"]
                            )

                            # 计算篮板（进攻篮板+防守篮板）
                            player_stats_df["篮板"] = (
                                player_stats_df["进攻篮板"]
                                + player_stats_df["防守篮板"]
                            )

                            # 将"本场比赛是否获胜"重命名为"获胜"
                            if "本场比赛是否获胜" in player_stats_df.columns:
                                player_stats_df = player_stats_df.rename(
                                    columns={"本场比赛是否获胜": "获胜"}
                                )

                            # 调整字段顺序
                            desired_cols = [
                                "球员名",
                                "球队名",
                                "位置",
                                "薪资",
                                "评分",
                                "上场时间",
                                "得分",
                                "助攻",
                                "篮板",
                                "抢断",
                                "盖帽",
                                "失误",
                                "犯规",
                                "三分命中数",
                                "三分出手数",
                                "两分命中数",
                                "两分出手数",
                                "罚球命中数",
                                "罚球出手数",
                            ]

                            # 确保所有列都存在
                            existing_cols = [
                                col
                                for col in desired_cols
                                if col in player_stats_df.columns
                            ]
                            # 添加剩余的列（如果有）
                            remaining_cols = [
                                col
                                for col in player_stats_df.columns
                                if col not in existing_cols and col != "获胜"
                            ]
                            # 构建最终列顺序：基础列 + 剩余列 + 获胜列（如果存在）
                            final_cols = existing_cols + remaining_cols
                            if "获胜" in player_stats_df.columns:
                                final_cols.append("获胜")

                            player_stats_df = player_stats_df[final_cols]

                            # 添加评分列
                            player_stats_df["评分"] = player_stats_df.apply(
                                calculate_per, axis=1
                            )

                            # 按评分排序
                            player_stats_df = player_stats_df.sort_values(
                                by="评分", ascending=False
                            )

                            # 重新排列列，将评分放到最前面，获胜放到最后面
                            non_rating_cols = [
                                col
                                for col in player_stats_df.columns
                                if col != "评分" and col != "获胜"
                            ]
                            if "获胜" in player_stats_df.columns:
                                cols = ["评分"] + non_rating_cols + ["获胜"]
                            else:
                                cols = ["评分"] + non_rating_cols
                            player_stats_df = player_stats_df[cols]

                            # 显示数据
                            st.header("📊 球员数据排行榜")
                            # 手动格式化薪资
                            def format_salary(salary):
                                if pd.isna(salary):
                                    return "$0"
                                try:
                                    return f"${int(salary):,}"
                                except:
                                    return "$0"
                            
                            # 创建一个带有格式化薪资的临时数据框
                            display_df = player_stats_df.copy()
                            display_df["薪资"] = display_df["薪资"].apply(format_salary)
                            
                            st.dataframe(
                                display_df,
                                use_container_width=True,
                                height=800,
                                column_config={
                                    "评分": st.column_config.NumberColumn(
                                        "评分",
                                        format="%.1f"
                                    )
                                },
                                hide_index=True
                            )
                        else:
                            st.error("数据获取失败，未生成CSV文件")

                    except Exception as e:
                        st.error(f"获取数据时出错: {e}")
                        import traceback

                        traceback.print_exc()


if __name__ == "__main__":
    main()
