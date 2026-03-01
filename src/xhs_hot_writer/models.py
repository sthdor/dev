from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Post:
    platform: str
    post_id: str
    author: str
    text: str
    url: str
    likes: int = 0
    comments: int = 0
    shares: int = 0
    created_at: datetime | None = None

    @property
    def engagement_score(self) -> int:
        return self.likes + self.comments * 2 + self.shares * 3


@dataclass(slots=True)
class RewrittenPost:
    source: Post
    title: str
    content: str
    hashtags: list[str]
