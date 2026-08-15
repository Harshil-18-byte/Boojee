# Comprehensive Security Policy & Hardening Guidelines

The Boojee Cafe platform team treats the security of our application, the integrity of our users' data, and the privacy of their transactions with the utmost seriousness. This document outlines our formal security policy, the scope of our active support, the precise procedures for safely reporting discovered vulnerabilities, and an exhaustive breakdown of the architectural security mechanisms currently implemented within the platform.

## Supported Versions and Security Patch Lifecycles

We maintain a strict release support lifecycle to ensure that we can dedicate our resources to providing the most secure experience on our active branches. Currently, **only the latest commit on the `main` branch** of the Boojee Cafe platform is actively supported with security updates and patches. 

| Platform Version | Active Support Status | Description & Patch Policy |
| :--- | :--- | :--- |
| **Main Branch (Latest)** | :white_check_mark: Fully Supported | Receives immediate, priority security patches, dependency updates, and architectural hardening. |
| **< 1.0 (Legacy Releases)**| :x: End of Life (Unsupported) | Will not receive security updates. Users are strongly urged to migrate to the `main` branch immediately. |

## Safe Vulnerability Reporting Procedure

If you are a security researcher, a penetration tester, or an observant user and you believe you have discovered a security vulnerability within the Boojee Cafe platform, we kindly ask that you follow these strict guidelines to report it responsibly. 

**CRITICAL RULE:** 
1. **Under absolutely no circumstances should you open a public GitHub issue, pull request, or public discussion regarding a suspected vulnerability.** Premature public disclosure puts our users at risk by exposing the flaw to malicious actors before a patch can be developed and deployed.
2. **Direct Communication:** Please email our dedicated security response team directly at `security@boojee.cafe` (or reach out privately to the primary repository owner's registered email address if the aforementioned address is unresponsive).

### What to Include in Your Report

To help us validate and remediate the issue as swiftly as possible, please ensure your email report contains the following detailed information:
- **Vulnerability Description**: A comprehensive explanation of the vulnerability, its underlying cause, and its potential impact (e.g., Remote Code Execution, SQL Injection, Cross-Site Scripting, Privilege Escalation).
- **Reproduction Steps**: A detailed, step-by-step guide explaining exactly how to reproduce the vulnerability reliably. If possible, include Proof of Concept (PoC) code or specific HTTP request payloads.
- **Environment Details**: Information about the environment where the bug was observed (e.g., Browser version, Python version, OS).
- **Proposed Remediation (Optional but Appreciated)**: Any proposed code fixes, architectural changes, or mitigation recommendations you might have.

### Our Commitment to Researchers

Upon receiving your report, our security team commits to the following timeline:
- **Initial Acknowledgment**: We will acknowledge receipt of your vulnerability report within **48 hours**.
- **Investigation & Patching**: We will strive to send you regular, transparent updates about our investigative progress and our timeline for developing a patch.
- **Disclosure & Credit**: Once the issue is fully resolved and the patch has been safely deployed across our infrastructure, we will publish a coordinated security advisory. If desired, we will publicly credit you for your responsible discovery and disclosure.

## Exhaustive Breakdown of Current Security Mechanisms

The Boojee Cafe platform employs a defense-in-depth strategy, integrating multiple layers of security at the application, network, and database levels to protect against modern attack vectors.

### 1. Identity and Access Management (IAM)
- **Stateless JWT Authentication**: We utilize the robust `PyJWT` library for completely stateless, secure session management. This eliminates the need for server-side session stores and minimizes the attack surface associated with traditional session hijacking.
- **Cryptographic Password Hashing**: Passwords are never stored in plain text. We utilize `werkzeug.security` to hash all passwords using the computationally intensive **PBKDF2 HMAC SHA256** algorithm. This ensures immense resistance to rainbow table attacks and brute-force guessing.

### 2. API Security and Authorization
- **Strict Cart & Profile Syncing**: All state-changing API endpoints that manipulate user data or process transactions explicitly require a cryptographically valid, non-expired `Bearer` token to be passed in the HTTP `Authorization` header. Requests lacking this are immediately rejected with a `401 Unauthorized` response.
- **Endpoint Rate Limiting (Throttling)**: Critical endpoints, specifically `/api/login` and `/api/register`, are heavily protected against automated credential stuffing and brute-force attacks via strict IP-based and token-based rate limiting algorithms.

### 3. Data Sanitization and Output Encoding
- **Cross-Site Scripting (XSS) Prevention**: We employ rigorous sanitization protocols to prevent malicious script injection. All user-provided data (e.g., during checkout procedures, profile management, or address input) is thoroughly sanitized. 
  - **Server-Side**: Processed using Python's `html.escape` to neutralize HTML entities before database insertion.
  - **Client-Side**: Dynamically escaped using `window.escapeHTML` utilities prior to being rendered in the DOM, ensuring that stored payloads cannot be executed by the browser.

### 4. Transport and Browser-Level Security
- **HTTP Security Headers**: The application server is configured to inject robust security headers into every HTTP response, mitigating a wide array of common browser-based attacks:
  - **Content-Security-Policy (CSP)**: Strictly defines which dynamic resources are permitted to load, virtually eliminating the risk of loading malicious external scripts.
  - **Strict-Transport-Security (HSTS)**: Forces all client connections to occur over secure HTTPS, preventing Man-in-the-Middle (MitM) protocol downgrade attacks.
  - **X-Frame-Options (`DENY` or `SAMEORIGIN`)**: Prevents the application from being embedded in malicious iframes, completely mitigating clickjacking attacks.
  - **X-Content-Type-Options (`nosniff`)**: Instructs the browser to strictly adhere to the declared MIME types, preventing dangerous MIME-sniffing vulnerabilities.
