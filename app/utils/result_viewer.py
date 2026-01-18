import os
import pandas as pd
import streamlit as st
from app.utils.scoring import calculate_per, calculate_score, calculate_rebounds, calculate_weighted_score
from app.utils.data_processor import format_salary


def load_lineup_data(uploaded_file):
    """加载上传的阵容数据"""
    try:
        lineup_df = pd.read_csv(uploaded_file, encoding="utf-8-sig")
        return lineup_df
    except Exception as e:
        st.error(f"加载阵容数据失败: {e}")
        return pd.DataFrame()


def get_latest_stats_file():
    """获取最新的统计数据文件"""
    try:
        stats_files = [f for f in os.listdir('player_stats_data') if f.startswith('nba_player_stats_') and f.endswith('.csv')]
        if stats_files:
            # 按文件名排序，获取最新的文件
            stats_files.sort(reverse=True)
            return stats_files[0]
        return None
    except Exception as e:
        st.warning(f"查找统计数据文件失败: {e}")
        return None


def merge_lineup_with_stats(lineup_df, stats_file):
    """将阵容数据与统计数据合并"""
    try:
        # 读取比赛统计数据
        stats_df = pd.read_csv(os.path.join('player_stats_data', stats_file), encoding="utf-8-sig")
        
        # 合并阵容数据和统计数据
        merged_df = pd.merge(
            lineup_df,
            stats_df,
            left_on="player_id",
            right_on="球员id",
            how="left"
        )
        
        return merged_df
    except Exception as e:
        st.error(f"合并数据失败: {e}")
        return pd.DataFrame()


def process_lineup_data(lineup_df):
    """处理阵容数据，计算相关统计信息"""
    # 计算总薪资
    total_salary = lineup_df["salary"].sum()
    
    # 计算球员数量
    total_players = len(lineup_df)
    
    # 计算首发和替补数量
    starters_count = len(lineup_df[lineup_df["角色"] == "首发"])
    bench_count = len(lineup_df[lineup_df["角色"] == "替补"])
    
    return {
        "total_salary": total_salary,
        "total_players": total_players,
        "starters_count": starters_count,
        "bench_count": bench_count
    }


def display_lineup_results(lineup_df):
    """显示阵容结果"""
    # 计算相关统计信息
    stats = process_lineup_data(lineup_df)
    
    # 显示基本信息
    st.write(f"总薪资: ${stats['total_salary']:,.0f}")
    st.write(f"球员数量: {stats['total_players']}")
    st.write(f"首发数量: {stats['starters_count']}")
    st.write(f"替补数量: {stats['bench_count']}")
    
    # 尝试读取最新的比赛统计数据
    st.subheader("📈 球员详细数据")
    
    # 查找最新的比赛统计CSV文件
    latest_stats_file = get_latest_stats_file()
    
    if latest_stats_file:
        # 合并阵容数据和统计数据
        merged_df = merge_lineup_with_stats(lineup_df, latest_stats_file)
        
        if not merged_df.empty:
            # 添加评分列
            merged_df["评分"] = merged_df.apply(calculate_per, axis=1)
            
            # 计算得分
            merged_df["得分"] = merged_df.apply(calculate_score, axis=1)
            
            # 计算篮板
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
            total_rating = calculate_weighted_score(display_df)
            st.write(f"总评分: {total_rating:.2f}")
            
            # 显示详细的得分计算
            st.subheader("📈 球员详细数据")
            
            # 格式化薪资
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
            st.warning("无法合并数据，请检查数据格式")
    else:
        st.warning("未找到比赛统计数据，请先在排行榜中获取数据")
        
        # 如果没有统计数据，使用薪资计算预估得分
        # 计算总得分（区分首发和替补）
        total_score = 0
        for _, row in lineup_df.iterrows():
            salary = row.get("salary", 0)
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