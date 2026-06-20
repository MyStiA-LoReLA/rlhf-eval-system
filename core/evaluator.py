
"""
评估引擎

实现结构化评分和失败标签检测逻辑，引导人工评估者完成标注流程。
"""

import sys
import time
from typing import List

from schemas.rlhf_schema import (
    EvaluationResult,
    SCORE_DIMENSIONS,
    FAILURE_TAGS,
    validate_score,
    describe_score,
)


def tag_failure(response: str) -> List[str]:
    """
    自动预扫描回复，识别潜在的失败标签。
    返回建议标签列表，供评估者确认或修改。
    """
    tags = []
    resp_text = response.strip()

    # 长度检测：过短 -> incomplete
    if len(resp_text) < 30:
        tags.append("incomplete")

    # 放弃/拒绝回答关键词检测 -> abstain
    abstain_patterns = [
        "我不确定", "我无法", "不知道", "不确定",
        "无法给出", "建议查阅", "I don't know", "abstain",
    ]
    if any(pattern in resp_text for pattern in abstain_patterns):
        tags.append("abstain")

    # 重复检测
    words = resp_text.split()
    if len(words) > 10:
        # 简单检查开头和结尾是否高度重复
        first_part = "".join(words[:5])
        last_part = "".join(words[-5:])
        if first_part == last_part and len(words) > 20:
            tags.append("repetition")

    return tags


def _read_int(prompt_text: str, min_val: int = 0, max_val: int = 5) -> int:
    """从命令行读取整数，附带输入校验"""
    while True:
        try:
            raw = input(prompt_text).strip()
            if raw == "":
                print("  输入不能为空，请重新输入。")
                continue
            value = int(raw)
            if min_val <= value <= max_val:
                return value
            print(f"  分数必须在 {min_val}-{max_val} 之间，请重新输入。")
        except ValueError:
            print("  请输入一个有效的整数。")
        except (EOFError, KeyboardInterrupt):
            print("\n  检测到中断，退出评估。")
            sys.exit(1)


def _select_tags(suggested: List[str]) -> List[str]:
    """
    交互式选择/添加失败标签。
    先展示自动检测的建议标签，再允许评估者手动调整。
    """
    selected = list(suggested)  # 初始采纳建议

    # 展示全部可用标签
    print("\n  [可用失败标签]")
    tag_list = list(FAILURE_TAGS.items())
    for i, (key, desc) in enumerate(tag_list, 1):
        marker = " ✓" if key in selected else ""
        print(f"    {i}. {key} - {desc}{marker}")
    print(f"    {len(tag_list) + 1}. 无 / 完成选择")

    while True:
        print(f"\n  当前标签：{selected if selected else '无'}")
        choice = _read_int("  请选择要切换的标签编号 (1-8): ", 1, len(tag_list) + 1)

        if choice == len(tag_list) + 1:
            # 结束选择
            break

        key = tag_list[choice - 1][0]
        if key in selected:
            selected.remove(key)
            print(f"  已移除标签：{key}")
        else:
            selected.append(key)
            print(f"  已添加标签：{key}")

    return selected


def evaluate_response(prompt: str, response: str, model_name: str) -> EvaluationResult:
    """
    完整评估流程：
    1. 自动扫描建议标签
    2. 人工逐维评分
    3. 确认/修改失败标签
    4. 返回 EvaluationResult
    """
    print(f"\n{'='*60}")
    print(f"  评估模型：{model_name}")
    print(f"  回复内容：")
    for line in response.split("\n"):
        print(f"    | {line}")
    print(f"{'='*60}")

    # 自动检测失败标签
    suggested_tags = tag_failure(response)
    if suggested_tags:
        print(f"\n  [自动检测] 建议标签：{', '.join(suggested_tags)}")
    else:
        print("\n  [自动检测] 未检测到明显问题。")

    # 逐维评分
    print("\n  [评分环节] 请在 0-5 分范围内打分：")
    scores = {}
    for dim in SCORE_DIMENSIONS:
        hint = describe_score(3)  # 给出参考基线
        score = _read_int(f"    {dim} (0-5): ")
        scores[dim] = score
        print(f"      -> {dim}: {score}/5 ({describe_score(score)})")

    # 失败标签选择
    final_tags = _select_tags(suggested_tags)

    # 构造结果
    return EvaluationResult(
        prompt=prompt,
        response=response,
        model_name=model_name,
        correctness=scores["correctness"],
        reasoning_quality=scores["reasoning_quality"],
        instruction_following=scores["instruction_following"],
        hallucination_risk=scores["hallucination_risk"],
        failure_tags=final_tags,
        timestamp=time.time(),
    )


def print_score_summary(result: EvaluationResult):
    """打印评估结果摘要"""
    print(f"\n  ── {result.model_name} 评估结果 ──")
    print(f"  最终得分：{result.final_score}/5.00")
    print(f"  正确性：{result.correctness}/5")
    print(f"  推理质量：{result.reasoning_quality}/5")
    print(f"  指令遵循：{result.instruction_following}/5")
    print(f"  幻觉风险：{result.hallucination_risk}/5")
    if result.failure_tags:
        print(f"  失败标签：{', '.join(result.failure_tags)}")
    else:
        print(f"  失败标签：无")
    print(f"  {'─' * 40}")
