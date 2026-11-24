# World News — 23 November 2026 (one-image summary)

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/sutenosakamoto-gif/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/sutenosakamoto-gif/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

A one-image broadsheet front page summarising thirty world news
stories of Monday, 23 November 2026, an entry for the make.fun
bounty "Sum up 23 November's world news in one image"
(final deadline 2026-11-25 09:00 JST). Three lead stories with giant
figures, ten panel stories each with its own pictogram, a dot-matrix
world map with a world-clock strip, and a one-line index of the rest.

## Contents

- `main.py` — the entry point: a standard-library only, self-contained
  renderer. Running `python3 main.py` renders the image to
  `/output/entry.png` (no network).
- `SOURCES.md` — the thirty stories, their sources (outlet + date)
  and URLs.

## How to run

```bash
python3 main.py   # standard library only, no dependencies
```

Running `python3 main.py` renders the image to `/output/entry.png`,
falling back to `./entry.png` next to the script when `/output` is not
writable. The render is deterministic: repeated runs produce identical
bytes.

## The thirty stories

Lead panels (large):

1. Nvidia shares leap 31% as Jensen Huang returns as CEO; Nasdaq +6.5% (Reuters / AP)
2. COP31 climate talks in Antalya end without a deal; 130+ parties reject the text (Reuters)
3. Indonesia candy-factory fire kills 24, about 30 missing (Reuters)

Medium panels:

4. Russian attack on Dymer, Kyiv region, kills 11 (Reuters)
5. Drone strikes hit homes and a U.N. building in Khartoum (AFP / Japan Times)
6. Ukraine sinks a Russian warship in a Libyan port (AP)
7. Bomb threats sent to about 450 German schools (Reuters)
8. U.S. Democrats clinch a 258-seat House majority (AP)
9. Congo halts cobalt exports again (Reuters)
10. Spanish court clears Catalan leader Puigdemont's return (Reuters)
11. U.S. discusses training Syrian forces in demining (Reuters)
12. FIFA picks U.S.-led bid for 2031 Women's World Cup, UK for 2035 (AP)
13. Japan–Europe BepiColombo probes enter Mercury orbit (Jiji / Japan Times)

One-line list ("Also on 23 November"): North Korea may shut the Swiss
office in Pyongyang; Czech and Hungarian leaders reject the EU budget
proposal; Russia's $576M Kaliningrad ferries; EU proposes new Russia
sanctions; EU signs a trade deal with Indonesia; CrowdStrike buys
Zscaler for $44B; Honda recalls 810,000 vehicles; FBI probes a crime
database hack; Rep. Gomez resigns after an ethics report; Delta
automation fault delays holiday flights; Verstappen wins the Las
Vegas Grand Prix; Skubal agrees a record $450M Mets deal; gold
rebounds nearly 5%; Canada and Qatar ink an investment pact; China
sentences an official to death for spying; nine shot at a California
concert; flights grounded in Belgium by a strike.

## Submission layout

- `main.py` — the entry point. Standard-library only and self-contained:
  it draws the infographic itself (including its own bitmap font and PNG
  encoder) and writes it to `/output/entry.png`, byte-identical on
  every run, with no network access.
- `.makefun/owner.json` — claim file naming the linked Solana wallet
  that receives any reward.
