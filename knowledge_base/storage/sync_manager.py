from sqlalchemy import event

from .chromadb_client import ChromaDBClient
from .mysql_client import MySQLClient
from .models import Question, KnowledgePoint
from ..utils import logger

class SyncManager:
    def __init__(self, mysql_client: MySQLClient, chromadb_client: ChromaDBClient):
        self.mysql_client = mysql_client
        self.chromadb_client = chromadb_client
        self.register_events()
    
    def _type_valid(self, target):
        """ 检查目标类型是否支持 """
        if isinstance(target, Question):
            return True
        elif isinstance(target, KnowledgePoint):
            return True
        else:
            logger.error(f"不支持的类型: {type(target)}")
            return False

    def sync_on_insert(self, mapper, connection, target):
        """监听 MySQL 插入事件，同步到 ChromaDB"""
        try:
            logger.debug(f"Syncing on insert: {target}")
            metadata = target.to_dict()
            if self._type_valid(target):
                if isinstance(target, Question):
                    self.chromadb_client.add_question(data=metadata)
                elif isinstance(target, KnowledgePoint):
                    self.chromadb_client.add_knowledge_point(data=metadata)
        except Exception as e:
            logger.exception(f"Failed to sync on insert: {e}")
            raise e

    def sync_on_update(self, mapper, connection, target):
        """监听 MySQL 更新事件，同步到 ChromaDB"""
        try:
            logger.debug(f"Syncing on update: {target}")
            metadata = target.to_dict()
            if self._type_valid(target):
                if isinstance(target, Question):
                    self.chromadb_client.update_document(collection_name="questions", uuid=str(target.uuid), metadata=metadata)
                elif isinstance(target, KnowledgePoint):
                    self.chromadb_client.update_document(collection_name="knowledge_points", uuid=str(target.uuid), metadata=metadata)
        except Exception as e:
            logger.exception(f"Failed to sync on update: {e}")
            raise e

    def sync_on_delete(self, mapper, connection, target):
        """监听 MySQL 删除事件，同步到 ChromaDB"""
        logger.debug(f"Syncing on delete: {target}")
        try:
            if self._type_valid(target):
                if isinstance(target, Question):
                    self.chromadb_client.delete_document(collection_name="questions", uuid=str(target.uuid))
                elif isinstance(target, KnowledgePoint):
                    self.chromadb_client.delete_document(collection_name="knowledge_points", uuid=str(target.uuid))
        except Exception as e:
            logger.exception(f"Failed to sync on delete: {e}")
            raise e

    def full_sync(self):
        """全量同步 MySQL 到 ChromaDB"""
        session = self.mysql_client.get_session()
        # 同步 questions
        questions = session.query(Question).all()
        for question in questions:
            self.chromadb_client.add_question(data=question.to_dict())
        # 同步 knowledge_points
        knowledge_points = session.query(KnowledgePoint).all()
        for knowledge_point in knowledge_points:
            self.chromadb_client.add_knowledge_point(data=knowledge_point.to_dict())

    def register_events(self):
        """注册 SQLAlchemy 事件监听"""
        event.listen(Question, "after_insert", self.sync_on_insert)
        event.listen(Question, "after_update", self.sync_on_update)
        event.listen(Question, "after_delete", self.sync_on_delete)
        event.listen(KnowledgePoint, "after_insert", self.sync_on_insert)
        event.listen(KnowledgePoint, "after_update", self.sync_on_update)
        event.listen(KnowledgePoint, "after_delete", self.sync_on_delete)