# Code of Conduct

The Boojee Platform operates under a strict, enterprise-grade professional code of conduct. This repository is maintained by a coalition of staff engineers, external contributors, and open-source advocates. We expect all interactions to remain strictly professional, objective, and laser-focused on engineering outcomes.

## 1. Core Tenets & Engineering Culture

*   **Objective Engineering**: Technical decisions must be driven by empirical data, architectural merit, mathematical proofs, and systemic stability—never by ego or personal preference.
*   **Constructive Disagreement**: Vigorous architectural debates are expected and encouraged. However, critiques must focus exclusively on the code, its computational complexity (Big O notation), and its systemic impact, never on the individual author.
*   **Blameless Post-Mortems**: When production outages occur, we do not hunt for a scapegoat. We hunt for the systemic vulnerability that allowed the human error to cascade into a failure. Root Cause Analyses (RCAs) must focus on process improvement, not personal blame.
*   **Zero-Tolerance**: Harassment, exclusionary behavior, discriminatory language, or unprofessional hostility will not be tolerated under any circumstances.

## 2. Expected Behaviors

To maintain an elite, high-velocity engineering culture, all participants are expected to:
1.  **Use Welcoming Language**: Utilize inclusive language across all issues, pull requests, and communication channels (Slack/Discord/GitHub).
2.  **Graceful Acceptance**: Gracefully accept constructive criticism during code reviews. If an architectural decision is rejected by the Technical Steering Committee (TSC) via an Architectural Decision Record (ADR), respect the consensus and implement the requested pivot.
3.  **Assume Positive Intent**: Assume that reviewers and contributors are acting in the best interest of the platform's stability.
4.  **Mentorship**: Senior engineers are expected to provide actionable, educational feedback to junior contributors rather than simply rejecting PRs with "fix this."

## 3. Unacceptable Behaviors

The following behaviors are strictly prohibited and represent immediate grounds for organizational banishment:
*   The use of sexualized language, imagery, or inappropriate advances.
*   Trolling, insulting/derogatory comments, and personal or political attacks.
*   Public or private harassment of maintainers, contributors, or users.
*   Publishing others' private information (doxing), such as physical or electronic addresses, without explicit cryptographic permission.
*   **"Sealioning"**: Intentionally derailing architectural discussions with bad-faith arguments, repetitive questioning, or feigning ignorance to exhaust the maintainers.
*   **Vulnerability Leaks**: Publicly disclosing a zero-day vulnerability without following the Coordinated Vulnerability Disclosure (CVD) process (see `SECURITY.md`).

## 4. Enforcement and Moderation

### 4.1. Reporting Workflows
Instances of abusive, harassing, or otherwise unacceptable behavior must be reported immediately to the core engineering moderation team at `compliance@boojee.invalid`. All complaints will be reviewed and investigated promptly and fairly by a rotating panel of three TSC members.

*Confidentiality*: The moderation team is legally and ethically bound to maintain strict confidentiality with regard to the reporter of an incident.

### 4.2. Moderation Actions
The Technical Steering Committee retains the right and responsibility to remove, edit, or reject comments, commits, code, wiki edits, issues, and other contributions that are not aligned to this Code of Conduct.

Upon validation of a violation, the TSC may execute the following escalation path:
1.  **Correction**: A private, formal warning from community leaders detailing the nature of the violation and an explanation of why the behavior was inappropriate, with a request for a public or private apology.
2.  **Warning**: An official warning with corresponding temporary suspension (typically 7-14 days) from specific repositories or communication channels.
3.  **Permanent Ban**: A permanent, irrevocable ban from all interactions within the Boojee organization, including the blocking of GitHub accounts and IP addresses from associated services.

## 5. Scope
This Code of Conduct applies within all project spaces, including the GitHub repository, Slack/Discord channels, and official mailing lists. It also applies when an individual is representing the project in public spaces, such as speaking at technical conferences, representing the company at a trade show, or interacting on social media regarding the platform.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

