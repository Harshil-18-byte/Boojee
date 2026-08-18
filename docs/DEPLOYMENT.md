# Production Deployment Topologies

This document outlines the strict operational procedures required to transition the Boojee Platform from a localized development environment into a highly available, globally distributed production state.

## 1. Cloud Agnostic Orchestration (Docker Compose)
The platform is fully containerized and designed to be strictly cloud-agnostic. While Kubernetes (K8s) is planned for Phase 3 of our roadmap, the current v2.0 architecture utilizes a highly optimized Docker Compose stack for deployment on bare-metal hardware or EC2 instances.

### 1.1. Prerequisite External Infrastructure
Before initiating the application gateway, the following managed services must be provisioned and their connection strings securely injected into the `.env` file via CI/CD pipelines:
1.  **MongoDB Atlas**: Minimum M10 Dedicated Cluster. Must have a replica set enabled (minimum 3 nodes) distributed across multiple Availability Zones to survive datacenter failures.
2.  **Redis**: Managed Redis Cluster (e.g., AWS ElastiCache, Redis Enterprise) for GCRA rate limiting and Arq task queues. Do not run Redis locally in production; it must be a managed service to survive instance failures.
3.  **SMTP Provider**: Mailgun/Sendgrid credentials for transactional routing.
4.  **Cloudflare**: The domain must be proxied through Cloudflare with strict SSL/TLS (Full Strict mode) enabled.

### 1.2. Environment Variable Secrecy (Secret Zero)
**CRITICAL**: You must never deploy with the default development `.env` configuration. You must generate a production `atlas-credentials.env` file injected securely via GitHub Actions Secrets or HashiCorp Vault.
```bash
# Example Secure .env Structure (atlas-credentials.env)
MONGO_URI=mongodb+srv://<admin-user>:<secure-password>@cluster0.mongodb.net/boojee_prod?retryWrites=true&w=majority
REDIS_URI=redis://:<secure-password>@production-redis.internal:6379/0
# Cryptographic Seed: Must be a 64-byte url-safe token. If this changes, all active JWTs are instantly invalidated.
SECRET_KEY=<generate via: python -c 'import secrets; print(secrets.token_urlsafe(64))'>
# SMTP Configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=<secure-sendgrid-api-key>
```

### 1.3. Execution Sequence
To deploy the isolated microservices, execute the following from the root directory on the host machine:
```bash
# Pull latest images from the registry (GHCR)
docker-compose -f docker-compose.prod.yml pull

# Bring up the stack in detached mode, forcing recreations
docker-compose -f docker-compose.prod.yml up -d --build
```
This command provisions the Quart API Gateway, the static NGINX file server (configured as a reverse proxy), and the asynchronous `arq` worker daemons in isolated, restart-secured containers.

## 2. CI/CD Pipeline (GitHub Actions)
Deployments are fully automated via GitHub Actions to eliminate human error during release cycles. Manual SSH deployments are strictly prohibited.

1.  **Trigger**: Pushing a tagged release (e.g., `git tag v2.0.1 && git push --tags`) triggers the production pipeline.
2.  **Test Matrix**: The pipeline boots a localized `mongomock` instance and executes the entire `pytest` suite.
3.  **Static Analysis**: `flake8` and `mypy` scan the repository for syntax errors and typing failures. `bandit` and `trufflehog` scan for known security vulnerabilities and accidentally committed secrets.
4.  **Container Registry**: The application is built and packaged into a minimal Alpine Linux Docker image and pushed to the GitHub Container Registry (GHCR).
5.  **Deployment**: Upon successful validation, the GitHub Runner connects to the production Swarm via SSH, pulls the latest tagged image, and triggers a zero-downtime rolling restart of the Quart containers.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

