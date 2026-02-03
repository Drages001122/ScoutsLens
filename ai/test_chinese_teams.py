from predict import main

# 测试中文球队名
if __name__ == "__main__":
    # 测试数据：中文球队名列表
    test_teams = ["黄蜂", "鹈鹕", "步行者", "火箭", "灰熊", "森林狼", "快船", "76人"]
    test_exclude_ids = [203944, 1641744]

    print(f"测试中文球队: {test_teams}")
    print(f"排除的player_id: {test_exclude_ids}")
    print()

    # 调用main函数
    main(team_names=test_teams, exclude_player_ids=test_exclude_ids)
