# Comprehensive Security Policy & Hardening Guidelines

The Boojee Cafe platform team treats the security of our distributed application architecture, the integrity of our users' data, and the privacy of their transactions with the utmost seriousness. This document outlines our formal security policy, the scope of our active support, the precise procedures for safely reporting discovered vulnerabilities, and an exhaustive breakdown of the architectural security mechanisms currently implemented within the platform's microservices.

## Supported Versions and Security Patch Lifecycles

We maintain a strict release support lifecycle to ensure that we can dedicate our resources to providing the most secure experience on our active branches. Currently, **only the latest commit on the `main` branch** of the Boojee Cafe platform is actively supported with security updates and patches. 

| Platform Version | Active Support Status | Description & Patch Policy |
| :--- | :--- | :--- |
| **Main Branch (Latest)** | :white_check_mark: Fully Supported | Receives immediate, priority security patches, dependency updates, and architectural hardening. |
| **< 2.0 (Legacy Monolith)**| :x: End of Life (Unsupported) | Will not receive security updates. Users are strongly urged to migrate to the `main` microservice architecture immediately. |

## Safe Vulnerability Reporting Procedure

If you are a security researcher, a penetration tester, or an observant user and you believe you have discovered a security vulnerability within the Boojee Cafe platform, we kindly ask that you follow these strict guidelines to report it responsibly. 

**CRITICAL RULE:** 
1. **Under absolutely no circumstances should you open a public GitHub issue, pull request, or public discussion regarding a suspected vulnerability.** Premature public disclosure puts our users at risk by exposing the flaw to malicious actors before a patch can be developed and deployed.
2. **Direct Communication:** Please email our dedicated security response team directly at `security@boojee.cafe`.

### What to Include in Your Report

To help us validate and remediate the issue as swiftly as possible, please ensure your email report contains the following detailed information:
- **Vulnerability Description**: A comprehensive explanation of the vulnerability, its underlying cause, and its potential impact (e.g., Remote Code Execution, SQL Injection, Cross-Site Scripting, Privilege Escalation).
- **Reproduction Steps**: A detailed, step-by-step guide explaining exactly how to reproduce the vulnerability reliably. If possible, include Proof of Concept (PoC) code or specific HTTP request payloads.
- **Environment Details**: Information about the environment where the bug was observed (e.g., Docker, Render PaaS, Browser version, Python version, OS).
- **Affected Microservice**: Specify whether the vulnerability resides in the Core Backend API, the Analytics Service, or the Frontend static assets.

## Exhaustive Breakdown of Current Security Mechanisms

The Boojee Cafe platform employs a defense-in-depth strategy, integrating multiple layers of security at the application, network, and database levels to protect against modern attack vectors.

### 1. Identity and Access Management (IAM)
- **Secure Cookie JWT Authentication**: We utilize the robust `PyJWT` library for completely stateless, secure session management. Instead of relying on vulnerable `localStorage` for token persistence, JWTs are issued via `HttpOnly`, `Secure`, and `SameSite=Strict` cookies. This effectively neutralizes Cross-Site Scripting (XSS) attacks from stealing session tokens.
- **Role-Based Access Control (RBAC)**: The application features a deeply integrated permission system. Core endpoints strictly validate the cryptographic signature of the token and subsequently verify the `role` (e.g., `user` vs. `admin`). Administrative routes (like managing the blog or retrieving employee telemetry) will aggressively reject requests from non-admin accounts with a `403 Forbidden` response.
- **Cryptographic Password Hashing**: Passwords are never stored in plain text. We utilize `werkzeug.security` to hash all passwords using the computationally intensive **PBKDF2 HMAC SHA256** algorithm. This ensures immense resistance to rainbow table attacks and brute-force guessing.

### 2. Microservice Isolation and Network Security
- **Decoupled Architecture**: By dividing the application into specialized services (Frontend, Backend API, Analytics Engine), we limit the blast radius of any potential compromise. 
- **Waitress Production Server**: The Flask APIs are served by Waitress, a production-quality WSGI server capable of safely handling highly concurrent connections while actively mitigating slowloris and malformed HTTP request attacks.
- **Persistent Disk Security**: In production (e.g., Render.com), SQLite databases (`cafe.db`) are attached to isolated Persistent Disks, ensuring that unauthorized container access does not inherently grant full file-system data exfiltration capabilities.

### 3. API Security and Data Integrity
- **Strict Endpoint Hardening**: All state-changing API endpoints (`POST`, `PUT`, `DELETE`) require rigorous authentication checks and schema validation.
- **SQL Injection Prevention**: All interactions with the database are facilitated through SQLAlchemy ORM. Parameterized queries and statement preparation are enforced globally, completely eliminating the risk of SQL injection vulnerabilities.

### 4. Data Sanitization and Output Encoding
- **Cross-Site Scripting (XSS) Prevention**: We employ rigorous sanitization protocols to prevent malicious script injection. All user-provided data (e.g., blog content, checkout details, newsletter emails) is thoroughly sanitized.
- **Client-Side Rendering Safety**: The vanilla JS frontend utilizes `textContent` and dynamically DOM-escaped rendering utilities to ensure that stored payloads cannot be executed by the browser as malicious HTML.

### 5. Transport and Browser-Level Security
- **HTTP Security Headers**: The application server is configured to inject robust security headers into every HTTP response, mitigating a wide array of common browser-based attacks:
  - **Content-Security-Policy (CSP)**: Strictly defines which dynamic resources are permitted to load, virtually eliminating the risk of loading malicious external scripts.
  - **Strict-Transport-Security (HSTS)**: Forces all client connections to occur over secure HTTPS, preventing Man-in-the-Middle (MitM) protocol downgrade attacks.
  - **X-Frame-Options (`DENY` or `SAMEORIGIN`)**: Prevents the application from being embedded in malicious iframes, completely mitigating clickjacking attacks.
  - **X-Content-Type-Options (`nosniff`)**: Instructs the browser to strictly adhere to the declared MIME types, preventing dangerous MIME-sniffing vulnerabilities.
