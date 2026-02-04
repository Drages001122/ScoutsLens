# 球队中文名到英文名的映射
TEAM_CHINESE_TO_ENGLISH = {
    '湖人队': 'Lakers',
    '勇士队': 'Warriors',
    '火箭队': 'Rockets',
    '雄鹿队': 'Bucks',
    '凯尔特人队': 'Celtics',
    '篮网队': 'Nets',
    '掘金队': 'Nuggets',
    '快船队': 'Clippers',
    '热火队': 'Heat',
    '猛龙队': 'Raptors',
    '爵士队': 'Jazz',
    '步行者队': 'Pacers',
    '活塞队': 'Pistons',
    '公牛队': 'Bulls',
    '魔术队': 'Magic',
    '黄蜂队': 'Hornets',
    '奇才队': 'Wizards',
    '尼克斯队': 'Knicks',
    '76人队': '76ers',
    '开拓者队': 'Trail Blazers',
    '国王队': 'Kings',
    '太阳队': 'Suns',
    '灰熊队': 'Grizzlies',
    '鹈鹕队': 'Pelicans',
    '老鹰队': 'Hawks',
    '骑士队': 'Cavaliers',
    '马刺队': 'Spurs',
    '雷霆队': 'Thunder',
    '森林狼队': 'Timberwolves',
    '独行侠队': 'Mavericks'
}

def match_team_chinese_to_english(chinese_team_name):
    """将中文球队名匹配到英文球队名"""
    # 直接映射
    if chinese_team_name in TEAM_CHINESE_TO_ENGLISH:
        return TEAM_CHINESE_TO_ENGLISH[chinese_team_name]
    
    # 模糊匹配
    for key, value in TEAM_CHINESE_TO_ENGLISH.items():
        if chinese_team_name in key or key in chinese_team_name:
            return value
    
    return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python match_team.py <chinese_team_name>")
        sys.exit(1)
    
    chinese_team_name = sys.argv[1]
    english_team_name = match_team_chinese_to_english(chinese_team_name)
    if english_team_name:
        print(f"Chinese team: {chinese_team_name} -> English team: {english_team_name}")
    else:
        print(f"Cannot match Chinese team: {chinese_team_name}")