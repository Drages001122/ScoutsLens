import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# 导入拆分的模块
from utils.constants import SALARY_LIMIT
from utils.data_utils import load_players_data, calculate_total_salary, get_team_id, get_games_by_date, get_player_game_stats
from utils.scoring_utils import calculate_player_score, calculate_weighted_score
from utils.lineup_utils import check_lineup_requirements

# 设置页面标题和布局
st.set_page_config(
    page_title="Scout's Lens",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 主应用
def main():
    # 初始化会话状态
    if 'selected_players' not in st.session_state:
        st.session_state.selected_players = pd.DataFrame()
    if 'starters' not in st.session_state:
        st.session_state.starters = pd.DataFrame()
    if 'bench' not in st.session_state:
        st.session_state.bench = pd.DataFrame()
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'
    
    # 侧边栏顶部：查看结果/返回按钮
    if st.session_state.current_page == 'main':
        if st.sidebar.button("📊 查看结果", use_container_width=True):
            st.session_state.current_page = 'results'
            st.rerun()
    else:
        if st.sidebar.button("⬅️ 返回", use_container_width=True):
            st.session_state.current_page = 'main'
            st.rerun()
    
    # 加载数据
    df = load_players_data()
    if df.empty:
        return
    
    # 主页面
    if st.session_state.current_page == 'main':
        st.title("🏀 Scout's Lens")
        
        # 侧边栏：过滤和排序选项
        st.sidebar.header("🔍 过滤和排序")
        
        # 位置过滤
        positions = ['后卫', '前锋', '中锋']
        selected_positions = st.sidebar.multiselect(
            "位置",
            positions,
            default=[]
        )
        
        # 球队过滤
        teams = sorted(df['team_name'].unique())
        selected_teams = st.sidebar.multiselect(
            "球队",
            teams,
            default=[]
        )
        
        # 薪资范围过滤
        min_salary, max_salary = int(df['salary'].min()), int(df['salary'].max())
        salary_range = st.sidebar.slider(
            "薪资范围 ($)",
            min_salary,
            max_salary,
            (min_salary, max_salary),
            step=1000000
        )
        
        # 排序选项
        sort_by = st.sidebar.selectbox(
            "排序依据",
            ['salary', 'player_id', 'full_name', 'team_name'],
            index=0
        )
        
        sort_order = st.sidebar.radio(
            "排序顺序",
            ['降序', '升序'],
            index=0
        )
        
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
            selected_player_ids = st.session_state.selected_players['player_id'].values
            filtered_df = filtered_df[~filtered_df['player_id'].isin(selected_player_ids)]
        
        if selected_positions:
            filtered_df = filtered_df[filtered_df['all_positions'].apply(
                lambda x: any(pos in x for pos in selected_positions)
            )]
        
        if selected_teams:
            filtered_df = filtered_df[filtered_df['team_name'].isin(selected_teams)]
        
        filtered_df = filtered_df[
            (filtered_df['salary'] >= salary_range[0]) & 
            (filtered_df['salary'] <= salary_range[1])
        ]
        
        # 应用排序
        ascending = sort_order == '升序'
        filtered_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # 主界面布局
        st.header("📋 球员列表")
        
        # 显示过滤后的球员数量
        st.write(f"找到 {len(filtered_df)} 名球员")
        
        # 分页控件
        page_size = st.selectbox("每页显示数量", options=[10, 15, 20, 50, 100], index=1)
        total_pages = (len(filtered_df) + page_size - 1) // page_size
        
        # 页码选择
        if total_pages > 1:
            page = st.number_input("页码", min_value=1, max_value=total_pages, value=1)
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
                st.write(player['full_name'])
            with col2:
                st.write(player['position'])
            with col3:
                st.write(player['team_name'])
            with col4:
                st.write(f"${player['salary']:,.0f}")
            with col5:
                if st.button("添加", key=f"add_{player['player_id']}"):
                    # 检查是否已经在阵容中
                    if not st.session_state.selected_players.empty:
                        if player['player_id'] in st.session_state.selected_players['player_id'].values:
                            continue
                    # 添加球员
                    new_player = filtered_df[filtered_df['player_id'] == player['player_id']]
                    st.session_state.selected_players = pd.concat([st.session_state.selected_players, new_player])
                    # 同时添加到替补阵容
                    st.session_state.bench = pd.concat([st.session_state.bench, new_player])
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
                        st.write(player['full_name'])
                    with col2:
                        st.write(player['position'])
                    with col3:
                        st.write(player['team_name'])
                    with col4:
                        st.write(f"${player['salary']:,.0f}")
                    with col5:
                        if st.button("→替补", key=f"to_bench_{player['player_id']}"):
                            # 从首发阵容移除
                            st.session_state.starters = st.session_state.starters[st.session_state.starters['player_id'] != player['player_id']]
                            st.session_state.starters = st.session_state.starters.reset_index(drop=True)
                            # 从selected_players中获取球员数据
                            player_data = st.session_state.selected_players[st.session_state.selected_players['player_id'] == player['player_id']]
                            # 添加到替补阵容
                            st.session_state.bench = pd.concat([st.session_state.bench, player_data])
                            st.session_state.bench = st.session_state.bench.reset_index(drop=True)
                            # 强制重新运行以更新界面
                            st.rerun()
            else:
                st.info("尚未选择首发球员")
        
        with lineup_col2:
            st.subheader("替补阵容")
            if not st.session_state.bench.empty:
                # 显示替补球员列表，带有管理按钮
                for i, player in st.session_state.bench.iterrows():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 2, 1, 1])
                    with col1:
                        st.write(player['full_name'])
                    with col2:
                        st.write(player['position'])
                    with col3:
                        st.write(player['team_name'])
                    with col4:
                        st.write(f"${player['salary']:,.0f}")
                    with col5:
                        if st.button("→首发", key=f"to_starter_{player['player_id']}"):
                            # 检查首发阵容是否已满
                            if len(st.session_state.starters) >= 5:
                                pass
                            else:
                                # 从替补阵容移除
                                st.session_state.bench = st.session_state.bench[st.session_state.bench['player_id'] != player['player_id']]
                                st.session_state.bench = st.session_state.bench.reset_index(drop=True)
                                # 从selected_players中获取球员数据
                                player_data = st.session_state.selected_players[st.session_state.selected_players['player_id'] == player['player_id']]
                                # 添加到首发阵容
                                st.session_state.starters = pd.concat([st.session_state.starters, player_data])
                                st.session_state.starters = st.session_state.starters.reset_index(drop=True)
                                # 强制重新运行以更新界面
                                st.rerun()
                    with col6:
                        if st.button("移除", key=f"remove_{player['player_id']}"):
                            # 从替补阵容移除
                            st.session_state.bench = st.session_state.bench[st.session_state.bench['player_id'] != player['player_id']]
                            # 从选中球员中移除
                            st.session_state.selected_players = st.session_state.selected_players[st.session_state.selected_players['player_id'] != player['player_id']]
                            # 如果在首发阵容中，也从首发阵容移除
                            if not st.session_state.starters.empty:
                                st.session_state.starters = st.session_state.starters[st.session_state.starters['player_id'] != player['player_id']]
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
            valid_lineup = starters_valid and bench_valid and positions_valid and salary_valid
            
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
                        min_value=datetime(2020, 1, 1)
                    )
                    
                    # 准备导出数据
                    export_data = {
                        '导出时间': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        '总薪资': total_salary,
                        '薪资上限': SALARY_LIMIT,
                        '已选择球员数': total_players,
                        '首发阵容': st.session_state.starters[["full_name", "position", "team_name", "salary"]].to_dict('records') if not st.session_state.starters.empty else [],
                        '替补阵容': st.session_state.bench[["full_name", "position", "team_name", "salary"]].to_dict('records') if not st.session_state.bench.empty else []
                    }
                    
                    # 转换为DataFrame格式以便导出
                    export_df = pd.DataFrame()
                    
                    # 添加首发
                    if not st.session_state.starters.empty:
                        starters_df = st.session_state.starters[['player_id', 'full_name', 'position', 'team_name', 'salary']].copy()
                        starters_df['角色'] = '首发'
                        export_df = pd.concat([export_df, starters_df])
                    
                    # 添加替补
                    if not st.session_state.bench.empty:
                        bench_df = st.session_state.bench[['player_id', 'full_name', 'position', 'team_name', 'salary']].copy()
                        bench_df['角色'] = '替补'
                        export_df = pd.concat([export_df, bench_df])
                    
                    # 导出为CSV
                    csv = export_df.to_csv(index=False, encoding='utf-8-sig')
                    
                    # 美化导出按钮
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📥 导出阵容为CSV文件",
                            data=csv,
                            file_name=f"scouts_lens_lineup_{export_date.strftime('%Y%m%d')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                else:
                    st.error("❌ 请满足以上限制条件问题后再尝试导出。")
                    st.info("💡 提示：点击上方的展开面板查看具体的限制条件详情")
        else:
            st.info("请先选择球员组成阵容")
    
    # 结果页面
    elif st.session_state.current_page == 'results':
        st.title("📊 查看结果")
        
        # 文件上传组件
        uploaded_file = st.file_uploader("上传阵容CSV文件", type="csv")
        
        if uploaded_file is not None:
            # 解析CSV文件
            try:
                lineup_df = pd.read_csv(uploaded_file)
                st.success("文件上传成功！")
                
                # 显示上传的阵容
                st.subheader("上传的阵容")
                st.dataframe(lineup_df)
                
                # 提取文件名中的日期
                file_name = uploaded_file.name
                import re
                date_match = re.search(r'\d{8}', file_name)
                
                if date_match:
                    file_date = date_match.group()
                    # 转换为日期对象
                    game_date = datetime.strptime(file_date, "%Y%m%d")
                    # 美国时间比文件名日期减一天
                    game_date = game_date - pd.Timedelta(days=1)
                    game_date_str = game_date.strftime("%Y-%m-%d")
                    
                    st.write(f"提取的比赛日期（美国时间）: {game_date_str}")
                    
                    # 开始查询比赛数据
                    st.info("正在查询比赛数据...")
                    
                    # 获取球队名称
                    if not lineup_df.empty:
                        team_name = lineup_df['team_name'].iloc[0]
                        st.write(f"球队: {team_name}")
                        
                        # 查询比赛数据
                        games = get_games_by_date(game_date_str)
                        
                        if not games.empty:
                            # 筛选出该球队的比赛
                            team_games = games[games['TEAM_NAME'].str.contains(team_name[:2])]
                            
                            if not team_games.empty:
                                # 获取比赛结果
                                game = team_games.iloc[0]
                                team_won = game['WL'] == 'W'
                                
                                st.write(f"比赛结果: {'获胜' if team_won else '落败'}")
                                st.write(f"对手: {game['MATCHUP'].split(' ')[2]}")
                                st.write(f"比分: {game['PTS']} - {game['PLUS_MINUS'] + game['PTS']}")
                                
                                # 计算每个球员的评分
                                st.subheader("球员评分")
                                
                                players_scores = []
                                results = []
                                
                                for _, player in lineup_df.iterrows():
                                    player_id = player['player_id']
                                    player_name = player['full_name']
                                    role = player['角色']
                                    
                                    # 查询球员比赛数据
                                    player_stats = get_player_game_stats(player_id, game_date_str)
                                    
                                    if not player_stats.empty:
                                        # 计算评分
                                        score = calculate_player_score(player_stats.to_dict('list'), team_won)
                                        
                                        # 获取比赛数据
                                        mp = player_stats['MIN'].iloc[0]
                                        fg3m = player_stats['FG3M'].iloc[0]
                                        fgm = player_stats['FGM'].iloc[0]
                                        fga = player_stats['FGA'].iloc[0]
                                        ftm = player_stats['FTM'].iloc[0]
                                        fta = player_stats['FTA'].iloc[0]
                                        reb = player_stats['REB'].iloc[0]
                                        ast = player_stats['AST'].iloc[0]
                                        stl = player_stats['STL'].iloc[0]
                                        blk = player_stats['BLK'].iloc[0]
                                        tov = player_stats['TOV'].iloc[0]
                                        pf = player_stats['PF'].iloc[0]
                                        pts = player_stats['PTS'].iloc[0]
                                        
                                        results.append({
                                            '球员': player_name,
                                            '角色': role,
                                            '上场时间': mp,
                                            '三分命中': fg3m,
                                            '投篮命中': fgm,
                                            '投篮出手': fga,
                                            '罚球命中': ftm,
                                            '罚球出手': fta,
                                            '篮板': reb,
                                            '助攻': ast,
                                            '抢断': stl,
                                            '盖帽': blk,
                                            '失误': tov,
                                            '犯规': pf,
                                            '得分': pts,
                                            '评分': score
                                        })
                                        
                                        players_scores.append({
                                            'name': player_name,
                                            'role': role,
                                            'score': score
                                        })
                                    else:
                                        # 球员未上场
                                        score = 0
                                        results.append({
                                            '球员': player_name,
                                            '角色': role,
                                            '上场时间': 0,
                                            '三分命中': 0,
                                            '投篮命中': 0,
                                            '投篮出手': 0,
                                            '罚球命中': 0,
                                            '罚球出手': 0,
                                            '篮板': 0,
                                            '助攻': 0,
                                            '抢断': 0,
                                            '盖帽': 0,
                                            '失误': 0,
                                            '犯规': 0,
                                            '得分': 0,
                                            '评分': score
                                        })
                                        
                                        players_scores.append({
                                            'name': player_name,
                                            'role': role,
                                            'score': score
                                        })
                                
                                # 显示球员数据和评分
                                results_df = pd.DataFrame(results)
                                st.dataframe(results_df)
                                
                                # 计算加权总分
                                weighted_score = calculate_weighted_score(players_scores)
                                
                                st.subheader("阵容评分")
                                st.metric("加权总分", weighted_score)
                                
                                # 显示评分详情
                                st.subheader("评分详情")
                                for player in players_scores:
                                    weight = 2 if player['role'] == '首发' else 1
                                    st.write(f"{player['name']} ({player['role']}): {player['score']} × {weight} = {player['score'] * weight}")
                            else:
                                st.error(f"未找到 {team_name} 在 {game_date_str} 的比赛数据")
                        else:
                            st.error(f"未找到 {game_date_str} 的比赛数据")
                    else:
                        st.error("阵容文件为空")
                else:
                    st.error("无法从文件名中提取日期，请确保文件名包含8位数字的日期格式（如20260116）")
                    
            except Exception as e:
                st.error(f"文件解析失败: {e}")
        else:
            st.info("请上传阵容CSV文件以查看结果")


if __name__ == "__main__":
    main()
