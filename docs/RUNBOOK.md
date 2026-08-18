# Emergency Operations Runbook (Playbook)

This runbook outlines the exact, deterministic recovery steps for Tier 3 Critical Incidents (Severity 1). It is intended for On-Call DevOps personnel responding to PagerDuty alerts. Time is of the essence; execute these steps methodically.

## Scenario 1: MongoDB Cluster Unreachable / Connection Timeouts
**Symptoms**: The Core API begins returning mass `500 Internal Server Error` responses. Sentry logs indicate `ServerSelectionTimeoutError` or `pymongo.errors.ConnectionFailure`.

**Immediate Actions**:
1.  **Verify External Status**: Check the MongoDB Atlas status page (`status.mongodb.com`) to determine if it is a localized network issue or a global cloud outage.
2.  **Check IP Whitelists**: Ensure the production application IP addresses (or the VPC peering connection) have not been inadvertently removed from the Atlas Network Access whitelist.
3.  **Circuit Breaker (Self-Preservation)**: If the outage is prolonged, temporarily scale down the API Gateway containers to zero. This prevents aggressive reconnection loops from exhausting the Redis connection pools and causing cascading failures across the remaining healthy infrastructure.
    ```bash
    docker-compose -f docker-compose.prod.yml scale boojee-core-api=0
    ```
4.  **Manual Failover**: If the primary replica node crashed and failed to auto-elect a successor, log into the MongoDB Atlas dashboard and manually trigger a replica-set election to promote a secondary node.

## Scenario 2: Active Layer 7 Application DDoS Attack
**Symptoms**: Massive spikes in inbound traffic. Gateway CPU utilization hits 100%. Legitimate users experience extreme latency (responses > 5 seconds) or `502 Bad Gateway` timeouts from NGINX.

**Immediate Actions**:
1.  **Aggressive Rate Limiting**: Access the production Redis cluster and drastically lower the global GCRA rate limit parameters via `redis-cli`. This instantly drops traffic at the gateway before it hits the database.
    ```bash
    # Connect to redis
    redis-cli -h production-redis.internal -a <password>
    
    # Flush existing penalty boxes to reset counters
    FLUSHDB
    ```
2.  **Edge Mitigation (Cloudflare)**: Log into the Cloudflare dashboard and activate "Under Attack Mode" (I'm Under Attack). This forces Javascript challenges (Turnstile) on all inbound TCP connections, instantly filtering out non-browser traffic.
3.  **Blackhole Offending Subnets**: If the attack stems from a concentrated subnet or ASN, identify the IP range in the NGINX access logs and deploy an active Cloudflare WAF block rule.

## Scenario 3: Accidental Secret Exposure in Git
**Symptoms**: A developer accidentally pushes an `atlas-credentials.env` file, Stripe secret key, or cryptographic JWT seed to the GitHub repository.

**Immediate Actions**:
1.  **DO NOT DELETE THE FILE AND PUSH**. A standard `git rm` commit will leave the secret exposed in the git history for bots to scrape.
2.  **Immediate Rotation**: Immediately log into the compromised service (e.g., MongoDB Atlas, Sendgrid, Stripe) and regenerate the password/API key. The exposed key must be neutralized instantly. Consider all data potentially compromised until rotation is complete.
3.  **Scrub History**: Use the BFG Repo-Cleaner tool to permanently rewrite the git history and forcefully remove the file from all past commits.
    ```bash
    bfg --delete-files atlas-credentials.env
    git reflog expire --expire=now --all && git gc --prune=now --aggressive
    git push origin main --force
    ```
4.  **Incident Report**: File a formal security incident report detailing the exposure duration and the scope of potential data exfiltration.


## Mobile App Support (Capacitor)

This project has been updated to include native mobile app support for iOS and Android using Capacitor. You can find the native wrappers in the `ios/` and `android/` directories. Use `npx cap open android` or `npx cap open ios` to build and deploy to the respective app stores.

