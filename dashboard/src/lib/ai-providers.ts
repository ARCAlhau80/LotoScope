export type AIProvider = 'openrouter' | 'openai' | 'google';

export interface ProviderConfig {
  apiKey: string;
  model: string;
  endpoint: string;
  headers: Record<string, string>;
  bodyTransformer: (params: { messages: any[]; maxTokens: number; temperature: number }) => any;
}

export const PROVIDERS: Record<AIProvider, ProviderConfig> = {
  openrouter: {
    apiKey: process.env.OPENROUTER_API_KEY || '',
    model: process.env.OPENROUTER_MODEL || 'google/gemini-2.5-pro',
    endpoint: 'https://openrouter.ai/api/v1/chat/completions',
    headers: {
      'Content-Type': 'application/json',
      'HTTP-Referer': 'http://localhost:3003',
      'X-Title': 'LotoScope',
    },
    bodyTransformer: ({ messages, maxTokens, temperature }) => ({
      model: process.env.OPENROUTER_MODEL || 'google/gemini-2.5-pro',
      messages,
      max_tokens: maxTokens,
      temperature,
    }),
  },
  openai: {
    apiKey: process.env.OPENAI_API_KEY || '',
    model: process.env.OPENAI_MODEL || 'gpt-4o',
    endpoint: 'https://api.openai.com/v1/chat/completions',
    headers: {
      'Content-Type': 'application/json',
    },
    bodyTransformer: ({ messages, maxTokens, temperature }) => ({
      model: process.env.OPENAI_MODEL || 'gpt-4o',
      messages,
      max_tokens: maxTokens,
      temperature,
    }),
  },
  google: {
    apiKey: process.env.GOOGLE_API_KEY || '',
    model: process.env.GOOGLE_MODEL || 'gemini-2.5-pro',
    endpoint: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent',
    headers: {
      'Content-Type': 'application/json',
    },
    bodyTransformer: ({ messages, maxTokens, temperature }) => ({
      contents: messages.map(m => ({
        role: m.role === 'assistant' ? 'model' : 'user',
        parts: [{ text: m.content }],
      })),
      generationConfig: {
        maxOutputTokens: maxTokens,
        temperature,
      },
    }),
  },
};

export function getProvider(provider?: string): ProviderConfig {
  const p = (provider || process.env.AI_PROVIDER || 'openrouter') as AIProvider;
  const config = PROVIDERS[p];
  if (!config || !config.apiKey) {
    throw new Error(`Provedor "${p}" não configurado ou sem API key`);
  }
  return config;
}

export function buildAuthHeader(config: ProviderConfig): Record<string, string> {
  if (config === PROVIDERS.google) {
    return { ...config.headers, 'x-goog-api-key': config.apiKey };
  }
  return { ...config.headers, Authorization: `Bearer ${config.apiKey}` };
}