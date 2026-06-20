"""
RLHF 评估系统 CLI 入口

提供交互式命令行界面，引导用户完成从输入 prompt 到导出数据集的完整流程。
"""

import sys
import os

# 将项目根目录加入 sys.path，确保模块导入正确
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm_runner import run_model_a, run_model_b
from core.evaluator import evaluate_response, print_score_summary
from core.comparator import display_side_by_side, display_simple_diff
from eval_logging.trace_logger import append_log, read_all_logs, print_stats
from eval_logging.dataset_writer import export_dataset, export_comparison_dataset, build_comparison_records


BANNER = r"""
╔══════════════════════════════════════════════════════╗
║          RLHF 评估终端 v1.0                          ║
║   Lightweight Evaluation System for LLM Outputs      ║
╚══════════════════════════════════════════════════════╝
"""


def clear_screen():
    """简单清屏"""
    os.system("cls" if os.name == "nt" else "clear")


def wait_enter():
    """等待用户按回车继续"""
    input("\n  按 Enter 继续...")


def run_single_evaluation():
    """单次评估流程"""
    print("\n" + "=" * 60)
    prompt = input("  请输入要评估的 prompt：\n  > ").strip()

    if not prompt:
        print("  [错误] prompt 不能为空。")
        return

    # 1. 运行两个模型
    print("\n  [运行模型] 正在生成回复...")
    response_a = run_model_a(prompt)
    response_b = run_model_b(prompt)

    # 2. 对比展示
    print("\n  [对比展示]")
    display_side_by_side(prompt, response_a, response_b)
    display_simple_diff(response_a, response_b)

    wait_enter()

    # 3. 评估 Model_A
    result_a = evaluate_response(prompt, response_a, "Model_A")
    print_score_summary(result_a)
    append_log(result_a)

    wait_enter()

    # 4. 评估 Model_B
    result_b = evaluate_response(prompt, response_b, "Model_B")
    print_score_summary(result_b)
    append_log(result_b)

    print("\n  [完成] 本轮评估已记录。")
    return result_a, result_b


def show_system_menu():
    """显示主菜单"""
    print("""
  ┌─────────────────────────────────────┐
  │  请选择操作：                         │
  │  1. 开始新一轮评估                    │
  │  2. 查看历史统计                      │
  │  3. 导出数据集                        │
  │  4. 导出对比数据集 (RLHF 偏好格式)    │
  │  5. 退出                              │
  └─────────────────────────────────────┘
  """)


def export_datasets():
    """导出各种格式的数据集"""
    records = read_all_logs()
    if not records:
        print("\n  [提示] 暂无数据可导出，请先进行评估。")
        return

    print("\n  [导出选项]")
    print("  1. 导出完整数据集（含元数据）")
    print("  2. 导出最小数据集（仅 prompt + response）")
    print("  3. 导出对比数据集 (pairwise)")
    print("  0. 返回主菜单")

    choice = input("  请选择 (0-3): ").strip()

    if choice == "1":
        export_dataset(records, include_metadata=True)
    elif choice == "2":
        export_dataset(records, "rlhf_minimal_dataset.jsonl", include_metadata=False)
    elif choice == "3":
        pairs = build_comparison_records(records)
        if pairs:
            export_comparison_dataset(pairs)
        else:
            print("\n  [提示] 未找到可配对的评估记录（可能需要完整的 Model_A + Model_B 配对）。")
    else:
        print("  返回主菜单。")


def main():
    """主入口：交互式循环"""
    clear_screen()
    print(BANNER)
    print("  Type 'exit' at any time to quit.\n")

    while True:
        show_system_menu()
        choice = input("  请输入选项 (1-5): ").strip()

        if choice == "1":
            clear_screen()
            run_single_evaluation()
            wait_enter()

        elif choice == "2":
            clear_screen()
            print_stats()
            wait_enter()

        elif choice == "3":
            clear_screen()
            export_datasets()
            wait_enter()

        elif choice == "4":
            clear_screen()
            records = read_all_logs()
            pairs = build_comparison_records(records)
            if pairs:
                export_comparison_dataset(pairs)
            else:
                print("\n  [提示] 未找到可配对的评估记录。")
            wait_enter()

        elif choice in ("5", "exit", "quit"):
            print("\n  感谢使用 RLHF 评估系统，再见！\n")
            sys.exit(0)

        else:
            print("  无效选项，请重新输入。")


if __name__ == "__main__":
    main()

