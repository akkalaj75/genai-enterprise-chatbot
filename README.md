# GenAI Enterprise Chatbot

A modern enterprise-grade AI chatbot application powered by OpenAI's GPT models.

## Features

- RESTful API for chat interactions
- Integration with OpenAI GPT models
- CORS support for cross-origin requests
- Health check endpoint
- Error handling and logging
- Environment configuration management

## Prerequisites

- Node.js v16 or higher
- npm or yarn
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/akkalaj75/genai-enterprise-chatbot.git
cd genai-enterprise-chatbot
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Add your OpenAI API key to `.env`

## Running the Application

Development mode:
```bash
npm run dev
```

Production mode:
```bash
npm start
```

The server will start on `http://localhost:3000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Chat Message
```
POST /api/chat/message
Content-Type: application/json

{
  "message": "Your message here"
}
```

## Project Structure

```
genai-enterprise-chatbot/
├── routes/
│   ├── chatbot.js
│   └── health.js
├── services/
│   └── openai.js
├── middleware/
│   └── errorHandler.js
├── server.js
├── package.json
├── .env.example
├── .gitignore
└── README.md
```

## Configuration

All configuration is managed through environment variables in `.env` file:

- `PORT`: Server port (default: 3000)
- `NODE_ENV`: Environment (development/production)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: Model to use (default: gpt-3.5-turbo)
- `API_TIMEOUT`: Request timeout in ms

## License

MIT License - see LICENSE file for details

## Author

Akkal
