# Project Governance & Control Structures

The Boojee Platform operates under a formalized, highly structured governance model designed to eliminate ambiguity, ensure rapid security responses, and maintain absolute architectural integrity as the project scales.

## 1. The Technical Steering Committee (TSC)
We explicitly reject the "Benevolent Dictator for Life" (BDFL) model in favor of a consensus-driven Technical Steering Committee. This prevents the platform from being held hostage by a single point of failure or an individual's burnout.

*   **Composition**: The TSC consists of 5 elected Staff/Principal Engineers who have demonstrated sustained, high-impact contributions to the core architecture over a minimum of 18 months.
*   **Authority**: The TSC holds ultimate authority over the repository. This includes:
    *   Final sign-off on Architectural Decision Records (ADRs).
    *   Approval of major version bumps (e.g., v2 to v3).
    *   Coordination of security vulnerability disclosures and zero-day patches.
    *   Enforcement of the Code of Conduct (including issuing permanent bans).
*   **Voting Mechanism**: Changes to the core framework (e.g., the historical migration from SQLAlchemy to the Beanie ODM) require a formal ADR submission and a supermajority (4 out of 5) affirmative vote from the TSC. Simple bug fixes do not require a TSC vote.

## 2. Maintainer Promotion Track
Contributors do not receive commit access by default. We operate on a model of earned trust. Promotion from Contributor to Maintainer is a formal process.

**Requirements for Promotion:**
1.  **Tenure**: A minimum of 6 months of active engagement within the ecosystem.
2.  **Impact**: Submission and successful squash-merge of at least 5 non-trivial features or critical security patches. Documentation updates, while valuable, do not count toward this technical threshold.
3.  **Nomination**: Nomination by an existing TSC member.
4.  **Confirmation**: A simple majority (3 out of 5) confirmation vote from the TSC.

**Maintainer Privileges:**
Maintainers are granted triage rights and merge capabilities on specific, non-critical subsystems (e.g., frontend React components, localized API routes, CI/CD pipeline tweaks). They cannot merge code into the core authentication, cryptography, or database configuration modules without TSC override.

## 3. Architectural Decision Records (ADR)
To prevent the loss of "tribal knowledge" and to permanently document the historical *why* behind massive engineering shifts, all major technical changes must be proposed via an ADR. This prevents circular arguments in the future ("Why did we stop using PostgreSQL?").

### The ADR Lifecycle
1.  **Draft**: An engineer authors an ADR and submits it as a Markdown pull request to the `/docs/adrs` directory.
2.  **Content Requirements**: The ADR must explicitly outline:
    *   **Context**: What is the current bottleneck or problem?
    *   **Proposed Solution**: The technical mechanism to solve it.
    *   **Systemic Consequences**: A brutal, honest assessment of the negative impacts (e.g., increased latency, higher RAM footprint, operational overhead, vendor lock-in).
    *   **Rejected Alternatives**: What else was considered and mathematically proven to be inferior?
3.  **Debate**: The TSC and Maintainers debate the PR on GitHub.
4.  **Ratification**: Only upon a supermajority TSC vote is the ADR merged. The merging of an ADR signals the engineering team to commence implementation. Until the ADR is merged, no code should be written.
