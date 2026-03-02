from xhs_hot_writer.fetchers import ApifyClient


def test_run_actor_encodes_slash_in_actor_id(monkeypatch):
    captured = {}

    def fake_post_json(url, payload, timeout=120):
        captured["url"] = url
        captured["payload"] = payload
        captured["timeout"] = timeout
        return []

    monkeypatch.setattr("xhs_hot_writer.fetchers.post_json", fake_post_json)

    client = ApifyClient("token-123")
    client.run_actor("apify/instagram-scraper", {"resultsLimit": 20})

    assert "acts/apify%2Finstagram-scraper/run-sync-get-dataset-items" in captured["url"]
    assert captured["url"].endswith("token=token-123")
    assert captured["payload"] == {"resultsLimit": 20}
    assert captured["timeout"] == 120
