from typing import Any, Optional
from .llm_client import LLMClient
from .types import ExecutionPlan, AnalysisTask, TaskTool


# 模拟数据
MOCK_DATA = {
    "SQL": {
        "query": "SELECT region, product_line, SUM(revenue) as rev, (rev - prev_rev)/prev_rev as growth FROM sales_q3 GROUP BY 1, 2 ORDER BY growth ASC LIMIT 3",
        "result": [
            {"region": "华东区", "product": "旗舰系列手机", "growth": "-28.4%", "impact": "High"},
            {"region": "华东区", "product": "智能穿戴", "growth": "-12.1%", "impact": "Mid"},
            {"region": "华中区", "product": "旗舰系列手机", "growth": "-5.2%", "impact": "Low"}
        ]
    },
    "RAG": {
        "query": "检索 Q3 华东区市场策略变更及供应链调整",
        "result": "【文档引用 P14】由于 Q3 期间华东大区启动'合作伙伴优化计划'，导致 35% 的核心分销商处于合同重签期，部分门店出现 2-3 周的断货。同时，上海物流中心升级导致旗舰系列周转率下降。"
    }
}


class ExecutionEngine:
    """执行任务引擎"""
    
    def __init__(self, client: LLMClient):
        self.client = client
        self.results_store: dict[int, Any] = {}
    
    async def run(self, plan: ExecutionPlan) -> Optional[str]:
        """
        执行计划中的所有任务
        
        Args:
            plan: 执行计划
        
        Returns:
            最终合成结果，如果失败则返回None
        """
        # 执行无依赖的独立任务
        independent_tasks = [task for task in plan.tasks if len(task.dependencies) == 0]
        
        # 并行执行独立任务
        import asyncio
        await asyncio.gather(*[
            self._execute_task(task) for task in independent_tasks
        ])
        
        # 查找合成任务
        synthesis_task = next(
            (task for task in plan.tasks if task.tool == TaskTool.Final_Synthesis),
            None
        )
        
        if not synthesis_task:
            return "规划中缺失合成节点"
        
        return await self._synthesize(synthesis_task)
    
    async def _execute_task(self, task: AnalysisTask):
        """执行单个任务"""
        if task.tool == TaskTool.Text2SQL:
            result = await self._execute_text2sql(task.subQuery)
            self.results_store[task.id] = result
        elif task.tool == TaskTool.RAG:
            result = await self._execute_rag(task.subQuery)
            self.results_store[task.id] = result
    
    async def _execute_text2sql(self, query: str):
        """模拟SQL执行"""
        # 这里可以接入真实的数据库查询
        return MOCK_DATA["SQL"]["result"]
    
    async def _execute_rag(self, query: str):
        """模拟RAG检索"""
        # 这里可以接入真实的RAG系统
        return MOCK_DATA["RAG"]["result"]
    
    async def _synthesize(self, task: AnalysisTask) -> Optional[str]:
        """
        聚合所有任务结果并生成最终分析
        
        Args:
            task: 合成任务
        
        Returns:
            最终分析结果
        """
        all_results = "\n".join([
            f"任务 {task_id} 结果: {result}"
            for task_id, result in self.results_store.items()
        ])
        
        prompt = f"""
基于以下多源数据分析结果，回答用户问题: "{task.description}"
执行上下文:
{all_results}
"""
        
        system_prompt = "你是一个深度的业务逻辑分析师。请结合数据结果和文档背景，输出一份客观、详尽的分析报告。"
        
        try:
            return await self.client.ask(prompt, system_prompt)
        except Exception as e:
            print(f"合成失败: {e}")
            return None

