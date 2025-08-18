from knowledge_base.storage.chromadb_client import ChromaDBClient
from knowledge_base.config import chromadb_config


class TestChromaDBClient:
    def test_init(self):
        client = ChromaDBClient(chromadb_config)
        assert client is not None

    def test_get_collection(self):
        client = ChromaDBClient(chromadb_config)
        collection = client.get_collection("questions")
        assert collection._embedding_function is not None
