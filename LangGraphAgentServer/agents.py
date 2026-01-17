"""
Agent节点定义 - 每个Agent负责不同的任务
"""
from typing import Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
import os
import json


# 模拟数据（实际应该从数据库/文档检索）
MOCK_DATA = {
    "SQL": {
        "result": [
            {"region": "华东区", "product": "旗舰系列手机", "growth": "-28.4%", "impact": "High"},
            {"region": "华东区", "product": "智能穿戴", "growth": "-12.1%", "impact": "Mid"},
            {"region": "华中区", "product": "旗舰系列手机", "growth": "-5.2%", "impact": "Low"}
        ]
    },
    "RAG": {
        "result": "【文档引用】由于 Q3 期间华东大区启动'合作伙伴优化计划'，导致 35% 的核心分销商处于合同重签期，部分门店出现 2-3 周的断货。同时，上海物流中心升级导致旗舰系列周转率下降。"
    }
}


def get_llm():
    """获取LangChain的LLM实例"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.2,
        openai_api_key=api_key,
        openai_api_base=base_url,
    )


async def planner_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    规划Agent - 将用户查询拆解为任务列表
    """
    query = state.get("query", "")
    llm = get_llm()
    
    system_prompt = """你是一个数据分析专家。请将用户请求拆解为任务列表。

可用的工具类型（tool字段只能是以下三种之一）：
1. "Text2SQL" - 用于数据库查询，将自然语言转换为SQL查询
2. "RAG" - 用于文档检索，从知识库中检索相关信息
3. "Final_Synthesis" - 用于综合所有结果，生成最终分析报告

必须返回 JSON 格式。
JSON Schema: 
{ 
  "planId": "string", 
  "tasks": [
    { "id": 1, "tool": "Text2SQL", "description": "任务描述", "subQuery": "子查询", "dependencies": [] }
  ] 
}

注意事项：
- tool字段必须是 "Text2SQL"、"RAG" 或 "Final_Synthesis" 之一
- 如果有多个任务，Final_Synthesis 应该放在最后，并且依赖前面的任务
- dependencies 字段是数组，包含该任务依赖的其他任务ID"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"用户查询: {query}")
    ]
    
    response = await llm.ainvoke(messages)
    response_text = response.content
    
    try:
        plan_dict = json.loads(response_text)
        tasks = plan_dict.get("tasks", [])
        
        return {
            "tasks": tasks,
            "current_step": "execution"
        }
    except Exception as e:
        print(f"规划Agent失败: {e}")
        return {
            "tasks": [],
            "current_step": "error"
        }


async def text2sql_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Text2SQL Agent - 执行SQL查询任务
    """
    tasks = state.get("tasks", [])
    results = state.get("results", {})
    
    # 找到所有Text2SQL任务
    sql_tasks = [task for task in tasks if task.get("tool") == "Text2SQL"]
    
    for task in sql_tasks:
        task_id = task.get("id")
        if task_id not in results:
            # 模拟SQL执行（实际应该连接到数据库）
            result = MOCK_DATA["SQL"]["result"]
            results[task_id] = {
                "task_id": task_id,
                "tool": "Text2SQL",
                "result": result
            }
            print(f"✅ Text2SQL Agent 完成任务 {task_id}: {len(result)} 条记录")
    
    return {"results": results}


async def rag_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    RAG Agent - 执行文档检索任务
    """
    tasks = state.get("tasks", [])
    results = state.get("results", {})
    
    # 找到所有RAG任务
    rag_tasks = [task for task in tasks if task.get("tool") == "RAG"]
    
    for task in rag_tasks:
        task_id = task.get("id")
        if task_id not in results:
            # 模拟RAG检索（实际应该连接到向量数据库）
            result = MOCK_DATA["RAG"]["result"]
            results[task_id] = {
                "task_id": task_id,
                "tool": "RAG",
                "result": result
            }
            print(f"✅ RAG Agent 完成任务 {task_id}: {len(result)} 字符")
    
    return {"results": results}


async def synthesis_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    综合Agent - 聚合所有结果并生成最终答案
    """
    query = state.get("query", "")
    tasks = state.get("tasks", [])
    results = state.get("results", {})
    
    llm = get_llm()
    
    # 构建所有结果文本
    all_results = []
    for task in tasks:
        task_id = task.get("id")
        if task_id in results:
            result_info = results[task_id]
            all_results.append(
                f"任务 {task_id} ({result_info['tool']}): {result_info['result']}"
            )
    
    results_text = "\n".join(all_results)
    
    system_prompt = "你是一个深度的业务逻辑分析师。请结合数据结果和文档背景，输出一份客观、详尽的分析报告。"
    
    prompt = f"""
基于以下多源数据分析结果，回答用户问题: "{query}"

执行上下文:
{results_text}
"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    
    response = await llm.ainvoke(messages)
    final_answer = response.content
    
    return {
        "final_answer": final_answer,
        "current_step": "completed"
    }


def should_continue(state: Dict[str, Any]) -> str:
    """
    路由函数 - 决定下一步执行哪个Agent
    """
    current_step = state.get("current_step", "planning")
    tasks = state.get("tasks", [])
    results = state.get("results", {})
    
    if current_step == "planning":
        return "planner"
    elif current_step == "execution":
        # 检查是否有未执行的任务
        sql_tasks = [t for t in tasks if t.get("tool") == "Text2SQL"]
        rag_tasks = [t for t in tasks if t.get("tool") == "RAG"]
        synthesis_tasks = [t for t in tasks if t.get("tool") == "Final_Synthesis"]
        
        # 检查Text2SQL任务是否完成
        sql_done = all(t.get("id") in results for t in sql_tasks)
        # 检查RAG任务是否完成
        rag_done = all(t.get("id") in results for t in rag_tasks)
        
        if sql_tasks and not sql_done:
            return "text2sql"
        elif rag_tasks and not rag_done:
            return "rag"
        elif synthesis_tasks:
            return "synthesis"
        else:
            return "end"
    elif current_step == "completed":
        return "end"
    else:
        return "end"
