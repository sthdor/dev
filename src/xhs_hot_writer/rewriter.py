from __future__ import annotations

import json

from .http import post_json
from .models import Post, RewrittenPost


class LLMRewriter:
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        if not api_key:
            raise ValueError("LLM_API_KEY is required for rewrite step")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    def rewrite_for_xiaohongshu(self, post: Post) -> RewrittenPost:
        prompt = (
            "你是小红书百万粉写手。请把输入内容改写成中文小红书爆款文案，输出 JSON: "
            '{"title": "...", "content": "...", "hashtags": ["#标签1", "#标签2"]}。'
            "要求：\n"
            "1) 标题20字以内，必须有钩子；\n"
            "2) 正文分段清晰、口语化、有实操建议；\n"
            "3) 保留原文核心信息，不编造数据；\n"
            "4) 至少5个标签，且和主题相关。\n\n"
            f"原文平台: {post.platform}\n"
            f"作者: {post.author}\n"
            f"原文内容: {post.text}\n"
            f"原文链接: {post.url}"
        )
        response = post_json(
            f"{self.base_url}/chat/completions",
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "你是顶级中文内容运营。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.8,
                "response_format": {"type": "json_object"},
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=120,
        )
        content = response["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return RewrittenPost(
            source=post,
            title=parsed.get("title", "未命名标题"),
            content=parsed.get("content", ""),
            hashtags=parsed.get("hashtags", []),
        )
