import OpenAI from 'openai';


const apiKey: string = "";
const baseURL: string = 'https://api.openai.com/v1';

/** LLM对话 */
export class LLMClient {
  private sdk: OpenAI;

  constructor() {
    this.sdk = new OpenAI({
      apiKey,
      baseURL,
      defaultHeaders: {
        Authorization: `Bearer ${apiKey}`,
      },
      dangerouslyAllowBrowser: true
    });
  }

  async ask(prompt: string, systemPrompt?: string, isJson: boolean = false) {
    const result = await this.sdk.chat.completions.create(
      {
        model: "gpt-3.5-turbo",
        messages: [
          ...(systemPrompt ? [{ role: "system" as const, content: systemPrompt }] : []),
          { role: "user" as const, content: prompt }
        ],

        stream: false,
        temperature: 0.2,
        ...(isJson ? { response_format: { type: "json_object" } } : {})
      },

    );
    return result.choices?.[0]?.message?.content || "";
  }
}
