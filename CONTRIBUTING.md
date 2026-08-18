# Contributing to the Boojee Platform

Thank you for your interest in contributing to Boojee. Because this platform serves as an enterprise-grade ecosystem processing transactional data and PII, we enforce extremely strict engineering, security, and stylistic protocols. Please read this document entirely before submitting any pull requests. Ignorance of these protocols will result in automated rejection of your contributions.

## 1. Code of Conduct
We operate under a strict professional code of conduct (see `CODE_OF_CONDUCT.md`). All interactions on issues, pull requests, and organizational communication channels must remain respectful, objective, and strictly focused on engineering outcomes. Leave your ego at the door.

## 2. Security Vulnerability Protocol
If you believe you have discovered a vulnerability (e.g., an unhandled injection vector, an exposed secret, a cryptographic flaw, or a business logic bypass), **DO NOT OPEN A GITHUB ISSUE.** 

You must strictly adhere to the Coordinated Vulnerability Disclosure (CVD) Protocol defined in `SECURITY.md`. Public disclosure of vulnerabilities is treated as hostile intent and will result in a permanent ban. Email `security@boojee.invalid` with a PGP-encrypted payload.

## 3. Local Development Environment

We utilize Docker to ensure complete environmental parity between developer machines and production clusters.

### Prerequisites
*   Python 3.11+
*   Docker Engine (v24+) & Docker Compose (v2+)
*   Git (configured with SSH keys and commit signing via GPG/SSH)

### Initialization Sequence
```bash
# 1. Clone your fork
git clone git@github.com:<your-username>/Boojee.git
cd Boojee

# 2. Configure isolated virtual environment
cd backend
python -m venv venv
# Activate the environment:
# Linux/macOS: source venv/bin/activate
# Windows: .\venv\Scripts\activate

# 3. Install dependencies (utilizing strict hash-checking if possible)
pip install -r requirements.txt
pip install -r requirements-dev.txt # Installs pytest, flake8, black, etc.

# 4. Boot the support infrastructure (MongoDB, Redis) via Compose
cd ..
docker-compose -f docker-compose.dev.yml up -d redis mongodb
```

## 4. Branching Strategy & GitFlow

We follow a strict, modified GitFlow branching model:
*   `main`: Represents the active, highly unstable production deployment. Commits directly to main are mathematically blocked by GitHub Branch Protection rules.
*   `feature/<ticket-id>-<brief-desc>`: For all new capabilities (e.g., `feature/BOO-412-add-stripe-webhooks`).
*   `bugfix/<ticket-id>-<brief-desc>`: For non-urgent defect resolution.
*   `hotfix/<ticket-id>-<brief-desc>`: For urgent zero-day patches branching off tagged releases.

Always branch directly from `main`. Do not branch from other feature branches to prevent cascading merge conflicts.

## 5. Coding Standards & Validation

Before you commit, your code must mathematically prove its stability. We do not accept "it works on my machine" as an excuse.

### 5.1. Static Analysis & Linting (Black & Flake8)
We enforce strict adherence to PEP 8, augmented by the `black` opinionated formatter.
```bash
# Format your code first
black backend/

# Run the strict linter
flake8 backend/ --max-line-length=100 --ignore=E203,W503
```
Any warnings or errors thrown by the linter will automatically fail the GitHub Actions CI/CD pipeline.

### 5.2. Type Hinting (Mypy)
All Python code must be statically typed. We enforce `mypy` checks. Missing type hints on function signatures will fail the build.
```bash
mypy backend/ --disallow-untyped-defs
```

### 5.3. Test Driven Development (TDD)
You must provide corresponding unit tests for every logical branch in your code. We utilize `pytest` combined with `mongomock-motor` for isolated database testing. We do not use live databases for unit tests to ensure hermetic execution.
```bash
# Run the test suite with coverage
pytest tests/ -v --cov=app --cov-report=term-missing
```
Coverage must not drop below 95%. If you add a new route, you must add tests covering the HTTP 200, 400, 401, and 422 scenarios.

## 6. The Pull Request (PR) Lifecycle

1. **Commit Convention**: Commit messages must be atomic and follow the Conventional Commits specification.
   *   *Good*: `feat(auth): implement totp verification window`
   *   *Good*: `fix(cart): resolve race condition in quantity increment`
   *   *Bad*: `fixed stuff and updated some things`
2. **Rebase**: Before opening a PR, rebase your branch against `main` to ensure a clean, linear history. `git pull --rebase origin main`.
3. **Open the PR**: Push your branch to your fork and open a PR against our `main` branch.
4. **PR Template**: You must fill out the provided PR template, explicitly detailing the architectural impact, the testing vectors applied, and the specific Jira/Linear issue resolved. Check all boxes.
5. **Peer Review**: At least two Staff Engineers must approve your PR. You are expected to gracefully handle architectural critiques and refactor your code as requested.
6. **Squash and Merge**: Once approved, your PR will be squash-merged by a maintainer to preserve a pristine git history.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

