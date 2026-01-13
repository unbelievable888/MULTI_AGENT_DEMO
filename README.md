# 多源数据路由与推理规划器 (Multi-Agent Demo)

本系统可以处理涉及多模态信息综合推理的用户请求，将复杂问题拆解为"文档检索(RAG)"和"数据库查询(Text2SQL)"两个子任务，并融合两者的结果生成最终回答。

### 示例查询

```
结合Q3财报PDF中的市场策略章节，分析数据库中Q3销售额下降的原因
```

## 功能特点

- **任务规划**：使用LLM将用户查询拆解为结构化任务列表
- **多源数据处理**：支持文档检索(RAG)和数据库查询(Text2SQL)
- **结果合成**：融合多个数据源的结果生成综合分析
- **直观的用户界面**：提供友好的Web界面进行交互

## 技术架构

### 核心组件

- **AgentPlanner**：负责创建执行计划，将用户查询拆解为任务列表
- **ExecutionEngine**：执行计划中的任务，并合成最终结果
- **LLMClient**：与LLM API通信，处理自然语言请求和响应

### 技术栈

- TypeScript
- React
- OpenAI API
- Webpack

## 项目结构

```
MULTI_AGENT_DEMO/
├── AgentPlanner/               # 核心功能实现
│   ├── AgentPlanner.ts         # 任务规划器
│   ├── ExecutionEngine.ts      # 执行引擎
│   ├── LLMClient.ts            # LLM客户端
│   ├── index.ts                # 入口文件
│   └── types.ts                # 类型定义
├── src/                        # 前端UI实现
│   ├── components/             # React组件
│   │   ├── AgentButton.tsx     # 查询输入和提交按钮
│   │   └── ResultDisplay.tsx   # 结果展示组件
│   ├── index.html              # HTML模板
│   └── index.tsx               # React应用入口
├── package.json                # 项目依赖和脚本
├── tsconfig.json               # TypeScript配置
└── webpack.config.js           # Webpack配置
```

## 安装与使用

### 前提条件

- Node.js (建议使用v16或更高版本)
- npm (Node.js包管理器)
- OpenAI API密钥 (在LLMClient.ts中配置)

### 安装步骤

1. 克隆仓库
```bash
git clone https://your-repository-url/MULTI_AGENT_DEMO.git
cd MULTI_AGENT_DEMO
```

2. 安装依赖
```bash
npm install
```

3. 配置OpenAI API密钥
打开 `AgentPlanner/LLMClient.ts` 文件，将您的API密钥填入 `apiKey` 变量。

### 运行应用

启动开发服务器：
```bash
npm start
# 或
npm run dev
```

构建生产版本：
```bash
npm run build
```

## 使用方法

1. 访问 `http://localhost:8080`（或webpack配置的其他端口）
2. 在文本框中输入您的分析请求
3. 点击"开始分析"按钮
4. 查看分析结果和执行计划

## 工作流程

1. 用户提交查询请求
2. AgentPlanner将查询拆解为任务列表
3. ExecutionEngine执行各个任务：
   - 对于Text2SQL任务，生成并执行SQL查询
   - 对于RAG任务，检索相关文档信息
4. 最终合成任务融合所有结果，生成综合分析报告

## 注意事项

- 当前版本使用模拟数据，在实际应用中需要连接真实数据源
- 确保正确配置OpenAI API密钥以保证LLM功能正常工作

