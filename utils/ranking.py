import os
import subprocess
import re
import pandas as pd
from datetime import datetime
from utils.constants import TEAM_TRANSLATION, POSITION_TRANSLATION
from utils.scoring import calculate_per, calculate_score, calculate_rebounds


def should_use_cache(target_date_str):
    """检查是否应该使用缓存数据"""
    # 检查缓存文件是否存在
    csv_file = f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
    if not os.path.exists(csv_file):
        return False
    
    # 获取当前北京时间
    now = datetime.now()
    current_hour = now.hour
    
    # 检查是否在北京时间0:00~16:00之间
    if 0 <= current_hour < 16:
        # 检查查询日期是否是当天的比赛（通过比较日期字符串）
        today = datetime.now().date().strftime("%Y-%m-%d")
        if target_date_str == today:
            return False
    
    return True


def get_player_stats(target_date_str, user_date_str):
    """获取球员统计数据"""
    # 检查缓存
    csv_file = f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
    
    try:
        # 检查文件是否存在
        if not os.path.exists(csv_file):
            return pd.DataFrame(), f"数据文件不存在: {csv_file}"
        
        # 读取球员信息文件，创建id到名字、位置、薪资的映射
        if not os.path.exists("data/player_information.csv"):
            return pd.DataFrame(), "球员信息文件不存在"
        
        player_info_df = pd.read_csv(
            "data/player_information.csv",
            encoding="utf-8-sig",
        )
        # 确保薪资是数字类型
        player_info_df["salary"] = pd.to_numeric(player_info_df["salary"], errors='coerce').fillna(0).astype(int)
        player_id_to_name = dict(
            zip(
                player_info_df["player_id"],
                player_info_df["full_name"],
            )
        )
        player_id_to_position = dict(
            zip(
                player_info_df["player_id"],
                player_info_df["position"],
            )
        )
        player_id_to_salary = dict(
            zip(
                player_info_df["player_id"],
                player_info_df["salary"],
            )
        )

        # 使用常量中的球队名到中文名的映射
        team_name_mapping = TEAM_TRANSLATION

        # 读取数据
        player_stats_df = pd.read_csv(
            csv_file, encoding="utf-8-sig"
        )

        # 将球员id替换为球员名
        player_stats_df["球员名"] = player_stats_df["球员id"].map(
            player_id_to_name
        )

        # 添加位置和薪资字段
        player_stats_df["位置"] = player_stats_df["球员id"].map(
            player_id_to_position
        )
        player_stats_df["薪资"] = player_stats_df["球员id"].map(
            player_id_to_salary
        )
        
        # 确保薪资是数字类型
        player_stats_df["薪资"] = pd.to_numeric(player_stats_df["薪资"], errors='coerce').fillna(0).astype(int)
        
        # 将位置转换为中文
        def translate_position(pos):
            if pd.isna(pos):
                return pos
            # 处理复合位置，如"Guard-Forward"
            translated_parts = []
            for part in str(pos).split('-'):
                translated_parts.append(POSITION_TRANSLATION.get(part.strip(), part.strip()))
            return '-'.join(translated_parts)
        
        player_stats_df["位置"] = player_stats_df["位置"].apply(translate_position)

        # 将球队名替换为中文名
        player_stats_df["球队名"] = player_stats_df["球队名"].map(
            team_name_mapping
        )

        # 移除原始球员id列
        player_stats_df = player_stats_df.drop("球员id", axis=1)

        # 计算得分
        player_stats_df["得分"] = (
            3 * player_stats_df["三分命中数"]
            + 2 * player_stats_df["两分命中数"]
            + 1 * player_stats_df["罚球命中数"]
        )

        # 计算篮板（进攻篮板+防守篮板）
        player_stats_df["篮板"] = (
            player_stats_df["进攻篮板"]
            + player_stats_df["防守篮板"]
        )

        # 将"本场比赛是否获胜"重命名为"获胜"
        if "本场比赛是否获胜" in player_stats_df.columns:
            player_stats_df = player_stats_df.rename(
                columns={"本场比赛是否获胜": "获胜"}
            )

        # 添加评分列
        player_stats_df["评分"] = player_stats_df.apply(
            calculate_per, axis=1
        )

        # 按评分排序
        player_stats_df = player_stats_df.sort_values(
            by="评分", ascending=False
        )

        # 重新排列列，与查看结果板块保持一致
        desired_cols = [
            "评分", "球员名", "球队名", "位置", "薪资",
            "上场时间", "得分", "助攻", "篮板", "抢断", "盖帽",
            "失误", "犯规", "三分命中数", "三分出手数", "两分命中数",
            "两分出手数", "罚球命中数", "罚球出手数", "获胜"
        ]

        # 确保所有列都存在
        existing_cols = [
            col for col in desired_cols if col in player_stats_df.columns
        ]

        player_stats_df = player_stats_df[existing_cols]

        return player_stats_df, None
    except FileNotFoundError as e:
        return pd.DataFrame(), f"文件不存在: {str(e)}"
    except pd.errors.EmptyDataError:
        return pd.DataFrame(), "数据文件为空"
    except pd.errors.ParserError:
        return pd.DataFrame(), "数据文件格式错误"
    except KeyError as e:
        return pd.DataFrame(), f"数据列不存在: {str(e)}"
    except Exception as e:
        return pd.DataFrame(), f"处理数据时出错: {str(e)}"


def run_stats_script(target_date_str):
    """运行统计脚本获取数据"""
    try:
        # 构建命令
        script_path = "scripts/nba_game_stats.py"
        command = f"python {script_path}"

        # 修改脚本中的TARGET_DATE
        with open(script_path, "r", encoding="utf-8") as f:
            script_content = f.read()

        # 更新TARGET_DATE
        new_script_content = re.sub(
            r"TARGET_DATE = '.*'",
            f"TARGET_DATE = '{target_date_str}'",
            script_content,
        )

        # 写回文件
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_script_content)

        # 运行脚本
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=".",
        )

        # 检查是否生成了CSV文件
        csv_file = (
            f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
        )
        if os.path.exists(csv_file):
            return True, csv_file
        else:
            return False, None
    except Exception as e:
        return False, str(e)