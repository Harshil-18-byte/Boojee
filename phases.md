# Boojee Evolution Phases

This document tracks the monumental architectural shifts and strategic development phases of the Boojee Platform. It serves to document our historical engineering decisions, explain why certain technical debts were incurred and resolved, and outline our forward-looking trajectory.

## Phase 1: The Monolithic Foundation (v1.x)
**Status**: Deprecated / Tagged `v1.0` / EOL (End of Life)

The original instantiation of Boojee was designed as a rapid Minimum Viable Product (MVP) to establish market viability, define core business logic, and secure initial user traction. Speed of iteration was prioritized over long-term architectural purity.

*   **Database Architecture**: Utilized a rigid, schema-bound SQL relational model. Development environments utilized SQLite, while production relied on PostgreSQL. Data mapping was handled via SQLAlchemy ORM, which inherently introduced N+1 query problems and complex join overheads.
*   **Execution Model**: Synchronous Flask WSGI blocking paradigm. Every HTTP request occupied a dedicated OS thread.
*   **State Management**: Relied heavily on traditional session-based, server-side states which complicated horizontal scaling and required sticky sessions at the load balancer.
*   **Deployment**: Singular containerized orchestration without isolated worker nodes. Background tasks were handled haphazardly via cron or inline execution.
*   **The Catalyst for Change (Limitations Overcome)**: As user concurrency spiked during flash sales, the blocking WSGI threads suffered severe starvation during heavy database I/O. The PostgreSQL database struggled with schema migrations (via Alembic) when rapidly prototyping new product features. The platform reached a hard vertical scaling limit, prompting the v2.0 rewrite.

## Phase 2: The Distributed Ecosystem (v2.x) - *Current*
**Status**: Active Production (`main`) / LTS (Long Term Support)

A complete, ground-up architectural rewrite engineered for high-availability, aggressive security posturing, and sub-second operational latency. This phase represents the maturation of the platform into an enterprise-grade ecosystem.

*   **Asynchronous Paradigm**: Total migration to the ASGI standard utilizing the `Quart` framework. The entire I/O stack (HTTP, Database, Caching) was rewritten to utilize non-blocking `await` coroutines, exponentially increasing throughput.
*   **NoSQL Migration**: SQLAlchemy and Alembic were violently excised. The data layer was migrated to a horizontally scalable MongoDB Atlas backend coupled with the `Beanie` asynchronous ODM. This allowed for embedded documents (e.g., placing Cart items directly inside the User document) which eliminated expensive SQL JOIN operations.
*   **Event-Driven Background Workers**: Heavy computational loads (SMTP dispatch, report generation) are now shunted to independent `arq` worker daemons via Redis, eliminating CPU starvation on the main Gateway.
*   **Cryptographic Security Core**: Complete overhaul of the authentication tier. Implementation of RFC 6238 TOTP Multi-Factor Authentication, strict JWT stateless sessions (eliminating sticky routing), and a mathematically rigorous GCRA Redis-backed rate limiting penalty box.
*   **Immutable Telemetry**: All administrative actions are permanently inscribed into a WORM (Write-Once, Read-Many) MongoDB audit ledger to satisfy strict compliance and non-repudiation requirements.

## Phase 3: The Edge Intelligence Tier (v3.x) - *Future Roadmap*
**Status**: R&D / Prototyping / Active Sprints

The forthcoming phase will shift focus away from foundational stability (which has been achieved) toward advanced machine learning integration, global edge delivery, and zero-trust networking.

*   **AI-Driven Recommendation Engine**: Integration of Vector Databases (e.g., Pinecone/Milvus). We will utilize sentence-transformers to convert product descriptions and user purchasing histories into high-dimensional embeddings, allowing for real-time, context-aware product suggestions based on cosine similarity searches.
*   **GraphQL Aggregation Layer**: Deprecation of the rigid REST API endpoints in favor of a highly flexible GraphQL gateway (utilizing Strawberry or Ariadne). This will allow front-end clients to query exact data shapes, minimizing over-fetching, under-fetching, and multiple network round-trips.
*   **Kubernetes (K8s) Orchestration**: Migration from basic Docker Compose (which lacks robust auto-healing) to a fully declarative Kubernetes cluster. This will feature automatic Horizontal Pod Autoscaling (HPA) based on CPU/Memory metrics, self-healing node replacements, and zero-downtime Canary rolling updates.
*   **Wasm (WebAssembly) Edge Computing**: Pushing cart synchronization logic and JWT verification directly to Cloudflare/AWS Edge nodes via WebAssembly. This aims to achieve literal zero-latency localized executions by processing requests physically closer to the user before they ever hit the core US-East gateway.
*   **Zero-Trust Service Mesh**: Implementing Istio or Linkerd to enforce mutual TLS (mTLS) authentication automatically between all internal microservices (e.g., between the Core API and the Arq Workers), assuming that the internal network is hostile.
