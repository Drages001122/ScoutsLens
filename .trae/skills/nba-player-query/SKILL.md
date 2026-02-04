---
name: "nba-player-query"
description: "查询NBA球员的player_id、英文球队名和英文球员名。当用户输入NBA球队中文名和球员英文名时调用。"
---

# NBA球员信息查询技能

## 功能描述

本技能用于查询NBA球员的详细信息，当用户输入一个NBA球队的中文名和一个NBA球员的英文名时，系统会准确输出该球员的player_id、英文球队名和英文球员名。

## 执行流程

1. **获取球队列表**：调用 `skill-script/get_teams.py` 脚本获取数据库中所有NBA球队的英文名列表，确保数据完整性和准确性。
2. **球队中文名匹配**：调用 `skill-script/match_team.py` 脚本对用户提供的球队中文名进行语义分析和匹配，将其准确对应到步骤1获取的英文球队名列表中的某一项。
3. **获取球员列表**：调用 `skill-script/get_players.py` 脚本，根据步骤2确定的英文球队名，获取该球队所有球员的英文名列表。
4. **球员英文名匹配**：调用 `skill-script/match_player.py` 脚本对用户提供的球员英文名进行精确匹配，从步骤3获取的球员列表中找到对应的球员英文名。
5. **获取球员ID**：调用 `skill-script/get_player_id.py` 脚本，根据匹配到的英文球队名和英文球员名，获取该球员的player_id。
6. **输出结果**：将获取到的player_id、英文球队名和英文球员名整合成结构化数据，以清晰、规范的格式输出最终结果。

## 技术实现

### 依赖文件

- `skill-script/get_teams.py`：获取所有NBA球队的英文名列表
- `skill-script/match_team.py`：将中文球队名匹配到英文球队名
- `skill-script/get_players.py`：根据球队名获取该球队的所有球员列表
- `skill-script/match_player.py`：将用户输入的球员名匹配到准确的球员英文名
- `skill-script/get_player_id.py`：根据球队名和球员名获取球员的player_id
- `skill-script/player_mapping.py`：提供球员信息查询功能
- `database/scoutslens.db`：存储球员和球队信息的数据库

### 核心函数

1. **get_all_teams()**：获取所有NBA球队的英文名列表
2. **get_players_by_team(team_name)**：根据球队名获取该球队的所有球员列表
3. **get_player_id(team_name, player_name)**：根据球队名和球员名获取球员的player_id
4. **match_team_chinese_to_english(chinese_team_name, team_list)**：将中文球队名匹配到英文球队名
5. **match_player_name(player_name, player_list)**：将用户输入的球员名匹配到准确的球员英文名

### 错误处理

- **球队不存在**：当用户输入的球队中文名无法匹配到任何英文球队名时，返回错误信息
- **球员不存在**：当用户输入的球员英文名无法在指定球队中找到时，返回错误信息
- **数据库连接失败**：当无法连接到数据库时，返回错误信息

### 响应格式

```json
{
  "player_id": 123456,
  "team_name": "Lakers",
  "player_name": "LeBron James"
}
```

## 使用示例

### 示例1：查询湖人队的LeBron James

**用户输入**：湖人队 LeBron James

**执行流程**：
1. 获取所有球队列表：['Kings', 'Rockets', 'Heat', 'Raptors', 'Grizzlies', 'Pelicans', 'Hawks', 'Suns', 'Cavaliers', 'Jazz', 'Bucks', 'Knicks', 'Trail Blazers', 'Lakers', 'Wizards', 'Hornets', 'Magic', '76ers', 'Spurs', 'Thunder', 'Nuggets', 'Clippers', 'Timberwolves', 'Celtics', 'Pacers', 'Warriors', 'Bulls', 'Mavericks', 'Nets', 'Pistons']
2. 匹配球队中文名"湖人队"到英文球队名"Lakers"
3. 获取湖人队的所有球员列表
4. 匹配球员名"LeBron James"到准确的球员英文名
5. 获取该球员的player_id
6. 输出结果

**输出结果**：
```json
{
  "player_id": 2544,
  "team_name": "Lakers",
  "player_name": "LeBron James"
}
```

### 示例2：查询勇士队的Stephen Curry

**用户输入**：勇士队 Stephen Curry

**执行流程**：
1. 获取所有球队列表
2. 匹配球队中文名"勇士队"到英文球队名"Warriors"
3. 获取勇士队的所有球员列表
4. 匹配球员名"Stephen Curry"到准确的球员英文名
5. 获取该球员的player_id
6. 输出结果

**输出结果**：
```json
{
  "player_id": 201939,
  "team_name": "Warriors",
  "player_name": "Stephen Curry"
}
```

## 注意事项

1. **球队中文名匹配**：支持常见的球队中文名，如"湖人队"、"勇士队"、"火箭队"等
2. **球员英文名匹配**：支持完整的球员英文名，如"LeBron James"、"Stephen Curry"等
3. **响应时间**：正常情况下，响应时间应在1秒以内
4. **数据更新**：当数据库中的球员信息更新时，技能会自动使用最新数据

## 维护说明

- 当添加新球队或球员时，数据库会自动更新，技能无需修改
- 当球队中文名与英文名的映射关系需要调整时，可修改`match_team_chinese_to_english`函数
- 当球员名匹配逻辑需要优化时，可修改`match_player_name`函数