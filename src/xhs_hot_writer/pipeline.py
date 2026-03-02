from __future__ import annotations

from datetime import date
from pathlib import Path

from .fetchers import InstagramFetcher, XFetcher
from .models import Post, RewrittenPost
from .rewriter import LLMRewriter
from .storage import StateStore


class DailyPipeline:
    def __init__(
        self,
        x_fetcher: XFetcher,
        ig_fetcher: InstagramFetcher,
        rewriter: LLMRewriter,
        state_store: StateStore,
        output_dir: Path,
        daily_top_n: int,
    ) -> None:
        self.x_fetcher = x_fetcher
        self.ig_fetcher = ig_fetcher
        self.rewriter = rewriter
        self.state_store = state_store
        self.output_dir = output_dir
        self.daily_top_n = daily_top_n

    def run(self, x_query: str, ig_hashtag: str, fetch_count: int) -> list[RewrittenPost]:
        x_posts = self.x_fetcher.fetch(x_query, fetch_count)
        ig_posts = self.ig_fetcher.fetch(ig_hashtag, fetch_count)

        selected = self._pick_top_posts(x_posts, "x") + self._pick_top_posts(ig_posts, "instagram")
        selected = sorted(selected, key=lambda p: p.engagement_score, reverse=True)[: self.daily_top_n]
        rewritten: list[RewrittenPost] = []
        for post in selected:
            rewritten_post = self.rewriter.rewrite_for_xiaohongshu(post)
            rewritten.append(rewritten_post)
            self.state_store.mark_processed(post.platform, post.post_id)

        self._save_markdown(rewritten)
        return rewritten

    def _pick_top_posts(self, posts: list[Post], platform: str) -> list[Post]:
        candidates = [
            post
            for post in posts
            if post.post_id and post.text and not self.state_store.already_processed(platform, post.post_id)
        ]
        ranked = sorted(candidates, key=lambda p: p.engagement_score, reverse=True)
        return ranked[: self.daily_top_n]

    def _save_markdown(self, posts: list[RewrittenPost]) -> None:
        target_dir = self.output_dir / date.today().isoformat()
        target_dir.mkdir(parents=True, exist_ok=True)

        for idx, post in enumerate(posts, start=1):
            filename = target_dir / f"{idx:02d}_{post.source.platform}_{post.source.post_id}.md"
            md = (
                f"# {post.title}\n\n"
                f"{post.content}\n\n"
                f"{' '.join(post.hashtags)}\n\n"
                "---\n"
                f"来源平台: {post.source.platform}\n"
                f"原作者: {post.source.author}\n"
                f"原文链接: {post.source.url}\n"
            )
            filename.write_text(md, encoding="utf-8")
