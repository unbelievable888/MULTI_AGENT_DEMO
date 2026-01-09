import React, { useState } from "react";
import { main } from "../../AgentPlanner";
import { ExecutionPlan } from "../../AgentPlanner/types";

interface AgentButtonProps {
  onResult: (plan: ExecutionPlan, finalAnswer: string) => void;
  loading: boolean;
  setLoading: (isLoading: boolean) => void;
}

const AgentButton: React.FC<AgentButtonProps> = ({
  onResult,
  loading,
  setLoading,
}) => {
  const [query, setQuery] = useState<string>(
    "结合Q3财报PDF中的市场策略章节，分析数据库中Q3销售额下降的原因"
  );

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const result = await main(query);
      if (result?.finalAnswer && result.plan) {
        onResult(result.plan, result.finalAnswer);
      }
    } catch (error) {
      console.error("执行失败:", error);
      alert(
        `执行失败: ${error instanceof Error ? error.message : String(error)}`
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="form-group">
        <label
          htmlFor="query"
          style={{ display: "block", marginBottom: "8px", fontWeight: "bold" }}
        >
          输入分析请求:
        </label>
        <textarea
          id="query"
          className="query-input"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          placeholder="输入分析请求..."
          style={{
            width: "100%",
            padding: "10px",
            borderRadius: "4px",
            border: "1px solid #ddd",
          }}
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading}
        style={{
          backgroundColor: loading ? "#bae7ff" : "#1890ff",
          color: "white",
          border: "none",
          padding: "10px 20px",
          borderRadius: "4px",
          fontSize: "16px",
          cursor: loading ? "not-allowed" : "pointer",
          display: "block",
          margin: "20px 0",
          width: "100%",
          transition: "background-color 0.3s",
        }}
      >
        {loading ? "正在分析中..." : "开始分析"}
      </button>
    </div>
  );
};

export default AgentButton;
