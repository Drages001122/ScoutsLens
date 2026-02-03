from predict import main

# 直接调用main函数，传入测试参数
if __name__ == "__main__":
    # 测试数据：球队名列表和要排除的player_id
    test_teams = ["Kings", "Rockets"]
    test_exclude_ids = []
    
    print(f"测试球队: {test_teams}")
    print(f"排除的player_id: {test_exclude_ids}")
    print()
    
    # 调用main函数
    main(team_names=test_teams, exclude_player_ids=test_exclude_ids)
