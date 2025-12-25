# Contributing Guide

## Setup Development Environment

1. Clone repository:
```bash
git clone https://github.com/akkalaj75/genai-enterprise-chatbot.git
cd genai-enterprise-chatbot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_services.py -v
```

## Code Style

We use Black for code formatting:

```bash
black app/ tests/
```

Lint with flake8:
```bash
flake8 app/ tests/
```

## Development Server

```bash
python app/main.py
```

Server runs on `http://localhost:5000`

API docs available at `http://localhost:5000/docs`

## Testing the API

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### Chat Query
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query":"What is the remote work policy?"}'
```

### Health Check
```bash
curl http://localhost:5000/health
```

## Project Structure

```
genai-enterprise-chatbot/
├── app/
│   ├── api/routes.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── azure_openai.py
│   │   └── auth.py
│   ├── prompts/templates.py
│   ├── ui/index.html
│   └── main.py
├── tests/
│   ├── test_services.py
│   └── test_api.py
├── data/sample_docs/
├── evaluation/metrics.py
├── .github/workflows/ci-cd.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and test:
```bash
pytest tests/ -v
```

3. Commit with descriptive message:
```bash
git commit -m "feat: add new feature description"
```

4. Push and create PR:
```bash
git push origin feature/your-feature-name
```

## Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Use FastAPI interactive docs at `/docs` for endpoint testing.

## Questions?

Open an issue or contact the maintainers.
