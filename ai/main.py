import sqlite3
import pulp
import sys
import os

# 添加项目根目录到 Python 路径，以便导入 backend 模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from backend.utils.rating import calculate_player_score


# 数据库连接函数
def get_player_data(date):
    # 使用绝对路径连接数据库
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "database", "scoutslens.db")
    )
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 查询该日期有比赛的球员及其详细统计数据
    query = """
    SELECT 
        p.player_id, 
        p.full_name, 
        p.salary, 
        p.position, 
        s.threePointersMade, 
        s.twoPointersMade, 
        s.freeThrowsMade, 
        s.reboundsOffensive, 
        s.reboundsDefensive, 
        s.assists, 
        s.steals, 
        s.blocks, 
        s.twoPointersAttempted + s.threePointersAttempted as field_goals_attempted, 
        s.twoPointersMade + s.threePointersMade as field_goals_made, 
        s.freeThrowsAttempted, 
        s.turnovers, 
        s.foulsPersonal, 
        s.IS_WINNER, 
        s.minutes
    FROM 
        player_information p
    JOIN 
        player_game_stats s ON p.player_id = s.personId
    WHERE 
        s.game_date = ?
    """

    cursor.execute(query, (date,))
    stats = cursor.fetchall()

    conn.close()

    # 直接处理每条数据（每个球员一天只有一条数据）
    player_data = []
    for stat in stats:
        # 计算单场比赛的评分
        rating = calculate_player_score(
            three_pointers=stat[4],
            two_pointers=stat[5],
            free_throws=stat[6],
            offensive_rebounds=stat[7],
            defensive_rebounds=stat[8],
            assists=stat[9],
            steals=stat[10],
            blocks=stat[11],
            field_goals_attempted=stat[12],
            field_goals_made=stat[13],
            free_throws_attempted=stat[14],
            turnovers=stat[15],
            personal_fouls=stat[16],
            team_won=stat[17],
            minutes_played=stat[18],
        )

        player_data.append(
            {
                "id": stat[0],
                "name": stat[1],
                "salary": stat[2],
                "position": stat[3],
                "rating": rating,
            }
        )

    return player_data


# 定义位置映射规则
def get_position_map():
    return {
        "Guard": ["PG", "SG"],
        "Guard-Forward": ["SG", "SF"], "Forward-Guard": ["SG", "SF"],
        "Forward": ["SF", "PF"],
        "Forward-Center": ["PF", "C"], "Center-Forward": ["PF", "C"],
        "Center": ["C"],
    }


# 求解最优阵容
def solve_roster(players_data):
    # 常量定义
    SALARY_CAP = 187895000
    starter_slots = ["PG", "SG", "SF", "PF", "C"]
    position_map = get_position_map()

    # 模型初始化
    prob = pulp.LpProblem("Basketball_Roster_Optimization", pulp.LpMaximize)

    # 决策变量
    x = {}

    for p in players_data:
        pid = p["id"]
        p_pos = p["position"]

        # 创建首发变量 (仅当球员有资格打该位置时)
        allowed_slots = position_map.get(p_pos, [])
        for slot in allowed_slots:
            x[(pid, slot)] = pulp.LpVariable(f"x_{pid}_{slot}", cat="Binary")

        # 创建替补变量 (所有人都可以打替补)
        x[(pid, "BENCH")] = pulp.LpVariable(f"x_{pid}_BENCH", cat="Binary")

    # 目标函数
    objective_terms = []
    for p in players_data:
        pid = p["id"]
        rating = p["rating"]

        # 首发项
        for slot in starter_slots:
            if (pid, slot) in x:
                objective_terms.append(2 * rating * x[(pid, slot)])

        # 替补项
        if (pid, "BENCH") in x:
            objective_terms.append(1 * rating * x[(pid, "BENCH")])

    prob += pulp.lpSum(objective_terms)

    # 约束条件

    # 1. 薪资上限
    salary_terms = []
    for p in players_data:
        pid = p["id"]
        sal = p["salary"]
        # 收集该球员所有的决策变量
        player_vars = [
            x[(pid, role)] for role in starter_slots + ["BENCH"] if (pid, role) in x
        ]
        for var in player_vars:
            salary_terms.append(sal * var)
    prob += pulp.lpSum(salary_terms) <= SALARY_CAP, "Total_Salary"

    # 2. 球员唯一性 (每人只能占1个坑位，或者不选)
    for p in players_data:
        pid = p["id"]
        player_vars = [
            x[(pid, role)] for role in starter_slots + ["BENCH"] if (pid, role) in x
        ]
        prob += pulp.lpSum(player_vars) <= 1, f"One_Role_{pid}"

    # 3. 首发位置填满 (每个位置必须正好有1人)
    for slot in starter_slots:
        slot_vars = [
            x[(pid, slot)]
            for p in players_data
            for pid in [p["id"]]
            if (pid, slot) in x
        ]
        prob += pulp.lpSum(slot_vars) == 1, f"Fill_Starter_{slot}"

    # 4. 替补席填满 (必须正好有7人)
    bench_vars = [
        x[(pid, "BENCH")]
        for p in players_data
        for pid in [p["id"]]
        if (pid, "BENCH") in x
    ]
    prob += pulp.lpSum(bench_vars) == 7, "Fill_Bench"

    # 求解
    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))

    # 输出结果
    if pulp.LpStatus[status] != "Optimal":
        print("无法找到满足条件的最优解 (可能薪资限制太严或人员不足)")
        return None

    roster = {"starters": {}, "bench": [], "total_rating": 0, "total_salary": 0}

    for p in players_data:
        pid = p["id"]

        # 检查是否入选首发
        for slot in starter_slots:
            if (pid, slot) in x and pulp.value(x[(pid, slot)]) == 1:
                roster["starters"][slot] = p
                roster["total_rating"] += p["rating"] * 2
                roster["total_salary"] += p["salary"]

        # 检查是否入选替补
        if (pid, "BENCH") in x and pulp.value(x[(pid, "BENCH")]) == 1:
            roster["bench"].append(p)
            roster["total_rating"] += p["rating"]
            roster["total_salary"] += p["salary"]

    return roster


# 主函数
def main():
    # 接收用户输入的日期
    date = input("请输入日期 (格式: YYYY-MM-DD): ")

    # 从数据库获取球员数据
    print("正在从数据库获取球员数据...")
    players_data = get_player_data(date)

    if not players_data:
        print(f"未找到 {date} 日期有比赛的球员数据")
        return

    print(f"共找到 {len(players_data)} 名球员")

    # 求解最优阵容
    print("正在求解最优阵容...")
    result = solve_roster(players_data)

    # 打印结果
    if result:
        print(f"--- 最佳阵容 (总评分: {result['total_rating']:.2f}) ---")
        print(f"总薪资: ${result['total_salary']:,}")
        print("\n[首发名单]")
        for slot in ["PG", "SG", "SF", "PF", "C"]:
            p = result["starters"].get(slot)
            if p:
                print(
                    f"{slot}: {p['name']} ({p.get('team', '无球队')}, 评分:{p['rating']:.2f}, 薪:${p['salary']:,}, 原位:{p['position']})"
                )

        print("\n[替补名单]")
        for p in result["bench"]:
            print(
                f"Bench: {p['name']} ({p.get('team', '无球队')}, 评分:{p['rating']:.2f}, 薪:${p['salary']:,}, 原位:{p['position']})"
            )


if __name__ == "__main__":
    main()
