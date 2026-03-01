from pathlib import Path

from xhs_hot_writer.models import Post, RewrittenPost
from xhs_hot_writer.pipeline import DailyPipeline
from xhs_hot_writer.storage import StateStore


class DummyFetcher:
    def __init__(self, posts):
        self.posts = posts

    def fetch(self, *_args, **_kwargs):
        return self.posts


class DummyRewriter:
    def rewrite_for_xiaohongshu(self, post: Post) -> RewrittenPost:
        return RewrittenPost(source=post, title=f"标题-{post.post_id}", content="内容", hashtags=["#测试"])


def test_pipeline_pick_top_and_persist(tmp_path: Path):
    x_posts = [
        Post(platform="x", post_id="1", author="a", text="A", url="u1", likes=5, comments=1, shares=1),
        Post(platform="x", post_id="2", author="b", text="B", url="u2", likes=10, comments=3, shares=2),
    ]
    ig_posts = [
        Post(platform="instagram", post_id="3", author="c", text="C", url="u3", likes=2, comments=1, shares=0),
        Post(platform="instagram", post_id="4", author="d", text="D", url="u4", likes=20, comments=2, shares=0),
    ]

    pipeline = DailyPipeline(
        x_fetcher=DummyFetcher(x_posts),
        ig_fetcher=DummyFetcher(ig_posts),
        rewriter=DummyRewriter(),
        state_store=StateStore(tmp_path / "state.db"),
        output_dir=tmp_path / "output",
        daily_top_n=1,
    )

    result = pipeline.run("query", "tag", 10)

    assert len(result) == 2
    assert result[0].source.post_id == "2"
    assert result[1].source.post_id == "4"

    generated = list((tmp_path / "output").rglob("*.md"))
    assert len(generated) == 2
