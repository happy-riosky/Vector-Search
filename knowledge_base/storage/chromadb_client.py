import chromadb
from typing import Optional, Union
from chromadb.api.types import Embedding, PyEmbedding, OneOrMany, Document, Image, URI, ID, Where, WhereDocument, Include
from chromadb.config import Settings

from ..utils import get_content_based_uuid, logger
from .text_sliptter import CharacterTextSplitter

class ChromaDBClient:
    def __init__(self, config: dict):
        self.config = config
        self.allow_reset = config.get("allow_reset", False)
        self.client = chromadb.PersistentClient(path=config["path"], settings=Settings(allow_reset=self.allow_reset))
        self.embedding_function = config.get("embedding_function", None)
        self.text_splitter = config.get(
            "text_splitter", CharacterTextSplitter())
        self.max_length = config.get("max_length", 10)
        self.overlap = config.get("overlap", 2)
        self._create_collections(config["collections"])

    def _is_collection_exists(self, collection_name: str):
        """
        检查集合是否存在

        Args:
            collection_name: 集合名称
        """
        try:
            self.client.get_collection(name=collection_name)
            return True
        except Exception as e:
            return False

    def _create_collections(self, collections: dict):
        """
        创建集合

        Args:
            collections: 集合名称和集合配置
        """
        for collection_name in collections.keys():
            logger.info(f"创建集合: {collection_name}, embedding_function: {self.embedding_function}")
            
            if self._is_collection_exists(collection_name):
                logger.debug(f"集合: {collection_name} 已存在")
                continue
            if self.embedding_function is not None:
                logger.info(
                    f"创建集合: {collection_name} 使用自定义 embedding_function: {self.embedding_function}")
                self.client.create_collection(
                    name=collection_name, embedding_function=self.embedding_function)
            else:
                logger.info(
                    f"创建集合: {collection_name} 使用默认 embedding_function")
                self.client.create_collection(name=collection_name)

    def _get_collection_with_embedding_function(self, collection_name: str):
        """
        获取集合并确保使用正确的embedding function
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Collection: 带有正确embedding function的集合对象
        """
        collection = self.client.get_collection(name=collection_name)
        
        # ChromaDB的一个问题：get_collection不会恢复原始的embedding function
        # 我们需要手动重新设置
        if self.embedding_function is not None:
            collection._embedding_function = self.embedding_function
            logger.debug(f"为集合 {collection_name} 重新应用自定义 embedding function")
        
        return collection
        
    def _add_document(self, collection_name: str, document: str, metadata: dict):
        """
        添加文档, 会先进行文本分割, 然后添加到集合中

        Args:
            collection_name: 集合名称
            document: 文档
            metadata: 文档元数据
        """
        chunks = self.text_splitter.split(
            document, self.max_length, self.overlap)
        collection = self._get_collection_with_embedding_function(collection_name)
        for chunk in chunks:
            chunk_uuid = get_content_based_uuid(chunk)
            collection.add(ids=[chunk_uuid], documents=[
                           chunk], metadatas=[metadata])

    def add_question(self, data: dict) -> None:
        try:
            self._add_document("questions", data["question"], data)
            self._add_document("questions", data["answer"], data)
            options = data.get("options", None)
            if options is not None:
                self._add_document("questions", data["options"], data)
        except Exception as e:
            logger.exception(f"Failed to add question: {e}")
            raise e
    
    def add_knowledge_point(self, data: dict) -> None:
        try:
            self._add_document("knowledge_points", data["document"], data)
        except Exception as e:
            logger.exception(f"Failed to add knowledge point: {e}")
            raise e

    def _extract_uuid_from(self, query_result) -> set:
        """从查询结果中提取 metadatas 里的 uuid 列表"""
        ids = query_result['ids'][0]
        metadatas = query_result['metadatas'][0]

        if len(ids) != len(metadatas):
            raise ValueError("ids 和 metadatas 的长度不匹配")

        uuid_list = [meta.get('uuid') for meta in metadatas]

        return set(uuid_list)

    def query_uuid(
        self,
        collection_name: str,
        query_embeddings: Optional[
            Union[
                OneOrMany[Embedding],
                OneOrMany[PyEmbedding],
            ]
        ] = None,
        query_texts: Optional[OneOrMany[Document]] = None,
        query_images: Optional[OneOrMany[Image]] = None,
        query_uris: Optional[OneOrMany[URI]] = None,
        ids: Optional[OneOrMany[ID]] = None,
        n_results: int = 10,
        where: Optional[Where] = None,
        where_document: Optional[WhereDocument] = None,
        include: Include = [
            "metadatas",
            "documents",
            "distances",
        ],
    ) -> list[str]:
        """
        查询文档, 在 chromadb 原生的 query 基础上, 添加了对 metadata 中 uuid 的提取
        """
        collection = self._get_collection_with_embedding_function(collection_name)
        result = collection.query(
            query_embeddings=query_embeddings,
            query_texts=query_texts,
            query_images=query_images,
            query_uris=query_uris,
            ids=ids,
            n_results=n_results + 100,  # FIXME: 这里加 100 是为了避免查询结果不足, 需要优化
            where=where,
            where_document=where_document,
            include=include,
        )
        uuids = list(self._extract_uuid_from(result))
        return list(set(uuids[:n_results]))
    
    def query_metadata(self, collection_name: str, uuids: list[str], include: Include = ["metadatas", "documents"]):
        """
        查询文档, 在 chromadb 原生的 query 基础上, 添加了对 metadata 中 uuid 的提取
        """
        collection = self._get_collection_with_embedding_function(collection_name)
        result = {}
        for uuid in uuids:
            result[uuid] = collection.get(where={"uuid": uuid}, include=include)
        return result

    def update_document(self, collection_name: str, uuid: str,  metadata: dict):
        """
        更新文档, 根据 uuid 删除文档, 然后重新添加

        Args:
            collection_name: 集合名称
            uuid: 文档 uuid
            metadata: 文档元数据
        """
        collection = self._get_collection_with_embedding_function(collection_name)
        collection.delete(where={"uuid": uuid})
        if collection_name == "questions":
            self.add_question(metadata)
        elif collection_name == "knowledge_points":
            self.add_knowledge_point(metadata)
        else:
            logger.error(f"不支持的集合名称: {collection_name}")

    def delete_document(self, collection_name: str, uuid: str):
        """
        删除文档, 使用 where 删除 metadata 中指定 uuid 的文档

        Args:
            collection_name: 集合名称
            uuid: 原始 uuid
        """
        collection = self._get_collection_with_embedding_function(collection_name)
        collection.delete(where={"uuid": uuid})

    def get_collection(self, collection_name: str):
        """
        获取集合，确保使用正确的embedding function
        
        Args:
            collection_name: 集合名称
            
        Returns:
            Collection: 带有正确embedding function的集合对象
            
        Note:
            这是对外的公共方法，可以用来替代直接访问 self.client.get_collection()
            以确保embedding function的正确性
        """
        return self._get_collection_with_embedding_function(collection_name)

    def desc_collection(self, collection_name: str, show_content: bool = True, limit: int = 10):
        """
        显示集合信息

        Args:
            collection_name: 集合名称
            show_content: 是否显示集合内容
            limit: 显示的内容数量限制
        """
        collection = self.client.get_collection(name=collection_name)
        count = collection.count()

        if show_content and count > 0:
            # 获取集合中的所有数据
            results = collection.get(limit=limit)

            # 构建JSON格式的数据
            collection_data = {
                "collection_name": collection_name,
                "total_count": count,
                "displayed_count": min(limit, count),
                "documents": []
            }

            # 处理文档数据
            if results['documents']:
                for i in range(len(results['documents'])):
                    doc_data = {
                        "id": results['ids'][i] if 'ids' in results else f"doc_{i}",
                        "document": results['documents'][i],
                        "metadata": results['metadatas'][i] if 'metadatas' in results and results['metadatas'] else {}
                    }
                    collection_data["documents"].append(doc_data)

            return collection_data

        return {"collection_name": collection_name, "total_count": count}

    def _reset(self):
        self.client.reset()
        self._create_collections(self.config["collections"])