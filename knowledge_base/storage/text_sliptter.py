from abc import ABC, abstractmethod
from typing import List

class TextSplitter(ABC):
    """抽象字符串切分接口类"""
    
    @abstractmethod
    def split(self, document: str, max_length: int, overlap: int) -> List[str]:
        """
        将输入文档切分为子字符串。
        
        Args:
            document: 输入文档字符串
            max_length: 子字符串最大长度
            overlap: 子字符串之间的重叠长度
            
        Returns:
            List of strings
        """
        pass
    
    def get_name(self) -> str:
        """
        返回切分器的名称
        
        Returns:
            切分器的名称
        """
        return self.__class__.__name__

class CharacterTextSplitter(TextSplitter):
    """基于字符的滑动窗口切分"""
    
    def split(self, document: str, max_length: int, overlap: int) -> List[str]:
        if not document:
            return [document]
        
        stride = max_length - overlap
        if len(document) <= max_length:
            return [document]
        
        chunks = []
        for i in range(0, len(document), stride):
            start = i
            end = min(i + max_length, len(document))
            chunks.append(document[start:end])
            if end == len(document):
                break
        
        return chunks
    