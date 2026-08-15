# Security Policy

## Supported Versions

Currently, only the latest `main` branch of **Boojee Cafe** is actively supported with security updates. 

| Version | Supported          |
| ------- | ------------------ |
| Main    | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of this project seriously. If you discover a security vulnerability within Boojee Cafe, please follow these steps to report it:

1. **Do not open a public issue.** This ensures that the vulnerability is not exploited before a patch is released.
2. **Email the maintainers directly** at `security@boojee.cafe` (or the repository owner's email).
3. Include the following details in your report:
   - A description of the vulnerability and its potential impact.
   - Detailed steps to reproduce the issue.
   - Any proposed fixes or recommendations if you have them.

We will acknowledge receipt of your vulnerability report within 48 hours and strive to send you regular updates about our progress. Once the issue is resolved, we will publish a security advisory and notify you.

## Current Security Mechanisms

- **Authentication**: We use `PyJWT` for stateless, secure session management.
- **Passwords**: All passwords are hashed using `werkzeug.security` (PBKDF2 HMAC SHA256) before being stored in the database.
- **Cart Syncing**: API endpoints manipulating user data require a valid `Bearer` token in the `Authorization` header.
- **Rate Limiting**: Endpoints such as `/api/login` and `/api/register` are protected against brute-force attacks via strict IP-based rate limiting.
- **Cross-Site Scripting (XSS) Prevention**: All user-provided data (e.g., during checkout or profile management) is thoroughly sanitized both server-side (`html.escape`) and client-side (`window.escapeHTML`) prior to storage and rendering.
- **HTTP Security Headers**: The application uses robust security headers, including `Content-Security-Policy (CSP)`, `Strict-Transport-Security (HSTS)`, `X-Frame-Options`, and `X-Content-Type-Options` to mitigate common browser-based attacks.
