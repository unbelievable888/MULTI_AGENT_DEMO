"""
知识图谱提取器 - 从文档中提取实体和关系

主流方法说明：
1. 文本预处理：文档分块，将大文档拆分为小段落
2. 实体识别（NER）：识别实体（人名、地名、组织等）
3. 关系抽取（RE）：识别实体间的关系，形成SPO三元组
4. 实体标准化：统一同一实体的不同表述
5. 关系推断：发现隐含关系
6. 知识图谱构建：将实体和关系组织成图结构

本模块使用LLM进行自动化提取（主流方法之一）
"""
from typing import List, Dict, Optional
import json
from .llm_client import LLMClient


class KnowledgeGraphExtractor:
    """从文档中提取知识图谱"""
    
    def __init__(self, client: LLMClient):
        self.client = client
    
    async def extract_from_document(self, document_text: str, chunk_size: int = 2000) -> List[Dict]:
        """
        从文档中提取知识图谱
        
        Args:
            document_text: 文档文本
            chunk_size: 文本分块大小
        
        Returns:
            提取的实体和关系列表
        """
        # 1. 文本分块
        chunks = self._split_text(document_text, chunk_size)
        
        # 2. 对每个文本块进行实体和关系提取
        all_entities = []
        all_relations = []
        
        for chunk in chunks:
            entities, relations = await self._extract_from_chunk(chunk)
            all_entities.extend(entities)
            all_relations.extend(relations)
        
        # 3. 实体标准化（去重和合并）
        standardized_entities = self._standardize_entities(all_entities)
        
        # 4. 构建知识图谱数据
        knowledge_base = self._build_knowledge_base(standardized_entities, all_relations)
        
        return knowledge_base
    
    def _split_text(self, text: str, chunk_size: int) -> List[str]:
        """文本分块"""
        # 简单的按句号和段落分块
        sentences = text.split('。')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += sentence + "。"
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _extract_from_chunk(self, chunk: str) -> tuple[List[Dict], List[Dict]]:
        """
        从文本块中提取实体和关系
        
        使用LLM进行提取（主流方法之一）
        """
        system_prompt = """你是一个知识图谱提取专家。请从给定的文本中提取实体和关系。
        
必须返回JSON格式，包含以下结构：
{
  "entities": [
    {
      "id": "entity_1",
      "type": "实体类型（如：公司、产品、事件、地点等）",
      "name": "实体名称",
      "description": "实体描述",
      "properties": {}
    }
  ],
  "relations": [
    {
      "source": "源实体ID",
      "target": "目标实体ID",
      "relation_type": "关系类型（如：影响、包含、发生等）",
      "description": "关系描述"
    }
  ]
}"""
        
        prompt = f"请从以下文本中提取实体和关系：\n\n{chunk}"
        
        try:
            response = await self.client.ask(prompt, system_prompt, is_json=True)
            data = json.loads(response)
            
            entities = data.get("entities", [])
            relations = data.get("relations", [])
            
            return entities, relations
        except Exception as e:
            print(f"提取失败: {e}")
            return [], []
    
    def _standardize_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        实体标准化：去重和合并同名实体
        
        主流方法包括：
        - 字符串相似度匹配
        - 同义词识别
        - 实体链接（Entity Linking）
        """
        # 简单的基于名称的去重
        entity_map = {}
        
        for entity in entities:
            name = entity.get("name", "")
            entity_id = entity.get("id", "")
            
            # 如果已存在同名实体，合并属性
            if name in entity_map:
                existing = entity_map[name]
                # 合并描述
                if entity.get("description") and entity.get("description") not in existing.get("description", ""):
                    existing["description"] += f"；{entity.get('description')}"
                # 合并属性
                existing["properties"].update(entity.get("properties", {}))
            else:
                entity_map[name] = entity.copy()
        
        return list(entity_map.values())
    
    def _build_knowledge_base(self, entities: List[Dict], relations: List[Dict]) -> List[Dict]:
        """构建知识图谱数据结构"""
        knowledge_base = []
        
        # 添加实体
        for entity in entities:
            knowledge_base.append({
                "id": entity.get("id", f"entity_{len(knowledge_base)}"),
                "type": entity.get("type", "实体"),
                "name": entity.get("name", ""),
                "description": entity.get("description", ""),
                "properties": entity.get("properties", {})
            })
        
        # 添加关系
        entity_id_map = {e.get("name"): e.get("id") for e in entities}
        
        for i, relation in enumerate(relations):
            source_name = relation.get("source")
            target_name = relation.get("target")
            
            # 通过名称找到实体ID
            source_id = entity_id_map.get(source_name, source_name)
            target_id = entity_id_map.get(target_name, target_name)
            
            knowledge_base.append({
                "id": f"relation_{i}",
                "type": "关系",
                "source": source_id,
                "target": target_id,
                "relation_type": relation.get("relation_type", ""),
                "description": relation.get("description", "")
            })
        
        return knowledge_base
    
    async def extract_from_file(self, file_path: str) -> List[Dict]:
        """
        从文件中提取知识图谱
        
        支持的文件格式：.txt, .md等文本文件
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return await self.extract_from_document(content)
        except Exception as e:
            print(f"读取文件失败: {e}")
            return []
