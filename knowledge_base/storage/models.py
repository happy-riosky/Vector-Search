from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import inspect
import enum

Base = declarative_base()

# 定义枚举类
class QuestionType(enum.Enum):
    SINGLE_CHOICE = "单选题"
    SHORT_ANSWER = "简答题"
    COMPREHENSIVE_APPLICATION = "综合应用题"
    MULTIPLE_CHOICE = "多选题"
    FILL_IN_THE_BLANK = "填空题"

class Subject(enum.Enum):
    DATA_STRUCTURE = "数据结构"
    COMPUTER_ORGANIZATION = "计算机组成原理"
    OPERATING_SYSTEM = "操作系统"
    COMPUTER_NETWORK = "计算机网络"
    MIX = "混合"

class Difficulty(enum.Enum):
    EASY = "简单"
    MEDIUM = "中等"
    HARD = "困难"

class Source(enum.Enum):
    REAL = "真题"
    INTERNET = "互联网"
    AI = "AI"

def to_dict(model) -> dict:
    """
    将Question对象转换为字典格式, 并将None值替换为空字符串
    """
    dict = {c.key: getattr(model, c.key) for c in inspect(model).mapper.column_attrs}
    for key, value in dict.items():
        if value is None:
            dict[key] = ""
    return dict

class Question(Base):
    __tablename__ = "questions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), nullable=False)
    document = Column(String(2048), nullable=False)  # 后期拼接，暂无枚举
    type = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    question = Column(String(2048), nullable=False)  # 文本，无枚举
    options = Column(String(255), nullable=False)  # 用 \n 分割选项
    answer = Column(String(255), nullable=False)  # 答案，无枚举
    difficulty = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    exam_point = Column(String(255), nullable=True)  # 可为空，无枚举

    def to_dict(self) -> dict:
        return to_dict(self)

class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    uuid = Column(String(255), nullable=False)
    document = Column(String(2048), nullable=False)  # 存入向量数据库的文本
    subject = Column(String(255), nullable=False)
    knowledge_point = Column(String(2048), nullable=False)
    difficulty = Column(String(255), nullable=False)
    source = Column(String(255), nullable=False)
    exam_point = Column(String(255), nullable=True)

    def to_dict(self) -> dict:
        return to_dict(self)