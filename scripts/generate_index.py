#!/usr/bin/env python3
"""Regenerates fintech/index.html, security/index.html, and the root index.html
from the dated *.html briefing files sitting in each topic folder.

Each topic page loads the latest day's briefing directly (in an iframe) and
offers a native date picker to jump to any older date without leaving the
page. Older files are never deleted — the date picker can reach all of them,
they're just not listed out on screen.

Run after adding new dated files:
    python scripts/generate_index.py
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

TOPICS = [
    {"key": "fintech", "dir": "fintech", "title": "핀테크·토큰증권 뉴스 브리핑", "emoji": "💳"},
    {"key": "security", "dir": "security", "title": "정보보안 뉴스 브리핑", "emoji": "🔐"},
]

ROOT_STYLE = """
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
    latest = dates[0] if dates else None
    earliest = dates[-1] if dates else None
    available_json = json.dumps(dates)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
<title>{topic['title']}</title>
<style>
  :root{{
    --bg:#f7f7f8;
    --card:#ffffff;
    --border:#e5e5ea;
    --text:#1c1c1e;
    --sub:#6b6b70;
    --accent:#2f5bea;
  }}
  *{{box-sizing:border-box;}}
  html,body{{height:100%;margin:0;}}
  body{{
    display:flex;
    flex-direction:column;
    background:var(--bg);
    color:var(--text);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Noto Sans KR",sans-serif;
    -webkit-text-size-adjust:100%;
  }}
  .header-bar{{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:12px 16px;
    background:var(--card);
    border-bottom:1px solid var(--border);
    flex-wrap:wrap;
  }}
  .title-group{{display:flex;align-items:center;gap:8px;min-width:0;}}
  .title-group .emoji{{font-size:19px;}}
  .title-group .name{{font-weight:700;font-size:15px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
  .date-picker{{display:flex;align-items:center;gap:8px;}}
  .date-picker .current{{font-size:12.5px;color:var(--sub);font-weight:600;white-space:nowrap;}}
  input[type=date]{{
    border:1px solid var(--border);
    border-radius:8px;
    padding:6px 8px;
    font-size:13px;
    font-family:inherit;
    background:var(--bg);
    color:var(--text);
  }}
  .frame-wrap{{flex:1;min-height:0;}}
  iframe{{width:100%;height:100%;border:none;display:block;background:var(--bg);}}
  .empty{{padding:40px 16px;text-align:center;color:var(--sub);font-size:14px;}}
</style>
</head>
<body>
  <div class="header-bar">
    <div class="title-group">
      <span class="emoji">{topic['emoji']}</span>
      <span class="name">{topic['title']}</span>
    </div>
    <div class="date-picker">
      <span class="current" id="currentLabel">{format_date(latest) if latest else ''}</span>
      <input type="date" id="datePicker" min="{earliest or ''}" max="{latest or ''}" value="{latest or ''}" aria-label="날짜 선택">
    </div>
  </div>
  <div class="frame-wrap">
    {'<iframe id="briefingFrame" title="' + topic['title'] + '"></iframe>' if latest else '<p class="empty">아직 등록된 브리핑이 없습니다.</p>'}
  </div>
  <script>
    const AVAILABLE = {available_json};
    const input = document.getElementById('datePicker');
    const frame = document.getElementById('briefingFrame');
    const label = document.getElementById('currentLabel');

    function nearestAvailable(target) {{
      for (const d of AVAILABLE) {{ if (d <= target) return d; }}
      return AVAILABLE[AVAILABLE.length - 1];
    }}

    function loadDate(d) {{
      if (!d || !frame) return;
      frame.src = './' + d + '.html';
      input.value = d;
      label.textContent = d.replaceAll('-', '.');
    }}

    if (AVAILABLE.length) {{
      input.addEventListener('change', () => {{
        const picked = input.value;
        const match = AVAILABLE.includes(picked) ? picked : nearestAvailable(picked);
        loadDate(match);
      }});
      loadDate(AVAILABLE[0]);
    }}
  </script>
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
<style>{ROOT_STYLE}</style>
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
