# Support & Service Level Agreements (SLA)

This document outlines the official support channels, incident response matrices, escalation paths, and operational guarantees for the Boojee Platform ecosystem.

## 1. Support Tiers & Service Level Agreements

### Tier 1: Community Support (Open Source)
For independent developers, researchers, students, and community contributors utilizing the Boojee source code without a commercial SLA.
*   **Channel**: GitHub Discussions & GitHub Issues.
*   **Scope**: Bug reports, feature requests, local development environment setup, and basic architectural queries.
*   **Response Time (Target)**: Best effort (typically 48 - 72 hours).
*   **Limitations**: We do not provide architectural consulting, direct production debugging, or guarantee patches for free-tier users. Issues are triaged based on community impact.

### Tier 2: Enterprise Commercial Support (Standard SLA)
For organizations operating the Boojee Platform under a commercial enterprise license, running active revenue-generating instances.
*   **Channel**: Dedicated Jira Service Desk Portal & Private Slack Connect channels.
*   **Scope**: Production deployment assistance, architectural scaling consulting, advanced integrations, and custom telemetry dashboard configurations.
*   **Response Time (SLA)**: 
    *   *Severity 4 (Trivial)*: 72 Hours.
    *   *Severity 3 (Minor)*: Next Business Day.
    *   *Severity 2 (Major - Degraded Performance)*: 4 Hours (24/7/365).
*   **Contact**: Initiated via your organization's designated Account Executive.

### Tier 3: Critical Incident Response (Severity 1 SLA)
For complete systemic failure, catastrophic data loss, database corruption, or active security breaches impacting commercial deployments.
*   **Channel**: Direct PagerDuty emergency hotline and dedicated escalation email.
*   **Response Time (SLA)**: < 15 Minutes (24/7/365).
*   **Execution**: Activates the emergency Technical Steering Committee (TSC) war room. A dedicated Incident Commander (IC) is assigned to coordinate the engineering response, communicate with stakeholders, and implement the disaster recovery runbook.

## 2. Security Vulnerability Reporting (Bug Bounty)

Under **no circumstances** should security vulnerabilities be reported via public GitHub Issues, Community Discussions, or public Slack channels. 

If you have discovered a zero-day exploit, cryptographic weakness, cross-site scripting (XSS) payload, or NoSQL injection vector:
1.  Consult the Coordinated Vulnerability Disclosure (CVD) process outlined in `SECURITY.md`.
2.  Immediately email `security-ops@boojee.invalid` with a PGP-encrypted payload detailing the exact reproduction steps. Do not include theoretical exploits; provide a working Proof of Concept (PoC).
3.  **Bug Bounty**: Eligible vulnerability disclosures are subject to the Boojee Bug Bounty Program (managed via HackerOne). Payouts are determined by the CVSS 3.1 base score, ranging from $50 (Low) to $10,000+ (Critical/Remote Code Execution).

## 3. Bug Report Requirements

When submitting a bug to GitHub Issues, you must provide a deterministic reproduction path. Ambiguous or incomplete reports will be automatically closed by our triage bots without human review.

Your report **MUST** include:
1.  **Environment Context**: 
    *   The exact Git commit hash of your deployment.
    *   Your Python environment version (e.g., 3.11.4).
    *   Your OS architecture (e.g., Ubuntu 22.04 LTS / macOS Sonoma / Windows 11).
2.  **Telemetry Logs**: Sanitized gateway logs demonstrating the failure (ensure no PII or JWTs are included).
3.  **Reproduction Matrix**: A minimal, self-contained script or `curl` command capable of reproducing the issue on a completely fresh, unconfigured deployment.
4.  **Expected vs Actual**: A clear mathematical or logical explanation of what the system *should* have done, versus what it *actually* did.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

