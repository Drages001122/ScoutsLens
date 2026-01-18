import pandas as pd
from datetime import datetime
from utils.constants import SALARY_LIMIT
from utils.lineup_utils import check_lineup_requirements


def add_player_to_lineup(selected_players, bench, player_data):
    """添加球员到阵容"""
    # 检查球员是否已在阵容中
    if not selected_players.empty:
        if player_data["player_id"].values[0] in selected_players["player_id"].values:
            return selected_players, bench
    
    # 添加到选中球员列表
    new_selected_players = pd.concat([selected_players, player_data])
    # 添加到替补阵容
    new_bench = pd.concat([bench, player_data])
    
    return new_selected_players, new_bench


def move_player_to_starters(starters, bench, selected_players, player_id):
    """将球员从替补移到首发"""
    if len(starters) >= 5:
        return starters, bench
    
    # 从替补移除
    new_bench = bench[bench["player_id"] != player_id]
    new_bench = new_bench.reset_index(drop=True)
    
    # 获取球员数据
    player_data = selected_players[selected_players["player_id"] == player_id]
    
    # 添加到首发
    new_starters = pd.concat([starters, player_data])
    new_starters = new_starters.reset_index(drop=True)
    
    return new_starters, new_bench


def move_player_to_bench(starters, bench, selected_players, player_id):
    """将球员从首发移到替补"""
    # 从首发移除
    new_starters = starters[starters["player_id"] != player_id]
    new_starters = new_starters.reset_index(drop=True)
    
    # 获取球员数据
    player_data = selected_players[selected_players["player_id"] == player_id]
    
    # 添加到替补
    new_bench = pd.concat([bench, player_data])
    new_bench = new_bench.reset_index(drop=True)
    
    return new_starters, new_bench


def remove_player_from_lineup(selected_players, starters, bench, player_id):
    """从阵容中移除球员"""
    # 从替补移除
    new_bench = bench[bench["player_id"] != player_id]
    
    # 从选中球员中移除
    new_selected_players = selected_players[selected_players["player_id"] != player_id]
    
    # 从首发移除
    new_starters = starters[starters["player_id"] != player_id]
    
    return new_selected_players, new_starters, new_bench


def validate_lineup(starters, bench, total_salary):
    """验证阵容是否符合要求"""
    starters_count = len(starters)
    bench_count = len(bench)
    
    # 检查首发人数
    starters_valid = starters_count == 5
    # 检查替补人数
    bench_valid = bench_count == 7
    # 检查首发位置要求
    positions_valid = check_lineup_requirements(starters)
    # 检查薪资要求
    salary_valid = total_salary <= SALARY_LIMIT
    
    return {
        "starters_valid": starters_valid,
        "bench_valid": bench_valid,
        "positions_valid": positions_valid,
        "salary_valid": salary_valid,
        "valid_lineup": starters_valid and bench_valid and positions_valid and salary_valid
    }


def prepare_export_data(starters, bench, total_salary):
    """准备导出数据"""
    export_data = {
        "导出时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "总薪资": total_salary,
        "薪资上限": SALARY_LIMIT,
        "已选择球员数": len(starters) + len(bench),
        "首发阵容": (
            starters[
                ["full_name", "position", "team_name", "salary"]
            ].to_dict("records")
            if not starters.empty
            else []
        ),
        "替补阵容": (
            bench[
                ["full_name", "position", "team_name", "salary"]
            ].to_dict("records")
            if not bench.empty
            else []
        ),
    }
    
    # 转换为DataFrame格式
    export_df = pd.DataFrame()
    
    # 添加首发
    if not starters.empty:
        starters_df = starters[
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
    if not bench.empty:
        bench_df = bench[
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
    
    return export_df


def reset_lineup():
    """重置阵容"""
    return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()