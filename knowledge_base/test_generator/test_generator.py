import json
from typing import List
from sqlalchemy.orm import Session

from ..utils import logger
from ..storage import MySQLClient, ChromaDBClient, Question
from .test_config import TestConfig, TestSectionConfig
from .question_finder import KeywordQuestionFinder, MySQLQuestionFinder

class Test():
    def __init__(self, questions: List[Question] | None = None):
        self.questions = questions or []

    def to_json(self):
        return {
            "length": len(self.questions),
            "questions": [question.to_dict() for question in self.questions]
        }
    
    def __str__(self):
        return json.dumps(self.to_json(), indent=4, ensure_ascii=False)
    
    def add(self, question: Question | List[Question]):
        if isinstance(question, Question):
            self.questions.append(question)
        elif isinstance(question, list):
            self.questions.extend(question)

class TestGenerator:
    """
    测试生成器, 能根据不同配置生成不同的测试试卷, 覆盖小测验和考研测试
    """
    def __init__(self, mysql_client: MySQLClient, chromadb_client: ChromaDBClient):
        self.mysql_client = mysql_client
        self.chromadb_client = chromadb_client
        self.keyword_question_finder = KeywordQuestionFinder()
        self.mysql_question_finder = MySQLQuestionFinder()

    def generate_test(self, config: TestConfig) -> Test:
        """生成测试试卷"""
        logger.info(f"开始生成测试试卷: \n{config}")
        test = Test()
        session = self.mysql_client.get_session()
        for section in config.sections:
            try:
                questions = self._get_questions(session, section)
                test.add(questions)
                logger.debug(f"生成测试段落完成, needed={section.number}, actual={len(questions)}, condition={section}")
            except Exception as e:
                logger.error(f"生成测试试卷时发生错误: {e}")
                raise e
        logger.info(f"生成测试试卷完成, needed={config.length}, actual={len(test.questions)}")
        logger.debug(f"测试试卷: \n{test}")
        session.close()
        return test

    def generate_test_section(self, section: TestSectionConfig) -> Test:
        """生成测试段落"""
        logger.info(f"开始生成测试段落: \n{section}")
        test = Test()
        session = self.mysql_client.get_session()
        questions = self._get_questions(session, section)
        test.add(questions)
        logger.info(f"生成测试段落完成, needed={section.number}, actual={len(questions)}")
        logger.debug(f"测试段落: \n{test}")
        session.close()
        return test
    
    def _get_questions(self, session: Session, section: TestSectionConfig) -> List[Question]:
        question_finder = self.keyword_question_finder if section.knowledge_point else self.mysql_question_finder
        return question_finder.find(session, self.chromadb_client, section)
