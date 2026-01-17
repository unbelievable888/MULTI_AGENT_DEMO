from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TaskTool(str, Enum):
    Text2SQL = 'Text2SQL'
    RAG = 'RAG'
    Final_Synthesis = 'Final_Synthesis'


class AgentState(BaseModel):
    """Agent状态定义 - LangGraph的状态"""
    query: str  # 用户查询
    tasks: List[Dict] = []  # 任务列表
    results: Dict[int, Any] = {}  # 任务执行结果
    final_answer: Optional[str] = None  # 最终答案
    current_step: str = "planning"  # 当前步骤
