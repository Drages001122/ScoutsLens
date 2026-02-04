# NBA球员信息查询技能使用说明

## 功能介绍

本技能用于查询NBA球员的详细信息，当用户输入一个NBA球队的中文名和一个NBA球员的英文名时，系统会准确输出该球员的player_id、英文球队名和英文球员名。

## 执行流程

1. **获取球队列表**：调用脚本获取数据库中所有NBA球队的英文名列表，确保数据完整性和准确性。
2. **球队中文名匹配**：利用映射表对用户提供的球队中文名进行匹配，将其准确对应到英文球队名。
3. **获取球员列表**：调用脚本，根据确定的英文球队名，获取该球队所有球员的英文名列表。
4. **球员英文名匹配**：对用户提供的球员英文名进行精确匹配，从球员列表中找到对应的球员英文名。
5. **获取球员ID**：调用脚本，根据匹配到的英文球队名和英文球员名，获取该球员的player_id。
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
4. **match_team_chinese_to_english(chinese_team_name)**：将中文球队名匹配到英文球队名
5. **match_player_name(input_player_name, player_list)**：将用户输入的球员名匹配到准确的球员英文名

## 使用示例

### 示例1：查询湖人队的LeBron James

**用户输入**：湖人队 LeBron James

**输出结果**：
```
Player ID: 2544
Team Name: Lakers
Player Name: LeBron James
```

### 示例2：查询勇士队的Stephen Curry

**用户输入**：勇士队 Stephen Curry

**输出结果**：
```
Player ID: 201939
Team Name: Warriors
Player Name: Stephen Curry
```

## 支持的球队中文名

- 湖人队
- 勇士队
- 火箭队
- 雄鹿队
- 凯尔特人队
- 篮网队
- 掘金队
- 快船队
- 热火队
- 猛龙队
- 爵士队
- 步行者队
- 活塞队
- 公牛队
- 魔术队
- 黄蜂队
- 奇才队
- 尼克斯队
- 76人队
- 开拓者队
- 国王队
- 太阳队
- 灰熊队
- 鹈鹕队
- 老鹰队
- 骑士队
- 马刺队
- 雷霆队
- 森林狼队
- 独行侠队

## 错误处理

- **球队不存在**：当用户输入的球队中文名无法匹配到任何英文球队名时，返回错误信息
- **球员不存在**：当用户输入的球员英文名无法在指定球队中找到时，返回错误信息
- **数据库连接失败**：当无法连接到数据库时，返回错误信息

## 响应时间

正常情况下，响应时间应在1秒以内。

## 维护说明

- 当添加新球队或球员时，数据库会自动更新，技能无需修改
- 当球队中文名与英文名的映射关系需要调整时，可修改`TEAM_CHINESE_TO_ENGLISH`字典
- 当球员名匹配逻辑需要优化时，可修改`match_player_name`函数