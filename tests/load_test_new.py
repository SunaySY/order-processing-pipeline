import requests
import time
import concurrent.futures
import statistics
from collections import Counter
from typing import Any
from requests import Response

URL = "https://q3j7sz7pxi.execute-api.ap-south-1.amazonaws.com/dev/order"
NUM_REQUESTS = 100
CONCURRENCY = 10


def send_request(i) -> dict[str, Any]:
    payload = {
        "item_name": f"LoadTestItem-{i}",
        "quantity": 1
    }

    start = time.time()

    try:
        resp = requests.post(
            URL,
            json=payload,
            timeout=30
        )

        elapsed = (time.time() - start) * 1000

        return {
            "success": resp.status_code == 201,
            "status_code": resp.status_code,
            "latency_ms": elapsed,
            "response": resp.text
        }

    except Exception as e:
        elapsed = (time.time() - start) * 1000

        return {
            "success": False,
            "status_code": None,
            "latency_ms": elapsed,
            "error": str(e)
        }


def main() -> None:
    results = []

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=CONCURRENCY
    ) as executor:

        futures = [
            executor.submit(send_request, i)
            for i in range(NUM_REQUESTS)
        ]

        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    latencies = sorted(
        [r["latency_ms"] for r in results]
    )

    successes = sum(
        1 for r in results if r["success"]
    )

    failures = [
        r for r in results
        if not r["success"]
    ]

    status_codes = Counter(
        r["status_code"]
        for r in failures
        if r["status_code"] is not None
    )

    errors = Counter(
        r["error"]
        for r in failures
        if "error" in r
    )

    print("\nFailure breakdown:")

    if status_codes:
        for status, count in status_codes.items():
            print(f"  HTTP {status}: {count}")

    if errors:
        for error, count in errors.items():
            print(f"  {error}: {count}")

    print("\nFailed requests:")

    for i, result in enumerate(failures):
        print(
            f"  Request {i}: "
            f"status={result.get('status_code')}, "
            f"response={result.get('response', result.get('error'))}"
        )

    p50 = statistics.median(latencies)
    p99 = latencies[int(len(latencies) * 0.99) - 1]

    print(f"\nTotal requests: {NUM_REQUESTS}")
    print(
        f"Successful: {successes} "
        f"({successes / NUM_REQUESTS * 100:.1f}%)"
    )
    print(f"Failed: {NUM_REQUESTS - successes}")
    print(f"p50 latency: {p50:.0f} ms")
    print(f"p99 latency: {p99:.0f} ms")
    print(f"Min latency: {min(latencies):.0f} ms")
    print(f"Max latency: {max(latencies):.0f} ms")


if __name__ == "__main__":
    main()