# Compliance & Regulatory Certifications

Because the Boojee platform processes Personally Identifiable Information (PII), shipping addresses, and transactional metadata, it is engineered at its absolute core to strictly adhere to international data privacy frameworks and enterprise audit criteria. Security is not an afterthought; it is mathematically enforced.

## 1. GDPR & CCPA (Data Privacy Mandates)
The platform infrastructure inherently supports strict EU General Data Protection Regulation (GDPR) and California Consumer Privacy Act (CCPA) mandates regarding user sovereignty over their data.

### 1.1. The "Right to be Forgotten" (Data Erasure)
*   **Implementation**: A hard deletion API endpoint `DELETE /api/users/me` exists to instantly purge a user's Document from the MongoDB cluster.
*   **Cascade Erase**: Because the architecture leverages Beanie Document references, deleting the core user identity automatically cascades the destruction of associated telemetry, active cart states, and temporary API keys.
*   **Exceptions (Anti-Fraud)**: To comply with international anti-money laundering (AML) laws and prevent accounting fraud, finalized financial transactions (orders) are anonymized rather than deleted. All PII (names, emails, IP addresses, physical addresses) is wiped, while retaining the mathematical ledger of the transaction (items purchased, tax collected).

### 1.2. Cryptographic Data at Rest
*   **Database Level**: The MongoDB Atlas cluster enforces transparent AES-256 encryption at rest on all storage volumes.
*   **Field-Level Encryption**: Highly sensitive fields within documents (e.g., OAuth tokens, external third-party API keys stored on behalf of the user) are manually encrypted at the Python application layer using the `cryptography.fernet` symmetric encryption library before ever touching the BSON marshaller. Even if a database administrator dumps the entire MongoDB cluster, the sensitive fields remain cryptographically scrambled.

## 2. SOC 2 Type II Audit Readiness
The v2.0 architecture was designed specifically to pass SOC 2 Security, Availability, and Confidentiality trust service criteria.

### 2.1. Immutable Audit Trails (Non-Repudiation)
*   To satisfy compliance auditors regarding administrative oversight, every single high-privilege action (e.g., modifying a user's role, accessing raw telemetry, changing global settings) is cryptographically logged to the `AuditLog` MongoDB collection.
*   **WORM Enforcement**: The application connects to MongoDB using a highly restricted IAM role that physically lacks the `update` or `delete` privileges on the `AuditLog` collection. This enforces a true Write-Once-Read-Many (WORM) ledger. Once an audit event is fired, it cannot be altered or erased by an attacker or a rogue administrator.

### 2.2. Secret Zero & Configuration Management
*   Source code repositories are rigorously scrubbed of secrets. The CI/CD pipeline runs `trufflehog` and `git-secrets` on every commit, aggressively scanning for accidental key inclusions.
*   The platform relies entirely on injected `.env` files mounted securely at runtime via Docker volumes or Kubernetes Secrets. Secrets are never baked into container images or passed via command-line arguments that could be exposed in `ps` dumps.

## 3. Accessibility (WCAG 2.1 AA)
The frontend presentation layer is strictly tested against the Web Content Accessibility Guidelines (WCAG) 2.1 AA standards, ensuring compliance with the Americans with Disabilities Act (ADA).
*   **Contrast Ratios**: The dark-mode HSL color palette guarantees a minimum contrast ratio of 4.5:1 for all textual elements against their backgrounds.
*   **Semantic HTML**: Aggressive use of ARIA attributes, semantic landmarks (`<main>`, `<nav>`, `<aside>`), and entirely keyboard-navigable focus states are enforced by the frontend linter. Mouse navigation is never strictly required to complete a checkout flow.
