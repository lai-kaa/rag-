"""RAG 检索增强生成服务，负责文档向量化和知识库问答。"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple

from langchain_chroma import Chroma
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
from langchain_core.documents import Document as LCDocument
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 中文 RAG 提示模板（支持多轮对话、跨文档推理与适度闲聊）
RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "你是一个企业内部知识库问答助手。请基于「上下文信息」和「对话历史」回答用户当前问题。\n\n"
        "回答要求：\n"
        "1. 综合所有召回文档片段进行推理，不要仅依据单一片段作答。\n"
        "2. 若文档中有相关配套内容（如班车、宿舍、交通补贴、留宿、返乡等），"
        "即使未直接写明用户问题的字面答案，也应主动关联说明，给出完整、实用的答复。\n"
        "3. 结合对话历史理解用户意图。"
        "例如：用户说「回不了家」「上班回不去」，应关联宿舍留宿、班车时段、交通补贴等制度；"
        "上一轮提到「下班晚了」，本轮问「有班车吗」，应说明正常班车与晚走方案。\n"
        "4. 若上下文标注为「未检索到文档」，但问题明显与员工生活/工作制度相关，"
        "应结合对话历史给出合理建议，并提示用户联系人事或宿管确认，不要机械复读「未找到」。\n"
        "5. 对于明显与制度无关的闲聊（如问年龄、天气、你是谁），"
        "可礼貌简短回应并说明你是企业知识库助手，不必说「未找到相关内容」。\n"
        "6. 仅当问题与企业管理完全无关且无法给出任何有用信息时，才简短说明知识库暂无依据。\n"
        "7. 使用中文，条理清晰，语气自然，避免死板套话。\n\n"
        "对话历史：\n{chat_history}\n\n"
        "上下文信息：\n{context}",
    ),
    ("human", "{question}"),
])


class RAGService:
    """RAG 服务类，封装文档入库与知识库问答逻辑。"""

    def __init__(self):
        """初始化嵌入模型、向量库和大语言模型。"""
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

        if settings.LLM_PROVIDER == "deepseek":
            from app.services.deepseek_api import create_api_embeddings, create_deepseek_llm

            self.embeddings = create_api_embeddings()
            self.llm = create_deepseek_llm()
            logger.info("RAG 使用 DeepSeek API 模式")
        else:
            self.embeddings = OllamaEmbeddings(
                model=settings.EMBED_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
            )
            self.llm = ChatOllama(
                model=settings.LLM_MODEL,
                base_url=settings.OLLAMA_BASE_URL,
                temperature=0.3,
            )
            logger.info("RAG 使用 Ollama 本地模式")

        self.vectorstore = Chroma(
            collection_name="knowledge_base",
            embedding_function=self.embeddings,
            persist_directory=settings.CHROMA_PERSIST_DIR,
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.RAG_CHUNK_SIZE,
            chunk_overlap=settings.RAG_CHUNK_OVERLAP,
            separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
        )
        self._log_vector_count()

    def _log_vector_count(self) -> None:
        """启动时记录向量数量，便于排查 Render 向量丢失。"""
        try:
            count = self.vectorstore._collection.count()
            if count == 0:
                logger.warning(
                    "知识库向量为空！请在管理后台重新上传文档。"
                    "Render 免费实例重启后本地向量会丢失，需重新向量化。"
                )
            else:
                logger.info("知识库向量数量: %s", count)
        except Exception as e:
            logger.warning("无法读取向量数量: %s", e)

    def _read_text_file(self, file_path: str) -> str:
        """读取文本文件，自动尝试多种常见编码。"""
        raw = open(file_path, "rb").read()
        for encoding in ("utf-8-sig", "utf-8", "gbk", "gb2312"):
            try:
                text = raw.decode(encoding)
                text = text.replace("\r\n", "\n").replace("\r", "\n")
                text = re.sub(r"\n{3,}", "\n\n", text.strip())
                if text:
                    return text
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法读取文档内容（编码不支持或文件为空）: {file_path}")

    def _load_document(self, file_path: str, file_type: str) -> List[LCDocument]:
        """根据文件类型加载文档内容。"""
        if file_type == "pdf":
            loader = PyPDFLoader(file_path)
            docs = loader.load()
        elif file_type == "docx":
            loader = Docx2txtLoader(file_path)
            docs = loader.load()
        else:
            content = self._read_text_file(file_path)
            docs = [LCDocument(page_content=content, metadata={"source": os.path.basename(file_path)})]

        return [d for d in docs if d.page_content and d.page_content.strip()]

    def _split_documents(self, docs: List[LCDocument]) -> List[LCDocument]:
        """将文档切分为非空片段。"""
        chunks = self.text_splitter.split_documents(docs)
        return [c for c in chunks if c.page_content and c.page_content.strip()]

    def ingest_document(self, file_path: str, document_id: int, title: str) -> int:
        """将文档切分并向量化写入 Chroma。"""
        file_type = os.path.splitext(file_path)[1].lstrip(".").lower()
        logger.info("开始文档向量化: id=%s, file=%s", document_id, file_path)

        docs = self._load_document(file_path, file_type)
        if not docs:
            raise ValueError("文档内容为空，无法进行切片")

        total_chars = sum(len(d.page_content) for d in docs)
        chunks = self._split_documents(docs)
        if not chunks:
            raise ValueError(f"文档切片失败（原文 {total_chars} 字，未产生有效片段）")

        for chunk in chunks:
            chunk.metadata["document_id"] = str(document_id)
            chunk.metadata["title"] = title
            chunk.metadata["source"] = os.path.basename(file_path)

        self.vectorstore.add_documents(chunks)
        logger.info("文档向量化完成: id=%s, chars=%s, chunks=%s", document_id, total_chars, len(chunks))
        return len(chunks)

    def delete_document_vectors(self, document_id: int) -> None:
        """从 Chroma 中删除指定文档的所有向量。"""
        try:
            collection = self.vectorstore._collection
            doc_id_str = str(document_id)
            results = collection.get(where={"document_id": doc_id_str})
            ids = results.get("ids") or []
            if ids:
                collection.delete(ids=ids)
                logger.info("已删除文档向量: id=%s, count=%s", document_id, len(ids))
            else:
                logger.info("未找到待删除向量: id=%s", document_id)
        except Exception as e:
            logger.error("删除文档向量失败: id=%s, error=%s", document_id, e)

    def _build_retrieval_query(self, question: str, chat_history: Optional[List[Dict[str, str]]]) -> str:
        """结合对话历史构建检索查询，提升多轮语境下的召回率。"""
        if not chat_history:
            return question

        recent_user_msgs = [
            m["content"] for m in chat_history if m.get("role") == "user" and m.get("content")
        ][-2:]
        if not recent_user_msgs:
            return question

        return " ".join(recent_user_msgs + [question])

    def _format_chat_history(self, chat_history: Optional[List[Dict[str, str]]]) -> str:
        """格式化对话历史供 LLM 理解上下文。"""
        if not chat_history:
            return "（无历史对话）"

        max_msgs = settings.RAG_HISTORY_TURNS * 2
        recent = chat_history[-max_msgs:]
        lines = []
        for msg in recent:
            role = "用户" if msg.get("role") == "user" else "助手"
            content = (msg.get("content") or "").strip()
            if content:
                lines.append(f"{role}：{content}")
        return "\n".join(lines) if lines else "（无历史对话）"

    def _retrieve_with_fallback(self, query: str, k: int) -> List[Tuple[LCDocument, float]]:
        """检索文档，相关性检索为空时回退到普通相似度检索。"""
        scored_docs: List[Tuple[LCDocument, float]] = []

        try:
            # 显式不传 score_threshold，避免低相关结果被全部过滤
            scored_docs = self.vectorstore.similarity_search_with_relevance_scores(query, k=k)
        except Exception as e:
            logger.warning("相关性检索失败，尝试普通检索: %s", e)

        if not scored_docs:
            docs = self.vectorstore.similarity_search(query, k=k)
            scored_docs = [(doc, 0.5) for doc in docs]
            if scored_docs:
                logger.info("相关性检索为空，已回退普通检索: count=%s", len(scored_docs))

        return scored_docs

    def query(
        self,
        question: str,
        top_k: Optional[int] = None,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """基于知识库检索并生成回答。"""
        k = top_k or settings.RAG_TOP_K
        retrieval_query = self._build_retrieval_query(question, chat_history)
        history_text = self._format_chat_history(chat_history)

        logger.info("RAG 问答: question=%s, retrieval=%s", question[:80], retrieval_query[:120])

        scored_docs = self._retrieve_with_fallback(retrieval_query, k)

        sources = []
        retrieved_docs = []
        for doc, score in scored_docs:
            retrieved_docs.append(doc)
            if score >= settings.RAG_SOURCE_MIN_SCORE:
                sources.append({
                    "title": doc.metadata.get("title", "未知文档"),
                    "content": doc.page_content.strip(),
                    "source": doc.metadata.get("source", ""),
                    "score": round(float(score), 4),
                })

        if retrieved_docs:
            context_parts = []
            for i, doc in enumerate(retrieved_docs, 1):
                title = doc.metadata.get("title", "未知文档")
                context_parts.append(f"【片段{i}｜{title}】\n{doc.page_content.strip()}")
            context = "\n\n".join(context_parts)
        else:
            context = "（未检索到知识库文档片段，请结合对话历史作答；若向量库为空需在管理后台重新上传文档）"
            logger.warning("检索结果为空，仍将调用 LLM 生成回答")

        chain = RAG_PROMPT | self.llm | StrOutputParser()
        answer = chain.invoke({
            "context": context,
            "chat_history": history_text,
            "question": question,
        })
        logger.info("RAG 问答完成: retrieved=%s, sources=%s", len(retrieved_docs), len(sources))

        return {"answer": answer, "sources": sources}


_rag_instance = None


def get_rag_service() -> RAGService:
    """获取 RAG 服务单例实例。"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGService()
    return _rag_instance
