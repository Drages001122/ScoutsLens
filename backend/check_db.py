import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "database", "scoutslens.db"
)

# 连接到SQLite数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查player_game_stats表是否存在
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='player_game_stats';"
)
table_exists = cursor.fetchone()

if table_exists:
    print("✓ player_game_stats表已成功创建!")

    # 查看表结构
    print("\n表结构:")
    cursor.execute("PRAGMA table_info(player_game_stats);")
    columns = cursor.fetchall()
    for column in columns:
        print(f"  - {column[1]} ({column[2]})")
else:
    print("✗ player_game_stats表未创建!")

# 关闭连接
conn.close()
