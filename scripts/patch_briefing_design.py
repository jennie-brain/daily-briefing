#!/usr/bin/env python3
"""One-off patch applied to every dated briefing file in fintech/ and security/:

- removes the bottom-right floating menu button (redundant with swipe/tabs/dots)
- replaces the tall title+tabs+swipe-hint header with a slim segmented control
- restyles the plain-text report date into a small pill/chip

Safe to re-run: each replacement is idempotent (skipped if the old string
is already gone), and every replacement is counted so mismatches are
reported instead of silently doing nothing.

Run:
    python scripts/patch_briefing_design.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.html$")

OLD_CSS = """  .nav-header{margin:2px 0 14px;}
  .screen-tabs{
    display:flex;
    gap:6px;
    margin-bottom:8px;
  }
  .screen-tab{
    flex:1;
    text-align:center;
    font-size:12.5px;
    font-weight:700;
    color:var(--sub);
    padding:7px 4px;
    border-radius:8px;
    background:var(--card);
    border:1px solid var(--border);
    cursor:pointer;
    -webkit-tap-highlight-color:transparent;
    transition:all 0.15s ease;
  }
  .screen-tab.active{
    background:var(--accent);
    border-color:var(--accent);
    color:#fff;
  }
  .swipe-hint{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:6px;
    text-align:center;
    font-size:12px;
    color:var(--sub);
  }
  .swipe-hint .kbd-hint{
    color:var(--sub);
    opacity:0.75;
  }"""

NEW_CSS = """  .top-bar{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    margin-bottom:14px;
  }
  .page-title{font-size:15.5px;margin:0;font-weight:700;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
  .screen-tabs{
    display:flex;
    gap:2px;
    background:var(--bg);
    border:1px solid var(--border);
    border-radius:10px;
    padding:3px;
    flex-shrink:0;
  }
  .screen-tab{
    text-align:center;
    font-size:12px;
    font-weight:600;
    color:var(--sub);
    padding:6px 10px;
    border-radius:8px;
    background:transparent;
    border:none;
    cursor:pointer;
    -webkit-tap-highlight-color:transparent;
    transition:all 0.15s ease;
  }
  .screen-tab.active{
    background:var(--card);
    color:var(--accent);
    box-shadow:0 1px 3px rgba(0,0,0,0.12);
  }
  .swipe-hint{
    display:none;
    align-items:center;
    justify-content:center;
    gap:6px;
    text-align:center;
    font-size:12px;
    color:var(--sub);
    margin-top:8px;
  }
  .swipe-hint .kbd-hint{
    color:var(--sub);
    opacity:0.75;
  }"""

OLD_PAGE_TITLE_RULE = """  .page-title{
    font-size:20px;
    margin:0 0 6px;
    font-weight:700;
  }
"""

OLD_DATE_CSS = "  .date{font-size:14px;color:var(--sub);margin-bottom:10px;}"
NEW_DATE_CSS = """  .date{
    display:inline-flex;
    align-items:center;
    gap:4px;
    font-size:12.5px;
    font-weight:600;
    color:var(--accent);
    background:var(--accent-bg);
    padding:4px 10px;
    border-radius:999px;
    margin-bottom:10px;
  }"""

OLD_FAB_CSS = """  .page-fab{
    position:fixed;
    right:18px;
    bottom:18px;
    width:48px;
    height:48px;
    border-radius:50%;
    background:var(--accent);
    color:#fff;
    border:none;
    box-shadow:0 2px 10px rgba(0,0,0,0.2);
    font-size:20px;
    display:flex;
    align-items:center;
    justify-content:center;
    cursor:pointer;
    z-index:50;
    -webkit-tap-highlight-color:transparent;
  }
  .page-fab:active{opacity:0.85;}
  .page-menu{
    position:fixed;
    right:18px;
    bottom:74px;
    background:var(--card);
    border:1px solid var(--border);
    border-radius:12px;
    box-shadow:0 4px 16px rgba(0,0,0,0.16);
    overflow:hidden;
    display:none;
    z-index:50;
    min-width:160px;
  }
  .page-menu.open{display:block;}
  .page-menu button{
    display:block;
    width:100%;
    text-align:left;
    padding:12px 16px;
    border:none;
    background:none;
    font-size:14px;
    font-weight:600;
    color:var(--text);
    cursor:pointer;
    -webkit-tap-highlight-color:transparent;
  }
  .page-menu button+button{border-top:1px solid var(--border);}
  .page-menu button.active{color:var(--accent);background:var(--accent-bg);}
  .kbd-hint{display:none;}
"""
NEW_FAB_CSS = "  .kbd-hint{display:none;}\n"

OLD_MEDIA = """  @media (hover:hover) and (pointer:fine){
    .kbd-hint{display:inline;}
    .nav-arrow{display:flex;}
  }"""
NEW_MEDIA = """  @media (hover:hover) and (pointer:fine){
    .kbd-hint{display:inline;}
    .nav-arrow{display:flex;}
    .swipe-hint{display:flex;}
  }"""

HEADER_RE = re.compile(
    r'  <h1 class="page-title">(.*?)</h1>\n'
    r'  <div class="nav-header">\n'
    r'    <div class="screen-tabs" id="screenTabs">\n'
    r'      <span class="screen-tab active" data-i="0">① 오늘</span>\n'
    r'      <span class="screen-tab" data-i="1">② 30일 트렌드</span>\n'
    r'      <span class="screen-tab" data-i="2">③ 1년 트렌드</span>\n'
    r'    </div>\n'
    r'    <div class="swipe-hint">↔ 좌우로 스와이프해 넘겨보세요<span class="kbd-hint"> · ←/→ 키로도 이동</span></div>\n'
    r'  </div>',
    re.MULTILINE,
)


def header_replacement(match):
    title = match.group(1)
    return (
        '  <div class="top-bar">\n'
        f'    <h1 class="page-title">{title}</h1>\n'
        '    <div class="screen-tabs" id="screenTabs">\n'
        '      <span class="screen-tab active" data-i="0">오늘</span>\n'
        '      <span class="screen-tab" data-i="1">30일</span>\n'
        '      <span class="screen-tab" data-i="2">1년</span>\n'
        '    </div>\n'
        '    <div class="swipe-hint">↔ 스와이프로 넘겨보세요<span class="kbd-hint"> · ←/→ 키로도 이동</span></div>\n'
        '  </div>'
    )


OLD_FAB_HTML = """
  <button class="page-fab" id="pageFab" aria-label="페이지 선택" onclick="togglePageMenu()">☰</button>
  <div class="page-menu" id="pageMenu">
    <button class="active" data-i="0" onclick="gotoScreen(0)">① 오늘</button>
    <button data-i="1" onclick="gotoScreen(1)">② 30일 트렌드</button>
    <button data-i="2" onclick="gotoScreen(2)">③ 1년 트렌드</button>
  </div>
"""

DATE_TEXT_RE = re.compile(r'<div class="date">(리포트 날짜|기준일): (.*?)</div>')


def date_replacement(match):
    return f'<div class="date">📅 {match.group(2)}</div>'


JS_REMOVALS = [
    "  var pageMenuBtns = document.querySelectorAll('#pageMenu button');\n",
    "    pageMenuBtns.forEach(function(b,i){ b.classList.toggle('active', i===idx); });\n",
    "    document.getElementById('pageMenu').classList.remove('open');\n",
    (
        "  function togglePageMenu(){\n"
        "    document.getElementById('pageMenu').classList.toggle('open');\n"
        "  }\n\n"
    ),
    (
        "  document.addEventListener('click', function(e){\n"
        "    var menu = document.getElementById('pageMenu');\n"
        "    var fab = document.getElementById('pageFab');\n"
        "    if(menu.classList.contains('open') && !menu.contains(e.target) && e.target !== fab){\n"
        "      menu.classList.remove('open');\n"
        "    }\n"
        "  });\n\n"
    ),
]


def patch_file(path: Path) -> list:
    text = path.read_text(encoding="utf-8")
    original = text
    issues = []

    if OLD_PAGE_TITLE_RULE in text:
        text = text.replace(OLD_PAGE_TITLE_RULE, "", 1)
    else:
        issues.append("page-title rule not found (may already be patched)")

    if OLD_CSS in text:
        text = text.replace(OLD_CSS, NEW_CSS, 1)
    else:
        issues.append("header CSS block not found")

    if OLD_DATE_CSS in text:
        text = text.replace(OLD_DATE_CSS, NEW_DATE_CSS, 1)
    else:
        issues.append(".date CSS rule not found")

    if OLD_FAB_CSS in text:
        text = text.replace(OLD_FAB_CSS, NEW_FAB_CSS, 1)
    else:
        issues.append("FAB CSS block not found")

    if OLD_MEDIA in text:
        text = text.replace(OLD_MEDIA, NEW_MEDIA, 1)
    else:
        issues.append("hover media query not found")

    text, n = HEADER_RE.subn(header_replacement, text, count=1)
    if n == 0:
        issues.append("header HTML block not matched")

    if OLD_FAB_HTML in text:
        text = text.replace(OLD_FAB_HTML, "", 1)
    else:
        issues.append("FAB HTML block not found")

    text, n = DATE_TEXT_RE.subn(date_replacement, text)
    if n == 0:
        issues.append("no .date text matched")

    for old in JS_REMOVALS:
        if old in text:
            text = text.replace(old, "", 1)
        else:
            issues.append(f"JS snippet not found: {old.strip()[:40]}...")

    if text != original:
        path.write_text(text, encoding="utf-8")

    return issues


def main():
    any_issue = False
    for topic_dir in ("fintech", "security"):
        directory = ROOT / topic_dir
        for name in sorted(p.name for p in directory.iterdir() if DATE_RE.match(p.name)):
            path = directory / name
            issues = patch_file(path)
            if issues:
                any_issue = True
                print(f"[{topic_dir}/{name}]")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"patched {topic_dir}/{name}")
    if any_issue:
        sys.exit(1)


if __name__ == "__main__":
    main()
