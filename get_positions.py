import sqlite3

# 连接到SQLite数据库
conn = sqlite3.connect("database/scoutslens.db")
cursor = conn.cursor()

# 获取所有唯一的位置名
cursor.execute("SELECT DISTINCT position FROM player_information ORDER BY position;")
positions = cursor.fetchall()

print("所有位置名:")
for position in positions:
    print(f"- {position[0]}")

print(f"\n总共有 {len(positions)} 个不同的位置名")

# 关闭连接
conn.close()
