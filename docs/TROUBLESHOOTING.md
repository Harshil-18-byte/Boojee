# Troubleshooting & Environmental Triage

This document catalogs common environmental bugs, setup warnings, and runtime errors encountered during local development or staging deployments, along with their immediate, deterministic workarounds.

## 1. Local Development Triage

### 1.1. `ModuleNotFoundError: No module named 'app.models'`
*   **Context**: Typically occurs when running `pytest`, attempting to execute the Quart server directly via `python app.py`, or running a background script.
*   **Root Cause**: Python's `sys.path` module resolution does not automatically include the parent `backend` directory when executing scripts from subfolders (like `tests/`).
*   **Resolution**: Always execute scripts from the absolute root of the repository. If running via terminal, explicitly set the `PYTHONPATH` variable:
    ```bash
    PYTHONPATH=. pytest tests/
    ```

### 1.2. Redis Connection Refused (`ConnectionError`)
*   **Context**: The application crashes immediately on boot with a Redis socket error, or `arq` workers fail to start.
*   **Root Cause**: The local Redis Docker container is either not running, or the `REDIS_URI` in your `.env` is pointing to the wrong port or host.
*   **Resolution**: 
    1. Verify Redis is running: `docker ps | grep redis`
    2. If missing, boot it: `docker-compose -f docker-compose.dev.yml up -d redis`
    3. Ensure `.env` is set to `redis://localhost:6379/0` (if running Quart natively) or `redis://redis:6379/0` (if Quart is running inside Docker).

## 2. Authentication & MFA Triage

### 2.1. TOTP Codes Constantly Rejected (MFA Failures)
*   **Context**: A user attempts to verify an MFA challenge, but valid codes generated from Google Authenticator or Authy are consistently rejected by the API with a 401 Unauthorized.
*   **Root Cause**: Cryptographic Clock Drift. TOTP (Time-Based One-Time Password) algorithms rely on the exact UTC Unix Epoch. If the host server running the Core API has a system clock that has drifted by more than 30 seconds, all MFA verifications will mathematically fail because the temporal windows will not align.
*   **Resolution**: Immediately synchronize the server's hardware clock using the Network Time Protocol (NTP).
    ```bash
    # Force an immediate NTP sync
    sudo ntpdate pool.ntp.org
    # Write the system time to the hardware clock
    sudo hwclock --systohc
    ```

## 3. Database & Testing Triage

### 3.1. `mongomock-motor` Feature Not Implemented
*   **Context**: During `pytest` execution, an error is thrown indicating `NotImplementedError: authorizedCollections is not supported`.
*   **Root Cause**: The testing framework utilizes `mongomock-motor` to simulate MongoDB locally in memory. However, Beanie's `init_beanie` initialization sequence attempts to query database collections using strict parameters that the mock library hasn't fully implemented in their open-source repository.
*   **Resolution**: The v2.0 test suite includes an explicit monkey-patch in `tests/test_backend.py` to overwrite `mongomock.database.Database.list_collection_names`. If you add new Beanie models, ensure they do not invoke unsupported advanced MongoDB aggregation pipelines during initialization.

### 3.2. Beanie Initialization Coroutine Errors
*   **Context**: Application fails to boot, throwing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
*   **Root Cause**: You are attempting to run `await init_beanie()` synchronously, or you are accidentally triggering nested event loops.
*   **Resolution**: Ensure `init_beanie` is exclusively called inside the Quart `before_serving` lifecycle hook, which inherently operates within the established ASGI event loop.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

