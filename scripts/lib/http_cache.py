"""Cached HTTP GET helper (stdlib only).

Responses are cached under <workspace>/.admissions/cache/<source>/<sha256>.json
with a TTL. Keeps DEMO_KEY usage well under rate limits and makes repeat
college-list sessions fast and offline-friendly.
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

USER_AGENT = "admission-skills/1.0 (+https://github.com/emili-kosik/admission-skills)"
DEFAULT_TTL_SECONDS = 7 * 24 * 3600


class HttpError(Exception):
    def __init__(self, status: int, url: str, body: str = ""):
        self.status = status
        self.url = url
        self.body = body[:2000]
        super().__init__(f"HTTP {status} for {url}")


def _cache_file(cache_dir: Path, url: str) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return cache_dir / f"{digest}.json"


def get_json(
    url: str,
    params: dict | None = None,
    *,
    source: str = "generic",
    workspace: Path | None = None,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    use_cache: bool = True,
    timeout: int = 30,
    headers: dict | None = None,
) -> dict:
    """GET a JSON document with optional workspace-scoped caching.

    `params` values that are None are dropped; the canonical URL (sorted
    query string) is the cache key.
    """
    if params:
        clean = {k: v for k, v in sorted(params.items()) if v is not None}
        url = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(clean)

    cache_dir = None
    if workspace is not None:
        cache_dir = workspace / ".admissions" / "cache" / source
        if use_cache:
            f = _cache_file(cache_dir, url)
            if f.is_file():
                try:
                    entry = json.loads(f.read_text(encoding="utf-8"))
                    if time.time() - entry.get("fetched_at", 0) < ttl_seconds:
                        return entry["body"]
                except (OSError, json.JSONDecodeError, KeyError):
                    pass

    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, url, e.read().decode("utf-8", "replace") if e.fp else "") from e
    except urllib.error.URLError as e:
        raise HttpError(0, url, str(e.reason)) from e
    except OSError as e:  # stalled/reset mid-read (incl. TimeoutError)
        raise HttpError(0, url, str(e)) from e

    try:
        body = json.loads(raw)
    except json.JSONDecodeError as e:
        # A 200 with a non-JSON body (captive portal, proxy error page) must
        # surface as a structured HttpError, not a raw traceback.
        raise HttpError(0, url, raw[:500]) from e

    if cache_dir is not None:
        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
            _cache_file(cache_dir, url).write_text(
                json.dumps({"fetched_at": time.time(), "url": url, "body": body}),
                encoding="utf-8",
            )
        except OSError:
            pass  # cache is best-effort

    return body
