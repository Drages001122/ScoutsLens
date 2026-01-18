import pandas as pd
import pytest
from utils.lineup_manager import (
    add_player_to_lineup, move_player_to_starters, move_player_to_bench, 
    remove_player_from_lineup, validate_lineup, prepare_export_data, reset_lineup
)
from utils.constants import SALARY_LIMIT


@pytest.fixture
def sample_player_data():
    """创建测试用的球员数据"""
    data = {
        "player_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        "full_name": [f"Player{i}" for i in range(1, 13)],
        "position": ["后卫", "后卫", "前锋", "前锋", "中锋", "后卫", "前锋", "中锋", "后卫", "前锋", "中锋", "后卫"],
        "team_name": ["湖人" for _ in range(12)],
        "salary": [10000000 for _ in range(12)],
        "team_abbr": ["LAL" for _ in range(12)]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


@pytest.fixture
def sample_selected_players(sample_player_data):
    """创建测试用的已选球员数据"""
    return sample_player_data.copy()


@pytest.fixture
def sample_starters(sample_player_data):
    """创建测试用的首发阵容数据"""
    return sample_player_data.iloc[:5].copy()


@pytest.fixture
def sample_bench(sample_player_data):
    """创建测试用的替补阵容数据"""
    return sample_player_data.iloc[5:12].copy()


def test_add_player_to_lineup():
    """测试添加球员到阵容功能"""
    # 创建空的阵容
    selected_players = pd.DataFrame()
    bench = pd.DataFrame()
    
    # 创建新球员数据
    new_player_data = {
        "player_id": [1],
        "full_name": ["NewPlayer"],
        "position": ["后卫"],
        "team_name": ["湖人"],
        "salary": [10000000],
        "team_abbr": ["LAL"]
    }
    new_player_df = pd.DataFrame(new_player_data)
    new_player_df["positions"] = new_player_df["position"].str.split("-")
    new_player_df["all_positions"] = new_player_df["position"].apply(lambda x: x.split("-"))
    
    # 测试添加新球员
    new_selected, new_bench = add_player_to_lineup(selected_players, bench, new_player_df)
    assert len(new_selected) == 1
    assert len(new_bench) == 1
    assert new_selected.iloc[0]["player_id"] == 1
    
    # 测试添加已存在的球员
    new_selected_2, new_bench_2 = add_player_to_lineup(new_selected, new_bench, new_player_df)
    assert len(new_selected_2) == 1  # 数量不变
    assert len(new_bench_2) == 1  # 数量不变


def test_move_player_to_starters(sample_selected_players, sample_bench):
    """测试将球员从替补移到首发功能"""
    # 创建空的首发阵容
    starters = pd.DataFrame()
    
    # 测试移动球员到首发（使用替补阵容中的第一个球员ID）
    player_id = sample_bench.iloc[0]["player_id"]
    new_starters, new_bench = move_player_to_starters(
        starters, sample_bench, sample_selected_players, player_id
    )
    assert len(new_starters) == 1
    assert len(new_bench) == len(sample_bench) - 1
    assert new_starters.iloc[0]["player_id"] == player_id
    
    # 测试首发已满的情况
    for i in range(2, 6):
        new_starters, new_bench = move_player_to_starters(
            new_starters, new_bench, sample_selected_players, i
        )
    assert len(new_starters) == 5  # 首发已满
    
    # 尝试再添加一个球员，应该失败
    new_starters_2, new_bench_2 = move_player_to_starters(
        new_starters, new_bench, sample_selected_players, 6
    )
    assert len(new_starters_2) == 5  # 数量不变


def test_move_player_to_bench(sample_selected_players, sample_starters):
    """测试将球员从首发移到替补功能"""
    # 创建空的替补阵容
    bench = pd.DataFrame()
    
    # 测试移动球员到替补
    new_starters, new_bench = move_player_to_bench(
        sample_starters, bench, sample_selected_players, 1
    )
    assert len(new_starters) == len(sample_starters) - 1
    assert len(new_bench) == 1
    assert new_bench.iloc[0]["player_id"] == 1


def test_remove_player_from_lineup(sample_selected_players, sample_starters, sample_bench):
    """测试从阵容中移除球员功能"""
    # 测试从首发和已选球员中移除球员
    player_id = sample_starters.iloc[0]["player_id"]
    new_selected, new_starters, new_bench = remove_player_from_lineup(
        sample_selected_players, sample_starters, sample_bench, player_id
    )
    assert len(new_selected) == len(sample_selected_players) - 1
    assert len(new_starters) == len(sample_starters) - 1
    assert len(new_bench) == len(sample_bench)


def test_validate_lineup():
    """测试阵容验证功能"""
    # 创建符合要求的阵容
    starters_data = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": [f"Player{i}" for i in range(1, 6)],
        "position": ["后卫", "后卫", "前锋", "前锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    starters = pd.DataFrame(starters_data)
    starters["positions"] = starters["position"].str.split("-")
    starters["all_positions"] = starters["position"].apply(lambda x: x.split("-"))
    
    bench_data = {
        "player_id": [6, 7, 8, 9, 10, 11, 12],
        "full_name": [f"Player{i}" for i in range(6, 13)],
        "position": ["后卫", "前锋", "中锋", "后卫", "前锋", "中锋", "后卫"],
        "team_name": ["湖人" for _ in range(7)],
        "salary": [10000000 for _ in range(7)],
        "team_abbr": ["LAL" for _ in range(7)]
    }
    bench = pd.DataFrame(bench_data)
    bench["positions"] = bench["position"].str.split("-")
    bench["all_positions"] = bench["position"].apply(lambda x: x.split("-"))
    
    total_salary = 120000000  # 12 * 1000万 = 1.2亿，低于薪资上限
    
    # 测试验证符合要求的阵容
    validation_result = validate_lineup(starters, bench, total_salary)
    assert validation_result["starters_valid"] is True
    assert validation_result["bench_valid"] is True
    assert validation_result["positions_valid"] is True
    assert validation_result["salary_valid"] is True
    assert validation_result["valid_lineup"] is True
    
    # 测试验证不符合要求的阵容（首发人数不足）
    short_starters = starters.iloc[:4].copy()
    validation_result = validate_lineup(short_starters, bench, total_salary)
    assert validation_result["starters_valid"] is False
    assert validation_result["valid_lineup"] is False
    
    # 测试验证不符合要求的阵容（薪资超过上限）
    validation_result = validate_lineup(starters, bench, SALARY_LIMIT + 1)
    assert validation_result["salary_valid"] is False
    assert validation_result["valid_lineup"] is False


def test_prepare_export_data(sample_starters, sample_bench):
    """测试准备导出数据功能"""
    total_salary = 120000000
    
    # 测试准备导出数据
    export_df = prepare_export_data(sample_starters, sample_bench, total_salary)
    assert isinstance(export_df, pd.DataFrame)
    assert len(export_df) == len(sample_starters) + len(sample_bench)
    assert "角色" in export_df.columns
    assert len(export_df[export_df["角色"] == "首发"]) == len(sample_starters)
    assert len(export_df[export_df["角色"] == "替补"]) == len(sample_bench)


def test_reset_lineup():
    """测试重置阵容功能"""
    # 测试重置阵容
    selected_players, starters, bench = reset_lineup()
    assert selected_players.empty
    assert starters.empty
    assert bench.empty
