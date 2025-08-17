from llama_index.embeddings.openai import OpenAIEmbedding
from chromadb import Documents, EmbeddingFunction, Embeddings

from .test_generator.test_config import TestConfig, TestSectionConfig
from .storage import QuestionType, Subject

# 演示自定义 EmbeddingFunction 的用法
# class MyEmbeddingFunction(EmbeddingFunction):
#     def __call__(self, input: Documents) -> Embeddings:
#         # embed the documents somehow
#         embeddings = OpenAIEmbedding().get_text_embedding_batch(input)
#         return embeddings

mysql_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'user',
    'password': 'user',
    'database': 'demo',
}

chromadb_config = {
    'allow_reset': True,
    'path': './db_demo',
    # 'embedding_model': MyEmbeddingFunction(),
    'collections': {
        'questions': {
            'name': 'questions',
            'metadata_fields': ['id', 'type', 'subject', 'question', 'options', 'answer', 'difficulty', 'source', 'exam_point'],
        },
        'knowledge_points': {
            'name': 'knowledge_points',
            'metadata_fields': ['id', 'type', 'subject', 'knowledge_point', 'difficulty', 'source', 'exam_point'],
        },
    },
    # 'text_splitter': CharacterTextSplitter(),
    'max_length': 200,
    'overlap': 20,
}

test_config_408: TestConfig = TestConfig(sections=[
    # 单选题
    TestSectionConfig(type=QuestionType.SINGLE_CHOICE, number=10, subject=Subject.DATA_STRUCTURE),
    TestSectionConfig(type=QuestionType.SINGLE_CHOICE, number=10, subject=Subject.COMPUTER_ORGANIZATION),
    TestSectionConfig(type=QuestionType.SINGLE_CHOICE, number=10, subject=Subject.OPERATING_SYSTEM),
    TestSectionConfig(type=QuestionType.SINGLE_CHOICE, number=10, subject=Subject.COMPUTER_NETWORK),
    TestSectionConfig(type=QuestionType.SHORT_ANSWER, number=1, subject=Subject.DATA_STRUCTURE),
    TestSectionConfig(type=QuestionType.SHORT_ANSWER, number=1, subject=Subject.COMPUTER_ORGANIZATION),
    TestSectionConfig(type=QuestionType.SHORT_ANSWER, number=1, subject=Subject.OPERATING_SYSTEM),
    TestSectionConfig(type=QuestionType.SHORT_ANSWER, number=1, subject=Subject.COMPUTER_NETWORK),
    TestSectionConfig(type=QuestionType.SHORT_ANSWER, number=3),
    # 其实应该是综合应用题，但是目前的数综合应用题据库中没有
    # TestSectionConfig(type=QuestionType.COMPREHENSIVE_APPLICATION, number=7),
])