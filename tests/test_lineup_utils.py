import pandas as pd
import pytest
from utils.lineup_utils import check_lineup_requirements


@pytest.fixture
def sample_starters_valid():
    """创建测试用的有效的首发阵容数据"""
    data = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫", "前锋", "前锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


@pytest.fixture
def sample_starters_invalid():
    """创建测试用的无效的首发阵容数据"""
    data = {
        "player_id": [1, 2, 3, 4],
        "full_name": ["Player1", "Player2", "Player3", "Player4"],
        "position": ["后卫", "后卫", "前锋", "前锋"],
        "team_name": ["湖人" for _ in range(4)],
        "salary": [10000000 for _ in range(4)],
        "team_abbr": ["LAL" for _ in range(4)]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


@pytest.fixture
def sample_starters_multi_position():
    """创建测试用的多位置首发阵容数据"""
    data = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫-前锋", "前锋", "前锋-中锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


@pytest.fixture
def sample_starters_no_positions():
    """创建测试用的无位置信息的首发阵容数据"""
    data = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫", "前锋", "前锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df = pd.DataFrame(data)
    # 不添加all_positions列
    return df


def test_check_lineup_requirements_valid(sample_starters_valid):
    """测试检查有效的首发阵容要求"""
    # 测试有效的首发阵容
    result = check_lineup_requirements(sample_starters_valid)
    assert result is True


def test_check_lineup_requirements_invalid(sample_starters_invalid):
    """测试检查无效的首发阵容要求"""
    # 测试人数不足的首发阵容
    result = check_lineup_requirements(sample_starters_invalid)
    assert result is False


def test_check_lineup_requirements_multi_position(sample_starters_multi_position):
    """测试检查多位置的首发阵容要求"""
    # 测试多位置的首发阵容
    result = check_lineup_requirements(sample_starters_multi_position)
    assert result is True


def test_check_lineup_requirements_no_positions(sample_starters_no_positions):
    """测试检查无位置信息的首发阵容要求"""
    # 测试无位置信息的首发阵容
    result = check_lineup_requirements(sample_starters_no_positions)
    assert result is False


def test_check_lineup_requirements_empty():
    """测试检查空的首发阵容要求"""
    # 测试空的首发阵容
    empty_df = pd.DataFrame()
    result = check_lineup_requirements(empty_df)
    assert result is False


def test_check_lineup_requirements_position_combinations():
    """测试检查不同位置组合的首发阵容要求"""
    # 测试多种位置组合的情况
    # 情况1：2后卫，2前锋，1中锋（标准组合）
    data1 = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫", "前锋", "前锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df1 = pd.DataFrame(data1)
    df1["positions"] = df1["position"].str.split("-")
    df1["all_positions"] = df1["position"].apply(lambda x: x.split("-"))
    result1 = check_lineup_requirements(df1)
    assert result1 is True
    
    # 情况2：使用后卫-前锋和前锋-中锋的组合
    data2 = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫-前锋", "前锋", "前锋-中锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df2 = pd.DataFrame(data2)
    df2["positions"] = df2["position"].str.split("-")
    df2["all_positions"] = df2["position"].apply(lambda x: x.split("-"))
    result2 = check_lineup_requirements(df2)
    assert result2 is True
    
    # 情况3：位置组合不符合要求（3后卫，1前锋，1中锋）
    data3 = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "后卫", "后卫", "前锋", "中锋"],
        "team_name": ["湖人" for _ in range(5)],
        "salary": [10000000 for _ in range(5)],
        "team_abbr": ["LAL" for _ in range(5)]
    }
    df3 = pd.DataFrame(data3)
    df3["positions"] = df3["position"].str.split("-")
    df3["all_positions"] = df3["position"].apply(lambda x: x.split("-"))
    result3 = check_lineup_requirements(df3)
    assert result3 is False
