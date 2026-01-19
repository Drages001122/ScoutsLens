from utils.constants import POSITION_ADAPTATION_RULES

# 确定球员的位置类型
def determine_position_type(player_positions):
    """根据球员的位置属性确定其位置类型"""
    has_guard = "后卫" in player_positions
    has_forward = "前锋" in player_positions
    has_center = "中锋" in player_positions
    
    if has_guard and not has_forward and not has_center:
        return "仅含后卫"
    elif has_guard and has_forward and not has_center:
        return "后卫+前锋"
    elif not has_guard and has_forward and not has_center:
        return "仅含前锋"
    elif not has_guard and has_forward and has_center:
        return "前锋+中锋"
    elif not has_guard and not has_forward and has_center:
        return "仅含中锋"
    else:
        return "未知"

# 检查球员是否可以担任指定位置
def can_play_position(player_positions, target_position):
    """检查球员是否可以担任指定位置"""
    position_type = determine_position_type(player_positions)
    if position_type not in POSITION_ADAPTATION_RULES:
        return False
    allowed_positions = POSITION_ADAPTATION_RULES[position_type]
    return target_position in allowed_positions

# 检查首发阵容是否符合新的位置规则
def check_lineup_requirements(starters):
    """检查首发阵容是否符合新的位置规则"""
    # 首先检查首发阵容是否有5人
    if len(starters) != 5:
        return False
    
    # 检查每个球员是否有位置信息
    for _, player in starters.iterrows():
        if "all_positions" not in player or not player["all_positions"]:
            return False
    
    # 这里暂时返回True，因为具体的位置分配检查将在UI和导出验证中进行
    # 实际的位置验证将基于用户的具体位置分配
    return True

# 验证具体的位置分配
def validate_position_assignment(starters_with_positions):
    """验证首发阵容的具体位置分配是否符合规则"""
    # 检查是否有5个位置分配
    if len(starters_with_positions) != 5:
        return False
    
    # 检查每个位置分配是否有效
    for player_info in starters_with_positions:
        if "player" not in player_info or "position" not in player_info:
            return False
        
        player = player_info["player"]
        assigned_position = player_info["position"]
        
        if "all_positions" not in player or not player["all_positions"]:
            return False
        
        if not can_play_position(player["all_positions"], assigned_position):
            return False
    
    return True
