import os
import json
from typing import List

EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def export_dataset(records, filename="rlhf_dataset.jsonl", include_metadata=True):
    """将评估记录列表导出为标准 JSONL 数据集"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    output_path = os.path.join(EXPORT_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        for rec in records:
            if include_metadata:
                line = json.dumps(rec, ensure_ascii=False)
            else:
                minimal = {
                    "prompt": rec.get("prompt", ""),
                    "response": rec.get("response", ""),
                    "model": rec.get("model_name", ""),
                }
                line = json.dumps(minimal, ensure_ascii=False)
            f.write(line + "\n")

    print(f"\n  [导出] 数据集已保存至 {output_path}（共 {len(records)} 条）")


def export_comparison_dataset(paired_records, filename="rlhf_comparison_dataset.jsonl"):
    """导出对比数据集（RLHF 偏好数据格式）"""
    os.makedirs(EXPORT_DIR, exist_ok=True)
    output_path = os.path.join(EXPORT_DIR, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        for rec in paired_records:
            line = json.dumps(rec, ensure_ascii=False)
            f.write(line + "\n")

    print(f"\n  [导出] 对比数据集已保存至 {output_path}（共 {len(paired_records)} 条）")


def build_comparison_records(all_records):
    """从平铺的评估记录中配对构建对比数据集"""
    pairs = []
    i = 0
    while i + 1 < len(all_records):
        r1 = all_records[i]
        r2 = all_records[i + 1]

        if r1.get("prompt") == r2.get("prompt") and r1.get("model_name") != r2.get("model_name"):
            s1 = r1.get("scores", {}).get("final_score", 0)
            s2 = r2.get("scores", {}).get("final_score", 0)
            chosen, rejected = (r1, r2) if s1 >= s2 else (r2, r1)
            pair = {
                "prompt": r1.get("prompt"),
                "chosen": {
                    "response": chosen.get("response"),
                    "score": chosen.get("scores", {}).get("final_score"),
                    "model": chosen.get("model_name"),
                },
                "rejected": {
                    "response": rejected.get("response"),
                    "score": rejected.get("scores", {}).get("final_score"),
                    "model": rejected.get("model_name"),
                },
            }
            pairs.append(pair)
        i += 2
    return pairs
