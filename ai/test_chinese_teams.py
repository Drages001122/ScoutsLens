from predict import main

# 测试中文球队名
if __name__ == "__main__":
    # 测试数据：中文球队名列表
    test_teams = [
        "活塞",
        "掘金",
        "步行者",
        "爵士",
        "奇才",
        "尼克斯",
        "篮网",
        "湖人",
        "热火",
        "老鹰",
        "雄鹿",
        "公牛",
        "独行侠",
        "凯尔特人",
        "雷霆",
        "魔术",
        "76人",
        "开拓者",
        "太阳",
    ]
    test_exclude_ids = [1630559,1628983,1631096,1631117,1629645,1641718,1631114]

    print(f"测试中文球队: {test_teams}")
    print(f"排除的player_id: {test_exclude_ids}")
    print()

    # 调用main函数
    main(team_names=test_teams, exclude_player_ids=test_exclude_ids)
