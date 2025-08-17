from pathlib import Path
import uuid

from .config import mysql_config, chromadb_config
from .storage import MySQLClient, ChromaDBClient, SyncManager
from .utils import load_data, logger
from .storage import Question, KnowledgePoint
from .test_generator import TestGenerator

class KnowledgeBase:
    def __init__(self, mysql_config: dict = mysql_config, chromadb_config: dict = chromadb_config):
        self.chromadb_config = chromadb_config
        self.mysql_client = MySQLClient(mysql_config)
        self.chromadb_client = ChromaDBClient(chromadb_config)
        self.sync_manager = SyncManager(self.mysql_client, self.chromadb_client)
        self.test_generator = TestGenerator(self.mysql_client, self.chromadb_client)
    
    def save_questions_from_file(self, file_path: str):
        """从文件中添加试题到 MySQL"""
        try:
            df = load_data(Path(file_path))
            # 只保留Question模型中定义的字段，忽略多余字段
            question_fields = {col.name for col in Question.__table__.columns}
            questions = [
                Question(**{k: v for k, v in row.items() if k in question_fields}, uuid=str(uuid.uuid4()))
                for row in df.to_dict(orient="records")
            ]
            self.mysql_client.save_questions(questions)
            logger.info(f"Saved {len(questions)} questions to MySQL")
        except Exception as e:
            logger.exception(f"Failed to save questions from file: {e}")
    
    def save_knowledge_points_from_file(self, file_path: str):
        """从文件中添加知识点到 MySQL"""
        try:
            df = load_data(Path(file_path))
            knowledge_point_fields = {col.name for col in KnowledgePoint.__table__.columns}
            knowledge_points = [
                KnowledgePoint(**{k: v for k, v in row.items() if k in knowledge_point_fields}, uuid=str(uuid.uuid4()))
                for row in df.to_dict(orient="records")
            ]
            self.mysql_client.save_knowledge_points(knowledge_points)
            logger.info(f"Saved {len(knowledge_points)} knowledge points to MySQL")
        except Exception as e:
            logger.exception(f"Failed to save knowledge points from file: {e}")
