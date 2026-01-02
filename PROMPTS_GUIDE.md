# Build an API Gateway with AI - Step-by-Step Prompts Guide

This guide shows you how to build a complete API Gateway from scratch using AI prompts. Follow each step in order and use the provided prompts with your AI coding assistant.

---

## 📋 Prerequisites

- Python 3.10+ installed
- VS Code with GitHub Copilot or any AI coding assistant
- Git installed
- GitHub account (for deployment)

---

## 🚀 Step-by-Step Prompts

### Step 1: Create the Basic FastAPI Application

**Prompt:**
```
Create a FastAPI application with:
- main.py entry point
- Health check endpoint at /health
- Use async FastAPI style
```

**Expected Output:** A `main.py` file with basic FastAPI setup and health endpoint.

---

### Step 2: Create API Key Authentication

**Prompt:**
```
Create a FastAPI dependency that:
- Reads X-API-Key header
- Validates against a dictionary of API keys
- Returns 401 if missing or invalid
```

**Expected Output:** A `dependencies.py` file with `verify_api_key` function.

---

### Step 3: Implement Rate Limiting

**Prompt:**
```
Implement a simple in-memory rate limiter in Python:
- Limit requests per API key
- Configurable max requests per minute
- Raise HTTPException 429 when exceeded
```

**Expected Output:** Rate limiter class with sliding window algorithm.

---

### Step 4: Create the Proxy Function

**Prompt:**
```
Create an async proxy function using httpx that:
- Accepts incoming request
- Forwards method, headers, query params, and body
- Returns backend response to client
```

**Expected Output:** A `proxy.py` file with async proxy functionality.

---

### Step 5: Set Up Backend URL

**Prompt:**
```
BASE_URL = "https://jsonplaceholder.typicode.com"
```

**Expected Output:** Configuration for the backend API.

---

### Step 6: Create Protected API Routes

**Prompt:**
```
Create FastAPI routes that:
- Require API key auth
- Apply rate limiting
- Proxy requests to JSONPlaceholder
- Support GET and POST
```

**Expected Output:** Multiple API endpoints for users, posts, comments, etc.

---

### Step 7: Generate Requirements File

**Prompt:**
```
generate a requirements.txt
```

**Expected Output:** 
```
fastapi>=0.109.0
uvicorn>=0.27.0
httpx>=0.26.0
```

---

### Step 8: Create Partner Management System

**Prompt:**
```
Create a partner management module with:
- Partner dataclass with id, name, api_key, allowed_services, rate_limit
- Service enum (USERS, POSTS, COMMENTS, TODOS, ALBUMS, PHOTOS)
- PartnerStore class with CRUD operations
- Pre-configure 3 demo partners with different access levels
```

**Expected Output:** A `partners.py` file with partner management.

---

### Step 9: Create Request Logging

**Prompt:**
```
Create a request logging module that:
- Logs all API requests with timestamp, partner, method, path, status, response time
- Provides recent logs retrieval
- Calculates aggregate statistics
```

**Expected Output:** A `logging_service.py` file for audit trail.

---

### Step 10: Build the Complete Gateway

**Prompt:**
```
Create the main API Gateway application that combines:
- Partner-based authentication (API key lookup)
- Service-level authorization (check allowed services)
- Per-partner rate limiting
- Request proxying to JSONPlaceholder
- Audit logging
- Admin endpoints for logs and stats

Use these services: users, posts, comments, todos, albums, photos
```

**Expected Output:** A complete `gateway.py` file.

---

### Step 11: Create Test Suite

**Prompt:**
```
Create an automated test script that tests:
- Health check (no auth)
- Missing API key (401)
- Invalid API key (401)
- Valid requests with different partners
- Access denied scenarios (403)
- POST requests
- Admin endpoints
```

**Expected Output:** A `test_gateway.py` file with comprehensive tests.

---

### Step 12: Generate Documentation

**Prompt:**
```
Create a document for entire flow and setup
```

**Expected Output:** A `README.md` with complete documentation.

---

### Step 13: Create Swagger UI Testing Guide

**Prompt:**
```
Generate a MD file for how to test in Swagger UI
```

**Expected Output:** A `SWAGGER_TESTING_GUIDE.md` with step-by-step instructions.

---

### Step 14: Push to GitHub

**Prompt:**
```
I want to commit it on GitHub
```

**Expected Output:** Git initialization, .gitignore creation, and push commands.

---

### Step 15: Deploy to Render.com

**Prompt:**
```
I want to deploy using Render.com, what configuration do I need?
```

**Expected Output:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn gateway:app --host 0.0.0.0 --port $PORT`

---

## 📁 Final Project Structure

After completing all steps, you should have:

```
api-gateway/
├── gateway.py              # Main application (entry point)
├── partners.py             # Partner management
├── rate_limiter.py         # Rate limiting logic
├── logging_service.py      # Request logging
├── proxy.py                # HTTP proxy utilities
├── dependencies.py         # Auth dependencies
├── main.py                 # Original simple version
├── test_gateway.py         # Test suite
├── requirements.txt        # Dependencies
├── .gitignore              # Git ignore file
├── README.md               # Documentation
└── SWAGGER_TESTING_GUIDE.md # Testing guide
```

---

## 🔑 Test API Keys

| Partner | API Key | Services | Rate Limit |
|---------|---------|----------|------------|
| Premium | `premium-key-001` | All | 100/min |
| Basic | `basic-key-002` | users, posts | 30/min |
| Social | `social-key-003` | posts, comments | 50/min |

---

## 🧪 Test Commands

```bash
# Start server
uvicorn gateway:app --reload

# Run tests (in another terminal)
python test_gateway.py

# Manual test with curl
curl -H "X-API-Key: premium-key-001" http://localhost:8000/api/posts
```

---

## ✅ Features Checklist

After following all prompts, you should have:

- [x] API Key Authentication
- [x] Service-level Authorization
- [x] Per-partner Rate Limiting
- [x] Request Proxying
- [x] Audit Logging
- [x] Admin Dashboard
- [x] Swagger UI Documentation
- [x] Automated Tests
- [x] GitHub Repository
- [x] Live Deployment

---

## 🎯 Key Learning Points

1. **FastAPI Dependencies** - Reusable authentication/authorization logic
2. **Async HTTP** - Using httpx for non-blocking requests
3. **Rate Limiting** - Sliding window algorithm implementation
4. **API Gateway Pattern** - Central entry point for microservices
5. **Access Control** - Service-level permissions per client

---

## 🔗 Resources

- FastAPI Docs: https://fastapi.tiangolo.com
- JSONPlaceholder: https://jsonplaceholder.typicode.com
- Render.com: https://render.com
- httpx Docs: https://www.python-httpx.org

---

## 💡 Tips for Using AI Prompts

1. **Be Specific** - Include exact requirements in your prompts
2. **Iterate** - If output isn't perfect, refine your prompt
3. **Test Frequently** - Run code after each step to catch issues early
4. **Ask for Explanations** - If you don't understand something, ask "explain this code"
5. **Request Improvements** - Ask "how can we improve this?" for better code

---

## 📝 Example Conversation Flow

```
You: Create a FastAPI application with health check endpoint
AI: [Creates main.py]

You: Add API key authentication
AI: [Creates dependencies.py]

You: Implement rate limiting
AI: [Adds rate limiter]

You: Create proxy to JSONPlaceholder
AI: [Creates proxy.py]

You: Combine everything into a complete gateway
AI: [Creates gateway.py]

You: Generate tests
AI: [Creates test_gateway.py]

You: Deploy to Render.com
AI: [Provides deployment instructions]
```

---

**Happy Building! 🚀**
