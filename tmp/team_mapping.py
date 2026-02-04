# 中英文球队名映射字典
team_name_mapping = {
    '国王队': 'Kings',
    '火箭队': 'Rockets',
    '热火队': 'Heat',
    '猛龙队': 'Raptors',
    '灰熊队': 'Grizzlies',
    '鹈鹕队': 'Pelicans',
    '老鹰队': 'Hawks',
    '太阳队': 'Suns',
    '骑士队': 'Cavaliers',
    '爵士队': 'Jazz',
    '雄鹿队': 'Bucks',
    '尼克斯队': 'Knicks',
    '开拓者队': 'Trail Blazers',
    '湖人队': 'Lakers',
    '奇才队': 'Wizards',
    '黄蜂队': 'Hornets',
    '魔术队': 'Magic',
    '76人队': '76ers',
    '马刺队': 'Spurs',
    '雷霆队': 'Thunder',
    '掘金队': 'Nuggets',
    '快船队': 'Clippers',
    '森林狼队': 'Timberwolves',
    '凯尔特人队': 'Celtics',
    '步行者队': 'Pacers',
    '勇士队': 'Warriors',
    '公牛队': 'Bulls',
    '独行侠队': 'Mavericks',
    '篮网队': 'Nets',
    '活塞队': 'Pistons'
}

# 反向映射，用于验证
translated_team_names = {
    'Kings': '国王队',
    'Rockets': '火箭队',
    'Heat': '热火队',
    'Raptors': '猛龙队',
    'Grizzlies': '灰熊队',
    'Pelicans': '鹈鹕队',
    'Hawks': '老鹰队',
    'Suns': '太阳队',
    'Cavaliers': '骑士队',
    'Jazz': '爵士队',
    'Bucks': '雄鹿队',
    'Knicks': '尼克斯队',
    'Trail Blazers': '开拓者队',
    'Lakers': '湖人队',
    'Wizards': '奇才队',
    'Hornets': '黄蜂队',
    'Magic': '魔术队',
    '76ers': '76人队',
    'Spurs': '马刺队',
    'Thunder': '雷霆队',
    'Nuggets': '掘金队',
    'Clippers': '快船队',
    'Timberwolves': '森林狼队',
    'Celtics': '凯尔特人队',
    'Pacers': '步行者队',
    'Warriors': '勇士队',
    'Bulls': '公牛队',
    'Mavericks': '独行侠队',
    'Nets': '篮网队',
    'Pistons': '活塞队'
}

def get_english_team_name(chinese_name):
    """根据中文球队名获取英文球队名"""
    # 去除可能的"队"字后缀
    if chinese_name.endswith('队'):
        chinese_name = chinese_name[:-1]
    
    # 遍历映射字典，查找匹配
    for key, value in team_name_mapping.items():
        if key.startswith(chinese_name) or chinese_name in key:
            return value
    
    # 如果没有找到精确匹配，尝试模糊匹配
    for key, value in team_name_mapping.items():
        if chinese_name in key:
            return value
    
    return None

if __name__ == '__main__':
    # 测试映射
    test_names = ['开拓者队', '湖人', '勇士', '火箭', '凯尔特人']
    for name in test_names:
        english_name = get_english_team_name(name)
        print(f"中文: {name} -> 英文: {english_name}")
