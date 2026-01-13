from typing import Optional
from .llm_client import LLMClient
from .types import ExecutionPlan


class AgentPlanner:
    """任务规划器"""
    
    def __init__(self, client: LLMClient):
        self.client = client
    
    async def create_plan(self, user_query: str) -> Optional[ExecutionPlan]:
        """
        根据用户查询创建执行计划
        
        Args:
            user_query: 用户查询字符串
        
        Returns:
            执行计划对象，如果失败则返回None
        """
        system_prompt = """你是一个数据分析专家。请将用户请求拆解为任务列表。
必须返回 JSON 格式。
JSON Schema 示例: 
{ 
  "planId": "string", 
  "tasks": [
    { "id": 1, "tool": "Text2SQL", "description": "...", "subQuery": "...", "dependencies": [] }
  ] 
}"""
        
        try:
            response_text = await self.client.ask(user_query, system_prompt, is_json=True)
            import json
            plan_dict = json.loads(response_text)
            return ExecutionPlan(**plan_dict)
        except Exception as e:
            print(f"创建计划失败: {e}")
            return None

