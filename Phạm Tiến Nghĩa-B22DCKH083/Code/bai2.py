import pandas as pd
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
import time

def export_top_players(df, columns_to_analyze, n=3):
    """
    Lưu vào file các cầu thủ có chỉ số cao nhất và thấp nhất cho các cột chỉ định.
    """
    # Xuất top N cầu thủ có chỉ số cao nhất và thấp nhất
    for top_type, func, filename in [("cao nhất", "nlargest", "Top3NguoiChiSoCaoNhat.txt"), 
                                     ("thấp nhất", "nsmallest", "Top3NguoiChiSoThapNhat.txt")]:
        with open(filename, "w", encoding="utf-8") as file:
            for column in columns_to_analyze:
                file.write(f"\nTop {n} cầu thủ {top_type} cho chỉ số '{column}':\n")
                top_players = getattr(df, func)(n, column)[['Player Name', 'Team', column]]
                file.write(tabulate(top_players, headers='keys', tablefmt='fancy_grid') + "\n")
            print(f"<<<<<<Đã ghi kết quả {top_type} vào file {filename}>>>>>>")

def calculate_statistics(df, columns_to_analyze):
    """
    Tính và xuất thống kê (median, mean, std) của các chỉ số cho toàn giải và từng đội.
    """
    # Tính toán toàn giải
    overall_stats = pd.DataFrame({
        'Team': ['All'],
        **{f"{stat.capitalize()} of {col}": getattr(df[col], stat)().round(2) for col in columns_to_analyze for stat in ['median', 'mean', 'std']}
    })
    
    # Tính toán cho từng đội
    team_stats = df.groupby('Team')[columns_to_analyze].agg(['median', 'mean', 'std']).round(2).reset_index()
    team_stats.columns = ['Team'] + [f"{stat.capitalize()} of {col}" for col in columns_to_analyze for stat in ['median', 'mean', 'std']]

    # Kết hợp và lưu file CSV
    final_stats = pd.concat([overall_stats, team_stats], ignore_index=True)
    final_stats.to_csv('results2.csv', index=False, encoding='utf-8-sig')
    print("<<<<<<<<Đã xuất kết quả ra file results2.csv>>>>>>>>")

def plot_historgrams(df, column_to_analyze):
    # Tên thư mục để lưu trữ các biểu đồ toàn giải
    output_folder_1 = "histograms_all"

    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(output_folder_1):
        os.makedirs(output_folder_1)

    # Vẽ histogram cho toàn giải
    for col in columns_to_analyze:
        plt.figure(figsize=(8, 6))
        sns.histplot(df[col], bins=20, kde=True, color='blue')
        plt.title(f'Histogram of {col} - Toàn Giải')
        plt.xlabel(col)
        plt.ylabel('Số lượng cầu thủ (Người)')
        plt.grid(True, linestyle='--', alpha=0.5)
        # Lưu biểu đồ vào thư mục "histograms_all"
        plt.savefig(os.path.join(output_folder_1, f"{df.columns.get_loc(col)}.png"))
        plt.close()

    print("Đã vẽ xong biểu đồ cho toàn giải")

    # Tên thư mục để lưu trữ các biểu đồ các đội
    output_folder_2 = "histograms_teams"

    # Tạo thư mục nếu chưa tồn tại
    if not os.path.exists(output_folder_2):
        os.makedirs(output_folder_2)

    # Vẽ histogram cho từng đội
    teams = df['Team'].unique()
    for team in teams:
        # Tên thư mục của đội
        team_folder = os.path.join(output_folder_2, team)
        # Tạo thư mục nếu chưa tồn tại
        if not os.path.exists(team_folder):
            os.makedirs(team_folder)

        team_data = df[df['Team'] == team]
        
        for col in columns_to_analyze:
            plt.figure(figsize=(8, 6))
            sns.histplot(team_data[col], bins=20, kde=True, color='green')
            plt.title(f'Histogram of {col} - {team}')
            plt.xlabel(col)
            plt.ylabel('Số lượng cầu thủ (Người)')
            plt.grid(True, linestyle='--', alpha=0.5)
            # Lưu biểu đồ vào thư mục của đội
            plt.savefig(os.path.join(team_folder, f"{df.columns.get_loc(col)}.png"))
            plt.close()
        
        print(f"Đã vẽ xong biểu đồ cho đội {team}")
        time.sleep(3)
    
    print("<<<<<<<<<Đã vẽ xong biểu đồ cho toàn giải và từng đội>>>>>>>>>>")


def find_best_team(df, columns_to_analyze):
    """
    Tìm đội có giá trị cao nhất ở từng chỉ số và đếm tần suất.
    """
    team_summary = df.groupby('Team')[columns_to_analyze].mean()
    best_teams = [(col, team_summary[col].idxmax(), team_summary[col].max()) for col in columns_to_analyze]

    # In kết quả
    print(tabulate(best_teams, headers=["Chỉ số", "Team", "Giá trị"], tablefmt="grid"))

    # Đếm tần suất
    team_counts = Counter([item[1] for item in best_teams])
    frequency_table = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)

    # In tần suất
    print("\nTần suất của từng đội:")
    print(tabulate(frequency_table, headers=["Team", "Số lần"], tablefmt="grid"))
    print(f"Đội có tần suất cao nhất là: {frequency_table[0][0]}")

if __name__ == "__main__":
    df = pd.read_csv("results.csv")
    columns_to_analyze = df.columns[4:]  # Các cột chỉ số

    df[columns_to_analyze] = df[columns_to_analyze].apply(pd.to_numeric, errors='coerce')

    print("Chọn chức năng muốn thực hiện:")
    print("1. Tìm Top 3 người có chỉ số cao nhất và thấp nhất")
    print("2. Tính trung vị, trung bình và độ lệch chuẩn của các chỉ số")
    print("3. Vẽ biểu đồ histogram")
    print("4. Tìm đội có giá trị cao nhất và đếm tần suất")
    print("5. Thoát chương trình")
    
    while True:
        try:
            choice = int(input("Nhập lựa chọn của bạn: "))
            if choice == 1:
                export_top_players(df, columns_to_analyze)
            elif choice == 2:
                calculate_statistics(df, columns_to_analyze)
            elif choice == 3:
                plot_historgrams(df, columns_to_analyze)
            elif choice == 4:
                find_best_team(df, columns_to_analyze)
            elif choice == 5:
                print("Thoát chương trình")
                break
            else:
                print("Lựa chọn không hợp lệ, vui lòng chọn lại.")
        except ValueError:
            print("Vui lòng nhập một số.")
