from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_dotenv(path: str = ".env") -> None:
    env_file = Path(path)
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


@dataclass(slots=True)
class Settings:
    apify_token: str = os.getenv("APIFY_TOKEN", "")
    apify_x_actor: str = os.getenv("APIFY_X_ACTOR", "61RPP7dywgiy0JPD0")
    apify_ig_actor: str = os.getenv("APIFY_IG_ACTOR", "apify/instagram-scraper")

    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o-mini")

    x_query: str = os.getenv(
        "X_QUERY",
        "(fashion OR outfit OR swimwear OR fitness OR workout) min_faves:300 lang:en",
    )
    ig_hashtag: str = os.getenv("IG_HASHTAG", "fashion")

    fetch_count: int = int(os.getenv("FETCH_COUNT", "20"))
    daily_top_n: int = int(os.getenv("DAILY_TOP_N", "6"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "output"))
    db_path: Path = Path(os.getenv("DB_PATH", "data/state.db"))


settings = Settings()
