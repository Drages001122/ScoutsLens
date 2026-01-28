import csv
import sqlite3
import os

# 文件路径
csv_file = "d:\\PycharmProjects\\ScoutsLens\\data\\player_information.csv"
db_file = "d:\\PycharmProjects\\ScoutsLens\\database\\scoutslens.db"

# 确保数据库目录存在
db_dir = os.path.dirname(db_file)
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

# 连接到SQLite数据库
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# 删除现有表（如果存在），然后重新创建
cursor.execute("DROP TABLE IF EXISTS player_information")

# 创建球员信息表
cursor.execute(
    """
CREATE TABLE player_information (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    player_id INTEGER,
    full_name TEXT,
    team_name TEXT,
    team_abbr TEXT,
    position TEXT,
    salary INTEGER
)
"""
)

# 读取CSV文件并插入数据
with open(csv_file, "r", encoding="utf-8-sig") as file:
    csv_reader = csv.DictReader(file)
    # 打印列名，用于调试
    print("CSV列名:", csv_reader.fieldnames)
    for row in csv_reader:
        # 处理salary字段，确保它是整数
        salary = int(row["salary"]) if row["salary"] else 0

        cursor.execute(
            """
        INSERT INTO player_information (player_id, full_name, team_name, team_abbr, position, salary)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                int(row["player_id"]),
                row["full_name"],
                row["team_name"],
                row["team_abbr"],
                row["position"],
                salary,
            ),
        )

# 提交更改并关闭连接
conn.commit()
conn.close()

print(f"成功将球员信息从 {csv_file} 导入到 {db_file}")
