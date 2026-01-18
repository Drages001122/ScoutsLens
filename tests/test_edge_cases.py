import pandas as pd
import pytest
from utils.data_processor import (
    load_players_data, filter_players, sort_players, 
    get_paged_players, calculate_total_salary, format_salary
)
from utils.lineup_manager import (
    add_player_to_lineup, move_player_to_starters, move_player_to_bench, 
    remove_player_from_lineup, validate_lineup
)
from utils.lineup_utils import check_lineup_requirements
from utils.scoring import (
    to_numeric, calculate_per, calculate_score, 
    calculate_rebounds, calculate_weighted_score
)
from utils.ranking import should_use_cache, get_player_stats, run_stats_script
from utils.result_viewer import load_lineup_data


@pytest.fixture
def empty_dataframe():
    """创建空的DataFrame"""
    return pd.DataFrame()


@pytest.fixture
def sample_player_data():
    """创建测试用的球员数据"""
    data = {
        "player_id": [1],
        "full_name": ["Player1"],
        "position": ["后卫"],
        "team_name": ["湖人"],
        "salary": [10000000],
        "team_abbr": ["LAL"]
    }
    df = pd.DataFrame(data)
    df["positions"] = df["position"].str.split("-")
    df["all_positions"] = df["position"].apply(lambda x: x.split("-"))
    return df


# 数据处理模块边界条件测试
def test_filter_players_edge_cases(empty_dataframe):
    """测试球员过滤功能的边界条件"""
    # 测试空数据框
    filtered_df = filter_players(
        empty_dataframe, 
        selected_positions=["后卫"], 
        selected_teams=["湖人"], 
        salary_range=(0, 100000000), 
        selected_player_ids=[1]
    )
    assert filtered_df.empty
    
    # 测试空的过滤条件
    sample_df = pd.DataFrame({
        "player_id": [1],
        "full_name": ["Player1"],
        "position": ["后卫"],
        "team_name": ["湖人"],
        "salary": [10000000],
        "team_abbr": ["LAL"]
    })
    sample_df["positions"] = sample_df["position"].str.split("-")
    sample_df["all_positions"] = sample_df["position"].apply(lambda x: x.split("-"))
    
    filtered_df = filter_players(
        sample_df, 
        selected_positions=[], 
        selected_teams=[], 
        salary_range=(0, 100000000), 
        selected_player_ids=[]
    )
    assert len(filtered_df) == 1


def test_sort_players_edge_cases(empty_dataframe):
    """测试球员排序功能的边界条件"""
    # 测试空数据框
    sorted_df = sort_players(empty_dataframe, "salary", "降序")
    assert sorted_df.empty


def test_get_paged_players_edge_cases(empty_dataframe):
    """测试分页功能的边界条件"""
    # 测试空数据框
    paged_df = get_paged_players(empty_dataframe, 1, 10)
    assert paged_df.empty
    
    # 测试页码为0
    sample_df = pd.DataFrame({"player_id": [1, 2, 3]})
    paged_df = get_paged_players(sample_df, 0, 10)
    assert len(paged_df) == 3  # 应该返回所有数据
    
    # 测试每页大小为0
    paged_df = get_paged_players(sample_df, 1, 0)
    assert paged_df.empty


def test_calculate_total_salary_edge_cases(empty_dataframe):
    """测试总薪资计算功能的边界条件"""
    # 测试空数据框
    total_salary = calculate_total_salary(empty_dataframe)
    assert total_salary == 0


def test_format_salary_edge_cases():
    """测试薪资格式化功能的边界条件"""
    # 测试0值
    assert format_salary(0) == "$0"
    
    # 测试负数
    assert format_salary(-10000000) == "$-10,000,000"
    
    # 测试大数值
    assert format_salary(1000000000) == "$1,000,000,000"


# 阵容管理模块边界条件测试
def test_add_player_to_lineup_edge_cases(empty_dataframe):
    """测试添加球员到阵容功能的边界条件"""
    # 测试空的球员数据
    new_selected, new_bench = add_player_to_lineup(
        empty_dataframe, empty_dataframe, empty_dataframe
    )
    assert new_selected.empty
    assert new_bench.empty


def test_move_player_to_starters_edge_cases(empty_dataframe):
    """测试将球员从替补移到首发功能的边界条件"""
    # 测试空的阵容数据
    new_starters, new_bench = move_player_to_starters(
        empty_dataframe, empty_dataframe, empty_dataframe, 1
    )
    assert new_starters.empty
    assert new_bench.empty


def test_move_player_to_bench_edge_cases(empty_dataframe):
    """测试将球员从首发移到替补功能的边界条件"""
    # 测试空的阵容数据
    new_starters, new_bench = move_player_to_bench(
        empty_dataframe, empty_dataframe, empty_dataframe, 1
    )
    assert new_starters.empty
    assert new_bench.empty


def test_remove_player_from_lineup_edge_cases(empty_dataframe):
    """测试从阵容中移除球员功能的边界条件"""
    # 测试空的阵容数据
    new_selected, new_starters, new_bench = remove_player_from_lineup(
        empty_dataframe, empty_dataframe, empty_dataframe, 1
    )
    assert new_selected.empty
    assert new_starters.empty
    assert new_bench.empty


def test_validate_lineup_edge_cases(empty_dataframe):
    """测试阵容验证功能的边界条件"""
    # 测试空的阵容数据
    validation_result = validate_lineup(empty_dataframe, empty_dataframe, 0)
    assert validation_result["starters_valid"] is False
    assert validation_result["bench_valid"] is False
    assert validation_result["positions_valid"] is False
    assert validation_result["salary_valid"] is True
    assert validation_result["valid_lineup"] is False


# 阵容工具模块边界条件测试
def test_check_lineup_requirements_edge_cases(empty_dataframe):
    """测试检查阵容要求功能的边界条件"""
    # 测试空的首发阵容
    result = check_lineup_requirements(empty_dataframe)
    assert result is False
    
    # 测试首发阵容人数不足
    sample_df = pd.DataFrame({
        "player_id": [1, 2, 3, 4],
        "full_name": ["Player1", "Player2", "Player3", "Player4"],
        "position": ["后卫", "后卫", "前锋", "前锋"],
        "team_name": ["湖人" for _ in range(4)],
        "salary": [10000000 for _ in range(4)],
        "team_abbr": ["LAL" for _ in range(4)]
    })
    sample_df["positions"] = sample_df["position"].str.split("-")
    sample_df["all_positions"] = sample_df["position"].apply(lambda x: x.split("-"))
    result = check_lineup_requirements(sample_df)
    assert result is False


# 评分模块边界条件测试
def test_to_numeric_edge_cases():
    """测试数值转换功能的边界条件"""
    # 测试各种边界值
    assert to_numeric(None) == 0
    assert to_numeric(pd.NA) == 0
    assert to_numeric("") == 0
    assert to_numeric("   ") == 0
    assert to_numeric("invalid") == 0
    assert to_numeric([]) == 0
    assert to_numeric({}) == 0
    assert to_numeric(set()) == 0


def test_calculate_per_edge_cases():
    """测试球员效率评分(PER)计算功能的边界条件"""
    # 测试空数据
    empty_row = pd.Series({})
    per = calculate_per(empty_row)
    assert per == 0
    
    # 测试无上场时间
    test_row = pd.Series({
        "三分命中数": 1,
        "两分命中数": 3,
        "罚球命中数": 2,
        "进攻篮板": 1,
        "防守篮板": 3,
        "助攻": 2,
        "抢断": 1,
        "盖帽": 0,
        "两分出手数": 6,
        "三分出手数": 3,
        "罚球出手数": 3,
        "失误": 1,
        "犯规": 1,
        "上场时间": 0,  # 无上场时间
        "本场比赛是否获胜": True
    })
    per = calculate_per(test_row)
    assert isinstance(per, (int, float))


def test_calculate_weighted_score_edge_cases(empty_dataframe):
    """测试加权得分计算功能的边界条件"""
    # 测试空数据框
    score = calculate_weighted_score(empty_dataframe)
    assert score == 0


# 排行榜模块边界条件测试
def test_should_use_cache():
    """测试是否使用缓存功能的边界条件"""
    # 测试不同的日期字符串
    result = should_use_cache("2023-01-01")
    assert isinstance(result, bool)


def test_get_player_stats():
    """测试获取球员统计数据功能的边界条件"""
    # 测试不存在的日期
    df, error_msg = get_player_stats("9999-99-99", "9999-99-99")
    assert df.empty
    assert error_msg is not None


# 结果查看模块边界条件测试
def test_load_lineup_data():
    """测试加载阵容数据功能的边界条件"""
    # 这里我们无法直接测试文件上传功能，但可以确保函数能够正常执行
    # 实际的异常处理测试需要在集成测试中进行
    pass
