import os
import sys

from flask import Flask

# 添加backend目录到系统路径
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from config import db, init_db
from models import PlayerInformation

app = Flask(__name__)
init_db(app)


def update_player_teams(player_team_pairs):
    """
    批量更新球员的球队名称

    Args:
        player_team_pairs (list): 包含(player_id, team_name)元组的列表

    Returns:
        dict: 包含更新结果的字典，包括成功和失败的记录数
    """
    results = {"success": 0, "failed": 0, "errors": []}

    with app.app_context():
        for player_id, team_name in player_team_pairs:
            try:
                # 查找球员
                player = PlayerInformation.query.filter_by(player_id=player_id).first()

                if player:
                    # 更新球队名称
                    old_team = player.team_name
                    player.team_name = team_name
                    db.session.commit()

                    print(
                        f"成功更新球员 ID {player_id} 的球队: {old_team} -> {team_name}"
                    )
                    results["success"] += 1
                else:
                    error_msg = f"未找到球员 ID {player_id}"
                    print(error_msg)
                    results["errors"].append(error_msg)
                    results["failed"] += 1
            except Exception as e:
                error_msg = f"更新球员 ID {player_id} 时出错: {str(e)}"
                print(error_msg)
                results["errors"].append(error_msg)
                results["failed"] += 1
                db.session.rollback()

    return results


if __name__ == "__main__":
    # 示例：批量填写player_id和team_name
    # 格式：[(player_id1, team_name1), (player_id2, team_name2), ...]
    player_team_pairs = [
        (1641801, "Cavaliers"),
        (1641871, "Hawks"),
        (1630249, "Trail Blazers"),
    ]

    if not player_team_pairs:
        print("请在脚本中填写要更新的球员ID和球队名称")
        print("示例格式：")
        print("player_team_pairs = [")
        print('    (12345, "Lakers"),')
        print('    (67890, "Celtics"),')
        print("]")
    else:
        print(f"开始更新 {len(player_team_pairs)} 条球员记录...")
        results = update_player_teams(player_team_pairs)

        print("\n更新结果:")
        print(f"成功: {results['success']}")
        print(f"失败: {results['failed']}")

        if results["errors"]:
            print("\n错误信息:")
            for error in results["errors"]:
                print(f"- {error}")

        print("\n更新完成！")
