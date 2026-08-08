# news-briefing

주제별 일일 뉴스 브리핑 아카이브. GitHub Pages로 게시됩니다: https://jennie-brain.github.io/news-briefing/

## 구조

- `fintech/` — 핀테크·토큰증권 뉴스 브리핑 (`YYYY-MM-DD.html`)
- `security/` — 정보보안 뉴스 브리핑 (`YYYY-MM-DD.html`)
- `index.html`, `fintech/index.html`, `security/index.html` — 각 최근 7일치를 보여주고 이전 기록은 접어서 보관하는 인덱스 페이지 (자동 생성됨)

## 새 브리핑 추가하는 법

1. 해당 주제 폴더(`fintech/` 또는 `security/`)에 `YYYY-MM-DD.html` 형식으로 파일 추가
2. 인덱스 재생성:
   ```
   python scripts/generate_index.py
   ```
3. 커밋 & 푸시
