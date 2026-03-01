from __future__ import annotations

from datetime import datetime
from typing import Any

from .http import post_json, with_query
from .models import Post


class ApifyClient:
    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("APIFY_TOKEN is required for fetching data")
        self.token = token
        self.base_url = "https://api.apify.com/v2"

    def run_actor(self, actor_id: str, payload: dict[str, Any]) -> list[dict[str, Any]]:
        url = with_query(f"{self.base_url}/acts/{actor_id}/run-sync-get-dataset-items", {"token": self.token})
        data = post_json(url, payload, timeout=120)
        if not isinstance(data, list):
            return []
        return data


class XFetcher:
    def __init__(self, client: ApifyClient, actor_id: str) -> None:
        self.client = client
        self.actor_id = actor_id

    def fetch(self, query: str, limit: int) -> list[Post]:
        payload = {"searchTerms": [query], "maxItems": limit, "sort": "Top"}
        items = self.client.run_actor(self.actor_id, payload)
        posts: list[Post] = []
        for item in items:
            posts.append(
                Post(
                    platform="x",
                    post_id=str(item.get("id") or item.get("tweetId") or ""),
                    author=item.get("author", {}).get("userName", "unknown"),
                    text=item.get("text") or "",
                    url=item.get("url") or "",
                    likes=int(item.get("likeCount") or 0),
                    comments=int(item.get("replyCount") or 0),
                    shares=int(item.get("retweetCount") or 0),
                    created_at=_parse_datetime(item.get("createdAt")),
                )
            )
        return posts


class InstagramFetcher:
    def __init__(self, client: ApifyClient, actor_id: str) -> None:
        self.client = client
        self.actor_id = actor_id

    def fetch(self, hashtag: str, limit: int) -> list[Post]:
        payload = {
            "directUrls": [f"https://www.instagram.com/explore/tags/{hashtag}/"],
            "resultsType": "posts",
            "resultsLimit": limit,
        }
        items = self.client.run_actor(self.actor_id, payload)
        posts: list[Post] = []
        for item in items:
            posts.append(
                Post(
                    platform="instagram",
                    post_id=str(item.get("id") or item.get("shortCode") or ""),
                    author=item.get("ownerUsername") or "unknown",
                    text=item.get("caption") or "",
                    url=item.get("url") or "",
                    likes=int(item.get("likesCount") or 0),
                    comments=int(item.get("commentsCount") or 0),
                    shares=0,
                    created_at=_parse_datetime(item.get("timestamp")),
                )
            )
        return posts


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
