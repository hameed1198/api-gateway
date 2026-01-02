# API Gateway - Swagger UI Testing Guide

## 🚀 Getting Started

### 1. Start the Server

```powershell
cd "C:\Users\Hameed khan\EIGHTGEN_AI"
uvicorn gateway:app --reload
```

### 2. Open Swagger UI

Navigate to: **http://127.0.0.1:8000/docs**

---

## 🔑 Test API Keys

Use these API keys in the `X-API-Key` header:

| Partner | API Key | Allowed Services | Rate Limit |
|---------|---------|------------------|------------|
| Premium Partner Inc. | `premium-key-001` | All services | 100/min |
| Basic Partner Ltd. | `basic-key-002` | users, posts | 30/min |
| Social Analytics Co. | `social-key-003` | posts, comments | 50/min |

---

## 📝 Testing Steps in Swagger UI

### Step 1: Test Health Check (No Auth Required)

1. Expand **GET /health** under "System"
2. Click **"Try it out"**
3. Click **"Execute"**
4. ✅ Expected: Status 200 with `{"status": "healthy", "service": "API Gateway"}`

---

### Step 2: Authorize with API Key

#### Option A: Use the Authorize Button (Recommended)

1. Click the **"Authorize"** button (🔒 lock icon at top right)
2. In the **X-API-Key (apiKey)** field, enter: `premium-key-001`
3. Click **"Authorize"**
4. Click **"Close"**

> Now all requests will automatically include your API key!

#### Option B: Add Header Manually Per Request

If you prefer to add the API key manually for each request:

1. Expand any endpoint (e.g., **GET /api/posts**)
2. Click **"Try it out"**
3. Look for the **X-API-Key** parameter field
4. Enter your API key: `premium-key-001`
5. Click **"Execute"**

---

### Step 3: Test Partner Info

1. Expand **GET /me** under "Partner"
2. Click **"Try it out"**
3. Click **"Execute"**
4. ✅ Expected: Status 200 with your partner details:
```json
{
  "id": "partner-001",
  "name": "Premium Partner Inc.",
  "allowed_services": ["users", "posts", "comments", "todos", "albums", "photos"],
  "rate_limit": 100,
  "rate_limit_remaining": 99,
  "is_active": true
}
```

---

### Step 4: Test GET Requests

#### Get All Posts
1. Expand **GET /api/posts** under "Posts Service"
2. Click **"Try it out"**
3. Click **"Execute"**
4. ✅ Expected: Status 200 with array of posts

#### Get Single User
1. Expand **GET /api/users/{user_id}** under "Users Service"
2. Click **"Try it out"**
3. Enter `1` in the **user_id** field
4. Click **"Execute"**
5. ✅ Expected: Status 200 with user data

---

### Step 5: Test POST Request

1. Expand **POST /api/posts** under "Posts Service"
2. Click **"Try it out"**
3. In the request body, enter:
```json
{
  "title": "My Test Post",
  "body": "This is a test post from Swagger UI",
  "userId": 1
}
```
4. Click **"Execute"**
5. ✅ Expected: Status 201 with created post data

---

### Step 6: Test Access Control (Authorization)

#### Test with Basic Partner (Limited Access)

1. Click **"Authorize"** → **"Logout"**
2. Re-authorize with: `basic-key-002`
3. Try **GET /api/posts** → ✅ Should work (Status 200)
4. Try **GET /api/todos** → ❌ Should fail (Status 403 Forbidden)

**Expected 403 Response:**
```json
{
  "detail": "Access denied to todos service. Allowed services: ['users', 'posts']"
}
```

---

### Step 7: Test Without API Key

1. Click **"Authorize"** → **"Logout"**
2. Try any `/api/*` endpoint
3. ❌ Expected: Status 401 Unauthorized

```json
{
  "detail": "X-API-Key header is required"
}
```

---

### Step 8: Test Admin Endpoints

1. Authorize with: `premium-key-001`
2. Expand **GET /admin/stats** under "Admin"
3. Click **"Try it out"** → **"Execute"**
4. ✅ See aggregate statistics:
```json
{
  "total_requests": 15,
  "requests_by_service": {"posts": 5, "users": 3, ...},
  "requests_by_partner": {"Premium Partner Inc.": 10, ...},
  "error_count": 2,
  "avg_response_time_ms": 245.5
}
```

5. Expand **GET /admin/logs** → See recent request logs

---

## 🧪 Test Scenarios Summary

| Test | API Key | Endpoint | Expected |
|------|---------|----------|----------|
| Health check | None | GET /health | 200 ✅ |
| Missing key | None | GET /api/posts | 401 ❌ |
| Invalid key | `wrong-key` | GET /api/posts | 401 ❌ |
| Premium - all access | `premium-key-001` | GET /api/todos | 200 ✅ |
| Basic - allowed | `basic-key-002` | GET /api/posts | 200 ✅ |
| Basic - denied | `basic-key-002` | GET /api/todos | 403 ❌ |
| Social - allowed | `social-key-003` | GET /api/comments | 200 ✅ |
| Social - denied | `social-key-003` | GET /api/users | 403 ❌ |

---

## 📊 Response Headers

Check the response headers for rate limit info:

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Max requests per minute |
| `X-RateLimit-Remaining` | Remaining requests in window |

---

## 🔗 Alternative: ReDoc

You can also view the API documentation at: **http://127.0.0.1:8000/redoc**

---

## 💡 Tips

1. **Use the "Try it out" button** to make live requests
2. **Check Response Headers** tab for rate limit info
3. **Use different API keys** to test access control
4. **Watch the terminal** to see server logs in real-time
