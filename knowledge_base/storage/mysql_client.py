from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

from .models import Base, Question, KnowledgePoint
from ..utils import logger

class MySQLClient:
    def __init__(self, config: dict):
        user = config.get("user")
        password = config.get("password")
        host = config.get("host")
        port = config.get("port")
        database = config.get("database")
        self.engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_questions(self, questions: List[Question]):
        session = self.Session()
        session.add_all(questions)
        session.commit()
    
    def save_knowledge_points(self, knowledge_points: List[KnowledgePoint]):
        session = self.Session()
        session.add_all(knowledge_points)
        session.commit()
    
    def get_record_by_uuid(self, table: type[Question] | type[KnowledgePoint], uuid: str) -> Question | KnowledgePoint | None:
        session = self.Session()
        return session.query(table).filter(table.uuid == uuid).first()
    
    def get_question_by_uuid(self, uuid: str) -> Question | None:
        session = self.Session()
        return session.query(Question).filter(Question.uuid == uuid).first()
    
    def get_session(self):
        return self.Session()
    
    def _reset_tables(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
    