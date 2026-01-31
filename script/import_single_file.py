import csv
import os
import sys
from datetime import datetime, timedelta

from flask import Flask

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from config import db, init_db
from models import PlayerGameStats

app = Flask(__name__)
init_db(app)


def time_to_minutes(time_str):
    if not time_str or time_str == "":
        return 0
    try:
        minutes, seconds = map(int, time_str.split(":"))
        return minutes
    except ValueError:
        return 0


def extract_game_date(file_path):
    file_name = os.path.basename(file_path)
    date_str = file_name.split("_")[3:6]
    if len(date_str) == 3:
        year, month, day = date_str[0], date_str[1], date_str[2].split(".")[0]
        file_date = datetime(int(year), int(month), int(day)).date()
        game_date = file_date + timedelta(days=1)
        return game_date
    return None


def import_csv_to_db(csv_path):
    game_date = extract_game_date(csv_path)
    if not game_date:
        print("无法从文件名提取游戏日期")
        return

    with app.app_context():
        existing_records = PlayerGameStats.query.filter_by(game_date=game_date).all()
        if existing_records:
            print(f"删除 {len(existing_records)} 条现有记录")
            for record in existing_records:
                db.session.delete(record)
            db.session.commit()

        with open(csv_path, "r", encoding="utf-8-sig") as csvfile:
            reader = csv.DictReader(csvfile)
            total_records = 0
            skipped_records = 0

            for row in reader:
                try:
                    minutes = time_to_minutes(row.get("minutes", ""))

                    stat = PlayerGameStats(
                        personId=int(row.get("personId", 0)),
                        teamName=row.get("teamName", ""),
                        minutes=minutes,
                        threePointersMade=int(row.get("threePointersMade", 0)),
                        threePointersAttempted=int(
                            row.get("threePointersAttempted", 0)
                        ),
                        twoPointersMade=int(row.get("twoPointersMade", 0)),
                        twoPointersAttempted=int(row.get("twoPointersAttempted", 0)),
                        freeThrowsMade=int(row.get("freeThrowsMade", 0)),
                        freeThrowsAttempted=int(row.get("freeThrowsAttempted", 0)),
                        reboundsOffensive=int(row.get("reboundsOffensive", 0)),
                        reboundsDefensive=int(row.get("reboundsDefensive", 0)),
                        assists=int(row.get("assists", 0)),
                        steals=int(row.get("steals", 0)),
                        blocks=int(row.get("blocks", 0)),
                        turnovers=int(row.get("turnovers", 0)),
                        foulsPersonal=int(row.get("foulsPersonal", 0)),
                        IS_WINNER=row.get("IS_WINNER", "False").lower() == "true",
                        game_date=game_date,
                    )

                    db.session.add(stat)
                    total_records += 1

                    if total_records % 100 == 0:
                        db.session.commit()
                        print(f"已提交 {total_records} 条记录")

                except Exception as e:
                    print(f"处理记录时出错: {e}")
                    skipped_records += 1
                    continue

            db.session.commit()
            print(f"导入完成！")
            print(f"成功导入: {total_records} 条记录")
            print(f"跳过: {skipped_records} 条记录")


if __name__ == "__main__":
    csv_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "player_stats_data",
        "nba_player_stats_2026_01_30.csv",
    )
    import_csv_to_db(csv_file_path)
