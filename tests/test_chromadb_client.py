import pytest
import tempfile
import os
import shutil

from knowledge_base import KnowledgeBase
from knowledge_base.storage.chromadb_client import ChromaDBClient
from knowledge_base.config import chromadb_config


class TestBasic:
    """ChromaDBClient 测试类"""

    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    @pytest.fixture
    def test_config(self, temp_db_path):
        """创建测试配置"""
        config = chromadb_config.copy()
        config["path"] = temp_db_path
        return config

    @pytest.fixture
    def chromadb_client(self, test_config):
        """创建 ChromaDBClient 实例"""
        return ChromaDBClient(test_config)

    @pytest.fixture
    def knowledge_base(self, test_config):
        """创建 KnowledgeBase 实例并保存问题"""
        kb = KnowledgeBase(chromadb_config=test_config)
        kb.save_questions_from_file("data/questions.csv")
        return kb

    def test_get_collection(self):
        client = ChromaDBClient(chromadb_config)
        collection = client.get_collection("questions")
        assert collection._embedding_function is not None

    def test_query(self, knowledge_base):
        collection = knowledge_base.chromadb_client.get_collection("questions")
        results = collection.query(
            query_texts=["程序的中断方式"],
            n_results=1,
        )
        assert results is not None
        assert "中断" in results["documents"][0][0]
