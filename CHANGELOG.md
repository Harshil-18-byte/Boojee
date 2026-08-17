# Changelog

All notable changes to the Boojee Platform will be documented in this file.

The format is strictly based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) (MAJOR.MINOR.PATCH).

---

## [Unreleased]
*Any features currently merged into `main` but not yet tagged in a formal release.*

### Added
- GitHub Actions CI/CD pipeline definitions for automated linting and testing.
- `.github/pull_request_template.md` to enforce contribution standards.

---

## [2.0.0] - 2026-08-17

This represents a monumental paradigm shift for the platform, moving from a synchronous monolithic state to a highly distributed, asynchronous microservice topology.

### Added
- **MongoDB NoSQL Integration**: Completely migrated the persistence layer to MongoDB utilizing the `Beanie` asynchronous ODM for vastly improved schema flexibility and lockless concurrency.
- **Background Worker Fleet**: Integrated `arq` and Redis to offload heavy computational algorithms and SMTP dispatching away from the main ASGI event loop.
- **Generic Cell Rate Algorithm (GCRA)**: Built a Redis-backed rate limiting penalty box (via `quart-rate-limiter`) to mathematically neutralize brute-force login attempts and Layer 7 volumetric attacks.
- **Multi-Factor Authentication (MFA)**: Implemented RFC 6238 Time-Based One-Time Passwords (TOTP) utilizing the `pyotp` library for administrative and high-privilege access vectors.
- **Immutable Audit Trails**: Engineered a dedicated Write-Once-Read-Many (WORM) MongoDB collection to permanently record all sensitive security and administrative operations with microsecond precision.
- **Pydantic Validation**: All ingress payloads are now strictly type-coerced via Pydantic v2 models to eliminate BSON-injection vulnerabilities and guarantee structural data integrity.
- **Redis Token Blacklisting**: Implemented O(1) time-complexity token revocation using Redis TTLs, allowing instant global logout capabilities.

### Changed
- Re-engineered the underlying Python framework to fully support `async`/`await` paradigms via `Quart`, replacing the synchronous `Flask` framework.
- Re-architected `tests/test_backend.py` to seamlessly execute against `mongomock-motor` to support isolated local pipeline verification without requiring a live Atlas cluster. Included monkey-patches for `authorizedCollections`.
- Hardened `docker-compose.yml` to securely consume isolated `.env` credential files, removing local database footprints in favor of managed cloud clusters.
- Updated `.gitignore` to strictly exclude all `*.env` files to prevent catastrophic credential leaks.

### Removed
- **SQLAlchemy & Alembic**: Entirely deprecated and excised the relational database ORM, the `sqlite` driver dependencies, and its corresponding migration tree (`migrations/` directory).
- Deprecated all blocking I/O calls within the API gateway.

### Security
- Purged all legacy sensitive credentials from the git history that were accidentally committed in prior iterations.
- Upgraded cryptographic hashing parameters for PBKDF2 to increase iteration counts, mitigating offline dictionary attacks.

---

## [1.0.0] - Prior Architectural State (Tagged)

### Added
- Minimum Viable Product (MVP) core business logic, cart routing definitions, and checkout flow.
- Monolithic PostgreSQL / SQLite relational architecture via SQLAlchemy.
- Ephemeral client-side `localStorage` synchronized cart mapping logic.
- Baseline JSON Web Token (JWT) stateless session issuing.
- Frontend rendering architecture utilizing standard HTML/CSS templates.
- Basic `.env` configuration loader.
