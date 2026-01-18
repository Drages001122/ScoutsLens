import pandas as pd
import pytest
from utils.data_processor import (
    load_players_data, filter_players, sort_players, 
    get_paged_players, calculate_total_salary, format_salary
)


@pytest.fixture
def sample_players_data():
    """创建测试用的球员数据"""
    data = {
        "player_id": [1, 2, 3, 4, 5],
        "full_name": ["Player1", "Player2", "Player3", "Player4", "Player5"],
        "position": ["后卫", "前锋", "中锋", "后卫-前锋", "前锋-中锋"],
        "team_name": ["湖人", "勇士", "篮网", "凯尔特人", "雄鹿"],
        "salary": [20000000, 25000000, 30000000, 15000000, 18000000],
        "team_abbr": ["LAL", "GSW", "BKN", "BOS", "MIL"]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


def test_filter_players(sample_players_data):
    """测试球员过滤功能"""
    # 测试位置过滤
    filtered_df = filter_players(
        sample_players_data, 
        selected_positions=["后卫"], 
        selected_teams=[], 
        salary_range=(0, 100000000), 
        selected_player_ids=[]
    )
    assert len(filtered_df) == 2  # 后卫和后卫-前锋
    
    # 测试球队过滤
    filtered_df = filter_players(
        sample_players_data, 
        selected_positions=[], 
        selected_teams=["湖人"], 
        salary_range=(0, 100000000), 
        selected_player_ids=[]
    )
    assert len(filtered_df) == 1
    assert filtered_df.iloc[0]["team_name"] == "湖人"
    
    # 测试薪资范围过滤
    filtered_df = filter_players(
        sample_players_data, 
        selected_positions=[], 
        selected_teams=[], 
        salary_range=(15000000, 25000000), 
        selected_player_ids=[]
    )
    assert len(filtered_df) == 4  # 1500万、1800万、2000万、2500万中的符合条件者
    
    # 测试排除已选球员
    filtered_df = filter_players(
        sample_players_data, 
        selected_positions=[], 
        selected_teams=[], 
        salary_range=(0, 100000000), 
        selected_player_ids=[1, 2]
    )
    assert len(filtered_df) == 3  # 排除ID为1和2的球员


def test_sort_players(sample_players_data):
    """测试球员排序功能"""
    # 测试按薪资降序排序
    sorted_df = sort_players(sample_players_data, "salary", "降序")
    assert sorted_df.iloc[0]["salary"] == 30000000  # 最高薪资
    assert sorted_df.iloc[-1]["salary"] == 15000000  # 最低薪资
    
    # 测试按薪资升序排序
    sorted_df = sort_players(sample_players_data, "salary", "升序")
    assert sorted_df.iloc[0]["salary"] == 15000000  # 最低薪资
    assert sorted_df.iloc[-1]["salary"] == 30000000  # 最高薪资


def test_get_paged_players(sample_players_data):
    """测试分页功能"""
    # 测试第一页，每页2条数据
    paged_df = get_paged_players(sample_players_data, 1, 2)
    assert len(paged_df) == 2
    assert paged_df.iloc[0]["player_id"] == 1
    assert paged_df.iloc[1]["player_id"] == 2
    
    # 测试第二页，每页2条数据
    paged_df = get_paged_players(sample_players_data, 2, 2)
    assert len(paged_df) == 2
    assert paged_df.iloc[0]["player_id"] == 3
    assert paged_df.iloc[1]["player_id"] == 4
    
    # 测试超出范围的页码
    paged_df = get_paged_players(sample_players_data, 10, 2)
    assert len(paged_df) == 0


def test_calculate_total_salary(sample_players_data):
    """测试总薪资计算功能"""
    # 测试正常情况
    total_salary = calculate_total_salary(sample_players_data)
    expected_total = 20000000 + 25000000 + 30000000 + 15000000 + 18000000
    assert total_salary == expected_total
    
    # 测试空数据框
    empty_df = pd.DataFrame()
    total_salary = calculate_total_salary(empty_df)
    assert total_salary == 0


def test_format_salary():
    """测试薪资格式化功能"""
    # 测试正常情况
    formatted = format_salary(15000000)
    assert formatted == "$15,000,000"
    
    # 测试空值情况
    formatted = format_salary(pd.NA)
    assert formatted == "$0"
    
    # 测试非数字情况
    formatted = format_salary("invalid")
    assert formatted == "$0"


def test_load_players_data():
    """测试加载球员数据功能"""
    # 测试加载数据
    df = load_players_data()
    # 检查是否返回DataFrame
    assert isinstance(df, pd.DataFrame)
    # 检查是否包含必要的列
    expected_columns = ["player_id", "full_name", "position", "team_name", "salary"]
    for col in expected_columns:
        assert col in df.columns
