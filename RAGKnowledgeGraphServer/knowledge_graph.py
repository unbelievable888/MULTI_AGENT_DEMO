from typing import List, Dict, Tuple
import numpy as np
from .llm_client import LLMClient


class KnowledgeGraphRAG:
    """基于知识图谱的RAG检索系统"""
    
    def __init__(self, client: LLMClient):
        self.client = client
        # 知识图谱数据存储：节点和关系
        self.knowledge_base: List[Dict] = []
        self.embeddings_cache: Dict[str, List[float]] = {}
        self._initialized = False
    
    async def initialize_knowledge_base(self):
        """
        初始化知识图谱数据
        
        注意：当前使用写死的数据作为示例。
        实际生产环境应该：
        1. 从图数据库（如Neo4j）加载
        2. 从文档中提取（使用kg_extractor.py）
        3. 从JSON/数据库文件加载
        """
        if self._initialized:
            return
        
        # 示例知识图谱数据（可以替换为真实的图数据库查询）
        # 详见 KG_EXTRACTION_GUIDE.md 了解如何从文档提取知识图谱
        self.knowledge_base = [
            {
                "id": "entity_1",
                "type": "公司",
                "name": "华东区",
                "description": "华东大区是公司重要的销售区域，覆盖上海、江苏、浙江等省份",
                "properties": {"region_code": "HD", "established_year": 2015}
            },
            {
                "id": "entity_2",
                "type": "产品",
                "name": "旗舰系列手机",
                "description": "公司核心产品线，面向高端市场",
                "properties": {"category": "手机", "price_range": "高端"}
            },
            {
                "id": "entity_3",
                "type": "事件",
                "name": "合作伙伴优化计划",
                "description": "Q3期间华东大区启动合作伙伴优化计划，导致35%的核心分销商处于合同重签期",
                "properties": {"time": "Q3", "impact": "高"}
            },
            {
                "id": "entity_4",
                "type": "事件",
                "name": "物流中心升级",
                "description": "上海物流中心升级导致旗舰系列周转率下降",
                "properties": {"location": "上海", "time": "Q3"}
            },
            {
                "id": "relation_1",
                "type": "关系",
                "source": "entity_1",
                "target": "entity_3",
                "relation_type": "发生",
                "description": "华东大区在Q3启动了合作伙伴优化计划"
            },
            {
                "id": "relation_2",
                "type": "关系",
                "source": "entity_1",
                "target": "entity_4",
                "relation_type": "包含",
                "description": "华东大区包含上海物流中心"
            },
            {
                "id": "relation_3",
                "type": "关系",
                "source": "entity_3",
                "target": "entity_2",
                "relation_type": "影响",
                "description": "合作伙伴优化计划影响了旗舰系列手机的销售"
            }
        ]
        
        # 为知识库生成嵌入向量
        await self._build_embeddings()
        self._initialized = True
    
    async def load_knowledge_base(self, knowledge_base: List[Dict]):
        """
        从外部加载知识图谱数据（如从文档提取的结果）
        
        Args:
            knowledge_base: 知识图谱数据列表（实体和关系）
        
        示例：
            from RAGKnowledgeGraphServer.kg_extractor import KnowledgeGraphExtractor
            
            extractor = KnowledgeGraphExtractor(llm_client)
            kg_data = await extractor.extract_from_document(document_text)
            await kg_rag.load_knowledge_base(kg_data)
        """
        self.knowledge_base = knowledge_base
        # 重新构建嵌入向量
        await self._build_embeddings()
        self._initialized = True
    
    async def _build_embeddings(self):
        """为知识库构建嵌入向量"""
        texts = []
        for item in self.knowledge_base:
            # 将实体/关系转换为检索文本
            if item["type"] == "关系":
                text = f"{item.get('description', '')} {item.get('relation_type', '')}"
            else:
                text = f"{item.get('name', '')} {item.get('description', '')}"
            texts.append(text)
        
        embeddings = await self.client.get_embeddings(texts)
        for i, item in enumerate(self.knowledge_base):
            self.embeddings_cache[item["id"]] = embeddings[i] if i < len(embeddings) else []
    
    async def search(self, query: str, top_k: int = 3) -> str:
        """
        基于向量相似度检索知识图谱
        
        Args:
            query: 查询字符串
            top_k: 返回最相关的k条结果
        
        Returns:
            检索到的相关知识图谱信息
        """
        if not self.knowledge_base:
            await self.initialize_knowledge_base()
        
        # 获取查询的嵌入向量
        query_embeddings = await self.client.get_embeddings([query])
        if not query_embeddings:
            return "无法生成查询嵌入向量"
        
        query_vector = query_embeddings[0]
        
        # 计算相似度
        similarities = []
        for item in self.knowledge_base:
            item_embedding = self.embeddings_cache.get(item["id"], [])
            if item_embedding:
                similarity = self._cosine_similarity(query_vector, item_embedding)
                similarities.append((similarity, item))
        
        # 排序并取top_k
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_results = similarities[:top_k]
        
        # 构建检索结果
        result_parts = []
        for similarity, item in top_results:
            if item["type"] == "关系":
                result_parts.append(
                    f"【关系】{item.get('description', '')} "
                    f"(来源: {item.get('source', '')}, 目标: {item.get('target', '')}, 相似度: {similarity:.3f})"
                )
            else:
                result_parts.append(
                    f"【{item.get('type', '实体')}】{item.get('name', '')}: {item.get('description', '')} "
                    f"(相似度: {similarity:.3f})"
                )
        
        # 如果检索到关系，尝试扩展相关实体
        expanded_entities = self._expand_related_entities(top_results)
        if expanded_entities:
            result_parts.append("\n【相关实体扩展】")
            result_parts.extend(expanded_entities)
        
        return "\n".join(result_parts) if result_parts else "未找到相关知识图谱信息"
    
    def _expand_related_entities(self, top_results: List[Tuple[float, Dict]]) -> List[str]:
        """扩展相关实体"""
        entity_ids = set()
        for _, item in top_results:
            if item["type"] == "关系":
                entity_ids.add(item.get("source"))
                entity_ids.add(item.get("target"))
            else:
                entity_ids.add(item.get("id"))
        
        expanded = []
        for item in self.knowledge_base:
            if item["id"] in entity_ids and item["type"] != "关系":
                # 查找与这些实体相关的关系
                for rel in self.knowledge_base:
                    if rel["type"] == "关系" and (
                        rel.get("source") == item["id"] or rel.get("target") == item["id"]
                    ):
                        expanded.append(f"- {item.get('name', '')} 通过 '{rel.get('relation_type', '')}' 关联: {rel.get('description', '')}")
                        break
        
        return expanded[:5]  # 限制扩展数量
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """计算余弦相似度"""
        vec1_np = np.array(vec1)
        vec2_np = np.array(vec2)
        
        dot_product = np.dot(vec1_np, vec2_np)
        norm1 = np.linalg.norm(vec1_np)
        norm2 = np.linalg.norm(vec2_np)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
