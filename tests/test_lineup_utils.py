import pandas as pd
import pytest
from utils.lineup_utils import check_lineup_requirements, determine_position_type, can_play_position, validate_position_assignment


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
    
    # 情况3：3后卫，1前锋，1中锋 - 现在只要有5人就返回True，具体位置分配验证在其他地方进行
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
    assert result3 is True  # 现在只要有5人就返回True


def test_determine_position_type():
    """测试确定球员位置类型的函数"""
    # 测试仅含后卫
    assert determine_position_type(["后卫"]) == "仅含后卫"
    # 测试后卫+前锋
    assert determine_position_type(["后卫", "前锋"]) == "后卫+前锋"
    # 测试仅含前锋
    assert determine_position_type(["前锋"]) == "仅含前锋"
    # 测试前锋+中锋
    assert determine_position_type(["前锋", "中锋"]) == "前锋+中锋"
    # 测试仅含中锋
    assert determine_position_type(["中锋"]) == "仅含中锋"
    # 测试未知类型
    assert determine_position_type([]) == "未知"
    assert determine_position_type(["后卫", "前锋", "中锋"]) == "未知"


def test_can_play_position():
    """测试检查球员是否可以担任指定位置的函数"""
    # 测试仅含后卫的球员
    assert can_play_position(["后卫"], "PG") is True
    assert can_play_position(["后卫"], "SG") is True
    assert can_play_position(["后卫"], "SF") is False
    assert can_play_position(["后卫"], "PF") is False
    assert can_play_position(["后卫"], "C") is False
    
    # 测试后卫+前锋的球员
    assert can_play_position(["后卫", "前锋"], "PG") is False
    assert can_play_position(["后卫", "前锋"], "SG") is True
    assert can_play_position(["后卫", "前锋"], "SF") is True
    assert can_play_position(["后卫", "前锋"], "PF") is False
    assert can_play_position(["后卫", "前锋"], "C") is False
    
    # 测试仅含前锋的球员
    assert can_play_position(["前锋"], "PG") is False
    assert can_play_position(["前锋"], "SG") is False
    assert can_play_position(["前锋"], "SF") is True
    assert can_play_position(["前锋"], "PF") is True
    assert can_play_position(["前锋"], "C") is False
    
    # 测试前锋+中锋的球员
    assert can_play_position(["前锋", "中锋"], "PG") is False
    assert can_play_position(["前锋", "中锋"], "SG") is False
    assert can_play_position(["前锋", "中锋"], "SF") is False
    assert can_play_position(["前锋", "中锋"], "PF") is True
    assert can_play_position(["前锋", "中锋"], "C") is True
    
    # 测试仅含中锋的球员
    assert can_play_position(["中锋"], "PG") is False
    assert can_play_position(["中锋"], "SG") is False
    assert can_play_position(["中锋"], "SF") is False
    assert can_play_position(["中锋"], "PF") is False
    assert can_play_position(["中锋"], "C") is True


def test_validate_position_assignment():
    """测试验证位置分配的函数"""
    # 创建测试用的球员数据
    player1 = {
        "player_id": 1,
        "full_name": "Player1",
        "all_positions": ["后卫"]
    }
    
    player2 = {
        "player_id": 2,
        "full_name": "Player2",
        "all_positions": ["后卫", "前锋"]
    }
    
    player3 = {
        "player_id": 3,
        "full_name": "Player3",
        "all_positions": ["前锋"]
    }
    
    player4 = {
        "player_id": 4,
        "full_name": "Player4",
        "all_positions": ["前锋", "中锋"]
    }
    
    player5 = {
        "player_id": 5,
        "full_name": "Player5",
        "all_positions": ["中锋"]
    }
    
    # 测试有效的位置分配
    valid_assignment = [
        {"player": player1, "position": "PG"},
        {"player": player2, "position": "SG"},
        {"player": player3, "position": "SF"},
        {"player": player4, "position": "PF"},
        {"player": player5, "position": "C"}
    ]
    assert validate_position_assignment(valid_assignment) is True
    
    # 测试无效的位置分配（球员分配到不可担任的位置）
    invalid_assignment = [
        {"player": player1, "position": "SF"},  # 后卫不能打小前锋
        {"player": player2, "position": "PG"},  # 后卫+前锋不能打控球后卫
        {"player": player3, "position": "C"},  # 前锋不能打中锋
        {"player": player4, "position": "SG"},  # 前锋+中锋不能打得分后卫
        {"player": player5, "position": "PF"}   # 中锋不能打大前锋
    ]
    assert validate_position_assignment(invalid_assignment) is False
    
    # 测试人数不足的情况
    insufficient_assignment = [
        {"player": player1, "position": "PG"},
        {"player": player2, "position": "SG"},
        {"player": player3, "position": "SF"},
        {"player": player4, "position": "PF"}
    ]
    assert validate_position_assignment(insufficient_assignment) is False


def test_all_position_combinations():
    """测试所有位置组合场景"""
    # 测试所有位置类型的组合
    position_types = [
        (["后卫"], ["PG", "SG"]),          # 仅含后卫
        (["后卫", "前锋"], ["SG", "SF"]),  # 后卫+前锋
        (["前锋"], ["SF", "PF"]),          # 仅含前锋
        (["前锋", "中锋"], ["PF", "C"]),   # 前锋+中锋
        (["中锋"], ["C"])                  # 仅含中锋
    ]
    
    for player_positions, allowed_positions in position_types:
        # 测试允许的位置
        for pos in allowed_positions:
            assert can_play_position(player_positions, pos) is True
        # 测试不允许的位置
        for pos in ["PG", "SG", "SF", "PF", "C"]:
            if pos not in allowed_positions:
                assert can_play_position(player_positions, pos) is False
