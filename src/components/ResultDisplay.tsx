import React, { useState } from 'react';
import { ExecutionPlan } from '../../AgentPlanner/types';

interface ResultDisplayProps {
  plan: ExecutionPlan | null;
  finalAnswer: string | null;
}

const ResultDisplay: React.FC<ResultDisplayProps> = ({ plan, finalAnswer }) => {
  const [activeTab, setActiveTab] = useState<'plan' | 'result'>('result');

  if (!plan && !finalAnswer) return null;

  return (
    <div className="result-container">
      <h2 style={{ borderBottom: '1px solid #eee', paddingBottom: '10px', color: '#1890ff' }}>执行结果</h2>
      
      <div className="tab-container">
        <div 
          className={`tab ${activeTab === 'result' ? 'active' : ''}`}
          onClick={() => setActiveTab('result')}
        >
          分析结果
        </div>
        <div 
          className={`tab ${activeTab === 'plan' ? 'active' : ''}`}
          onClick={() => setActiveTab('plan')}
        >
          执行计划
        </div>
      </div>
      
      <div className={`tab-content ${activeTab === 'result' ? 'active' : ''}`}>
        {finalAnswer ? (
          <div style={{ backgroundColor: '#f9f9f9', padding: '15px', borderRadius: '4px', marginTop: '10px' }}>
            <div dangerouslySetInnerHTML={{ __html: finalAnswer.replace(/\n/g, '<br/>') }} />
          </div>
        ) : (
          <div>尚未生成分析结果</div>
        )}
      </div>
      
      <div className={`tab-content ${activeTab === 'plan' ? 'active' : ''}`}>
        {plan ? (
          <div>
            <h3>计划ID: {plan.planId}</h3>
            <div>
              <h4>任务列表:</h4>
              {plan.tasks.map((task) => (
                <div 
                  key={task.id}
                  style={{ 
                    margin: '10px 0', 
                    padding: '15px', 
                    backgroundColor: getTaskColor(task.tool),
                    borderRadius: '4px'
                  }}
                >
                  <div><strong>任务ID:</strong> {task.id}</div>
                  <div><strong>工具:</strong> {task.tool}</div>
                  <div><strong>描述:</strong> {task.description}</div>
                  <div><strong>子查询:</strong> {task.subQuery}</div>
                  <div>
                    <strong>依赖:</strong> {task.dependencies.length > 0 
                      ? task.dependencies.join(', ') 
                      : '无依赖'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>尚未生成执行计划</div>
        )}
      </div>
    </div>
  );
};

// 根据任务类型返回不同的背景色
const getTaskColor = (tool: string): string => {
  switch (tool) {
    case 'Text2SQL':
      return '#e6f7ff'; // 浅蓝色
    case 'RAG':
      return '#f6ffed'; // 浅绿色
    case 'Final_Synthesis':
      return '#fff7e6'; // 浅黄色
    default:
      return '#f9f9f9'; // 默认灰色
  }
};

export default ResultDisplay;
