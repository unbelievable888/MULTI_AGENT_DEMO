"""
测试LangGraph多Agent系统
"""
import asyncio
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LangGraphAgentServer.graph_builder import run_agent_graph


async def test_langgraph():
    """测试LangGraph多Agent流程"""
    print("=" * 80)
    print("测试 LangGraph 多Agent系统")
    print("=" * 80)
    print()
    
    # 测试查询
    test_query = "结合Q3财报PDF中的市场策略章节，分析数据库中Q3销售额下降的原因"
    
    print(f"📝 测试查询: {test_query}")
    print()
    print("开始执行多Agent流程...")
    print("-" * 80)
    
    try:
        # 运行LangGraph
        final_state = await run_agent_graph(test_query)
        
        print()
        print("=" * 80)
        print("✅ 执行完成！")
        print("=" * 80)
        print()
        
        # 显示结果
        print("📋 执行计划:")
        tasks = final_state.get("tasks", [])
        for task in tasks:
            print(f"  任务 {task.get('id')}: {task.get('tool')} - {task.get('description')}")
        
        print()
        print("📊 执行结果:")
        results = final_state.get("results", {})
        for task_id, result in results.items():
            print(f"  任务 {task_id} ({result.get('tool')}):")
            if isinstance(result.get('result'), list):
                print(f"    {len(result.get('result'))} 条记录")
            else:
                print(f"    {result.get('result')[:100]}...")
        
        print()
        print("📄 最终答案:")
        print("-" * 80)
        final_answer = final_state.get("final_answer", "无结果")
        print(final_answer)
        
        return final_state
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    # 检查API密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ 警告: 未设置 OPENAI_API_KEY 环境变量")
        print("请设置环境变量: export OPENAI_API_KEY='your-api-key'")
        print("       export OPENAI_BASE_URL='https://oneapi.qunhequnhe.com/v1/'")
        print()
    
    asyncio.run(test_langgraph())
