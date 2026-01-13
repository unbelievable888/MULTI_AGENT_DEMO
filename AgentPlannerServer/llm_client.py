from openai import AsyncOpenAI
import os


class LLMClient:
    """LLM对话客户端"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        self.sdk = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
    
    async def ask(self, prompt: str, system_prompt: str = None, is_json: bool = False) -> str:
        """
        向LLM发送请求
        
        Args:
            prompt: 用户提示
            system_prompt: 系统提示（可选）
            is_json: 是否要求返回JSON格式
        
        Returns:
            LLM的响应文本
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {
            "model": "gpt-3.5-turbo",
            "messages": messages,
            "temperature": 0.2,
        }
        
        if is_json:
            params["response_format"] = {"type": "json_object"}
        
        result = await self.sdk.chat.completions.create(**params)
        return result.choices[0].message.content or ""

