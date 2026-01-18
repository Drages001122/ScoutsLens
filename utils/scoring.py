import pandas as pd


def to_numeric(value, default=0):
    """将值转换为数字，处理"none"和NaN情况"""
    if value is None:
        return default
    if isinstance(value, str):
        if value.strip().lower() == "none":
            return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def calculate_per(row):
    """计算球员效率评分(PER)"""
    # 提取并转换所有需要的数值
    stats = {
        "three_pointers_made": to_numeric(row.get("三分命中数", 0)),
        "two_pointers_made": to_numeric(row.get("两分命中数", 0)),
        "free_throws_made": to_numeric(row.get("罚球命中数", 0)),
        "offensive_rebounds": to_numeric(row.get("进攻篮板", 0)),
        "defensive_rebounds": to_numeric(row.get("防守篮板", 0)),
        "assists": to_numeric(row.get("助攻", 0)),
        "steals": to_numeric(row.get("抢断", 0)),
        "blocks": to_numeric(row.get("盖帽", 0)),
        "field_goals_attempted": to_numeric(row.get("两分出手数", 0)) + to_numeric(row.get("三分出手数", 0)),
        "free_throws_attempted": to_numeric(row.get("罚球出手数", 0)),
        "turnovers": to_numeric(row.get("失误", 0)),
        "personal_fouls": to_numeric(row.get("犯规", 0))
    }

    # 计算投篮和罚球的未命中数
    stats["field_goals_made"] = stats["three_pointers_made"] + stats["two_pointers_made"]
    stats["field_goals_missed"] = stats["field_goals_attempted"] - stats["field_goals_made"]
    stats["free_throws_missed"] = stats["free_throws_attempted"] - stats["free_throws_made"]

    # 计算PER
    try:
        per = (
            stats["three_pointers_made"]
            + (stats["two_pointers_made"] * 0.8)
            + (stats["free_throws_made"] * 0.5)
            + stats["offensive_rebounds"]
            + (stats["defensive_rebounds"] * 0.7)
            + stats["assists"]
            + stats["steals"]
            + stats["blocks"]
            - (stats["field_goals_missed"] * 0.7)
            - (stats["free_throws_missed"] * 0.4)
            - stats["turnovers"]
            - (stats["personal_fouls"] * 0.4)
        )
        # 确保per是一个有效的数字
        if pd.isna(per):
            per = 0
    except Exception:
        per = 0

    # 检查是否有上场时间且球队获胜/落败
    playing_time = row.get("上场时间", "")
    # 同时检查"获胜"和"本场比赛是否获胜"字段，确保在不同场景下都能正确获取获胜状态
    game_won = row.get("获胜", row.get("本场比赛是否获胜", False))

    # 处理game_won的值，确保它是布尔类型
    if isinstance(game_won, str):
        game_won_str = game_won.strip().lower()
        game_won = game_won_str in ("true", "1", "是")
    elif not isinstance(game_won, bool):
        try:
            game_won = bool(game_won)
        except Exception:
            game_won = False

    # 只有当有上场时间且上场时间不为None、不为空字符串、不为NaN时才考虑胜负加成
    has_playing_time = False
    if playing_time is not None:
        if isinstance(playing_time, str):
            has_playing_time = playing_time.strip() != ""
        else:
            # 处理数值类型（如NaN）
            has_playing_time = not pd.isna(playing_time) and playing_time > 0

    if has_playing_time:
        per += 2 if game_won else -2

    return per


def calculate_score(row):
    """计算球员得分"""
    three_pointers = to_numeric(row.get("三分命中数", 0))
    two_pointers = to_numeric(row.get("两分命中数", 0))
    free_throws = to_numeric(row.get("罚球命中数", 0))
    return 3 * three_pointers + 2 * two_pointers + 1 * free_throws


def calculate_rebounds(row):
    """计算球员篮板总数"""
    offensive = to_numeric(row.get("进攻篮板", 0))
    defensive = to_numeric(row.get("防守篮板", 0))
    return offensive + defensive


def calculate_weighted_score(players, role_column="角色"):
    """计算加权总分，首发球员权重为2，替补为1"""
    total_score = 0
    for _, row in players.iterrows():
        rating = to_numeric(row.get("评分", 0))
        weight = 2 if row.get(role_column) == "首发" else 1
        total_score += rating * weight
    return round(total_score, 2)