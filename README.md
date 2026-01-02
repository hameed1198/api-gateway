# API Gateway - Complete Documentation

## 📋 Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Solution Architecture](#-solution-architecture)
3. [Project Structure](#-project-structure)
4. [Setup & Installation](#-setup--installation)
5. [How It Works](#-how-it-works)
6. [API Endpoints](#-api-endpoints)
7. [Partner Management](#-partner-management)
8. [Testing](#-testing)
9. [Configuration](#-configuration)

---

## 🎯 Problem Statement

A company has multiple internal APIs (user service, posts service, todos service, etc.). They want to expose these APIs to external partners — but securely and in a controlled manner.

**Challenges:**
- Partners call internal services directly
- No central control over who can access what
- No way to prevent a partner from overwhelming the system with too many requests

**Solution:** Build an API Management Layer that sits between external partners and internal services.

---

## 🏗 Solution Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              EXTERNAL PARTNERS                               │
├─────────────────┬─────────────────┬─────────────────┬───────────────────────┤
│  Premium Partner │  Basic Partner  │ Social Partner  │    Other Partners     │
│  (Full Access)   │ (Users, Posts)  │(Posts, Comments)│                       │
└────────┬────────┴────────┬────────┴────────┬────────┴───────────┬───────────┘
         │                 │                 │                     │
         │    X-API-Key    │    X-API-Key    │    X-API-Key        │
         ▼                 ▼                 ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (FastAPI)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Auth      │  │   Access    │  │    Rate     │  │     Request         │ │
│  │ Validation  │─▶│   Control   │─▶│   Limiter   │─▶│     Logging         │ │
│  │ (API Key)   │  │ (Services)  │  │ (Per-Partner│  │    (Audit)          │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                        │                                     │
│                              ┌─────────▼─────────┐                          │
│                              │   Proxy Engine    │                          │
│                              │   (httpx async)   │                          │
│                              └─────────┬─────────┘                          │
└────────────────────────────────────────┼────────────────────────────────────┘
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
┌─────────────────┐           ┌─────────────────┐           ┌─────────────────┐
│  Users Service  │           │  Posts Service  │           │  Todos Service  │
│    /users       │           │    /posts       │           │    /todos       │
└─────────────────┘           └─────────────────┘           └─────────────────┘
         ▼                               ▼                               ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    BACKEND: JSONPlaceholder API                              │
│                 https://jsonplaceholder.typicode.com                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
EIGHTGEN_AI/
├── gateway.py              # Main FastAPI application (entry point)
├── partners.py             # Partner management & access control
├── rate_limiter.py         # Per-partner rate limiting
├── logging_service.py      # Request auditing & statistics
├── proxy.py                # HTTP proxy utilities
├── test_gateway.py         # Automated test suite
├── requirements.txt        # Python dependencies
├── README.md               # This documentation
└── SWAGGER_TESTING_GUIDE.md # Swagger UI testing guide
```

### File Descriptions

| File | Purpose |
|------|---------|
| **gateway.py** | Main application with all API routes, middleware, and dependencies |
| **partners.py** | Partner model, service enum, and partner store (in-memory database) |
| **rate_limiter.py** | Sliding window rate limiter with per-partner limits |
| **logging_service.py** | Request logger for audit trail and statistics |
| **proxy.py** | Async HTTP proxy function using httpx |
| **test_gateway.py** | Comprehensive test suite for all features |

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Step 1: Clone/Navigate to Project

```powershell
cd "C:\Users\Hameed khan\EIGHTGEN_AI"
```

### Step 2: Install Dependencies

```powershell
pip install -r requirements.txt
```

**Dependencies:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client for proxying

### Step 3: Start the Server

```powershell
uvicorn gateway:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
🚀 API Gateway starting up...
📡 Backend URL: https://jsonplaceholder.typicode.com
👥 Registered partners: 3
INFO:     Application startup complete.
```

### Step 4: Access the API

| URL | Description |
|-----|-------------|
| http://127.0.0.1:8000 | API Base URL |
| http://127.0.0.1:8000/docs | Swagger UI (Interactive Docs) |
| http://127.0.0.1:8000/redoc | ReDoc (Alternative Docs) |
| http://127.0.0.1:8000/health | Health Check |

---

## ⚙ How It Works

### Request Flow

```
1. Partner sends request with X-API-Key header
                    ↓
2. Authentication: Validate API key exists and is active
                    ↓
3. Authorization: Check if partner can access the requested service
                    ↓
4. Rate Limiting: Check if partner is within their request quota
                    ↓
5. Proxy: Forward request to backend service (JSONPlaceholder)
                    ↓
6. Logging: Record request details for audit
                    ↓
7. Response: Return backend response with rate limit headers
```

### Authentication Flow

```python
# Request without API key
GET /api/posts
→ 401 Unauthorized: "X-API-Key header is required"

# Request with invalid API key
GET /api/posts
X-API-Key: invalid-key
→ 401 Unauthorized: "Invalid API key"

# Request with valid API key
GET /api/posts
X-API-Key: premium-key-001
→ 200 OK: [posts data...]
```

### Authorization Flow

```python
# Basic partner trying to access allowed service
GET /api/posts
X-API-Key: basic-key-002
→ 200 OK: [posts data...]

# Basic partner trying to access restricted service
GET /api/todos
X-API-Key: basic-key-002
→ 403 Forbidden: "Access denied to todos service. Allowed services: ['users', 'posts']"
```

### Rate Limiting Flow

```python
# First 30 requests (within limit)
GET /api/posts
X-API-Key: basic-key-002
→ 200 OK
→ Headers: X-RateLimit-Remaining: 29

# 31st request (limit exceeded)
GET /api/posts
X-API-Key: basic-key-002
→ 429 Too Many Requests: "Rate limit exceeded. Limit: 30 requests/minute"
→ Headers: Retry-After: 45
```

---

## 📡 API Endpoints

### System Endpoints (No Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/info` | Gateway information |

### Partner Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/me` | Get current partner info |

### Users Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users` | Get all users |
| GET | `/api/users/{id}` | Get user by ID |
| POST | `/api/users` | Create a user |

### Posts Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/posts` | Get all posts |
| GET | `/api/posts/{id}` | Get post by ID |
| POST | `/api/posts` | Create a post |
| PUT | `/api/posts/{id}` | Update a post |
| DELETE | `/api/posts/{id}` | Delete a post |
| GET | `/api/posts/{id}/comments` | Get comments for a post |

### Comments Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments` | Get all comments |
| GET | `/api/comments/{id}` | Get comment by ID |
| POST | `/api/comments` | Create a comment |

### Todos Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/todos` | Get all todos |
| GET | `/api/todos/{id}` | Get todo by ID |
| POST | `/api/todos` | Create a todo |

### Albums Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/albums` | Get all albums |
| GET | `/api/albums/{id}` | Get album by ID |
| GET | `/api/albums/{id}/photos` | Get photos in album |

### Photos Service

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/photos` | Get all photos |
| GET | `/api/photos/{id}` | Get photo by ID |

### Admin Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/partners` | List all partners |
| GET | `/admin/logs` | Get request logs |
| GET | `/admin/stats` | Get aggregate statistics |

---

## 👥 Partner Management

### Pre-configured Partners

| Partner | API Key | Services | Rate Limit |
|---------|---------|----------|------------|
| Premium Partner Inc. | `premium-key-001` | All 6 services | 100/min |
| Basic Partner Ltd. | `basic-key-002` | users, posts | 30/min |
| Social Analytics Co. | `social-key-003` | posts, comments | 50/min |

### Service Access Matrix

| Service | Premium | Basic | Social |
|---------|---------|-------|--------|
| Users   | ✅ | ✅ | ❌ |
| Posts   | ✅ | ✅ | ✅ |
| Comments | ✅ | ❌ | ✅ |
| Todos   | ✅ | ❌ | ❌ |
| Albums  | ✅ | ❌ | ❌ |
| Photos  | ✅ | ❌ | ❌ |

### Adding a New Partner (Code)

```python
# In partners.py
partner_store.create_partner(
    partner_id="partner-004",
    name="New Partner Corp.",
    allowed_services={Service.USERS, Service.POSTS, Service.TODOS},
    rate_limit=50,
    api_key="new-partner-key-004"  # Optional, auto-generated if not provided
)
```

---

## 🧪 Testing

### Option 1: Automated Test Suite

```powershell
# Terminal 1: Start server
uvicorn gateway:app --reload

# Terminal 2: Run tests
python test_gateway.py
```

**Expected Output:**
```
==================🧪 API GATEWAY TEST SUITE ==================

✅ PASSED: Health Check
✅ PASSED: Gateway Info
✅ PASSED: Missing API Key
✅ PASSED: Invalid API Key
✅ PASSED: Premium - Posts
✅ PASSED: Premium - Todos
✅ PASSED: Basic - Posts
✅ PASSED: Basic - Todos Denied
✅ PASSED: Social - Comments
✅ PASSED: Social - Users Denied
✅ PASSED: Partner Info
✅ PASSED: Create Post
✅ PASSED: Get User by ID
✅ PASSED: Admin Stats
✅ PASSED: Admin Logs

============================================================
RESULTS: 15 passed, 0 failed
============================================================
```

### Option 2: Swagger UI

1. Open http://127.0.0.1:8000/docs
2. Click **"Authorize"** button
3. Enter API key: `premium-key-001`
4. Test endpoints interactively

See [SWAGGER_TESTING_GUIDE.md](SWAGGER_TESTING_GUIDE.md) for detailed instructions.

### Option 3: PowerShell Commands

```powershell
# Health check (no auth)
Invoke-RestMethod http://127.0.0.1:8000/health

# Get posts with API key
Invoke-RestMethod "http://127.0.0.1:8000/api/posts?_limit=2" -Headers @{"X-API-Key"="premium-key-001"}

# Test access denied
Invoke-RestMethod http://127.0.0.1:8000/api/todos -Headers @{"X-API-Key"="basic-key-002"}

# Get partner info
Invoke-RestMethod http://127.0.0.1:8000/me -Headers @{"X-API-Key"="premium-key-001"}

# Create a post
$body = @{title="Test"; body="Content"; userId=1} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/api/posts -Method POST -Headers @{"X-API-Key"="premium-key-001"; "Content-Type"="application/json"} -Body $body
```

### Option 4: cURL Commands

```bash
# Health check
curl http://127.0.0.1:8000/health

# Get posts
curl -H "X-API-Key: premium-key-001" http://127.0.0.1:8000/api/posts

# Create post
curl -X POST http://127.0.0.1:8000/api/posts \
  -H "X-API-Key: premium-key-001" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "body": "Content", "userId": 1}'
```

---

## ⚙ Configuration

### Environment Variables (Future Enhancement)

```python
# Can be added to gateway.py
import os

BASE_URL = os.getenv("BACKEND_URL", "https://jsonplaceholder.typicode.com")
DEFAULT_RATE_LIMIT = int(os.getenv("DEFAULT_RATE_LIMIT", "60"))
```

### Rate Limiter Settings

```python
# In rate_limiter.py
rate_limiter = RateLimiter(window_seconds=60)  # 1-minute window
```

### Partner Rate Limits

Edit `partners.py` to change default rate limits:

```python
self.create_partner(
    partner_id="partner-001",
    name="Premium Partner Inc.",
    allowed_services={...},
    rate_limit=100  # Change this value
)
```

---

## 📊 Monitoring & Logging

### Request Logs

All requests are logged with:
- Timestamp
- Partner ID & Name
- HTTP Method & Path
- Service accessed
- Response status code
- Response time (ms)
- Client IP
- Error message (if any)

### View Logs

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/admin/logs?limit=10" -Headers @{"X-API-Key"="premium-key-001"}
```

### View Statistics

```powershell
Invoke-RestMethod http://127.0.0.1:8000/admin/stats -Headers @{"X-API-Key"="premium-key-001"}
```

**Sample Response:**
```json
{
  "total_requests": 150,
  "requests_by_service": {
    "posts": 45,
    "users": 30,
    "comments": 25,
    "todos": 20,
    "albums": 15,
    "photos": 15
  },
  "requests_by_partner": {
    "Premium Partner Inc.": 80,
    "Basic Partner Ltd.": 40,
    "Social Analytics Co.": 30
  },
  "error_count": 5,
  "avg_response_time_ms": 234.5
}
```

---

## 🔒 Security Features

| Feature | Implementation |
|---------|----------------|
| **Authentication** | API Key validation via `X-API-Key` header |
| **Authorization** | Service-level access control per partner |
| **Rate Limiting** | Sliding window algorithm, per-partner limits |
| **Audit Logging** | All requests logged for compliance |
| **Error Handling** | Proper HTTP status codes (401, 403, 429, 502, 504) |

---

## 🚀 Future Enhancements

1. **Database Storage** - Replace in-memory stores with PostgreSQL/Redis
2. **JWT Authentication** - Add token-based auth option
3. **API Key Rotation** - Automatic key expiration and rotation
4. **Dashboard UI** - Web interface for partner management
5. **Metrics Export** - Prometheus/Grafana integration
6. **Caching** - Redis caching for frequently accessed data
7. **Load Balancing** - Support multiple backend instances

---

## 📝 License

This project was created as a proof-of-concept for API Gateway design.

---

## 🤝 Support

For questions or issues, refer to:
- [Swagger UI Testing Guide](SWAGGER_TESTING_GUIDE.md)
- FastAPI Documentation: https://fastapi.tiangolo.com
- JSONPlaceholder API: https://jsonplaceholder.typicode.com
