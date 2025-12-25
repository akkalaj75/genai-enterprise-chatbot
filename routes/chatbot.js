import express from 'express';
import { generateResponse } from '../services/openai.js';

const router = express.Router();

// POST /api/chat/message
router.post('/message', async (req, res) => {
  try {
    const { message, conversationHistory } = req.body;

    if (!message || typeof message !== 'string') {
      return res.status(400).json({ error: 'Invalid message format' });
    }

    if (message.trim().length === 0) {
      return res.status(400).json({ error: 'Message cannot be empty' });
    }

    const response = await generateResponse(message, conversationHistory || []);

    res.status(200).json({
      success: true,
      message: message,
      response: response,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Chat endpoint error:', error);
    res.status(500).json({ 
      error: 'Failed to generate response',
      details: error.message 
    });
  }
});

// GET /api/chat/info
router.get('/info', (req, res) => {
  res.status(200).json({
    name: 'GenAI Enterprise Chatbot',
    version: '1.0.0',
    model: process.env.OPENAI_MODEL || 'gpt-3.5-turbo'
  });
});

export default router;
