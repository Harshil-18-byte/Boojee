# API Documentation

The Boojee Platform exposes an asynchronous RESTful API built on **Quart** (ASGI) and **Beanie** (MongoDB ODM).

## Base URL
```
/api
```

---

## Endpoints

### 1. Authentication
* `POST /api/register` — Create new customer account with strict password validation.
* `POST /api/login` — Authenticate and receive session JWT cookie.
* `POST /api/logout` — Revoke active token in Redis blacklist.
* `GET /api/me` — Retrieve authenticated user profile.
* `POST /api/profile` — Update customer delivery details and phone.

### 2. Catalog & Products
* `GET /api/products` — Retrieve inventory of whole beans, merchandise, and bakery items.
* `GET /api/tables` — Retrieve dine-in table availability and capacity.

### 3. Cart & Orders
* `GET /api/cart` — Fetch active synchronized cart.
* `POST /api/cart` — Differential merge of local cart items into database.
* `GET /api/orders` — List user's past and active orders.
* `POST /api/orders` — Submit a click-and-collect or dine-in order.

### 4. Enquiries & Newsletters
* `POST /api/enquiries` — Submit group booking or gathering request.
  ```json
  {
    "name": "Alex",
    "email": "alex@example.com",
    "enquiry_type": "gathering",
    "date": "2026-09-10",
    "message": "Private tasting for 10 guests."
  }
  ```
* `POST /api/newsletter` — Subscribe email address for cafe fresh drop alerts.

### 5. Administrative Controls
* `GET /api/admin/orders` — Manage live order queue.
* `GET /api/admin/tables` — Manage table floor plan.
* `GET /api/admin/employees` — View staff directory and roles.
