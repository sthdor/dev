from __future__ import annotations

import json
import time
from typing import Any
from urllib import error, parse, request


class HttpError(RuntimeError):
    pass


def post_json(url: str, payload: dict[str, Any], headers: dict[str, str] | None = None, timeout: int = 120) -> Any:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})})
    return _send(req, timeout)


def _send(req: request.Request, timeout: int) -> Any:
    attempts = 3
    for i in range(attempts):
        try:
            with request.urlopen(req, timeout=timeout) as resp:
                content = resp.read().decode("utf-8")
                return json.loads(content)
        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            if i == attempts - 1:
                raise HttpError(str(exc)) from exc
            time.sleep(2**i)
    raise HttpError("unreachable")


def with_query(url: str, query: dict[str, str]) -> str:
    return f"{url}?{parse.urlencode(query)}"
