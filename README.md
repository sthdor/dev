# XHS Hot Writer（树莓派可运行）

一个可在 **树莓派 4B（8G）** 上长期运行的自动化项目：
- 每天从 **X + Instagram** 综合抓取爆款内容 **6 篇**
- 自动翻译 + 润色成适合 **小红书发布** 的中文爆款文案
- 按天输出 Markdown 文件，并用 SQLite 去重，避免重复改写

## 1. 功能说明

- 数据抓取：使用 Apify Actor（稳定、免本地浏览器，适合树莓派）
- 爆款筛选：按互动分（点赞 + 2×评论 + 3×转发）排序
- 文案生成：调用 OpenAI 兼容 LLM 接口输出 JSON 格式的小红书文案
- 结果落盘：`output/YYYY-MM-DD/*.md`
- 去重：`data/state.db` 记录已经处理过的帖子 ID

## 2. 环境要求

- Python 3.10+
- Raspberry Pi OS 64-bit（推荐 Bookworm）
- 可访问外网（Apify + LLM API）

## 3. 快速启动

```bash
cd /home/pi/xhs-hot-writer
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
cp .env.example .env
```

填写 `.env` 的关键参数：
- `APIFY_TOKEN`
- `LLM_API_KEY`

然后手工执行一次：

```bash
xhs-hot-writer --dry-run
```

如果你在 `--dry-run` 阶段遇到超时（例如网络受限），可先给当前 shell 配置 Clash 代理后重试：

```bash
# Clash 常见本地端口，按你的实际配置修改
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
export ALL_PROXY=socks5://127.0.0.1:7890

# 建议把本机和局域网地址排除代理
export NO_PROXY=127.0.0.1,localhost,::1

xhs-hot-writer --dry-run
```

也可以把以上变量写入 `.env`（项目启动时会自动加载），避免每次手动 `export`。

## 4. 输出结构

```text
output/
  2026-01-01/
    01_x_1234567890.md
    02_x_2345678901.md
    03_x_3456789012.md
    04_instagram_abc123.md
    05_instagram_def456.md
    06_instagram_ghi789.md
```

每篇文案内容包含：
- 小红书标题
- 正文（口语化、结构化）
- 标签
- 原文来源信息（平台、作者、原链接）

## 5. 树莓派长期运行（systemd 定时）

项目已提供：
- `config/xhs-hot-writer.service`
- `config/xhs-hot-writer.timer`

安装步骤：

```bash
sudo cp config/xhs-hot-writer.service /etc/systemd/system/
sudo cp config/xhs-hot-writer.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now xhs-hot-writer.timer
sudo systemctl status xhs-hot-writer.timer
```

查看任务执行日志：

```bash
tail -f /home/pi/xhs-hot-writer/logs/daily.log
```

## 6. 可配置参数（.env）

- `X_QUERY`: X 搜索词，例如 `(fashion OR outfit OR swimwear OR fitness OR workout) min_faves:300 lang:en`
- `IG_HASHTAG`: Instagram 标签，例如 `fashion`
- `FETCH_COUNT`: 每个平台抓取候选条数（默认 20）
- `DAILY_TOP_N`: 每日最终输出总条数（默认 6）
- `LLM_MODEL`: 生成模型名
- `HTTP_PROXY` / `HTTPS_PROXY` / `ALL_PROXY`: 代理地址（可选，适合 Clash）
- `NO_PROXY`: 不走代理的地址列表（可选）

## 7. 合规建议

- 发布前请人工复核事实和数据
- 保留来源信息，避免侵权和误导
- 遵守 X/Instagram/小红书各自平台政策

## 8. 测试

```bash
pytest
```
