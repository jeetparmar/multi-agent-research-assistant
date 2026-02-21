import asyncio
from typing import List, Callable, Any, Coroutine


# -------------------------------------------------
# 1️⃣ Safe Gather (Doesn't crash entire pipeline)
# -------------------------------------------------
async def safe_gather(tasks: List[Coroutine]) -> List[Any]:
    """
    Runs tasks concurrently.
    If one fails, it returns None for that task instead of crashing.
    """
    results = await asyncio.gather(*tasks, return_exceptions=True)

    safe_results = []
    for result in results:
        if isinstance(result, Exception):
            print(f"[ERROR] Task failed: {result}")
            safe_results.append(None)
        else:
            safe_results.append(result)

    return safe_results


# -------------------------------------------------
# 2️⃣ Timeout Wrapper
# -------------------------------------------------
async def with_timeout(task: Coroutine, seconds: int = 30):
    """
    Adds timeout to async task.
    """
    try:
        return await asyncio.wait_for(task, timeout=seconds)
    except asyncio.TimeoutError:
        print("[TIMEOUT] Task exceeded limit")
        return None


# -------------------------------------------------
# 3️⃣ Retry with Exponential Backoff
# -------------------------------------------------
async def retry_async(
    func: Callable, retries: int = 3, base_delay: float = 1.0, *args, **kwargs
):
    """
    Retry async function with exponential backoff.
    """

    for attempt in range(retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == retries - 1:
                raise e

            sleep_time = base_delay * (2**attempt)
            print(f"[RETRY] Attempt {attempt+1} failed. Retrying in {sleep_time}s")
            await asyncio.sleep(sleep_time)


# -------------------------------------------------
# 4️⃣ Concurrency Limiter (Important for LLM cost)
# -------------------------------------------------
class AsyncLimiter:
    """
    Limits number of concurrent async tasks.
    Useful for:
    - LLM calls
    - Web scraping
    - Rate-limited APIs
    """

    def __init__(self, max_concurrent: int):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def run(self, coro: Coroutine):
        async with self.semaphore:
            return await coro


# -------------------------------------------------
# 5️⃣ Batch Processor
# -------------------------------------------------
async def process_in_batches(
    items: List[Any], processor: Callable, batch_size: int = 5
) -> List[Any]:
    """
    Process items in batches.
    Prevents overwhelming APIs.
    """

    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        tasks = [processor(item) for item in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)

    return results
