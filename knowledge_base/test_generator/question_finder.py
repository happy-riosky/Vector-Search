from abc import abstractmethod
from typing import List
from sqlalchemy.orm import Session
from .test_config import TestSectionConfig
from ..storage import ChromaDBClient, Question
from ..utils import logger
from ..utils.instructor import instructor_client

class QuestionFinder():
    """问题查找器父类"""

    def _build_static_conditions(self, section: TestSectionConfig) -> List:
        conditions = [
            Question.type == section.type.value,
            Question.subject == section.subject.value if section.subject else True,
            Question.difficulty == section.difficulty.value if section.difficulty else True,
            Question.source == section.source.value if section.source else True,
        ]
        return conditions
    
    @abstractmethod
    def _find_questions(self, session: Session, chromadb_client: ChromaDBClient, section: TestSectionConfig) -> List[Question]:
        """
        根据知识点查找问题。
        
        Args:
            session: 数据库会话
            chromadb_client: ChromaDB 客户端
            section: 测试段落配置
            
        Returns:
            List of question ids
        """
        pass

    def find(self, session: Session, chromadb_client: ChromaDBClient, section: TestSectionConfig) -> List[Question]:
        questions = self._find_questions(session, chromadb_client, section)
        logger.debug(f"使用 {self.name} 查找问题完成, needed={section.number}, actual={len(questions)}")
        return questions
    
    @property
    def name(self) -> str:
        """
        返回问题查找器的名称
        
        Returns:
            问题查找器的名称
        """
        return self.__class__.__name__

class ChromaDBQuestionFinder(QuestionFinder):
    """基于 ChromaDB 的问题查找"""
    
    def _find_questions(self,
        session: Session,
        chromadb_client: ChromaDBClient,
        section: TestSectionConfig,
    ) -> List[Question]:
        condition = self._build_static_conditions(section)
        if section.knowledge_point:
            question_ids = chromadb_client.query_uuid(collection_name="questions", query_texts=section.knowledge_point, where={"type": section.type.value})
            condition.append(Question.uuid.in_(list(question_ids)))
        questions = session.query(Question).filter(*condition).limit(section.number).all()
        return questions
    
class KeywordQuestionFinder(QuestionFinder):
    """基于 MySQL 的问题查找"""
    
    def _find_questions(self, session: Session, chromadb_client: ChromaDBClient, section: TestSectionConfig) -> List[Question]:
        condition = self._build_static_conditions(section)
        if section.knowledge_point:
            keyword = instructor_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": f"请将该知识点简化为一个词汇, 不要使用知识点内容以外的其它字眼: {section.knowledge_point}"}],
                response_model=str
            )
            logger.debug(f"keyword: {keyword}")
            condition.append(Question.question.like(f"%{keyword}%"))
        questions = session.query(Question).filter(*condition).limit(section.number).all()
        return questions


class MySQLQuestionFinder(QuestionFinder):
    """基于 MySQL 的问题查找, 当不使用内容进行检索时, 使用该类"""
    
    def _find_questions(self, session: Session, chromadb_client: ChromaDBClient, section: TestSectionConfig) -> List[Question]:
        condition = self._build_static_conditions(section)
        questions = session.query(Question).filter(*condition).limit(section.number).all()
        return questions