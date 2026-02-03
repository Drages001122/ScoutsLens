import pulp
from config import db
from models import PlayerGameStats, PlayerInformation
from utils.rating import calculate_player_score


def get_player_data(date):

    stats = (
        db.session.query(
            PlayerInformation.player_id,
            PlayerInformation.full_name,
            PlayerInformation.salary,
            PlayerInformation.position,
            PlayerGameStats.threePointersMade,
            PlayerGameStats.twoPointersMade,
            PlayerGameStats.freeThrowsMade,
            PlayerGameStats.reboundsOffensive,
            PlayerGameStats.reboundsDefensive,
            PlayerGameStats.assists,
            PlayerGameStats.steals,
            PlayerGameStats.blocks,
            (
                PlayerGameStats.twoPointersAttempted
                + PlayerGameStats.threePointersAttempted
            ).label("field_goals_attempted"),
            (PlayerGameStats.twoPointersMade + PlayerGameStats.threePointersMade).label(
                "field_goals_made"
            ),
            PlayerGameStats.freeThrowsAttempted,
            PlayerGameStats.turnovers,
            PlayerGameStats.foulsPersonal,
            PlayerGameStats.IS_WINNER,
            PlayerGameStats.minutes,
        )
        .join(PlayerGameStats, PlayerInformation.player_id == PlayerGameStats.personId)
        .filter(PlayerGameStats.game_date == date)
        .all()
    )

    player_data = []
    for stat in stats:
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


def get_position_map():
    return {
        "Guard": ["PG", "SG"],
        "Guard-Forward": ["SG", "SF"],
        "Forward-Guard": ["SG", "SF"],
        "Forward": ["SF", "PF"],
        "Forward-Center": ["PF", "C"],
        "Center-Forward": ["PF", "C"],
        "Center": ["C"],
    }


def solve_roster(players_data):
    SALARY_CAP = 187895000
    starter_slots = ["PG", "SG", "SF", "PF", "C"]
    position_map = get_position_map()

    prob = pulp.LpProblem("Basketball_Roster_Optimization", pulp.LpMaximize)

    x = {}

    for p in players_data:
        pid = p["id"]
        p_pos = p["position"]

        allowed_slots = position_map.get(p_pos, [])
        for slot in allowed_slots:
            x[(pid, slot)] = pulp.LpVariable(f"x_{pid}_{slot}", cat="Binary")

        x[(pid, "BENCH")] = pulp.LpVariable(f"x_{pid}_BENCH", cat="Binary")

    objective_terms = []
    for p in players_data:
        pid = p["id"]
        rating = p["rating"]
        for slot in starter_slots:
            if (pid, slot) in x:
                objective_terms.append(2 * rating * x[(pid, slot)])
        if (pid, "BENCH") in x:
            objective_terms.append(1 * rating * x[(pid, "BENCH")])

    prob += pulp.lpSum(objective_terms)

    salary_terms = []
    for p in players_data:
        pid = p["id"]
        sal = p["salary"]
        player_vars = [
            x[(pid, role)] for role in starter_slots + ["BENCH"] if (pid, role) in x
        ]
        for var in player_vars:
            salary_terms.append(sal * var)
    prob += pulp.lpSum(salary_terms) <= SALARY_CAP, "Total_Salary"

    for p in players_data:
        pid = p["id"]
        player_vars = [
            x[(pid, role)] for role in starter_slots + ["BENCH"] if (pid, role) in x
        ]
        prob += pulp.lpSum(player_vars) <= 1, f"One_Role_{pid}"

    for slot in starter_slots:
        slot_vars = [
            x[(pid, slot)]
            for p in players_data
            for pid in [p["id"]]
            if (pid, slot) in x
        ]
        prob += pulp.lpSum(slot_vars) == 1, f"Fill_Starter_{slot}"

    bench_vars = [
        x[(pid, "BENCH")]
        for p in players_data
        for pid in [p["id"]]
        if (pid, "BENCH") in x
    ]
    prob += pulp.lpSum(bench_vars) == 7, "Fill_Bench"

    status = prob.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[status] != "Optimal":
        return None

    roster = {"starters": {}, "bench": [], "total_rating": 0, "total_salary": 0}

    for p in players_data:
        pid = p["id"]

        for slot in starter_slots:
            if (pid, slot) in x and pulp.value(x[(pid, slot)]) == 1:
                roster["starters"][slot] = p
                roster["total_rating"] += p["rating"] * 2
                roster["total_salary"] += p["salary"]

        if (pid, "BENCH") in x and pulp.value(x[(pid, "BENCH")]) == 1:
            roster["bench"].append(p)
            roster["total_rating"] += p["rating"]
            roster["total_salary"] += p["salary"]

    return roster


def get_best_lineup(date):
    players_data = get_player_data(date)
    if not players_data:
        return None
    return solve_roster(players_data)
