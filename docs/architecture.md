# Boojee Cafe Platform - Master Architecture Documentation

This document serves as the canonical reference for the internal architecture, network topology, and systemic boundaries of the Boojee platform. It is intended for Staff Engineers, DevOps personnel, and Core Contributors who need a deep, intrinsic understanding of the data flow and systemic isolation boundaries.

## 1. System Context & Paradigm

The Boojee platform operates under a strictly **Decoupled, Microservice-Oriented Architecture**. We reject monolithic paradigms in favor of isolated, bounded contexts to ensure deterministic scaling, isolated failure domains, and uncompromising cryptographic security.

The runtime leverages **Asynchronous Event-Driven Loops** utilizing the Python `asyncio` framework. Synchronous blocking I/O is fundamentally rejected within the core API pathways. Any thread-blocking operation will instantly stall the event loop, causing latency spikes. Therefore, strict adherence to `await` paradigms is required.

## 2. Infrastructure Topology & Network Flow

The architecture is partitioned into four primary, mutually-distrusting tiers, separated by virtual private clouds (VPCs) and strict ingress/egress firewall rules.

```mermaid
graph TD
    Client[Client Browser / Mobile PWA] -->|HTTPS TLS 1.3 / HTTP2| WAF[Cloudflare WAF / Edge CDN]
    WAF -->|Validated Traffic| Gateway[API Gateway / NGINX Ingress Controller]
    
    Gateway -->|REST / JWT Auth / Port 443| CoreAPI[Core Quart API - ASGI]
    Gateway -->|WebSocket Upgrade / Port 443| Analytics[Analytics & Telemetry Engine]
    
    CoreAPI -->|BSON / TLS / Port 27017| Mongo[(MongoDB Atlas Replica Set)]
    CoreAPI -->|Multiplexed TCP / Port 6379| Redis[(Redis Enterprise Cluster)]
    CoreAPI -->|Enqueue Task (MsgPack)| ArqQ[Arq Job Queue in Redis]
    
    Analytics -->|Pub/Sub Event Bus| Redis
    
    ArqQ -->|Process Task| Worker[Async Worker Nodes (Horizontally Scaled)]
    Worker -->|SMTP / External HTTPS| ExternalServices[Third-Party Services (Sendgrid, Stripe)]
    
    %% Security Isolation Boundaries
    subgraph DMZ [Demilitarized Zone]
        Gateway
    end
    
    subgraph Compute [Stateless Compute Cluster]
        CoreAPI
        Analytics
        Worker
    end
    
    subgraph State [Stateful Persistence Layer]
        Mongo
        Redis
        ArqQ
    end
```

### 2.1. The Edge Presentation Layer (Client & CDN)
*   **Asset Delivery**: Static assets (HTML/CSS/JS, WebP/JPG images, MP4 video streams) are delivered via a globally distributed Content Delivery Network (Cloudflare) utilizing Edge Compute nodes for localized caching. The Cache-Control headers are aggressively tuned to `max-age=31536000` for immutable media assets.
*   **State Management**: Ephemeral guest states (e.g., Unauthenticated Cart permutations, dark mode preferences) are stored locally in the browser's `localStorage` and `IndexedDB`. This entirely eliminates server-side memory overhead until a formal cryptographic authentication handshake occurs.
*   **Media Streaming**: High-definition video files (`frontend/videos/roastery-process.mp4`) support HTTP 206 Partial Content range requests for instant scrubbing without buffering delays.
*   **Service Workers**: A Progressive Web App (PWA) service worker intercepts network requests, providing offline fallback UI and caching critical API payloads.

### 2.2. The Core API Gateway (Quart / Python ASGI)
*   **Framework**: Built on `Quart`, an ASGI microframework allowing native `async`/`await` primitives while preserving Flask-compatible routing structures.
*   **Concurrency Model**: Executed within a single-threaded ASGI event loop per CPU core, orchestrated by Hypercorn or Uvicorn. I/O wait times (Database queries, Redis calls) yield execution context back to the event loop. This allows a single CPU core to maintain tens of thousands of concurrent TCP sockets.
*   **Stateless Execution**: The API Gateway maintains absolutely zero runtime state. It acts strictly as a data-transformation pipe. All session memory is entirely offloaded to cryptographically signed JWTs and Redis cache vectors. A gateway container can be arbitrarily killed and respawned without dropping any user state.

### 2.3. The Persistence Layer (MongoDB Atlas & Beanie ODM)
*   **NoSQL Engine**: We utilize a MongoDB Atlas replica-set cluster (minimum 3 nodes across diverse availability zones) for durable, schema-flexible storage.
*   **Object-Document Mapper (ODM)**: `Beanie` handles asynchronous object mapping. All data ingress is fiercely guarded by `Pydantic` v2 schema validations. This forces strict type-coercion before data is ever marshaled into raw BSON strings.
*   **Document Models**:
    1. `User`: Customer and staff credentials, encrypted PII, and TOTP MFA secrets.
    2. `Product`: Specialty whole bean packs (*Coal Black*, *Experimental Lot*), barista apparel, ceramic stoneware, and bakery inventory.
    3. `Order`: Click-and-collect orders with customer details, collection times, and statuses.
    4. `Enquiry`: Gathering reservations, salon bookings, and contact inquiries.
    5. `Cart`: Persistent synchronized multi-device user carts.
    6. `AuditLog`: Immutable write-once administrative mutations.

### 2.4. The Caching & State Layer (Redis Enterprise)
*   Redis acts as the central nervous system for ephemeral, high-velocity state.
*   **GCRA Rate Limiting**: Redis holds the temporal buckets for the Generic Cell Rate Algorithm to strictly throttle incoming client traffic. This is implemented via LUA scripts to ensure absolute atomicity.
*   **Token Blacklisting**: Revoked or logged-out JWT hashes are stored in Redis with an absolute Time-To-Live (TTL) matching the token's original expiration epoch. A background sweep clears out dead tokens, maintaining low memory footprints.
*   **Pub/Sub Bus**: The Analytics engine uses Redis Pub/Sub channels to broadcast real-time telemetry across all disconnected WebSocket nodes.

### 2.5. Background Task Processing (Arq)
*   **The Queue**: Heavy computational tasks, such as triggering transactional SMTP emails, generating comprehensive financial reports, or recalculating massive cart vectors, are offloaded to an asynchronous Redis-backed queue powered by `arq`.
*   **Worker Nodes**: Independent `arq` daemon processes consume the queue. These workers run in completely separate orchestration environments, shielding the Core API Gateway from CPU-bound starvation. They implement exponential backoff retry algorithms for handling transient third-party API failures.

## 3. Data Integrity & Concurrency Strategies

### 3.1. Distributed Cart Synchronization
To solve the complex problem of state-merging between anonymous users and authenticated profiles, Boojee relies on a differential merge algorithm:
1. User operates anonymously; state lives in `localStorage`.
2. User authenticates via `/api/login`.
3. Client dispatches the entire local cart vector to `/api/cart`.
4. The Core API validates the payload, executes a differential update against the persistent MongoDB user document, and returns the merged synchronized state.

### 3.2. Lockless Event Processing
Because the Core API uses Python's `asyncio` single-threaded event loop, race conditions regarding shared memory *within* a single gateway instance are theoretically impossible (cooperative multitasking). For cross-cluster concurrency, we rely exclusively on atomic transactions at the MongoDB document layer and atomic Redis `INCR` sequences.

## Mobile App Support (Capacitor)
This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.
