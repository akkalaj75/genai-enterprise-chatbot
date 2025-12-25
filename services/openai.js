import { OpenAI } from 'openai';
import dotenv from 'dotenv';

dotenv.config();

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY
});

const MODEL = process.env.OPENAI_MODEL || 'gpt-3.5-turbo';

export async function generateResponse(userMessage, conversationHistory = []) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is not set');
    }

    // Build message history for context
    const messages = [
      {
        role: 'system',
        content: 'You are a helpful, professional enterprise AI assistant. Provide clear, concise, and accurate responses.'
      },
      ...conversationHistory.map(msg => ({
        role: msg.role || 'user',
        content: msg.content
      })),
      {
        role: 'user',
        content: userMessage
      }
    ];

    const response = await client.chat.completions.create({
      model: MODEL,
      messages: messages,
      temperature: 0.7,
      max_tokens: 500,
      top_p: 1,
      frequency_penalty: 0,
      presence_penalty: 0
    });

    return response.choices[0].message.content;
  } catch (error) {
    console.error('OpenAI API error:', error);
    throw error;
  }
}

export async function generateStreamResponse(userMessage, conversationHistory = []) {
  try {
    if (!process.env.OPENAI_API_KEY) {
      throw new Error('OPENAI_API_KEY is not set');
    }

    const messages = [
      {
        role: 'system',
        content: 'You are a helpful, professional enterprise AI assistant.'
      },
      ...conversationHistory,
      {
        role: 'user',
        content: userMessage
      }
    ];

    const stream = await client.chat.completions.create({
      model: MODEL,
      messages: messages,
      stream: true,
      temperature: 0.7,
      max_tokens: 500
    });

    return stream;
  } catch (error) {
    console.error('OpenAI streaming error:', error);
    throw error;
  }
}
