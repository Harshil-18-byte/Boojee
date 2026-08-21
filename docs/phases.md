# Boojee Evolution Phases

This document tracks the architectural shifts and strategic development phases of the Boojee Platform. It serves to document our historical engineering decisions, explain why certain technical debts were incurred and resolved, and outline our forward-looking trajectory.

## Phase 1: The Monolithic Foundation (v1.x)
**Status**: Deprecated / Tagged `v1.0` / EOL (End of Life)

The original instantiation of Boojee was designed as a rapid Minimum Viable Product (MVP) to establish market viability, define core business logic, and secure initial user traction.

*   **Database Architecture**: Utilized a rigid, schema-bound SQL relational model. Development environments utilized SQLite, while production relied on PostgreSQL. Data mapping was handled via SQLAlchemy ORM.
*   **Execution Model**: Synchronous Flask WSGI blocking paradigm. Every HTTP request occupied a dedicated OS thread.
*   **State Management**: Relied heavily on traditional session-based, server-side states which complicated horizontal scaling.
*   **The Catalyst for Change**: As user concurrency spiked during flash sales, the blocking WSGI threads suffered severe starvation during heavy database I/O. The platform reached a vertical scaling limit, prompting the v2.0 rewrite.

## Phase 2: The Distributed Ecosystem (v2.x) - *Current Core*
**Status**: Active Production (`main`) / LTS (Long Term Support)

A complete, ground-up architectural rewrite engineered for high-availability, aggressive security posturing, and sub-second operational latency.

*   **Asynchronous Paradigm**: Total migration to the ASGI standard utilizing the `Quart` framework with non-blocking `await` coroutines.
*   **NoSQL Migration**: SQLAlchemy and Alembic were replaced with a horizontally scalable MongoDB Atlas backend coupled with the `Beanie` asynchronous ODM.
*   **Event-Driven Background Workers**: Heavy computational loads (SMTP dispatch, report generation) are shunted to independent `arq` worker daemons via Redis.
*   **Cryptographic Security Core**: Implementation of RFC 6238 TOTP Multi-Factor Authentication, strict JWT stateless sessions, and a mathematically rigorous GCRA Redis-backed rate limiting penalty box.
*   **Immutable Telemetry**: All administrative actions are permanently inscribed into a WORM (Write-Once, Read-Many) MongoDB audit ledger.

## Phase 3: Brand Media Harmonization & Full-Stack Enrichment (v2.2) - *Completed*
**Status**: Active Production (`main`)

Ingestion of the complete authentic asset archive from [boojeecafe.com](https://boojeecafe.com) and platform-wide synchronization:

*   **Authentic Multimedia Pipeline**: 4K MP4 Roastery process video player, 12-item visual gallery with interactive Lightbox, and CDN-optimized merchandise/coffee bean inventory.
*   **OLED Pure Black Dark Mode**: Overhauled dark mode into a true OLED black (`#000000`) canvas with high-contrast text and interactive white button controls.
*   **Enquiry & Table Booking Subsystem**: Built backend `/api/enquiries` route with Beanie `Enquiry` model and interactive client confirmation cards (`visit.html`, `contact.html`).
*   **Universal 15-Page Directory Footer**: Standardized directory navigation across all pages of the site.

## Phase 4: The Edge Intelligence Tier (v3.x) - *Future Roadmap*
**Status**: R&D / Prototyping / Active Sprints

*   **AI-Driven Recommendation Engine**: Integration of Vector Databases (e.g., Pinecone/Milvus) with sentence-transformers for real-time flavor profiling suggestions based on cosine similarity.
*   **GraphQL Aggregation Layer**: Introduction of a flexible GraphQL gateway (utilizing Strawberry or Ariadne) to eliminate over-fetching across mobile and web clients.
*   **Kubernetes (K8s) Orchestration**: Migration to a fully declarative Kubernetes cluster with Horizontal Pod Autoscaling (HPA) and zero-downtime rolling updates.
*   **Wasm (WebAssembly) Edge Computing**: Pushing cart synchronization logic and JWT verification directly to Cloudflare/AWS Edge nodes via WebAssembly.

## Mobile App Support (Capacitor)
This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.
