import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st

# 导入拆分的模块
from utils.constants import SALARY_LIMIT, FIXED_POSITIONS, POSITION_FULL_NAMES
from utils.data_processor import load_players_data, filter_players, sort_players, get_paged_players, calculate_total_salary, format_salary
from utils.lineup_manager import add_player_to_lineup, move_player_to_starters, move_player_to_bench, remove_player_from_lineup, validate_lineup, prepare_export_data, reset_lineup
from utils.lineup_utils import can_play_position
from utils.ranking import get_player_stats, run_stats_script, should_use_cache
from utils.result_viewer import load_lineup_data, display_lineup_results

# 设置页面标题和布局
st.set_page_config(
    page_title="Scout's Lens", layout="wide", initial_sidebar_state="expanded"
)

# 主应用
def main():
    # 初始化会话状态
    if "selected_players" not in st.session_state:
        st.session_state.selected_players = pd.DataFrame()
    if "starters" not in st.session_state:
        st.session_state.starters = pd.DataFrame()
    if "bench" not in st.session_state:
        st.session_state.bench = pd.DataFrame()
    if "starters_positions" not in st.session_state:
        # 存储首发球员的位置分配，格式为 {player_id: position}
        st.session_state.starters_positions = {}
    if "current_page" not in st.session_state:
        st.session_state.current_page = "main"
    if "active_section" not in st.session_state:
        st.session_state.active_section = "阵容选择"
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False

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
            min_salary = 0
            max_salary = 60000000  # 设置最大薪资上限为6千万美元
            
            # 手动输入薪资范围（单位：千万美元）
            st.sidebar.subheader("手动输入薪资范围")
            col1, col2 = st.sidebar.columns(2)
            
            # 转换为千万美元单位显示
            min_salary_million = min_salary / 10000000
            max_salary_million = max_salary / 10000000
            
            with col1:
                manual_min_million = st.number_input(
                    "最小薪资 (千万美元)",
                    min_value=min_salary_million,
                    max_value=max_salary_million,
                    value=min_salary_million,
                    step=0.1,
                    format="%.1f"
                )
            with col2:
                manual_max_million = st.number_input(
                    "最大薪资 (千万美元)",
                    min_value=min_salary_million,
                    max_value=max_salary_million,
                    value=max_salary_million,
                    step=0.1,
                    format="%.1f"
                )

            # 转换回美元单位用于过滤
            manual_min = int(manual_min_million * 10000000)
            manual_max = int(manual_max_million * 10000000)

            # 确保手动输入的值有效
            if manual_min > manual_max:
                st.sidebar.error("最小薪资不能大于最大薪资")
                # 重置为默认值
                manual_min, manual_max = min_salary, max_salary

            # 设置薪资范围
            salary_range = (manual_min, manual_max)

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
                st.session_state.selected_players, st.session_state.starters, st.session_state.bench = reset_lineup()
                st.session_state.starters_positions = {}
                # 强制重新运行以更新界面
                st.rerun()

            # 应用过滤
            selected_player_ids = []
            if not st.session_state.selected_players.empty:
                selected_player_ids = st.session_state.selected_players["player_id"].values
            
            filtered_df = filter_players(df, selected_positions, selected_teams, salary_range, selected_player_ids)

            # 应用排序
            filtered_df = sort_players(filtered_df, sort_by, sort_order)

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
            current_page_players = get_paged_players(filtered_df, page, page_size)

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
                        # 添加球员
                        new_player = filtered_df[
                            filtered_df["player_id"] == player["player_id"]
                        ]
                        st.session_state.selected_players, st.session_state.bench = add_player_to_lineup(
                            st.session_state.selected_players, 
                            st.session_state.bench, 
                            new_player
                        )
                        # 强制重新运行以更新界面
                        st.rerun()

            # 显示当前阵容
            st.header("🏆 当前阵容")

            # 首发阵容：五槽位配置界面
            st.subheader("首发阵容 - 位置配置")
            
            # 创建五列布局，每列对应一个位置槽位
            position_cols = st.columns(5)
            
            # 存储首发球员的位置分配信息
            starters_with_positions = []
            
            # 遍历每个位置槽位
            for i, (position, col) in enumerate(zip(FIXED_POSITIONS, position_cols)):
                with col:
                    # 显示位置标签
                    st.markdown(f"### {position}\n*{POSITION_FULL_NAMES[position]}*")
                    
                    # 检查是否有球员分配到当前位置
                    assigned_player = None
                    for player_id, pos in st.session_state.starters_positions.items():
                        if pos == position:
                            # 找到分配到当前位置的球员
                            if not st.session_state.starters.empty:
                                player_mask = st.session_state.starters['player_id'] == player_id
                                if player_mask.any():
                                    assigned_player = st.session_state.starters[player_mask].iloc[0]
                    
                    # 确定槽位背景颜色
                    slot_color = "#e0e0e0"  # 默认灰色
                    if assigned_player is not None:
                        # 检查球员是否可以担任当前位置
                        if "all_positions" in assigned_player:
                            player_positions = assigned_player["all_positions"]
                            if can_play_position(player_positions, position):
                                slot_color = "#c8e6c9"  # 绿色：可以担任
                            else:
                                slot_color = "#ffcdd2"  # 红色：不能担任
                    
                    # 使用容器显示槽位，设置背景颜色
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="background-color: {slot_color}; padding: 15px; border-radius: 10px;">
                            """, 
                            unsafe_allow_html=True
                        )
                        
                        # 显示槽位内容
                        if assigned_player is not None:
                            # 显示已分配的球员
                            st.markdown(f"**{assigned_player['full_name']}**")
                            st.markdown(f"{assigned_player['team_name']}")
                            st.markdown(f"${assigned_player['salary']:,.0f}")
                            
                            # 添加操作按钮
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"→替补", key=f"to_bench_{assigned_player['player_id']}"):
                                    # 从首发移到替补
                                    st.session_state.starters, st.session_state.bench = move_player_to_bench(
                                        st.session_state.starters, 
                                        st.session_state.bench, 
                                        st.session_state.selected_players, 
                                        assigned_player["player_id"]
                                    )
                                    # 从位置分配中移除
                                    if assigned_player["player_id"] in st.session_state.starters_positions:
                                        del st.session_state.starters_positions[assigned_player["player_id"]]
                                    # 强制重新运行以更新界面
                                    st.rerun()
                            with col2:
                                # 位置选择下拉框
                                available_positions = []
                                if "all_positions" in assigned_player:
                                    player_positions = assigned_player["all_positions"]
                                    for pos in FIXED_POSITIONS:
                                        if can_play_position(player_positions, pos):
                                            available_positions.append(pos)
                                
                                if available_positions:
                                    new_position = st.selectbox(
                                        "调整位置", 
                                        available_positions, 
                                        index=available_positions.index(position) if position in available_positions else 0,
                                        key=f"pos_select_{assigned_player['player_id']}"
                                    )
                                    
                                    if new_position != position:
                                        # 检查目标位置是否已被其他球员占用
                                        position_occupied = False
                                        for player_id, pos in st.session_state.starters_positions.items():
                                            if pos == new_position and player_id != assigned_player["player_id"]:
                                                position_occupied = True
                                                break
                                        
                                        if position_occupied:
                                            # 显示错误提示
                                            st.error("无法完成操作：目标位置已被占用，请先调整该位置的现有球员")
                                        else:
                                            # 更新位置分配
                                            st.session_state.starters_positions[assigned_player["player_id"]] = new_position
                                            # 强制重新运行以更新界面
                                            st.rerun()
                        else:
                            # 显示空槽位
                            st.info("点击下方替补球员的'→首发'按钮添加球员")
                        
                        st.markdown(
                            f"""
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
            
            # 替补阵容
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
                            # 从替补移到首发
                            st.session_state.starters, st.session_state.bench = move_player_to_starters(
                                st.session_state.starters, 
                                st.session_state.bench, 
                                st.session_state.selected_players, 
                                player["player_id"]
                            )
                            
                            # 为新添加的首发球员分配位置
                            # 找到第一个可用的位置槽位
                            available_position = None
                            for pos in FIXED_POSITIONS:
                                # 检查位置是否已被占用
                                position_taken = False
                                for p_id, assigned_pos in st.session_state.starters_positions.items():
                                    if assigned_pos == pos:
                                        position_taken = True
                                        break
                                
                                if not position_taken:
                                    # 检查球员是否可以担任该位置
                                    if "all_positions" in player:
                                        player_positions = player["all_positions"]
                                        if can_play_position(player_positions, pos):
                                            available_position = pos
                                            break
                            
                            # 如果找到可用位置，分配给球员
                            if available_position:
                                st.session_state.starters_positions[player["player_id"]] = available_position
                                # 强制重新运行以更新界面
                                st.rerun()
                            else:
                                # 没有可用位置，将球员移回替补
                                st.session_state.starters, st.session_state.bench = move_player_to_bench(
                                    st.session_state.starters, 
                                    st.session_state.bench, 
                                    st.session_state.selected_players, 
                                    player["player_id"]
                                )
                                # 显示错误提示
                                st.error("无法完成操作：所有首发位置已被占用，且没有适合该球员的可用位置")
                                # 强制重新运行以更新界面
                                st.rerun()
                    with col6:
                        if st.button("移除", key=f"remove_{player['player_id']}"):
                            # 从阵容中移除
                            st.session_state.selected_players, st.session_state.starters, st.session_state.bench = remove_player_from_lineup(
                                st.session_state.selected_players, 
                                st.session_state.starters, 
                                st.session_state.bench, 
                                player["player_id"]
                            )
                            # 从位置分配中移除（如果存在）
                            if player["player_id"] in st.session_state.starters_positions:
                                del st.session_state.starters_positions[player["player_id"]]
                            # 强制重新运行以更新界面
                            st.rerun()
            else:
                st.info("尚未选择替补球员")
            
            # 准备位置分配验证数据
            for player_id, position in st.session_state.starters_positions.items():
                if not st.session_state.starters.empty:
                    player_mask = st.session_state.starters['player_id'] == player_id
                    if player_mask.any():
                        player = st.session_state.starters[player_mask].iloc[0]
                        starters_with_positions.append({
                            "player": player,
                            "position": position
                        })

            # 导出功能
            st.header("📤 导出阵容")

            if not st.session_state.selected_players.empty:
                # 检查各项限制条件
                validation_result = validate_lineup(
                    st.session_state.starters, 
                    st.session_state.bench, 
                    total_salary,
                    starters_with_positions
                )
                
                valid_lineup = validation_result["valid_lineup"]
                starters_count = len(st.session_state.starters)
                bench_count = len(st.session_state.bench)

                # 显示阵容限制条件
                with st.container():
                    st.subheader("📋 阵容限制条件")
                    st.markdown("---")

                    # 首发阵容检查
                    with st.expander("1. 首发阵容", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：首发必须有5名球员")
                        with col_right:
                            if validation_result["starters_valid"]:
                                st.success(f"✅ {starters_count}/5")
                            else:
                                st.error(f"❌ {starters_count}/5")

                    # 替补阵容检查
                    with st.expander("2. 替补阵容", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：替补必须有7名球员")
                        with col_right:
                            if validation_result["bench_valid"]:
                                st.success(f"✅ {bench_count}/7")
                            else:
                                st.error(f"❌ {bench_count}/7")

                    # 首发位置要求检查
                    with st.expander("3. 首发位置要求", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：首发必须有5名球员")
                        with col_right:
                            if validation_result["positions_valid"]:
                                st.success(f"✅ 符合要求")
                            else:
                                st.error(f"❌ 不符合要求")
                    
                    # 位置分配验证
                    with st.expander("4. 位置分配验证", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write("要求：每个球员必须分配到其可担任的位置")
                        with col_right:
                            if validation_result["position_assignment_valid"]:
                                st.success(f"✅ 符合要求")
                            else:
                                st.error(f"❌ 不符合要求")

                    # 薪资要求检查
                    with st.expander("5. 薪资要求", expanded=True):
                        col_left, col_right = st.columns([3, 2])
                        with col_left:
                            st.write(f"要求：总薪资不超过 ${SALARY_LIMIT:,.0f}")
                        with col_right:
                            if validation_result["salary_valid"]:
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
                        export_df = prepare_export_data(
                            st.session_state.starters, 
                            st.session_state.bench, 
                            total_salary
                        )

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
                # 加载阵容数据
                lineup_df = load_lineup_data(uploaded_file)
                
                if not lineup_df.empty:
                    # 显示导入的球员数据
                    st.header("📋 导入的球员数据")
                    st.dataframe(lineup_df, use_container_width=True, hide_index=True)
                    
                    # 显示结果
                    st.header("📊 得分计算")
                    display_lineup_results(lineup_df)
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
            if st.button("获取数据", disabled=st.session_state.is_loading):
                # 设置加载状态为True
                st.session_state.is_loading = True
                # 显示用户选择的原始日期
                user_date_str = selected_date.strftime("%Y-%m-%d")
                
                try:
                    # 检查缓存
                    csv_file = f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
                    if os.path.exists(csv_file) and should_use_cache(target_date_str):
                        st.success(f"使用缓存数据: {user_date_str}")
                        # 直接读取缓存文件
                        try:
                            player_stats_df, error_msg = get_player_stats(target_date_str, user_date_str)
                            
                            if not player_stats_df.empty:
                                # 显示数据
                                st.header("📊 球员数据排行榜")
                                
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
                                if error_msg:
                                    st.error(f"读取缓存数据失败: {error_msg}")
                                else:
                                    st.error("缓存数据为空")
                        except Exception as e:
                            st.error(f"读取缓存数据时出错: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        with st.spinner(f"正在获取 {user_date_str} 的比赛数据..."):
                            try:
                                # 运行脚本
                                success, result = run_stats_script(target_date_str)
                                
                                if success:
                                    player_stats_df, error_msg = get_player_stats(target_date_str, user_date_str)
                                    
                                    if not player_stats_df.empty:
                                        # 显示数据
                                        st.header("📊 球员数据排行榜")
                                        
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
                                        if error_msg:
                                            st.error(f"获取数据失败: {error_msg}")
                                        else:
                                            st.error("获取的数据为空")
                                else:
                                    st.error(f"数据获取失败: {result}")

                            except Exception as e:
                                st.error(f"获取数据时出错: {e}")
                                import traceback
                                traceback.print_exc()
                finally:
                    # 无论成功失败，都设置加载状态为False
                    st.session_state.is_loading = False


if __name__ == "__main__":
    main()