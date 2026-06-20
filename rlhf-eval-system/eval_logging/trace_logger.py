
"""
执行追踪日志：记录每次评估的完整元数据，
以便后续核查和调试。
"""

import os
import json
from typing import List

from schemas.rlhf_schema import EvaluationResult


# 日志文件路径
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
LOG_FILE = os.path.join(LOG_DIR, "logs.jsonl")


def ensure_log_dir():
    """确保日志目录存在"""
    os.makedirs(LOG_DIR, exist_ok=True)


def append_log(result: EvaluationResult):
    """
    将单条评估结果追加写入 JSONL 日志文件。
    JSONL 格式：每行一个完整的 JSON 对象。
    """
    ensure_log_dir()
    line = result.to_json()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(f"\n  [日志] 已写入 {LOG_FILE}")


def read_all_logs() -> List[dict]:
    """读取全部历史日志记录"""
    ensure_log_dir()
    if not os.path.exists(LOG_FILE):
        return []

    records = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  [警告] 跳过损坏的日志行：{line[:50]}...")
                    continue
    return records


def print_stats():
    """
    打印历史评估的统计信息：
    - 总评估次数
    - 各模型的平均分
    - 标签分布
    """
    records = read_all_logs()

    if not records:
        print("\n  [统计] 暂无历史评估记录。")
        return

    print(f"\n{'='*60}")
    print("  历史评估统计")
    print(f"{'='*60}")
    print(f"  总评估次数：{len(records)}")

    # 按模型分组
    model_scores = {}
    model_counts = {}
    tag_counter = {}

    for rec in records:
        model = rec.get("model_name", "unknown")
        score = rec.get("scores", {}).get("final_score", 0)

        model_scores.setdefault(model, []).append(score)
        model_counts[model] = model_counts.get(model, 0) + 1

        for tag in rec.get("failure_tags", []):
            tag_counter[tag] = tag_counter.get(tag, 0) + 1

    # 各模型平均分
    print(f"\n  [各模型平均分]")
    for model, scores in model_scores.items():
        avg = sum(scores) / len(scores)
        print(f"    {model}: {avg:.2f}/5.00 (共 {len(scores)} 次评估)")

    # 标签统计
    if tag_counter:
        print(f"\n  [失败标签分布]")
        for tag, count in sorted(tag_counter.items(), key=lambda x: -x[1]):
            print(f"    {tag}: {count} 次")

    print(f"{'='*60}\n")
