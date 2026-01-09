import { LLMClient } from "./LLMClient";
import { ExecutionPlan } from "./types";

/** 任务规划 */
export class AgentPlanner {
    constructor(private client: LLMClient) {}

    async createPlan(userQuery: string): Promise<ExecutionPlan | undefined> {
    const systemPrompt = `你是一个数据分析专家。请将用户请求拆解为任务列表。
    必须返回 JSON 格式。
    JSON Schema 示例: 
    { 
      "planId": "string", 
      "tasks": [
        { "id": 1, "tool": "Text2SQL", "description": "...", "subQuery": "...", "dependencies": [] }
      ] 
    }`;

    const responseText = await this.client.ask(userQuery, systemPrompt, true);
   return JSON.parse(responseText) as ExecutionPlan;
  }
}