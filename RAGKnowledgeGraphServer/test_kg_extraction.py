"""
测试知识图谱提取功能

使用test_document.md作为测试文档
"""
import asyncio
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from RAGKnowledgeGraphServer.llm_client import LLMClient
from RAGKnowledgeGraphServer.kg_extractor import KnowledgeGraphExtractor
from RAGKnowledgeGraphServer.knowledge_graph import KnowledgeGraphRAG


async def test_kg_extraction():
    """测试知识图谱提取"""
    # 初始化LLM客户端
    client = LLMClient()
    
    # 读取测试文档
    document_path = os.path.join(os.path.dirname(__file__), "test_document.md")
    with open(document_path, 'r', encoding='utf-8') as f:
        document_text = f.read()
    
    print("=" * 80)
    print("测试知识图谱提取")
    print("=" * 80)
    print(f"\n文档长度: {len(document_text)} 字符")
    print(f"文档预览（前200字符）:\n{document_text[:200]}...\n")
    
    # 创建提取器
    extractor = KnowledgeGraphExtractor(client)
    
    print("开始提取知识图谱...")
    print("-" * 80)
    
    # 提取知识图谱
    knowledge_base = await extractor.extract_from_document(document_text)
    
    print(f"\n提取结果:")
    print(f"知识图谱项数: {len(knowledge_base)}")
    print("-" * 80)
    
    # 统计实体和关系
    entities = [item for item in knowledge_base if item.get("type") != "关系"]
    relations = [item for item in knowledge_base if item.get("type") == "关系"]
    
    print(f"\n实体数量: {len(entities)}")
    print(f"关系数量: {len(relations)}")
    print("\n提取的实体示例:")
    for i, entity in enumerate(entities[:5], 1):
        print(f"{i}. 【{entity.get('type', '')}】{entity.get('name', '')}")
        print(f"   描述: {entity.get('description', '')[:100]}...")
    
    print("\n提取的关系示例:")
    for i, relation in enumerate(relations[:5], 1):
        print(f"{i}. {relation.get('source', '')} -[{relation.get('relation_type', '')}]-> {relation.get('target', '')}")
        print(f"   描述: {relation.get('description', '')[:100]}...")
    
    # 测试加载到RAG系统
    print("\n" + "=" * 80)
    print("测试加载到RAG系统并进行检索")
    print("=" * 80)
    
    kg_rag = KnowledgeGraphRAG(client)
    await kg_rag.load_knowledge_base(knowledge_base)
    
    # 测试检索
    test_queries = [
        "华东大区的合作伙伴优化计划",
        "旗舰系列手机的销量下降原因",
        "上海物流中心升级的影响",
        "公司的高管团队",
    ]
    
    for query in test_queries:
        print(f"\n查询: {query}")
        print("-" * 80)
        result = await kg_rag.search(query, top_k=3)
        print(result)
        print()


if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: 未设置 OPENAI_API_KEY 环境变量")
        print("请设置环境变量: export OPENAI_API_KEY='your-api-key'")
        print("\n将继续运行，但LLM调用可能会失败")
    
    asyncio.run(test_kg_extraction())
