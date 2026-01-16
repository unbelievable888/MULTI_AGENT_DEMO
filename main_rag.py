from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from RAGKnowledgeGraphServer.llm_client import LLMClient
from RAGKnowledgeGraphServer.agent_planner import AgentPlanner
from RAGKnowledgeGraphServer.execution_engine import ExecutionEngine
from RAGKnowledgeGraphServer.types import ExecutionPlan


app = FastAPI(title="基于知识图谱的RAG检索服务器", version="1.0.0")

# 配置CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str


class QueryResponse(BaseModel):
    """查询响应模型"""
    plan: Optional[ExecutionPlan] = None
    finalAnswer: Optional[str] = None
    success: bool
    message: Optional[str] = None


# 提供静态文件服务
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
if os.path.exists(templates_dir):
    @app.get("/")
    async def index():
        """根路径，返回前端页面"""
        return FileResponse(os.path.join(templates_dir, "index.html"))
else:
    @app.get("/")
    async def root():
        """根路径，返回API信息"""
        return {
            "name": "基于知识图谱的RAG检索服务器",
            "version": "1.0.0",
            "description": "使用知识图谱RAG检索方式的数据分析Agent"
        }


@app.post("/analyze", response_model=QueryResponse)
async def analyze(request: QueryRequest):
    """
    分析接口 - 使用知识图谱RAG检索
    
    接收用户查询，创建执行计划，执行任务并返回结果
    """
    try:
        # 初始化组件
        client = LLMClient()
        planner = AgentPlanner(client)
        engine = ExecutionEngine(client)
        
        # 创建计划
        plan = await planner.create_plan(request.query)
        
        if not plan:
            return QueryResponse(
                success=False,
                message="创建执行计划失败"
            )
        
        # 执行计划
        final_answer = await engine.run(plan)
        
        return QueryResponse(
            plan=plan,
            finalAnswer=final_answer,
            success=True
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
