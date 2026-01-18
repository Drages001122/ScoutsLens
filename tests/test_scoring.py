import pandas as pd
import pytest
from utils.scoring import (
    to_numeric, calculate_per, calculate_score, 
    calculate_rebounds, calculate_weighted_score
)


@pytest.fixture
def sample_player_stats():
    """创建测试用的球员统计数据"""
    data = {
        "三分命中数": [2, 1, 0, 3, 1],
        "两分命中数": [5, 3, 8, 2, 4],
        "罚球命中数": [4, 2, 6, 1, 3],
        "进攻篮板": [1, 0, 3, 0, 2],
        "防守篮板": [4, 3, 5, 2, 3],
        "助攻": [3, 2, 1, 5, 2],
        "抢断": [1, 2, 0, 1, 1],
        "盖帽": [0, 1, 2, 0, 1],
        "两分出手数": [10, 6, 12, 4, 8],
        "三分出手数": [5, 3, 2, 6, 4],
        "罚球出手数": [5, 3, 8, 2, 4],
        "失误": [2, 1, 3, 1, 2],
        "犯规": [1, 2, 1, 2, 1],
        "上场时间": [30, 25, 35, 20, 28],
        "本场比赛是否获胜": [True, False, True, False, True]
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_players_with_role():
    """创建测试用的带角色的球员数据"""
    data = {
        "评分": [15.5, 12.3, 18.7, 10.1, 14.2, 9.8, 11.5],
        "角色": ["首发", "首发", "首发", "首发", "首发", "替补", "替补"]
    }
    return pd.DataFrame(data)


def test_to_numeric():
    """测试数值转换功能"""
    # 测试正常数值
    assert to_numeric(10) == 10
    assert to_numeric(10.5) == 10.5
    
    # 测试字符串数值
    assert to_numeric("10") == 10
    assert to_numeric("10.5") == 10.5
    
    # 测试"none"字符串
    assert to_numeric("none") == 0
    assert to_numeric("None") == 0
    assert to_numeric("NONE") == 0
    
    # 测试空值
    assert to_numeric(None) == 0
    assert to_numeric(pd.NA) == 0
    
    # 测试其他类型
    assert to_numeric([]) == 0
    assert to_numeric({}) == 0


def test_calculate_score(sample_player_stats):
    """测试得分计算功能"""
    # 测试得分计算
    for i, row in sample_player_stats.iterrows():
        calculated_score = calculate_score(row)
        expected_score = (
            3 * row["三分命中数"] +
            2 * row["两分命中数"] +
            1 * row["罚球命中数"]
        )
        assert calculated_score == expected_score


def test_calculate_rebounds(sample_player_stats):
    """测试篮板计算功能"""
    # 测试篮板计算
    for i, row in sample_player_stats.iterrows():
        calculated_rebounds = calculate_rebounds(row)
        expected_rebounds = row["进攻篮板"] + row["防守篮板"]
        assert calculated_rebounds == expected_rebounds


def test_calculate_per(sample_player_stats):
    """测试球员效率评分(PER)计算功能"""
    # 测试PER计算
    for i, row in sample_player_stats.iterrows():
        calculated_per = calculate_per(row)
        # 检查返回值是否为数字
        assert isinstance(calculated_per, (int, float))
        # 检查返回值是否合理
        assert calculated_per >= -20  # 最低可能值
        assert calculated_per <= 50  # 最高可能值


def test_calculate_weighted_score(sample_players_with_role):
    """测试加权得分计算功能"""
    # 测试加权得分计算
    calculated_score = calculate_weighted_score(sample_players_with_role)
    expected_score = (
        15.5 * 2 + 12.3 * 2 + 18.7 * 2 + 10.1 * 2 + 14.2 * 2 +
        9.8 * 1 + 11.5 * 1
    )
    assert abs(calculated_score - expected_score) < 0.01


def test_calculate_per_with_different_win_values():
    """测试不同获胜值的PER计算"""
    # 测试获胜和失败的情况
    # 创建获胜测试数据
    win_data = {
        "三分命中数": [1],
        "两分命中数": [3],
        "罚球命中数": [2],
        "进攻篮板": [1],
        "防守篮板": [3],
        "助攻": [2],
        "抢断": [1],
        "盖帽": [0],
        "两分出手数": [6],
        "三分出手数": [3],
        "罚球出手数": [3],
        "失误": [1],
        "犯规": [1],
        "上场时间": [25],
        "获胜": [True]
    }
    win_df = pd.DataFrame(win_data)
    
    # 创建失败测试数据
    lose_data = win_data.copy()
    lose_data["获胜"] = [False]
    lose_df = pd.DataFrame(lose_data)
    
    # 计算获胜和失败的PER
    win_per = calculate_per(win_df.iloc[0])
    lose_per = calculate_per(lose_df.iloc[0])
    
    # 检查获胜和失败的PER差异是否约为4（2 - (-2)）
    assert abs(win_per - lose_per - 4) < 0.1


def test_calculate_per_with_no_playing_time():
    """测试无上场时间的PER计算"""
    # 创建测试数据（无上场时间）
    test_data = {
        "三分命中数": [1],
        "两分命中数": [3],
        "罚球命中数": [2],
        "进攻篮板": [1],
        "防守篮板": [3],
        "助攻": [2],
        "抢断": [1],
        "盖帽": [0],
        "两分出手数": [6],
        "三分出手数": [3],
        "罚球出手数": [3],
        "失误": [1],
        "犯规": [1],
        "上场时间": [0],  # 无上场时间
        "本场比赛是否获胜": [True]
    }
    test_df = pd.DataFrame(test_data)
    
    # 计算PER
    per = calculate_per(test_df.iloc[0])
    # 检查返回值是否为数字
    assert isinstance(per, (int, float))
