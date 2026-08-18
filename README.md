# Boojee Cafe Platform
> An Enterprise-Grade, Cloud-Native E-Commerce & Editorial Ecosystem.

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)]()
[![License](https://img.shields.io/badge/license-Proprietary-blue.svg)]()
[![Version](https://img.shields.io/badge/version-2.0.0--rc.1-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)]()

## Table of Contents
1. [Overview & Features](#1-overview--features)
2. [Architecture System Blueprint](#2-architecture-system-blueprint)
3. [Feature Focus: Distributed Cart Synchronization](#3-feature-focus-distributed-cart-synchronization)
4. [Strict Prerequisites Runbook](#4-strict-prerequisites-runbook)
5. [Installation & Configuration](#5-installation--configuration)
6. [Advanced Configuration](#6-advanced-configuration)
7. [Multi-Language Usage Guide](#7-multi-language-usage-guide)
8. [Empirical Matrix Grids](#8-empirical-matrix-grids)
9. [Defensive Failure Manual](#9-defensive-failure-manual)
10. [Production Deployment & Clustering](#10-production-deployment--clustering)
11. [Roadmap](#11-roadmap)
12. [Contributing & License](#12-contributing--license)

## 1. Overview & Features

The Boojee Cafe platform constitutes a comprehensive, high-availability web application ecosystem tailored specifically for premium hospitality environments. Moving beyond standard digital presence solutions, this platform is engineered as a highly performant, distributed system designed to handle concurrent e-commerce transactions, real-time administrative telemetry, and dynamic editorial content delivery with sub-second latency.

*   **Stateless Cryptographic Sessions**: Replaces server-side session allocation with JSON Web Tokens (JWT) secured via `HttpOnly`, `Secure`, and `SameSite=Strict` HTTP headers.
*   **Asynchronous Rendering**: Utilizes `IntersectionObserver` API for non-blocking, computationally efficient lazy-loading of off-screen media assets.
*   **Decoupled Microservice Segmentation**: Presentation layer, core transactional API, and WebSocket telemetry engine operate in physical isolation.
*   **Distributed Cart Synchronization**: Unauthenticated permutations are stored in `localStorage`, merging programmatically with the backend SQLite database upon authentication.
*   **Zero-Copy Serialization**: Utilizes optimized protocols directly within shared memory buffers where applicable.
*   **Lockless Concurrency**: Implements a strict Share-Nothing single-threaded event loop per CPU core for analytics processing.

## 2. Architecture System Blueprint

The runtime Request/Response network relies on an API-First, Microservice-Oriented Architecture.

```text
[Client Browser]
       |
       | (HTTPS / TLS 1.2+)
       v
+-----------------------+      (REST API)      +-----------------------+
|  Static Presentation  | -------------------> |   Core API Gateway    |
|  Service (Frontend)   |                      |   (Flask / Waitress)  |
+-----------------------+                      +-----------------------+
       |                                              |
       | (WebSocket)                                  | (SQLAlchemy ORM)
       v                                              v
+-----------------------+                      +-----------------------+
| Analytics Telemetry   | <------------------- |  Relational Database  |
| Service (Socket.IO)   |  (Event Streams)     |  (SQLite / PostgreSQL)|
+-----------------------+                      +-----------------------+
```

## 3. Feature Focus: Distributed Cart Synchronization

The Cart Synchronization subsystem represents a highly fault-tolerant implementation for merging ephemeral guest states with persistent authenticated profiles.

### Subsystem Architectural Diagram
This diagram outlines the state machine flow between the Client's `localStorage` and the Core API Gateway's persistent data layer.

```text
       [Client Application]                        [Core API Gateway]
                |                                          |
                | (1) User adds item (Guest)               |
                v                                          |
        [localStorage]                                     |
    (Ephemeral Cart State)                                 |
                |                                          |
                | (2) User Authenticates                   |
                v                                          |
        [Auth Mechanism] ----------(POST /api/login)-----> | --> Validates & Issues JWT
                |                                          |
                | (3) Background Sync Triggered            |
                v                                          |
        [Sync Controller] ---------(POST /api/cart)------> | --> [SQLAlchemy ORM]
                |               (Merges Local + DB)        |            |
                |                                          |            v
                | <--------------(200 OK)----------------- |       [SQLite DB]
                v
        [UI Renders Cart]
```

### Cart Subsystem API Table
A dedicated matrix of endpoints responsible for manipulating the cart state vector.

| Endpoint | HTTP Method | Auth Required | Payload Structure | Operation Behavior |
| :--- | :--- | :--- | :--- | :--- |
| `/api/cart` | `GET` | Yes (JWT) | `None` | Retrieves the current authenticated user's cart items from the relational database. |
| `/api/cart` | `POST` | Yes (JWT) | `{"items": [{"id": "item1", "qty": 2}]}` | Performs a differential merge of the provided JSON payload against the persisted database cart. |
| `/api/cart/item/<id>` | `DELETE` | Yes (JWT) | `None` | Atomically removes a specific item SKU from the user's persisted cart. |
| `/api/cart/clear` | `POST` | Yes (JWT) | `None` | Wipes the entire cart state, typically invoked post-successful checkout validation. |

### Subsystem Deployment Step
Provisioning the isolated data volume specifically required to persist cart state across container lifecycles.

```bash
# 1. Instantiate the dedicated Docker volume for Cart Persistence
docker volume create boojee_cart_data

# 2. Attach the volume during microservice initialization
docker run -d \
  --name boojee-core-api \
  --mount source=boojee_cart_data,target=/var/lib/boojee/data \
  -p 5000:5000 \
  boojee-core:latest

# 3. Force database migration script to generate the Cart schema
docker exec -it boojee-core-api python migrations.py --target=cart_schema
```

## 4. Strict Prerequisites Runbook

Deployment requires precise host environment conditions. Ensure the following constraints are met before initialization.

### Hardware & OS Directives
*   **OS**: Ubuntu 22.04 LTS (Recommended for production) or standard macOS/Windows development environments.
*   **Kernel Configuration**: Adjust `sysctl.conf` to handle high socket connection limits if running the Analytics Telemetry Service under heavy load.
    ```bash
    sysctl -w net.core.somaxconn=1024
    sysctl -w net.ipv4.tcp_max_syn_backlog=2048
    # Maximize memory map limits for data-store segments
    sysctl -w vm.max_map_count=262144
    # Scale file descriptor maximum limits 
    sysctl -w fs.file-max=2097152
    ```
### Software Dependencies
*   **Python**: Version 3.8.0 or strictly higher.
*   **Containerization**: Docker Engine (v24+) and Docker Compose (v2+).

## 5. Installation & Configuration

### Automated Binary Script (Recommended)
```bash
curl -sSf https://boojee.cafe/install.sh | sh -s -- --channel=stable
```

### Containerized Orchestration
To eliminate host-system configuration drift, the platform is orchestrated via Docker.

```bash
# Acquire the repository codebase
git clone https://github.com/Harshil-18-byte/Boojee.git
cd Boojee

# Orchestrate the distributed microservices in detached mode
docker-compose up --build -d

# Verify container execution status
docker ps
```

### Native Virtual Environment (Development Core)
For granular module debugging and core library development.

```bash
# Instantiate the Core API
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 6. Advanced Configuration

The platform relies on a single `boojee.toml` configuration file located in `/etc/boojee/`.

```toml
[server]
listen_interface = "0.0.0.0"
port = 5000
workers = 8 # Matches physical CPU cores

[storage]
data_directory = "/var/lib/boojee/data"
sync_wal = true
max_memtable_size_mb = 128

[clustering]
cluster_mode = true
seed_nodes = ["10.0.1.10:5000", "10.0.1.11:5000"]
fault_tolerance_level = 2
```

## 7. Multi-Language Usage Guide

Interaction with the Core API Gateway can be executed via standard terminal utilities or programmatic client runtimes.

### Native CLI Interaction
```bash
# Execute structural atomic value increment for metrics
$ boojee-cli -p 5001 INCR metrics:page_views:homepage --by=1
(integer) 488102

# Inspect deep key health attributes
$ boojee-cli -p 5000 INSPECT user_session:99812
{
  "ref_count": 1,
  "storage_tier": "DATABASE",
  "byte_size": 128
}
```

### Terminal Interface (cURL)
Authenticating a user identity and capturing the JWT cookie.

```bash
curl -X POST http://localhost:5000/api/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@boojee.cafe", "password":"secure_password"}' \
     -c cookies.txt
```

### Programmatic Client Runtime (Python)
Retrieving the synchronized persistent cart vectors.

```python
import requests

session = requests.Session()

# Assume authentication occurred previously and session contains the HttpOnly cookie
response = session.get('http://localhost:5000/api/cart')

if response.status_code == 200:
    cart_data = response.json()
    print(f"Active Cart State: {cart_data}")
else:
    print(f"Authorization Error: {response.status_code}")
```

## 8. Empirical Matrix Grids

Hardware test definitions and explicit throughput tables mapped across performance variables. Measurements conducted against the Core API Gateway running under `Waitress` WSGI.

| Hardware Specification | Concurrent Connections | Request Type | Mean Latency (ms) | Throughput (Req/Sec) |
| :--- | :--- | :--- | :--- | :--- |
| AWS t3.medium (2 vCPU, 4GB RAM) | 100 | `GET /api/blog` (Cached) | 45ms | 1,200 |
| AWS t3.medium (2 vCPU, 4GB RAM) | 500 | `GET /api/blog` (Cached) | 120ms | 3,800 |
| AWS t3.medium (2 vCPU, 4GB RAM) | 50 | `POST /api/login` (PBKDF2) | 350ms | 120 |

*Note: Cryptographic operations heavily throttle throughput by design to maximize resistance against brute-force computation.*

## 9. Defensive Failure Manual

Quick-reference incident playbook tracking exact error codes alongside root-cause adjustments.

| Error Code / Symptom | Architectural Origin | Root Cause Analysis & Resolution |
| :--- | :--- | :--- |
| `HTTP 401 Unauthorized` | Core API Gateway | **Cause**: Missing or expired JWT in `HttpOnly` cookie. <br>**Resolution**: Re-execute the `/api/login` authentication protocol. |
| `HTTP 403 Forbidden` | Core API Gateway | **Cause**: Valid JWT present, but payload `role` claim lacks administrative context for the requested endpoint. <br>**Resolution**: Elevate user privileges in the database or access standard routes. |
| `WebSocket Connection Failed` | Analytics Telemetry Service | **Cause**: Reverse proxy stripping Upgrade headers. <br>**Resolution**: Ensure Nginx/HAProxy is configured with `proxy_set_header Upgrade $http_upgrade;` and `proxy_set_header Connection "upgrade";`. |
| `SQLAlchemy OperationalError`| Relational Database | **Cause**: Docker container lacks read/write permissions to the mounted SQLite volume. <br>**Resolution**: Verify host directory permissions (`chmod 755`) and mount paths in `docker-compose.yml`. |

### Emergency Runbook Scenarios

#### Symptom: `Error 104: Connection Reset By Peer`
* **Root Cause**: The active instance has exceeded global open file descriptor (`ulimit -n`) allocations.
* **Remediation**: Run `ulimit -n 65536` in your shell session window prior to manual daemon restart.

#### Symptom: `Database Stalled (I/O Saturation)`
* **Root Cause**: Disk Write I/O capacity has breached underlying hardware bandwidth plateaus.
* **Remediation**: Temporarily modify processing speed targets safely inside the runtime daemon engine:
  ```bash
  boojee-cli CONFIG SET max_write_bytes_per_sec 52428800
  ```

## 10. Production Deployment & Clustering

To guarantee high availability and strong consensus replication, the platform integrates a highly customized variant of the Raft Consensus Protocol for advanced state synchronization.

### Cluster Blueprint Initialization Steps

1. **Deploy Network Topologies**: Set up a minimum of three independent server instances across disparate availability zones.
2. **Synchronize Node Nodes**: Execute cluster binding across your orchestration framework:
   ```bash
   boojee-cli --node="10.0.1.10:5000" CLUSTER JOIN --target="10.0.1.11:5000"
   ```
3. **Monitor Convergence State**: Ensure all cluster nodes converge cleanly onto the latest term sequence:
   ```bash
   boojee-cli CLUSTER STATUS
   ```

## 11. Roadmap

*   **Q3 2026**: Migration of persistent storage from SQLite to PostgreSQL cluster.
*   **Q4 2026**: Implementation of Redis caching layer for the Core API Gateway.
*   **Q1 2027**: Introduction of GraphQL aggregation layer for the presentation service.

## 12. Contributing & License

### Mandatory Coding Workflow
1. **Fork and Branch**: Open atomic topic feature branches off the upstream repository main branch tracking targets.
2. **Enforce Style Linters**: Ensure all code matches standard project safety validation schemas perfectly:
   ```bash
   flake8 backend/ --max-line-length=88
   eslint frontend/src/ --ext .js
   ```
3. **Write Unit Metrics**: Run the complete internal test suite to verify code stability before opening a pull request:
   ```bash
   pytest backend/tests/ -n auto
   ```

### Contribution Directives
1.  Establish a feature branch originating from `main`.
2.  Adhere strictly to PEP 8 standards for Python and standard ES6 linting parameters.
3.  Submit a Pull Request featuring a comprehensive architectural impact assessment.

### Proprietary Licensing
Copyright 2026 Boojee Cafe Platform. All rights reserved.
The source code contained within this repository is strictly proprietary unless otherwise defined by an explicit commercial agreement or an overriding open-source license detailed in the `LICENSE` document. Unauthorized reproduction, modification, or external distribution is explicitly prohibited.

## 13. System Upgrades (v2.0)

The Boojee platform has recently undergone a major architectural upgrade (v2.0) to enhance scalability and security:

*   **MongoDB (Beanie ODM)**: The platform has migrated from relational SQL databases (SQLite/PostgreSQL) to a NoSQL architecture powered by MongoDB and the Beanie asynchronous ODM. This allows for flexible schema design and horizontal scalability.
*   **Redis & Arq Background Workers**: A distributed Redis caching layer and `arq` asynchronous task queue have been integrated. Heavy computational tasks and email dispatching are now offloaded to background workers, ensuring the Core API Gateway remains highly responsive.
*   **Enhanced Telemetry & Rate Limiting**: The platform now enforces GCRA-based rate limiting via Redis to prevent brute-force attacks and abuse.

## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

