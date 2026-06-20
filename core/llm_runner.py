
"""
模拟 LLM 推理引擎

提供两个模拟模型（Model_A 和 Model_B），用于生成对比回答以便人工评估。
"""

import random
import time


# ---------------------------------------------------------------------------
# 模拟模型内部"知识库"
# ---------------------------------------------------------------------------

_A_SHORT_ANSWERS = [
    "当然，这是一个常见的概念。",
    "这个问题涉及很多方面，建议进一步查阅相关资料。",
    "根据基本知识，答案是肯定的。",
    "抱歉，我暂时无法给出详尽的解答。",
    "简单来说，是的。",
]

_A_REASONABLE = [
    "这是一个关于机器学习的经典问题。监督学习通过标注数据训练模型，"
    "而无监督学习则从无标签数据中发现模式。两者各有适用场景。",

    "Python 中的列表推导式是一种简洁的构建列表的方式。"
    "它比传统的 for 循环更紧凑，可读性也更好，例如 `[x**2 for x in range(10)]`。",

    "Redis 是一个内存中的数据结构存储系统，常用作缓存和消息代理。"
    "它支持字符串、哈希、列表、集合等多种数据结构，性能非常高。",

    "在 RESTful API 设计中，GET 请求用于获取资源，POST 用于创建，"
    "PUT 用于整体更新，PATCH 用于部分更新，DELETE 用于删除。",

    "GPT 模型基于 Transformer 架构，通过自注意力机制捕捉文本中的长距离依赖关系。"
    "预训练阶段使用海量文本，微调阶段针对特定任务进行优化。",
]

_B_STEP_BY_STEP = [
    "让我分步骤分析这个问题：\n\n"
    "步骤 1：理解需求\n用户询问的是监督学习和无监督学习的区别。\n\n"
    "步骤 2：核心区别分析\n- 监督学习需要标注数据，目标是从输入映射到输出。\n"
    "- 无监督学习不需要标签，目标是发现数据内在结构。\n\n"
    "步骤 3：典型算法\n- 监督：线性回归、SVM、随机森林。\n"
    "- 无监督：K-Means、DBSCAN、PCA。\n\n"
    "步骤 4：适用场景对比\n监督学习适合分类和回归任务；无监督学习适合聚类和降维。\n\n"
    "总结：选择哪种方法取决于是否有标注数据以及任务目标。",

    "让我们一步一步解析列表推导式：\n\n"
    "步骤 1：传统写法\n"
    "```python\nsquares = []\nfor x in range(10):\n    squares.append(x**2)\n```\n\n"
    "步骤 2：列表推导式等价写法\n"
    "```python\nsquares = [x**2 for x in range(10)]\n```\n\n"
    "步骤 3：优势\n- 代码更短，意图更明确\n- 执行速度略快（底层 C 循环）\n\n"
    "步骤 4：注意事项\n- 嵌套推导式可能降低可读性\n- 复杂逻辑建议保留 for 循环",

    "分析 Redis 作为缓存的工作原理：\n\n"
    "1. 数据模型：Key-Value 存储，支持多种数据结构。\n"
    "2. 持久化：RDB（快照）和 AOF（追加日志）两种方式。\n"
    "3. 缓存策略：支持 LRU、TTL 过期、惰性删除等。\n"
    "4. 高可用：通过 Redis Sentinel 实现主从切换。\n\n"
    "实际应用中，Redis 常用于缓存数据库查询结果、会话管理、实时排行榜等场景。",
]


def _simulate_latency(model_name: str):
    """模拟推理延迟，让体验更真实"""
    delay = random.uniform(0.3, 1.2)
    print(f"  [{model_name}] 正在推理中...（约 {delay:.1f}s）")
    time.sleep(delay)


def _pick_response(pool: list, prompt: str) -> str:
    """
    根据 prompt 从候选池中选择最合适的回复。
    简单实现：检查 prompt 关键词做模糊匹配，否则随机返回。
    """
    prompt_lower = prompt.lower()
    # 关键词匹配（模拟语义理解）
    topics = [
        (["监督学习", "无监督学习", "机器学习", "ml", "deep learning"], 0),
        (["python", "列表推导", "列表推导式", "list comprehension"], 1),
        (["redis", "缓存", "cache"], 2),
        (["rest", "api", "restful", "http"], 3),
        (["gpt", "transformer", "attention", "注意力", "llm"], 4),
    ]

    for keywords, idx in topics:
        if any(kw in prompt_lower for kw in keywords):
            if idx < len(pool):
                return pool[idx]
    # 兜底：随机选
    return random.choice(pool)


def run_model_a(prompt: str) -> str:
    """
    Model_A (Standard-LLM)：生成合理但略显通用的回答。
    在复杂场景下偶尔会注入一些"缺陷"，用于测试 failure tag 的识别效果。
    """
    _simulate_latency("Model_A")

    # 约 20% 概率返回过短的"缺陷"回答，用于测试 incomplete 标签
    if random.random() < 0.20:
        return random.choice(_A_SHORT_ANSWERS)

    # 约 15% 概率混入 "I don't know" 风格的回应
    if random.random() < 0.15:
        return "我不太确定这个问题的答案，我建议你查阅权威资料。我知道有这方面的知识，但目前无法给出准确答复。"

    return _pick_response(_A_REASONABLE, prompt)


def run_model_b(prompt: str) -> str:
    """
    Model_B (Reasoning-LLM)：生成结构化、分步骤推理的回答。
    定位为更高质量的 reasoning model。
    """
    _simulate_latency("Model_B")
    return _pick_response(_B_STEP_BY_STEP, prompt)
