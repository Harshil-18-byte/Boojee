import asyncio
import os
from arq.connections import RedisSettings

async def send_newsletter_email(ctx, email: str):
    """
    Background task to send a newsletter confirmation email.
    """
    print(f"[WORKER] Simulating sending newsletter email to: {email}")
    await asyncio.sleep(2) # Simulate network IO
    print(f"[WORKER] Successfully sent email to: {email}")
    return True

class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(
        os.environ.get('REDIS_URL', 'redis://localhost:6379')
    )
    functions = [send_newsletter_email]
