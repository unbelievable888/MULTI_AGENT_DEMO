from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os

from LangGraphAgentServer.graph_builder import run_agent_graph


app = FastAPI(title="基于LangGraph的多Agent调度服务器", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str


class QueryResponse(BaseModel):
    """查询响应模型"""
    finalAnswer: Optional[str] = None
    success: bool
    message: Optional[str] = None
    execution_state: Optional[dict] = None


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
            "name": "基于LangGraph的多Agent调度服务器",
            "version": "1.0.0",
            "description": "使用LangGraph实现的多Agent任务调度系统"
        }


@app.post("/analyze", response_model=QueryResponse)
async def analyze(request: QueryRequest):
    """
    分析接口 - 使用LangGraph调度多个Agent
    
    接收用户查询，通过LangGraph调度多个Agent执行任务并返回结果
    """
    try:
        # 使用LangGraph运行多Agent流程
        final_state = await run_agent_graph(request.query)
        
        return QueryResponse(
            finalAnswer=final_state.get("final_answer"),
            success=True,
            execution_state={
                "tasks": final_state.get("tasks", []),
                "results_count": len(final_state.get("results", {}))
            }
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"执行失败: {str(e)}")


@app.get("/health")
async def health():
    """健康检查接口"""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
