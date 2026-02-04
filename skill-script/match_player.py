def match_player_name(input_player_name, player_list):
    """将用户输入的球员名匹配到准确的球员英文名"""
    # 标准化输入
    input_normalized = input_player_name.strip().lower()
    
    # 精确匹配
    for player_name in player_list:
        if player_name.lower() == input_normalized:
            return player_name
    
    # 模糊匹配
    for player_name in player_list:
        if input_normalized in player_name.lower() or player_name.lower() in input_normalized:
            return player_name
    
    # 部分匹配
    for player_name in player_list:
        input_parts = input_normalized.split()
        player_parts = player_name.lower().split()
        # 检查是否有共同的部分
        common_parts = set(input_parts) & set(player_parts)
        if common_parts:
            return player_name
    
    return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print("Usage: python match_player.py <input_player_name> <player1> <player2> ...")
        sys.exit(1)
    
    input_player_name = sys.argv[1]
    player_list = sys.argv[2:]
    matched_player = match_player_name(input_player_name, player_list)
    if matched_player:
        print(f"Input: {input_player_name} -> Matched: {matched_player}")
    else:
        print(f"Cannot match player: {input_player_name}")