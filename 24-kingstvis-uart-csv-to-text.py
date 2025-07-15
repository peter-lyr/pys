import csv
import os
import sys


def process_uart_csv(input_file):
    """
    处理UART CSV文件：提取第二列并替换标记，直接生成输出文件
    """
    # 生成输出文件名（在输入文件名后加-output）
    # 示例：input.csv -> input-output.csv，data.txt -> data-output.txt
    file_name, file_ext = os.path.splitext(input_file)
    output_file = f"{file_name}-output{file_ext}"

    try:
        # 提取第二列数据并暂存到列表
        second_columns = []
        with open(input_file, "r", newline="", encoding="utf-8") as csvfile:
            csv_reader = csv.reader(csvfile)
            for row_num, row in enumerate(csv_reader, 1):
                if row_num == 1:
                    continue
                if len(row) >= 2:
                    second_column = row[1].strip()
                    second_columns.append(second_column)
                else:
                    print(f"警告: 第{row_num}行没有足够的列，已跳过")

        # 处理内容（无临时文件，直接在内存中处理）
        content = "".join(second_columns)  # 合并所有第二列内容
        content = content.replace("(SP)", " ")  # 替换空格标记
        content = content.replace("CRLF", "\n")  # 替换换行标记

        # 写入最终结果
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"处理完成，结果已保存至：{output_file}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 {input_file}")
    except Exception as e:
        print(f"处理时发生错误: {str(e)}")


if __name__ == "__main__":
    # 检查是否提供了输入文件路径
    if len(sys.argv) != 2:
        print("使用方法: python kingstvis-uart-csv-to-text.py <输入文件路径>")
        print("示例: python kingstvis-uart-csv-to-text.py 2025-07-15_16-54-14.txt")
        sys.exit(1)

    # 获取命令行参数中的输入文件路径
    input_file_path = sys.argv[1]
    process_uart_csv(input_file_path)
