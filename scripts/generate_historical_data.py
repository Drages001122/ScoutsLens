import os
import subprocess
import re
from datetime import datetime, timedelta

# 定义起始和结束日期
start_date = datetime(2025, 10, 22)
end_date = datetime(2025, 12, 30)

# 脚本路径
script_path = "scripts/nba_game_stats.py"

# 读取原始脚本内容
with open(script_path, "r", encoding="utf-8") as f:
    original_content = f.read()

try:
    # 遍历每一天
    current_date = start_date
    while current_date <= end_date:
        target_date_str = current_date.strftime("%Y-%m-%d")
        print(f"\n{'='*50}")
        print(f"处理日期: {target_date_str}")
        print(f"{'='*50}")
        
        # 检查文件是否已存在
        output_file = f"player_stats_data/nba_player_stats_{target_date_str.replace('-', '_')}.csv"
        if os.path.exists(output_file):
            print(f"文件已存在，跳过: {output_file}")
            current_date += timedelta(days=1)
            continue
        
        # 更新脚本中的TARGET_DATE
        new_script_content = re.sub(
            r"TARGET_DATE = '.*'",
            f"TARGET_DATE = '{target_date_str}'",
            original_content,
        )
        
        # 写回文件
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(new_script_content)
        
        # 运行脚本
        print(f"运行脚本获取数据...")
        try:
            result = subprocess.run(
                ["python", script_path],
                shell=True,
                capture_output=True,
                text=True,
                cwd="."
            )
            
            print(f"脚本输出:")
            print(result.stdout)
            if result.stderr:
                print(f"错误信息:")
                print(result.stderr)
            
            # 检查是否生成了文件
            if os.path.exists(output_file):
                print(f"✓ 成功生成文件: {output_file}")
            else:
                print(f"✗ 未能生成文件: {output_file}")
                
        except Exception as e:
            print(f"运行脚本时出错: {e}")
        
        # 增加一天
        current_date += timedelta(days=1)
        
finally:
    # 恢复原始脚本内容
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(original_content)
    print(f"\n{'='*50}")
    print("脚本执行完成，已恢复原始脚本内容")
    print(f"{'='*50}")
