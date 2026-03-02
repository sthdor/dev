from __future__ import annotations

import argparse
import json

from .fetchers import ApifyClient, InstagramFetcher, XFetcher
from .pipeline import DailyPipeline
from .rewriter import LLMRewriter
from .settings import settings
from .storage import StateStore


def build_pipeline() -> DailyPipeline:
    client = ApifyClient(settings.apify_token)
    x_fetcher = XFetcher(client, settings.apify_x_actor)
    ig_fetcher = InstagramFetcher(client, settings.apify_ig_actor)
    rewriter = LLMRewriter(settings.llm_api_key, settings.llm_base_url, settings.llm_model)
    state_store = StateStore(settings.db_path)

    return DailyPipeline(
        x_fetcher=x_fetcher,
        ig_fetcher=ig_fetcher,
        rewriter=rewriter,
        state_store=state_store,
        output_dir=settings.output_dir,
        daily_top_n=settings.daily_top_n,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Xiaohongshu-ready posts from X and Instagram")
    parser.add_argument("--dry-run", action="store_true", help="Print result JSON to stdout")
    args = parser.parse_args()

    pipeline = build_pipeline()
    rewritten = pipeline.run(
        x_query=settings.x_query,
        ig_hashtag=settings.ig_hashtag,
        fetch_count=settings.fetch_count,
        dry_run=args.dry_run,
    )

    if args.dry_run:
        print(
            json.dumps(
                [
                    {
                        "platform": p.source.platform,
                        "post_id": p.source.post_id,
                        "title": p.title,
                        "hashtags": p.hashtags,
                    }
                    for p in rewritten
                ],
                ensure_ascii=False,
                indent=2,
            )
        )


if __name__ == "__main__":
    main()
