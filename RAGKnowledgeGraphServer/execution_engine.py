from typing import Any, Optional
from .llm_client import LLMClient
from .types import ExecutionPlan, AnalysisTask, TaskTool
from .knowledge_graph import KnowledgeGraphRAG


class ExecutionEngine:
    """执行任务引擎 - 使用知识图谱RAG检索"""
    
    def __init__(self, client: LLMClient):
        self.client = client
        self.results_store: dict[int, Any] = {}
        self.kg_rag = KnowledgeGraphRAG(client)
    
    async def run(self, plan: ExecutionPlan) -> Optional[str]:
        """
        执行计划中的所有任务
        
        Args:
            plan: 执行计划
        
        Returns:
            最终合成结果，如果失败则返回None
        """
        # 初始化知识图谱
        await self.kg_rag.initialize_knowledge_base()
        
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
        """模拟SQL执行（可以使用知识图谱增强）"""
        # 这里可以接入真实的数据库查询
        # 为了演示，我们也可以从知识图谱中检索相关数据
        kg_result = await self.kg_rag.search(query, top_k=2)
        
        # 模拟SQL结果（实际应该从数据库查询）
        result = {
            "query": query,
            "kg_context": kg_result,  # 添加知识图谱上下文
            "data": [
                {"region": "华东区", "product": "旗舰系列手机", "growth": "-28.4%", "impact": "High"},
                {"region": "华东区", "product": "智能穿戴", "growth": "-12.1%", "impact": "Mid"},
                {"region": "华中区", "product": "旗舰系列手机", "growth": "-5.2%", "impact": "Low"}
            ]
        }
        return result
    
    async def _execute_rag(self, query: str):
        """使用知识图谱RAG检索"""
        # 使用知识图谱进行RAG检索
        result = await self.kg_rag.search(query, top_k=5)
        return result
    
    async def _synthesize(self, task: AnalysisTask) -> Optional[str]:
        """
        聚合所有任务结果并生成最终分析
        
        Args:
            task: 合成任务
        
        Returns:
            最终分析结果
        """
        all_results = []
        for task_id, result in self.results_store.items():
            if isinstance(result, dict):
                # Text2SQL结果
                result_str = f"数据查询结果: {result.get('data', [])}\n"
                if result.get('kg_context'):
                    result_str += f"知识图谱上下文: {result.get('kg_context')}"
                all_results.append(f"任务 {task_id} 结果:\n{result_str}")
            else:
                # RAG检索结果
                all_results.append(f"任务 {task_id} 结果 (知识图谱检索):\n{result}")
        
        all_results_text = "\n".join(all_results)
        
        prompt = f"""
基于以下多源数据分析结果（包括知识图谱检索结果），回答用户问题: "{task.description}"

执行上下文:
{all_results_text}

请结合知识图谱中的实体关系和数据分析结果，输出一份客观、详尽的分析报告。
"""
        
        system_prompt = "你是一个深度的业务逻辑分析师。请结合知识图谱中的实体关系、数据分析结果和文档背景，输出一份客观、详尽的分析报告。"
        
        try:
            return await self.client.ask(prompt, system_prompt)
        except Exception as e:
            print(f"合成失败: {e}")
            return None
