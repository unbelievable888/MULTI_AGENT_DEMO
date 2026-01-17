"""
LangGraph图构建 - 定义Agent之间的执行流程
"""
from typing import Dict, Any

# LangGraph导入（根据版本可能有不同的导入路径）
try:
    from langgraph.graph import StateGraph, END
except ImportError:
    try:
        from langgraph.graph.graph import StateGraph, END
    except ImportError:
        # 如果都导入失败，在运行时会有提示
        StateGraph = None
        END = None

from .agents import planner_agent, text2sql_agent, rag_agent, synthesis_agent, should_continue


def build_agent_graph():
    """
    构建多Agent执行图
    
    流程:
    planner -> text2sql -> rag -> synthesis -> END
    """
    if StateGraph is None:
        raise ImportError("请安装langgraph: pip install langgraph")
    
    # 定义状态结构
    def create_initial_state(query: str) -> Dict[str, Any]:
        return {
            "query": query,
            "tasks": [],
            "results": {},
            "final_answer": None,
            "current_step": "planning"
        }
    
    # 创建状态图
    workflow = StateGraph(Dict[str, Any])
    
    # 添加节点（每个Agent）
    workflow.add_node("planner", planner_agent)
    workflow.add_node("text2sql", text2sql_agent)
    workflow.add_node("rag", rag_agent)
    workflow.add_node("synthesis", synthesis_agent)
    
    # 设置入口点
    workflow.set_entry_point("planner")
    
    # 添加条件边（根据状态决定下一步）
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "text2sql": "text2sql",
            "rag": "rag",
            "synthesis": "synthesis",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "text2sql",
        should_continue,
        {
            "rag": "rag",
            "synthesis": "synthesis",
            "end": END
        }
    )
    
    workflow.add_conditional_edges(
        "rag",
        should_continue,
        {
            "synthesis": "synthesis",
            "end": END
        }
    )
    
    workflow.add_edge("synthesis", END)
    
    # 编译图
    app = workflow.compile()
    
    return app, create_initial_state


async def run_agent_graph(query: str) -> Dict[str, Any]:
    """
    运行Agent图
    
    Args:
        query: 用户查询
    
    Returns:
        最终状态（包含final_answer）
    """
    app, create_initial_state = build_agent_graph()
    
    initial_state = create_initial_state(query)
    
    # 运行图
    final_state = await app.ainvoke(initial_state)
    
    return final_state
