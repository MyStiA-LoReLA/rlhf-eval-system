
"""
RLHF 评估标准 schema 定义

定义了标准化的评估指标和数据结构，用于对 LLM 输出进行多维评分。
"""

from dataclasses import dataclass, field, asdict
from typing import List, Optional
import json


# 评分维度常量：0-5 分
SCORE_DIMENSIONS = [
    "correctness",           # 正确性：答案是否准确无误
    "reasoning_quality",     # 推理质量：逻辑链条是否清晰完整
    "instruction_following", # 指令遵循：是否严格遵循了用户指令
    "hallucination_risk",    # 幻觉风险：是否存在编造事实的风险（分数越高越安全）
]

# 预定义的失败标签
FAILURE_TAGS = {
    "incomplete":       "回答不完整，缺少关键内容",
    "abstain":          "模型拒绝回答或放弃作答",
    "hallucination":    "包含编造的、不存在的证据或事实",
    "reasoning_error":  "推理过程中出现逻辑错误",
    "format_violation": "输出格式不符合指令要求",
    "repetition":       "内容重复或陷入循环",
    "off_topic":        "偏离了用户提问的主题",
}


@dataclass
class EvaluationResult:
    """单次评估的完整结果"""
    prompt: str
    response: str
    model_name: str
    correctness: int = 0
    reasoning_quality: int = 0
    instruction_following: int = 0
    hallucination_risk: int = 0
    failure_tags: List[str] = field(default_factory=list)
    timestamp: Optional[float] = None  # Unix 时间戳

    @property
    def final_score(self) -> float:
        """四个维度的平均分，保留两位小数"""
        scores = [self.correctness, self.reasoning_quality,
                  self.instruction_following, self.hallucination_risk]
        return round(sum(scores) / len(scores), 2)

    def to_dict(self) -> dict:
        """转成字典，便于序列化为 JSON"""
        return {
            "prompt": self.prompt,
            "response": self.response,
            "model_name": self.model_name,
            "scores": {
                "correctness": self.correctness,
                "reasoning_quality": self.reasoning_quality,
                "instruction_following": self.instruction_following,
                "hallucination_risk": self.hallucination_risk,
                "final_score": self.final_score,
            },
            "failure_tags": self.failure_tags,
            "timestamp": self.timestamp,
        }

    def to_json(self) -> str:
        """输出标准 JSONL 行格式"""
        return json.dumps(self.to_dict(), ensure_ascii=False)


def validate_score(value: int) -> bool:
    """校验分数是否在 0-5 范围内"""
    return 0 <= value <= 5


def describe_score(value: int) -> str:
    """将数字分数转化为可读的描述"""
    descriptions = {
        0: "完全错误或无关",
        1: "大部分错误，仅少量相关",
        2: "部分正确但有明显缺陷",
        3: "基本正确，但存在细节问题",
        4: "大部分正确，质量良好",
        5: "完全正确，质量优秀",
    }
    return descriptions.get(value, "未知分数")
