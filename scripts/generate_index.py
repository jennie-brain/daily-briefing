#!/usr/bin/env python3
"""Regenerates fintech/index.html, security/index.html, and the root index.html
from the dated *.html briefing files sitting in each topic folder.

Run after adding new dated files:
    python scripts/generate_index.py
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECENT_COUNT = 7

TOPICS = [
    {"key": "fintech", "dir": "fintech", "title": "핀테크·토큰증권 뉴스 브리핑", "emoji": "💳"},
    {"key": "security", "dir": "security", "title": "정보보안 뉴스 브리핑", "emoji": "🔐"},
]

STYLE = """
  :root{
    --bg:#f7f7f8;
    --card:#ffffff;
    --border:#e5e5ea;
    --text:#1c1c1e;
    --sub:#6b6b70;
    --accent:#2f5bea;
    --accent-bg:#eef1fd;
    --radius:14px;
  }
  *{box-sizing:border-box;}
  body{
    margin:0;
    background:var(--bg);
    color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",sans-serif;
    line-height:1.5;
    -webkit-text-size-adjust:100%;
  }
  .wrap{max-width:640px;margin:0 auto;padding:20px 16px 40px;}
  .page-title{font-size:20px;margin:0 0 6px;font-weight:700;}
  .sub{color:var(--sub);font-size:13px;margin:0 0 20px;}
  a{color:inherit;text-decoration:none;}
  .back{display:inline-block;margin-bottom:14px;color:var(--accent);font-size:13px;font-weight:600;}
  .section-label{font-size:13px;font-weight:700;color:var(--sub);margin:22px 0 8px;text-transform:uppercase;letter-spacing:.03em;}
  .card{
    display:block;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:var(--radius);
    padding:14px 16px;
    margin-bottom:10px;
  }
  .card:hover{border-color:var(--accent);}
  .card .date{font-weight:700;font-size:15px;}
  .card .rel{color:var(--sub);font-size:12px;margin-top:2px;}
  .topic-card{
    display:block;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:var(--radius);
    padding:18px;
    margin-bottom:14px;
  }
  .topic-card .emoji{font-size:26px;}
  .topic-card .name{font-weight:700;font-size:17px;margin:8px 0 4px;}
  .topic-card .sub{margin:0;}
  details{margin-top:6px;}
  summary{cursor:pointer;color:var(--accent);font-size:13px;font-weight:600;padding:8px 0;}
  .archive-list{display:flex;flex-wrap:wrap;gap:6px;padding:6px 0 4px;}
  .archive-list a{
    border:1px solid var(--border);
    border-radius:8px;
    padding:5px 10px;
    font-size:12.5px;
    background:var(--card);
  }
  .archive-list a:hover{border-color:var(--accent);color:var(--accent);}
"""

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")


def format_date(date_str: str) -> str:
    y, m, d = date_str.split("-")
    return f"{y}.{m}.{d}"


def list_dated_files(directory: Path):
    if not directory.exists():
        return []
    dates = [p.name[:-5] for p in directory.iterdir() if DATE_RE.match(p.name)]
    return sorted(dates, reverse=True)


def build_topic_index(topic: dict) -> str:
    directory = ROOT / topic["dir"]
    dates = list_dated_files(directory)
    recent = dates[:RECENT_COUNT]
    archive = dates[RECENT_COUNT:]

    card_blocks = []
    for i, d in enumerate(recent):
        rel_tag = '<div class="rel">최신</div>' if i == 0 else ""
        card_blocks.append(
            f'      <a class="card" href="./{d}.html">\n'
            f'        <div class="date">{format_date(d)}</div>\n'
            f'        {rel_tag}\n'
            f"      </a>"
        )
    recent_html = "\n".join(card_blocks)

    archive_html = ""
    if archive:
        links = "\n".join(f'          <a href="./{d}.html">{format_date(d)}</a>' for d in archive)
        archive_html = (
            "      <details>\n"
            f"        <summary>지난 기록 더보기 ({len(archive)}개)</summary>\n"
            '        <div class="archive-list">\n'
            f"{links}\n"
            "        </div>\n"
            "      </details>"
        )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<title>{topic['title']}</title>
<style>{STYLE}</style>
</head>
<body>
  <div class="wrap">
    <a class="back" href="../index.html">← 전체 브리핑</a>
    <h1 class="page-title">{topic['emoji']} {topic['title']}</h1>
    <p class="sub">최근 {RECENT_COUNT}일치 브리핑입니다. 이전 기록은 아래에서 볼 수 있어요.</p>
    <div class="section-label">최근 브리핑</div>
{recent_html}
{archive_html}
  </div>
</body>
</html>
"""


def build_root_index() -> str:
    cards = []
    for topic in TOPICS:
        dates = list_dated_files(ROOT / topic["dir"])
        latest = dates[0] if dates else None
        sub = f"최신: {format_date(latest)}" if latest else "기록 없음"
        cards.append(
            f'      <a class="topic-card" href="./{topic["dir"]}/index.html">\n'
            f'        <div class="emoji">{topic["emoji"]}</div>\n'
            f'        <div class="name">{topic["title"]}</div>\n'
            f'        <div class="sub">{sub}</div>\n'
            "      </a>"
        )
    cards_html = "\n".join(cards)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<title>뉴스 브리핑</title>
<style>{STYLE}</style>
</head>
<body>
  <div class="wrap">
    <h1 class="page-title">📰 뉴스 브리핑</h1>
    <p class="sub">주제별 일일 뉴스 브리핑 모음</p>
{cards_html}
  </div>
</body>
</html>
"""


def main():
    for topic in TOPICS:
        directory = ROOT / topic["dir"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(build_topic_index(topic), encoding="utf-8")
        print(f"generated {topic['dir']}/index.html")

    (ROOT / "index.html").write_text(build_root_index(), encoding="utf-8")
    print("generated index.html")


if __name__ == "__main__":
    main()
