# Core API Reference (v2.2)

This document provides a highly technical, rigorous overview of the Boojee Core REST API. All endpoints are secured behind the Gateway and enforce strict JSON schemas via Pydantic type-coercion.

## 1. Global Request/Response Paradigms

### 1.1. Data Serialization Format
All ingress (POST/PUT/PATCH) payloads must be transmitted as strictly formatted `application/json`.
All egress payloads are guaranteed to return `application/json`. XML or Form-Data payloads will be instantly rejected with an HTTP 415 (Unsupported Media Type).

The platform enforces a standardized envelope response format to allow client-side reducers to parse responses predictably:
```json
{
  "status": "success | error | fail",
  "data": { ... }, // Payload on success, null on failure
  "message": "Human readable context", // Optional
  "error_code": "ERR_SPECIFIC_CODE", // Present only on fail/error
  "metadata": { // Optional telemetry
      "execution_time_ms": 12.4
  }
}
```

### 1.2. Cryptographic Authentication (Stateless JWT)
Protected endpoints require a cryptographic JSON Web Token (JWT) passed via the `Authorization` header or `HttpOnly` cookie:
`Authorization: Bearer <ey...>`

*   **Signature**: Tokens are aggressively validated for signature integrity using HS256 (HMAC with SHA-256). The secret key is never stored in version control.
*   **Revocation (Redis Blacklist)**: Before processing the payload, the gateway performs an O(1) time-complexity check against the Redis cluster. If the token's unique `jti` (JWT ID) exists in the blacklist, the request is instantly aborted with an HTTP 401, neutralizing stolen session tokens.

### 1.3. Rate Limiting Headers (GCRA)
Every API response includes critical telemetry regarding your current rate limit penalty bucket. The API utilizes the Generic Cell Rate Algorithm (GCRA) to ensure microsecond-level precision across all distributed nodes.

*   `X-RateLimit-Limit`: The absolute maximum requests allowed in the current temporal window.
*   `X-RateLimit-Remaining`: The exact number of requests remaining before a ban is issued.
*   `X-RateLimit-Reset`: The exact UTC Unix Epoch timestamp when the penalty box will completely flush.

Exceeding the threshold triggers an immediate `429 Too Many Requests` response. Continued bombardment post-429 will result in an IP-level shadow ban at the WAF edge.

## 2. Pydantic Error Schemas (HTTP 422 Unprocessable Entity)
If an incoming request violates the Beanie ODM / Pydantic validation schema (e.g., missing a required field, providing a string instead of an integer, or violating a regex bound), the API short-circuits the BSON query builder. This is our primary defense against NoSQL injection.

The response will detail the exact byte-level failure:
```json
{
  "status": "fail",
  "error_code": "ERR_VALIDATION",
  "details": [
    {
      "loc": ["body", "password"], 
      "msg": "String should have at least 8 characters", 
      "type": "string_too_short"
    },
    {
      "loc": ["body", "email"], 
      "msg": "value is not a valid email address", 
      "type": "value_error.email"
    }
  ]
}
```

## 3. Core Endpoints & Payloads

### 3.1. Authentication & Identity
*   **`POST /api/register`**
    *   *Payload*: `{ "email" (str), "password" (str), "name" (str) }`
    *   *Rate Limit*: 5 per 60 seconds / IP
    *   *Description*: Hashes the password via PBKDF2 (minimum 600,000 iterations), stores the User Document in MongoDB, and triggers an asynchronous welcome email via the Arq task queue. Returns a 201 Created.
*   **`POST /api/login`**
    *   *Payload*: `{ "email" (str), "password" (str) }`
    *   *Rate Limit*: 5 per 60 seconds / IP
    *   *Description*: Verifies credentials. Returns the primary JWT. If the user has TOTP MFA enabled in their Document, returns an `MFA_REQUIRED` status with a temporary 30-second challenge token instead of the primary JWT.
*   **`POST /api/mfa/verify`**
    *   *Payload*: `{ "challenge_token" (str), "totp_code" (str: length 6) }`
    *   *Rate Limit*: 3 per 60 seconds / IP
    *   *Description*: Consumes the 6-digit authenticator code and the challenge token. If the TOTP algorithm mathematically verifies the code against the user's secret base32 seed, the primary authorization JWT is issued.

### 3.2. Products & Inventory
*   **`GET /api/products`**
    *   *Auth*: Public (Cached in Redis)
    *   *Description*: Retrieves active catalog of specialty coffees (*Coal Black*, *Experimental Lot*), barista apparel, ceramic stoneware, and bakery items.
*   **`GET /api/tables`**
    *   *Auth*: Public (Cached in Redis)
    *   *Description*: Retrieves real-time table availability and seat capacity for dine-in.

### 3.3. Cart & Orders
*   **`GET /api/cart`**
    *   *Auth*: JWT Required
    *   *Description*: Retrieves user's active cloud synchronized cart.
*   **`POST /api/cart`**
    *   *Auth*: JWT Required
    *   *Payload*: `{ "cart": { "Item Name": 2 } }`
    *   *Description*: Merges client `localStorage` vector with persisted user cart document.
*   **`GET /api/orders`**
    *   *Auth*: JWT Required
    *   *Description*: Returns user's order history with status telemetry.
*   **`POST /api/orders`**
    *   *Auth*: JWT Required
    *   *Payload*: `{ "cart": {...}, "total": 1200, "collection_time": "10:30 AM", "customer_name": "Alex", "phone": "+919876543210" }`
    *   *Description*: Creates a new confirmed click-and-collect or dine-in order.

### 3.4. Enquiries & Gathering Bookings
*   **`POST /api/enquiries`**
    *   *Auth*: Public
    *   *Payload*: `{ "name" (str), "email" (str), "enquiry_type" (str), "date" (str), "message" (str) }`
    *   *Description*: Persists gathering reservations, salon bookings, and general contact messages into the MongoDB `Enquiry` collection. Returns a 201 Created.

### 3.5. Administrative & Security
*   **`GET /api/admin/orders`**
    *   *Auth*: Requires valid JWT containing `role: admin`.
    *   *Description*: Live queue of all active store orders and fulfillment states.
*   **`GET /api/admin/tables`**
    *   *Auth*: Requires valid JWT containing `role: admin`.
    *   *Description*: Full floor plan status management.
*   **`GET /api/admin/employees`**
    *   *Auth*: Requires valid JWT containing `role: admin`.
    *   *Description*: Lists active staff members, roles, and assigned stations.
*   **`GET /api/admin/audit-logs`**
    *   *Auth*: Requires valid JWT containing `role: admin`.
    *   *Description*: Paginates the WORM MongoDB `AuditLog` collection, returning a chronological ledger of all high-privilege system mutations.
*   **`DELETE /api/admin/revoke-user`**
    *   *Auth*: Requires valid JWT containing `role: super_admin`.
    *   *Payload*: `{ "target_user_id" (uuid) }`
    *   *Description*: Locates all active JWTs issued to the target user and instantly injects their `jti` claims into the distributed Redis blacklist, forcing a global logout across all edge nodes.

## Mobile App Support (Capacitor)
This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.
