# Architecture Blueprint

## 1. System Topology

The Boojee Platform utilizes an asynchronous microservice-oriented topology with decoupled presentation and transactional layers.

```text
[Client Layer: Web & Mobile]
       |
       | HTTPS (TLS 1.3)
       v
+-----------------------------------+
| Static Presentation Engine        |
| - 15 Unified Pages                |
| - Media Streaming Pipeline        |
| - Pure Black Dark Mode Theme      |
+-----------------------------------+
       |
       | REST / JSON
       v
+-----------------------------------+
| Core ASGI Gateway (Quart)         |
| - JWT Stateless Session Engine    |
| - Pydantic Ingress Validation     |
| - Redis Rate Limiter (GCRA)       |
+-----------------------------------+
       |                    |
       | Beanie ODM         | Caching / Worker
       v                    v
+---------------+    +--------------------+
| MongoDB Atlas |    | Redis & ARQ Worker |
| (Data Models) |    | (Token Blacklist)  |
+---------------+    +--------------------+
```

## 2. Media & Static Asset Subsystem
* Video assets (`frontend/videos/`) are served with HTTP 206 Partial Content support for smooth scrub and streaming.
* Image assets are categorized into structured domain directories (`gallery/`, `roastery/`, `shop/`, `team/`, `cafe/`).

## 3. Data Models
1. **User**: Authentication, MFA secrets, and encrypted customer PII.
2. **Product**: Whole beans, barista merch, and bakery inventory.
3. **Order**: Click-and-collect orders with timestamps and collection notes.
4. **Enquiry**: Gathering reservations, salon bookings, and contact inquiries.
5. **Cart**: Multi-device synchronized cart vectors.
