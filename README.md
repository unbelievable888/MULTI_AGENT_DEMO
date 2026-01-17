# 多源数据路由与推理规划器

一个基于Python和FastAPI的多源数据路由与推理规划系统，能够将复杂的用户查询拆解为多个子任务（如Text2SQL、RAG检索等），并融合结果生成最终分析报告。

## 项目简介

数据分析Agent中，用户的请求往往涉及多模态信息的综合推理。例如："结合Q3财报PDF中的市场策略章节，分析数据库中Q3销售额下降的原因"。

本项目设计了两种Agent架构：
- **Agent Planner架构**：将复杂问题拆解为多个子任务，并行执行独立任务，融合多源数据结果生成最终回答
- **LangGraph Agent架构**：基于LangGraph框架构建的工作流，支持更复杂的任务编排和状态管理

## 技术栈

- **后端框架**: FastAPI
- **LLM客户端**: OpenAI API (AsyncOpenAI)
- **前端**: HTML + JavaScript (原生)
- **工作流框架**: LangGraph (用于LangGraph Agent实现)
- **Python版本**: 3.9+

## 项目结构

```
MULTI_AGENT_DEMO/
├── main.py                      # 基础FastAPI服务器主文件
├── main_rag.py                  # RAG专用服务器入口
├── main_langgraph.py            # LangGraph版本服务器入口
├── templates/
│   └── index.html              # 前端页面
├── AgentPlannerServer/          # 核心业务逻辑模块
│   ├── __init__.py
│   ├── types.py                 # 数据类型定义
│   ├── llm_client.py            # LLM客户端封装
│   ├── agent_planner.py        # 任务规划器
│   ├── execution_engine.py     # 任务执行引擎
│   └── requirements.txt        # Python依赖包
├── LangGraphAgentServer/        # LangGraph实现模块
│   ├── __init__.py
│   ├── agent_types.py           # Agent类型定义
│   ├── agents.py                # 各类Agent实现
│   ├── graph_builder.py         # 工作流图构建器
│   ├── test_langgraph.py        # 测试文件
│   └── requirements.txt        # LangGraph依赖包
└── README.md
```

## 快速开始

### 1. 安装依赖

基础版本：
```bash
pip3 install -r AgentPlannerServer/requirements.txt
```

如需使用LangGraph版本：
```bash
pip3 install -r LangGraphAgentServer/requirements.txt
```

### 2. 配置环境变量（可选）

设置OpenAI API密钥（如果使用OpenAI服务）：

```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # 可选，默认值
```

或者创建 `.env` 文件：

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 3. 启动服务器

基础版本：
```bash
python3 main.py
```

RAG专用版本：
```bash
python3 main_rag.py
```

LangGraph版本：
```bash
python3 main_langgraph.py
```

服务器将在 `http://0.0.0.0:8000` 启动。

### 4. 访问前端页面

在浏览器中打开：
- `http://localhost:8000` 或
- `http://127.0.0.1:8000`

## API接口

### POST /analyze

分析接口，接收用户查询并返回执行计划和结果。

**请求体**:
```json
{
  "query": "结合Q3财报PDF中的市场策略章节，分析数据库中Q3销售额下降的原因"
}
```

**响应**:
```json
{
  "success": true,
  "plan": {
    "planId": "plan_xxx",
    "tasks": [
      {
        "id": 1,
        "tool": "Text2SQL",
        "description": "查询Q3销售额数据",
        "subQuery": "...",
        "dependencies": []
      },
      {
        "id": 2,
        "tool": "RAG",
        "description": "检索Q3财报PDF中的市场策略章节",
        "subQuery": "...",
        "dependencies": []
      },
      {
        "id": 3,
        "tool": "Final_Synthesis",
        "description": "综合分析结果",
        "subQuery": "...",
        "dependencies": [1, 2]
      }
    ]
  },
  "finalAnswer": "根据数据分析结果...",
  "message": null
}
```

### GET /health

健康检查接口。

**响应**:
```json
{
  "status": "ok"
}
```

### GET /

返回前端页面或API信息。

## 核心模块说明

### AgentPlannerServer

#### AgentPlannerServer.types

定义数据类型：
- `TaskTool`: 任务工具枚举（Text2SQL、RAG、Final_Synthesis）
- `AnalysisTask`: 分析任务模型
- `ExecutionPlan`: 执行计划模型

#### AgentPlannerServer.llm_client

LLM客户端封装，支持：
- 异步调用OpenAI API
- 系统提示和用户提示
- JSON格式响应

#### AgentPlannerServer.agent_planner

任务规划器，负责：
- 接收用户查询
- 使用LLM将查询拆解为任务列表
- 返回结构化的执行计划

#### AgentPlannerServer.execution_engine

执行引擎，负责：
- 并行执行独立任务（无依赖任务）
- 模拟Text2SQL和RAG检索
- 聚合所有任务结果
- 生成最终分析报告

### LangGraphAgentServer

#### LangGraphAgentServer.agent_types

定义LangGraph Agent类型和状态：
- 各种Agent角色的类型定义
- 工作流状态和消息格式

#### LangGraphAgentServer.agents

实现各类专用Agent：
- 规划Agent：负责任务分解和规划
- 执行Agent：执行特定类型的任务
- 综合Agent：整合多个任务结果

#### LangGraphAgentServer.graph_builder

工作流图构建器，负责：
- 定义Agent之间的工作流
- 设置条件分支和状态转换
- 构建完整的执行图

## 使用示例

### 前端使用

1. 打开 `http://localhost:8000`
2. 在输入框中输入分析请求
3. 点击"开始分析"按钮
4. 查看执行计划和最终分析结果

### API调用示例

基础版本：
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"query": "分析Q3销售额下降的原因"}'
```

LangGraph版本：
```bash
curl -X POST http://localhost:8000/analyze_langgraph \
  -H "Content-Type: application/json" \
  -d '{"query": "分析Q3销售额下降的原因"}'
```

## 开发说明

### 扩展任务类型

在 `AgentPlannerServer/types.py` 中添加新的 `TaskTool` 枚举值，并在 `execution_engine.py` 中实现对应的执行逻辑。

对于LangGraph版本，需要在 `LangGraphAgentServer/agent_types.py` 中添加新的Agent类型，并在 `agents.py` 中实现对应的Agent逻辑。

### 接入真实数据源

修改 `execution_engine.py` 中的：
- `_execute_text2sql()`: 接入真实数据库
- `_execute_rag()`: 接入真实RAG系统

对于LangGraph版本，修改 `LangGraphAgentServer/agents.py` 中对应的Agent实现。

### 自定义LLM服务

修改 `llm_client.py` 中的 `AsyncOpenAI` 配置，或替换为其他LLM服务提供商。

## 版本对比

| 特性 | 基础版本 (main.py) | RAG版本 (main_rag.py) | LangGraph版本 (main_langgraph.py) |
|------|-------------------|---------------------|--------------------------------|
| 任务规划 | ✅ | ✅ | ✅ |
| 并行执行 | ✅ | ✅ | ✅ |
| RAG检索 | 模拟 | 真实实现 | ✅ |
| 工作流编排 | 简单 | 简单 | 高级（状态管理） |
| 条件分支 | ❌ | ❌ | ✅ |
| 错误恢复 | 基础 | 基础 | 高级 |
| 适用场景 | 简单查询 | 文档分析 | 复杂推理链 |

## 注意事项

1. **API密钥**: 确保设置了正确的OpenAI API密钥，否则LLM调用会失败
2. **端口占用**: 默认使用8000端口，如被占用请修改对应主文件中的端口配置
3. **CORS配置**: 生产环境建议修改主文件中的CORS配置，限制允许的源
4. **错误处理**: 当前版本包含基本的错误处理，生产环境建议添加更详细的日志和监控
5. **LangGraph依赖**: LangGraph版本需要安装额外的依赖，请确保正确安装

## 许可证

MIT License
