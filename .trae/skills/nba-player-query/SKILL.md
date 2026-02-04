---
name: "nba-player-query"
description: "查询NBA球员的player_id、英文球队名和英文球员名。当用户输入NBA球队中文名和球员中文名时调用。"
---

# NBA球员信息查询技能

## 描述

本技能用于查询NBA球员的详细信息，当用户输入一个NBA球队的中文名和一个NBA球员的中文名时，系统会准确输出该球员的player_id、英文球队名和英文球员名。

## 使用场景

当用户需要查询NBA球员的player_id、英文球队名和英文球员名时，输入NBA球队中文名和球员中文名即可触发此技能。

## 指令

1. **获取球队列表**：调用 `get_teams.py` 脚本获取数据库中所有NBA球队的英文名列表，确保数据完整性和准确性。
2. **球队中文名匹配**：判断用户提供的球队中文名匹配到步骤1获取的英文球队名列表中的哪一个。
3. **获取球员列表**：调用 `get_players.py` 脚本，根据步骤2确定的英文球队名，获取该球队所有球员的英文名列表。
4. **球员中文名匹配**：判断用户提供的球员中文名匹配到步骤3获取的球员列表中的哪一个。
5. **获取球员ID**：调用 `get_player_id.py` 脚本，根据匹配到的英文球队名和英文球员名，获取该球员的player_id。
6. **输出结果**：将获取到的player_id、英文球队名和英文球员名整合成结构化数据，以清晰、规范的格式输出最终结果。

## 使用示例

### 示例1：查询湖人队的勒布朗·詹姆斯

**用户输入**：湖人队 勒布朗·詹姆斯

**执行流程**：
1. 获取所有球队列表：['Kings', 'Rockets', 'Heat', 'Raptors', 'Grizzlies', 'Pelicans', 'Hawks', 'Suns', 'Cavaliers', 'Jazz', 'Bucks', 'Knicks', 'Trail Blazers', 'Lakers', 'Wizards', 'Hornets', 'Magic', '76ers', 'Spurs', 'Thunder', 'Nuggets', 'Clippers', 'Timberwolves', 'Celtics', 'Pacers', 'Warriors', 'Bulls', 'Mavericks', 'Nets', 'Pistons']
2. 匹配球队中文名"湖人队"到英文球队名"Lakers"
3. 获取湖人队的所有球员列表
4. 匹配球员中文名"勒布朗·詹姆斯"到准确的球员英文名"LeBron James"
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

### 示例2：查询勇士队的斯蒂芬·库里

**用户输入**：勇士队 斯蒂芬·库里

**执行流程**：
1. 获取所有球队列表
2. 匹配球队中文名"勇士队"到英文球队名"Warriors"
3. 获取勇士队的所有球员列表
4. 匹配球员中文名"斯蒂芬·库里"到准确的球员英文名"Stephen Curry"
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
