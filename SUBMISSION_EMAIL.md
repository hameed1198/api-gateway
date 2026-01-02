# Assignment Submission Email

---

**Subject:** API Gateway Assignment Submission - API Management Layer Solution

---

Dear Hiring Team,

I am pleased to submit my solution for the API Gateway assignment. I have designed and implemented a fully functional **API Management Layer** that addresses the challenge of exposing internal APIs to external partners securely and in a controlled manner.

---

## 🎯 Problem Solved

The solution addresses the core challenges:
- **No central authentication** → Implemented API Key-based authentication
- **No access control** → Implemented service-level authorization per partner
- **No rate limiting** → Implemented per-partner rate limiting to prevent system overload

---

## 🏗️ Solution Architecture

```
External Partners (with API Keys)
            ↓
    ┌───────────────────────────────────────┐
    │         API GATEWAY (FastAPI)          │
    │  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
    │  │  Auth   │→│ Access  │→│  Rate   │  │
    │  │(API Key)│ │ Control │ │ Limiter │  │
    │  └─────────┘ └─────────┘ └─────────┘  │
    │              ↓                         │
    │       Request Logging                  │
    │              ↓                         │
    │        Proxy Engine                    │
    └───────────────────────────────────────┘
            ↓
    Backend Services (JSONPlaceholder)
    - Users, Posts, Comments, Todos, Albums, Photos
```

---

## ✨ Key Features Implemented

| Feature | Description |
|---------|-------------|
| **Authentication** | API Key validation via `X-API-Key` header |
| **Authorization** | Service-level access control - each partner can only access permitted services |
| **Rate Limiting** | Sliding window algorithm with configurable per-partner limits |
| **Request Proxying** | Async HTTP proxy forwarding requests to backend services |
| **Audit Logging** | Complete request logging with timestamps, response times, and statistics |
| **Admin Dashboard** | Endpoints to view logs, statistics, and partner information |

---

## 👥 Pre-configured Test Partners

| Partner | API Key | Allowed Services | Rate Limit |
|---------|---------|------------------|------------|
| Premium Partner Inc. | `premium-key-001` | All 6 services | 100 req/min |
| Basic Partner Ltd. | `basic-key-002` | Users, Posts only | 30 req/min |
| Social Analytics Co. | `social-key-003` | Posts, Comments only | 50 req/min |

---

## 🌐 Live Demo

The API Gateway is deployed and accessible at:

**🔗 Live URL:** https://api-gateway-deio.onrender.com

**📖 Interactive Documentation:** https://api-gateway-deio.onrender.com/docs

**📦 GitHub Repository:** https://github.com/hameed1198/api-gateway

---

## 🧪 How to Test (Step-by-Step Guide)

### Step 1: Open the Swagger Documentation
Navigate to: **https://api-gateway-deio.onrender.com/docs**

*(Note: First request may take ~50 seconds if the server is cold)*

### Step 2: Test Public Endpoints (No Authentication)
1. Expand **GET /health** under "System"
2. Click **"Try it out"** → **"Execute"**
3. ✅ You should see: `{"status": "healthy", "service": "API Gateway"}`

### Step 3: Authorize with API Key
1. Click the **"Authorize"** button (🔒 at top right)
2. Enter: `premium-key-001`
3. Click **"Authorize"** → **"Close"**

### Step 4: Test Protected Endpoints
1. Expand **GET /api/posts** under "Posts Service"
2. Click **"Try it out"** → **"Execute"**
3. ✅ You should receive a list of posts from the backend

### Step 5: Test Access Control (Authorization)
1. Click **"Authorize"** → **"Logout"**
2. Re-authorize with: `basic-key-002` (Basic Partner)
3. Try **GET /api/posts** → ✅ Works (Status 200)
4. Try **GET /api/todos** → ❌ Returns 403 Forbidden

**Expected 403 Response:**
```json
{
  "detail": "Access denied to todos service. Allowed services: ['users', 'posts']"
}
```

### Step 6: Test Without API Key
1. Logout from Authorize
2. Try any `/api/*` endpoint
3. ❌ Returns 401: `"X-API-Key header is required"`

### Step 7: Test Admin Endpoints
1. Authorize with: `premium-key-001`
2. **GET /admin/stats** → View aggregate statistics
3. **GET /admin/logs** → View recent request logs

---

## 📁 Project Structure

```
api-gateway/
├── gateway.py           # Main FastAPI application (entry point)
├── partners.py          # Partner management & access control
├── rate_limiter.py      # Per-partner rate limiting logic
├── logging_service.py   # Request auditing & statistics
├── proxy.py             # HTTP proxy utilities
├── test_gateway.py      # Automated test suite
├── requirements.txt     # Python dependencies
├── README.md            # Complete documentation
└── SWAGGER_TESTING_GUIDE.md  # Testing guide
```

---

## 🛠️ Technology Stack

- **Framework:** FastAPI (Python)
- **Server:** Uvicorn (ASGI)
- **HTTP Client:** httpx (async)
- **Deployment:** Render.com
- **Backend Simulation:** JSONPlaceholder API

---

## 🧪 Test Scenarios Summary

| Scenario | API Key | Endpoint | Expected Result |
|----------|---------|----------|-----------------|
| No API Key | None | GET /api/posts | 401 Unauthorized |
| Invalid Key | `wrong-key` | GET /api/posts | 401 Unauthorized |
| Premium Access | `premium-key-001` | GET /api/todos | 200 OK |
| Basic - Allowed | `basic-key-002` | GET /api/posts | 200 OK |
| Basic - Denied | `basic-key-002` | GET /api/todos | 403 Forbidden |
| Create Resource | `premium-key-001` | POST /api/posts | 201 Created |

---

## 📊 Additional Features

- **Rate Limit Headers:** Every response includes `X-RateLimit-Limit` and `X-RateLimit-Remaining`
- **Error Handling:** Proper HTTP status codes (401, 403, 429, 502, 504)
- **CORS Enabled:** Supports cross-origin requests
- **Health Monitoring:** `/health` endpoint for uptime monitoring

---

## 🚀 Running Locally

```bash
# Clone the repository
git clone https://github.com/hameed1198/api-gateway.git
cd api-gateway

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn gateway:app --reload

# Run automated tests (in another terminal)
python test_gateway.py
```

---

## Summary

This API Gateway successfully demonstrates:

1. ✅ **Centralized Authentication** - Single entry point with API key validation
2. ✅ **Fine-grained Authorization** - Service-level access control per partner
3. ✅ **Rate Limiting** - Protection against system overload
4. ✅ **Request Proxying** - Seamless forwarding to backend services
5. ✅ **Audit Trail** - Complete logging for monitoring and compliance
6. ✅ **Live Deployment** - Accessible via public URL

I would be happy to walk through the solution in more detail or answer any questions.

Thank you for the opportunity.

Best regards,
Hameed Khan

---

**Links:**
- 🌐 Live API: https://api-gateway-deio.onrender.com
- 📖 Documentation: https://api-gateway-deio.onrender.com/docs
- 📦 GitHub: https://github.com/hameed1198/api-gateway
