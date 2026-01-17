# 检查首发阵容是否符合要求
def check_lineup_requirements(starters):
    # 首先检查首发阵容是否至少有5人
    if len(starters) < 5:
        return False
    
    # 获取所有首发球员的位置信息
    player_positions = []
    for _, player in starters.iterrows():
        if 'all_positions' in player and player['all_positions']:
            player_positions.append(player['all_positions'])
        else:
            # 如果球员没有位置信息，无法满足要求
            return False
    
    # 尝试所有可能的位置分配组合，看是否能满足2-2-1的要求
    # 这里使用回溯法来尝试不同的分配方式
    def backtrack(index, guards, forwards, centers):
        # 如果所有球员都已分配位置
        if index == len(player_positions):
            return guards == 2 and forwards == 2 and centers == 1
        
        # 尝试将当前球员分配到不同的位置
        positions = player_positions[index]
        
        # 尝试分配为后卫
        if guards < 2 and '后卫' in positions:
            if backtrack(index + 1, guards + 1, forwards, centers):
                return True
        
        # 尝试分配为前锋
        if forwards < 2 and '前锋' in positions:
            if backtrack(index + 1, guards, forwards + 1, centers):
                return True
        
        # 尝试分配为中锋
        if centers < 1 and '中锋' in positions:
            if backtrack(index + 1, guards, forwards, centers + 1):
                return True
        
        # 如果当前球员无法分配到任何需要的位置，返回False
        return False
    
    # 开始尝试分配
    return backtrack(0, 0, 0, 0)
