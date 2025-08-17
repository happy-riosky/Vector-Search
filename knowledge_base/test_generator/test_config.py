from typing import List, override
from pydantic import BaseModel

from ..storage import QuestionType, Subject, Difficulty, Source

class TestSectionConfig(BaseModel):
  """一个部分试卷的配置
  每个部分可以有不同的题目类型和数量
  """
  type: QuestionType
  number: int
  subject: Subject | None = None
  difficulty: Difficulty | None = None
  knowledge_point: str | None = None
  source: Source | None = None

  def __str__(self):
    return ', '.join([
      f"type={self.type.value}",
      f"number={self.number}",
      f"subject={self.subject.value if self.subject else 'None'}",
      f"difficulty={self.difficulty.value if self.difficulty else 'None'}",
      f"knowledge_point={self.knowledge_point if self.knowledge_point else 'None'}",
      f"source={self.source.value if self.source else 'None'}"
    ])

class TestConfig(BaseModel):
  """一套试卷的配置
  试卷由多个部分组成，每个部分由多个题目组成
  每个部分可以有不同的题目类型和数量
  """
  sections: List[TestSectionConfig]
  
  @property
  def length(self) -> int:
    return sum(section.number for section in self.sections)

  @override
  def __str__(self):
    return "\n".join(f"section {i}: {section.__str__() if section else 'None'}" for i, section in enumerate(self.sections))