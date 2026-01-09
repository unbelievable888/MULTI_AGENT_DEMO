import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import AgentButton from './components/AgentButton';
import ResultDisplay from './components/ResultDisplay';
import { ExecutionPlan } from '../AgentPlanner/types';

const App: React.FC = () => {
  const [loading, setLoading] = useState<boolean>(false);
  const [plan, setPlan] = useState<ExecutionPlan | null>(null);
  const [finalAnswer, setFinalAnswer] = useState<string | null>(null);

  const handleResult = (resultPlan: ExecutionPlan, resultAnswer: string) => {
    setPlan(resultPlan);
    setFinalAnswer(resultAnswer);
  };

  return (
    <div>
      <AgentButton 
        onResult={handleResult} 
        loading={loading} 
        setLoading={setLoading} 
      />
      
      {loading ? (
        <div style={{ textAlign: 'center', margin: '20px 0' }}>
          <div style={{ fontSize: '18px', color: '#1890ff', marginBottom: '10px' }}>
            正在执行分析...
          </div>
          <div style={{ color: '#666' }}>
            请耐心等待，LLM正在处理您的请求
          </div>
        </div>
      ) : (
        <ResultDisplay plan={plan} finalAnswer={finalAnswer} />
      )}
    </div>
  );
};

// 渲染React应用
const rootElement = document.getElementById('root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  console.error('找不到root元素');
}
