from enum import Enum
from typing import List
from pydantic import BaseModel


class TaskTool(str, Enum):
    Text2SQL = 'Text2SQL'
    RAG = 'RAG'
    Final_Synthesis = 'Final_Synthesis'


class AnalysisTask(BaseModel):
    id: int
    tool: TaskTool
    description: str
    subQuery: str
    dependencies: List[int]


class ExecutionPlan(BaseModel):
    planId: str
    tasks: List[AnalysisTask]

