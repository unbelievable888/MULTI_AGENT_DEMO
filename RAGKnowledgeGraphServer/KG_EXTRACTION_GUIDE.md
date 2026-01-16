# 知识图谱提取指南

## 为什么当前实现使用写死的数据？

当前的 `initialize_knowledge_base()` 方法使用写死的数据，这是为了：
1. **演示目的**：作为示例代码，展示知识图谱的结构和RAG检索的工作方式
2. **快速启动**：不需要外部数据源即可运行和测试
3. **简化实现**：专注于展示RAG检索的核心逻辑

## 主流文档转知识图谱的方法

将文档转换为知识图谱的主流方法包括以下步骤：

### 1. **文本预处理与分块**
- 将大型文档拆分为较小的段落或句子
- 处理格式、去除噪音
- 保持语义完整性

### 2. **实体识别（NER - Named Entity Recognition）**
从文本中识别实体，如：
- **人物**：人名
- **组织**：公司、机构
- **地点**：地名、位置
- **事件**：活动、事件
- **产品**：商品、服务
- **时间**：日期、时间段

### 3. **关系抽取（RE - Relation Extraction）**
识别实体之间的关系，形成**SPO三元组**（Subject-Predicate-Object）：
- 主语（实体1）
- 谓语（关系类型）
- 宾语（实体2）

例如："华东大区启动合作伙伴优化计划" → (华东大区, 启动, 合作伙伴优化计划)

### 4. **实体标准化（Entity Normalization）**
- 统一同一实体的不同表述（如："华东大区"和"华东区"）
- 实体链接（Entity Linking）：将提及链接到标准实体
- 同义词识别和合并

### 5. **关系推断（Relation Inference）**
- 发现图谱中不连续部分之间的关系
- 通过图的遍历和推理发现隐含关系
- 使知识图谱更完整

### 6. **知识图谱构建**
- 将提取的实体和关系组织成图结构
- 存储在图数据库中（如Neo4j、ArangoDB等）
- 或存储在向量数据库中（如Milvus、Pinecone等）用于RAG检索

## 主流技术方案

### 方案1：基于LLM的提取（推荐，易于实现）
**优点**：
- 利用LLM强大的理解能力
- 无需训练专门的NER/RE模型
- 灵活性高，易于调整

**实现方式**：
- 使用GPT-4、Claude等大模型
- 通过Prompt工程指导提取
- 返回结构化的实体和关系

**适用场景**：
- 快速原型开发
- 中小规模知识图谱
- 对准确率要求不是极高的场景

### 方案2：传统NLP管道（传统方法）
**工具链**：
- **NER**：spaCy、Stanford NER、BERT-NER
- **RE**：OpenIE、关系分类模型
- **实体链接**：Wikipedia API、知识库对齐

**优点**：
- 可控性强
- 对特定领域可以fine-tune
- 计算资源需求相对较低

**缺点**：
- 需要多个模型配合
- 错误传播问题
- 开发复杂度高

### 方案3：端到端神经网络（学术界方法）
**模型**：
- 联合抽取模型（Joint Extraction）
- 图神经网络（GNN）进行关系推理
- T5/BART等序列到序列模型

**优点**：
- 端到端优化
- 在特定数据集上效果好

**缺点**：
- 需要大量标注数据
- 训练成本高
- 通用性相对较差

### 方案4：混合方法（生产环境推荐）
**组合**：
- LLM进行粗提取
- 规则/NLP模型进行精化
- 图数据库存储和查询
- 向量数据库用于RAG检索

## 本项目的实现方式

本项目提供了 `kg_extractor.py` 模块，展示了**基于LLM的提取方法**：

```python
from RAGKnowledgeGraphServer.kg_extractor import KnowledgeGraphExtractor

# 1. 从文档文本提取
extractor = KnowledgeGraphExtractor(llm_client)
knowledge_base = await extractor.extract_from_document(document_text)

# 2. 从文件提取
knowledge_base = await extractor.extract_from_file("document.txt")

# 3. 将提取的知识图谱加载到RAG系统
kg_rag = KnowledgeGraphRAG(llm_client)
kg_rag.load_knowledge_base(knowledge_base)
```

## 生产环境建议

1. **数据存储**：
   - 使用图数据库（Neo4j、ArangoDB）存储结构化知识
   - 使用向量数据库（Milvus、Weaviate）存储嵌入向量
   - 定期更新和增量构建

2. **质量控制**：
   - 实体标准化和去重
   - 关系验证
   - 置信度评分

3. **性能优化**：
   - 批量处理文档
   - 缓存嵌入向量
   - 增量更新策略

4. **集成方式**：
   - 图数据库查询（精确查询）
   - 向量相似度检索（语义检索）
   - 混合检索（结合两种方式）
