
"""
对比工具：将 Model_A 和 Model_B 的输出并排或堆叠展示，
方便人工评估者直观比较两个模型的差异。
"""

def _print_separator(char: str = "─", width: int = 60):
    print(char * width)


def display_side_by_side(prompt: str, response_a: str, response_b: str):
    """
    以堆叠（上下）方式展示两个模型的回答。
    CLI 环境下并排展示宽度受限，堆叠更清晰。
    """
    print("\n" + "█" * 60)
    print("  提示词 (Prompt)")
    print("█" * 60)
    print(f"  {prompt}")

    # ── Model_A ──
    print("\n" + "█" * 60)
    print("  ▌ Model_A (Standard-LLM)")
    print("█" * 60)
    _print_separator("─")
    for line in response_a.strip().split("\n"):
        print(f"  │ {line}")
    _print_separator("─")
    print(f"  ▌ 字符数：{len(response_a)}  |  词数：{len(response_a.split())}")

    # ── Model_B ──
    print("\n" + "█" * 60)
    print("  ▌ Model_B (Reasoning-LLM)")
    print("█" * 60)
    _print_separator("─")
    for line in response_b.strip().split("\n"):
        print(f"  │ {line}")
    _print_separator("─")
    print(f"  ▌ 字符数：{len(response_b)}  |  词数：{len(response_b.split())}")

    # 简单对比指标
    print("\n" + "─" * 60)
    print("  [快速对比]")

    a_lines = response_a.count("\n") + 1
    b_lines = response_b.count("\n") + 1
    print(f"  行数：Model_A={a_lines} 行  |  Model_B={b_lines} 行")

    a_has_steps = "步骤" in response_b or "Step" in response_b
    b_has_steps = "步骤" in response_b or "Step" in response_b

    if b_has_steps:
        print(f"  结构差异：Model_B 包含步骤化推理结构，Model_A 未使用分步格式。")

    if len(response_b) > len(response_a) * 1.3:
        print(f"  长度差异：Model_B 比 Model_A 详细约 {int(len(response_b) / max(len(response_a), 1))} 倍。")
    elif len(response_a) > len(response_b) * 1.3:
        print(f"  长度差异：Model_A 比 Model_B 详细。")

    _print_separator("─")
    print()


def display_simple_diff(response_a: str, response_b: str):
    """
    极简差异展示：逐行对比两个回复的结构差异。
    """
    print("\n  [行级结构对比]")
    max_len = max(len(response_a), len(response_b))
    ratio = min(len(response_a), len(response_b)) / max(max_len, 1)
    if ratio < 0.6:
        print("  两个回复的长度差异显著，内容结构差异较大。")
    elif ratio < 0.9:
        print("  两个回复长度接近但仍有差异。")
    else:
        print("  两个回复长度基本一致。")

    # 检查是否包含代码块
    if "```" in response_a or "```" in response_b:
        print("  检测到代码块：至少一个回复包含了格式化代码。")
    if "步骤" in response_b or "Step" in response_b:
        print("  Model_B 使用了分步骤推理格式。")
