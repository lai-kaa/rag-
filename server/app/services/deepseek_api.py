"""DeepSeek V4 API 模型调用模块（OpenAI 兼容接口，无需本地部署模型）。"""

from typing import List

from langchain_core.embeddings import Embeddings
from langchain_openai import ChatOpenAI
from openai import OpenAI

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RemoteEmbeddings(Embeddings):
    """远程 Embedding API 封装，兼容 SiliconFlow 等 OpenAI 兼容服务。

    SiliconFlow 的 BAAI 系列模型不支持 dimensions 参数，
    因此不使用 LangChain OpenAIEmbeddings，直接调用 API 避免 400 错误。
    """

    def __init__(self, api_key: str, base_url: str, model: str, batch_size: int = 16):
        """初始化远程 Embedding 客户端。

        Args:
            api_key: API 密钥
            base_url: API 基础地址
            model: Embedding 模型名称
            batch_size: 每批请求的文本数量
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.batch_size = batch_size

    def _embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量调用 Embedding API（不传 dimensions 参数）。"""
        # 过滤空文本，避免 API 拒绝
        safe_texts = [t if t and t.strip() else " " for t in texts]
        response = self.client.embeddings.create(
            model=self.model,
            input=safe_texts,
        )
        sorted_data = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_data]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """对多个文档片段生成向量。"""
        all_embeddings: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            all_embeddings.extend(self._embed_batch(batch))
        return all_embeddings

    def embed_query(self, text: str) -> List[float]:
        """对查询文本生成向量。"""
        return self._embed_batch([text])[0]


def create_deepseek_llm() -> ChatOpenAI:
    """创建 DeepSeek V4 对话大模型实例。

    使用 OpenAI 兼容接口调用 DeepSeek API。
    模型可选：deepseek-v4-flash（快速）/ deepseek-v4-pro（高质量）

    Returns:
        LangChain ChatOpenAI 实例

    Raises:
        ValueError: API Key 未配置时抛出
    """
    if not settings.DEEPSEEK_API_KEY:
        raise ValueError("未配置 DEEPSEEK_API_KEY，请在 .env 中设置 DeepSeek API 密钥")

    logger.info("初始化 DeepSeek LLM: model=%s", settings.DEEPSEEK_MODEL)
    return ChatOpenAI(
        model=settings.DEEPSEEK_MODEL,
        api_key=settings.DEEPSEEK_API_KEY,
        base_url=settings.DEEPSEEK_BASE_URL,
        temperature=settings.DEEPSEEK_TEMPERATURE,
        max_tokens=settings.DEEPSEEK_MAX_TOKENS,
    )


def create_api_embeddings() -> RemoteEmbeddings:
    """创建远程 Embedding API 实例（无需本地部署模型）。

    DeepSeek 不提供 Embedding 接口，通过 SiliconFlow 等 OpenAI 兼容 API 调用。

    Returns:
        RemoteEmbeddings 实例

    Raises:
        ValueError: Embedding API Key 未配置时抛出
    """
    if not settings.EMBED_API_KEY:
        raise ValueError(
            "未配置 EMBED_API_KEY，请在 .env 中设置 Embedding API 密钥"
            "（SiliconFlow 等平台，无需本地模型）"
        )

    logger.info(
        "初始化远程 Embedding API: model=%s, base=%s",
        settings.EMBED_API_MODEL,
        settings.EMBED_API_BASE_URL,
    )
    return RemoteEmbeddings(
        api_key=settings.EMBED_API_KEY,
        base_url=settings.EMBED_API_BASE_URL,
        model=settings.EMBED_API_MODEL,
    )
