import os
import sqlite3
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import solve_roster

from backend.utils.rating import calculate_player_score


# 数据库连接函数
def get_db_connection():
    db_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "database", "scoutslens.db")
    )
    conn = sqlite3.connect(db_path)
    return conn


# 获取指定球队的球员信息（平均rating、薪资、位置）
def get_players_by_teams(team_names, exclude_player_ids):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查询这些球队的所有球员
    placeholders = ",".join(["?"] * len(team_names))
    query = f"""
    SELECT 
        p.player_id, 
        p.full_name, 
        p.team_name, 
        p.position, 
        p.salary,
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
        p.team_name IN ({placeholders})
        AND p.player_id NOT IN ({','.join(['?'] * len(exclude_player_ids))})
    """

    params = team_names + exclude_player_ids
    cursor.execute(query, params)
    stats = cursor.fetchall()

    conn.close()

    # 按球员分组计算平均数据
    player_stats = {}
    for stat in stats:
        player_id = stat[0]
        if player_id not in player_stats:
            player_stats[player_id] = {
                "id": player_id,
                "name": stat[1],
                "team": stat[2],
                "position": stat[3],
                "salary": stat[4],
                "stats": [],
            }
        player_stats[player_id]["stats"].append(stat[5:])

    # 计算每个球员的平均rating
    players_data = []
    for player_id, data in player_stats.items():
        # 计算所有比赛的平均rating
        total_rating = 0
        for game_stat in data["stats"]:
            rating = calculate_player_score(
                three_pointers=game_stat[0],
                two_pointers=game_stat[1],
                free_throws=game_stat[2],
                offensive_rebounds=game_stat[3],
                defensive_rebounds=game_stat[4],
                assists=game_stat[5],
                steals=game_stat[6],
                blocks=game_stat[7],
                field_goals_attempted=game_stat[8],
                field_goals_made=game_stat[9],
                free_throws_attempted=game_stat[10],
                turnovers=game_stat[11],
                personal_fouls=game_stat[12],
                team_won=game_stat[13],
                minutes_played=game_stat[14],
            )
            total_rating += rating

        avg_rating = total_rating / len(data["stats"])

        players_data.append(
            {
                "id": data["id"],
                "name": data["name"],
                "team": data["team"],
                "salary": data["salary"],
                "position": data["position"],
                "rating": avg_rating,
            }
        )

    return players_data


# 中文球队名到英文球队名的映射
CHINESE_TEAM_MAP = {
    "国王": "Kings",
    "火箭": "Rockets",
    "热火": "Heat",
    "猛龙": "Raptors",
    "灰熊": "Grizzlies",
    "鹈鹕": "Pelicans",
    "老鹰": "Hawks",
    "太阳": "Suns",
    "骑士": "Cavaliers",
    "爵士": "Jazz",
    "雄鹿": "Bucks",
    "尼克斯": "Knicks",
    "开拓者": "Trail Blazers",
    "湖人": "Lakers",
    "奇才": "Wizards",
    "黄蜂": "Hornets",
    "魔术": "Magic",
    "76人": "76ers",
    "马刺": "Spurs",
    "雷霆": "Thunder",
    "勇士": "Warriors",
    "凯尔特人": "Celtics",
    "篮网": "Nets",
    "公牛": "Bulls",
    "活塞": "Pistons",
    "步行者": "Pacers",
    "掘金": "Nuggets",
    "森林狼": "Timberwolves",
    "快船": "Clippers",
}


# 将中文球队名转换为英文
def translate_team_names(team_names):
    translated = []
    for team in team_names:
        # 先尝试直接映射
        if team in CHINESE_TEAM_MAP:
            translated.append(CHINESE_TEAM_MAP[team])
        else:
            # 如果不是中文，直接使用
            translated.append(team)
    return translated


# 主函数
def main(team_names=None, exclude_player_ids=None):
    # 如果没有提供参数，使用交互式输入
    if team_names is None:
        # 接收用户输入的球队名列表
        team_input = input("请输入球队名列表（用逗号分隔）: ")
        team_names = [team.strip() for team in team_input.split(",")]

        # 接收用户输入的要排除的player_id列表
        try:
            exclude_input = input("请输入要排除的player_id列表（用逗号分隔）: ")
            exclude_player_ids = (
                [pid.strip() for pid in exclude_input.split(",")]
                if exclude_input
                else []
            )
        except EOFError:
            exclude_player_ids = []
    else:
        # 测试模式，使用提供的参数
        exclude_player_ids = exclude_player_ids or []

    # 转换中文球队名为英文
    team_names = translate_team_names(team_names)

    # 获取球员数据
    print("正在查询数据库获取球员信息...")
    players_data = get_players_by_teams(team_names, exclude_player_ids)

    if not players_data:
        print("未找到符合条件的球员数据")
        return

    print(f"共找到 {len(players_data)} 名球员")
    
    # 调试：检查前几个球员是否包含球队信息
    if players_data:
        print(f"调试信息：前3名球员数据")
        for i, p in enumerate(players_data[:3]):
            print(f"{i+1}. {p['name']} - 球队: {p.get('team', '无')}")
    
    # 使用main.py计算最优阵容
    print("正在计算最优阵容...")
    roster = solve_roster(players_data)

    # 打印结果
    if roster:
        print(f"--- 最佳阵容 (总评分: {roster['total_rating']:.2f}) ---")
        print(f"总薪资: ${roster['total_salary']:,}")
        print("\n[首发名单]")
        for slot in ["PG", "SG", "SF", "PF", "C"]:
            p = roster["starters"].get(slot)
            if p:
                print(
                    f"{slot}: {p['name']} ({p.get('team', '无球队')}, 评分:{p['rating']:.2f}, 薪:${p['salary']:,}, 原位:{p['position']})"
                )

        print("\n[替补名单]")
        for p in roster["bench"]:
            print(
                f"Bench: {p['name']} ({p.get('team', '无球队')}, 评分:{p['rating']:.2f}, 薪:${p['salary']:,}, 原位:{p['position']})"
            )
    else:
        print("无法找到满足条件的最优解")


if __name__ == "__main__":
    main()
