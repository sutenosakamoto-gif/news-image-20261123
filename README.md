# World News — 23 November 2026 (one-image summary)

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/sutenosakamoto-gif/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/sutenosakamoto-gif/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-image infographic summarising six major world news stories of
Monday, 23 November 2026, prepared as a local draft entry for the
make.fun bounty "Sum up 23 November's world news in one image"
(final deadline 2026-11-25 09:00 JST). Nothing has been submitted.

## Contents

- `main.py` — the entry point: a standard-library only, self-contained
  renderer. Running `python3 main.py` renders the image to
  `/output/entry.png` (no network).
- `SOURCES.md` — the six stories, their sources (outlet + date) and URLs.

## How to run

```bash
python3 main.py   # standard library only, no dependencies
```

Running `python3 main.py` renders the image to `/output/entry.png`,
falling back to `./entry.png` next to the script when `/output` is not
writable. The render is deterministic: repeated runs produce identical
bytes.

## The six stories

1. COP31 climate talks in Antalya end without a deal (Reuters)
2. Russian attack on Dymer, Kyiv region, kills 11 (Reuters)
3. Drone strikes hit homes and a U.N. building in Khartoum (AFP / Japan Times)
4. Indonesia candy-factory fire kills 24, about 30 missing (Reuters)
5. AI sell-off shakes markets as U.S. futures rebound (Reuters)
6. Japan–Europe BepiColombo probes enter Mercury orbit (Jiji / Japan Times)

## Submission layout

- `main.py` — the entry point. Standard-library only and self-contained:
  it draws the infographic itself (including its own bitmap font and PNG
  encoder) and writes it to `/output/entry.png`, byte-identical on
  every run, with no network access.
- `.makefun/owner.json` — claim file naming the linked Solana wallet
  that receives any reward.
