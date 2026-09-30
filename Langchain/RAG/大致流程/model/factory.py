from abc import ABC,abstractmethod
from typing import Optional
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
#工程模式代码示例
class BaseModelFactory(ABC):   #ABC为抽象类基，全名为Abstract Base Class，就是继承了抽象类基
    @abstractmethod  #抽象方法申明
    def generator(self) -> Optional[Embeddings | BaseChatModel]:  #用pass，抽象方法不需要函数体  optional为可选项 就是返回值可以为这两个
        pass

class ChatModelFactory(BaseModelFactory):  #抽象方法实现一
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return ChatTongyi(model="qwen3-max")

class EmbeddingsFactory(BaseModelFactory):  #抽象方法实现二
    def generator(self) -> Optional[Embeddings | BaseChatModel]:
        return DashScopeEmbeddings(model="text-embedding-v4")

chat_model = ChatModelFactory().generator()  #快速生成对象，其他类直接可获取
embeddings_model = EmbeddingsFactory().generator()  #快速生成对象，其他类直接可获取