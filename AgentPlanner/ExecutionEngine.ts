import { LLMClient } from "./LLMClient";
import { AnalysisTask, ExecutionPlan, TaskTool } from "./types";


const MOCK_DATA = {
    SQL: {
        query: "SELECT region, product_line, SUM(revenue) as rev, (rev - prev_rev)/prev_rev as growth FROM sales_q3 GROUP BY 1, 2 ORDER BY growth ASC LIMIT 3",
        result: [
            { region: "华东区", product: "旗舰系列手机", growth: "-28.4%", impact: "High" },
            { region: "华东区", product: "智能穿戴", growth: "-12.1%", impact: "Mid" },
            { region: "华中区", product: "旗舰系列手机", growth: "-5.2%", impact: "Low" }
        ]
    },
    RAG: {
        query: "检索 Q3 华东区市场策略变更及供应链调整",
        result: "【文档引用 P14】由于 Q3 期间华东大区启动‘合作伙伴优化计划’，导致 35% 的核心分销商处于合同重签期，部分门店出现 2-3 周的断货。同时，上海物流中心升级导致旗舰系列周转率下降。"
    }
};

/** 执行任务引擎 */
export class ExecutionEngine {
    private resultsStore: Map<number, any> = new Map();

    constructor(private client: LLMClient) { }

    async run(plan: ExecutionPlan): Promise<string | undefined> {
        const independentTasks = plan.tasks.filter(t => t.dependencies.length === 0);
        await Promise.all(independentTasks.map(async (task) => {
            if (task.tool === TaskTool.Text2SQL) {
                this.resultsStore.set(task.id, await this.executeText2SQL(task.subQuery));
            } else if (task.tool === TaskTool.RAG) {
                this.resultsStore.set(task.id, await this.executeRAG(task.subQuery));
            }
        }));

        const synthesisTask = plan.tasks.find(t => t.tool === TaskTool.Final_Synthesis);
        if (!synthesisTask) return "规划中缺失合成节点";

        return await this.synthesize(synthesisTask);
    }

    // 模拟 SQL
    private async executeText2SQL(query: string) {
        return MOCK_DATA.SQL.result;
    }

    // 模拟 RAG
    private async executeRAG(query: string) {
        const res = MOCK_DATA.RAG.result;
        return res ?? '';
    }

    // 聚合
    private async synthesize(task: AnalysisTask): Promise<string|undefined> {
        const allResults = Array.from(this.resultsStore.entries())
            .map(([id, res]) => `任务 ${id} 结果: ${JSON.stringify(res)}`)
            .join("\n");

        const prompt = `
      基于以下多源数据分析结果，回答用户问题: "${task.description}"
      执行上下文:
      ${allResults}
    `;

        const systemPrompt = "你是一个深度的业务逻辑分析师。请结合数据结果和文档背景，输出一份客观、详尽的分析报告。";
       return;
        // return await this.client.ask(prompt, systemPrompt);
    }
}