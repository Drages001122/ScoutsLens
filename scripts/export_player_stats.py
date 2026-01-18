import os
import pandas as pd
from datetime import datetime, timedelta

# 定义起始日期
start_date = datetime(2025, 10, 22)
end_date = datetime.now()

# 数据目录
data_dir = "player_stats_data"

# 收集所有文件
all_files = []
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y-%m-%d")
    file_name = f"nba_player_stats_{date_str.replace('-', '_')}.csv"
    file_path = os.path.join(data_dir, file_name)
    if os.path.exists(file_path):
        all_files.append(file_path)
    current_date += timedelta(days=1)

print(f"找到 {len(all_files)} 个数据文件")
print(f"文件列表:")
for file in all_files:
    print(f"  - {file}")

# 合并所有数据
if not all_files:
    print("未找到任何数据文件")
    exit(1)

# 读取并合并所有数据
all_data = []
for file_path in all_files:
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        # 添加日期列
        date_str = os.path.basename(file_path).replace("nba_player_stats_", "").replace(".csv", "").replace("_", "-")
        df["日期"] = date_str
        all_data.append(df)
        print(f"✓ 读取文件: {file_path} (行数: {len(df)})")
    except Exception as e:
        print(f"✗ 读取文件失败: {file_path}, 错误: {e}")

if not all_data:
    print("未成功读取任何数据文件")
    exit(1)

# 合并数据
combined_df = pd.concat(all_data, ignore_index=True)
print(f"\n合并后数据:")
print(f"总记录数: {len(combined_df)}")
print(f"字段数: {len(combined_df.columns)}")
print(f"字段列表: {list(combined_df.columns)}")

# 导出为CSV文件
export_file = "d:\\PycharmProjects\\ScoutsLens\\player_stats_data\\all_player_stats_2025_10_22_to_present.csv"
try:
    combined_df.to_csv(export_file, index=False, encoding="utf-8-sig")
    print(f"\n✓ 数据导出完成！")
    print(f"文件保存为: {export_file}")
except Exception as e:
    print(f"\n✗ 导出文件失败: {e}")
