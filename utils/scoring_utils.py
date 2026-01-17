# 计算球员评分
def calculate_player_score(stats, team_won):
    if stats.empty:
        return 0

    # 提取数据
    mp = stats.get("MIN", [0])[0]
    if mp == 0:
        return 0

    three_p = stats.get("FG3M", [0])[0]
    two_p = stats.get("FGM", [0])[0] - three_p
    ft = stats.get("FTM", [0])[0]
    orb = stats.get("OREB", [0])[0]
    drb = stats.get("DREB", [0])[0]
    ast = stats.get("AST", [0])[0]
    stl = stats.get("STL", [0])[0]
    blk = stats.get("BLK", [0])[0]
    fga = stats.get("FGA", [0])[0]
    fg = stats.get("FGM", [0])[0]
    fta = stats.get("FTA", [0])[0]
    tov = stats.get("TOV", [0])[0]
    pf = stats.get("PF", [0])[0]

    # 计算基础评分
    score = (
        three_p
        + (two_p * 0.8)
        + (ft * 0.5)
        + orb
        + (drb * 0.7)
        + ast
        + stl
        + blk
        - ((fga - fg) * 0.7)
        - ((fta - ft) * 0.4)
        - tov
        - (pf * 0.4)
    )

    # 根据球队胜负调整
    if team_won:
        score += 2
    else:
        score -= 2

    return round(score, 2)


# 计算加权总分
def calculate_weighted_score(players_scores):
    total_score = 0
    for player in players_scores:
        weight = 2 if player["role"] == "首发" else 1
        total_score += player["score"] * weight
    return round(total_score, 2)
