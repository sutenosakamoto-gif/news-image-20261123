#!/usr/bin/env python3
"""Render the 'World News - 23 November 2026' one-image summary.

Deterministic: no network access, no randomness, no timestamps.
Running this file writes entry.png to /output/entry.png, falling back
to ./output/entry.png (next to this script) when /output is not writable.
"""

import io
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
BOLD = str(FONT_DIR / "DejaVuSans-Bold.ttf")
REG = str(FONT_DIR / "DejaVuSans.ttf")

BG = (247, 243, 234)
INK = (26, 30, 38)
MUTED = (88, 94, 106)
CARD = (255, 255, 255)
NAVY = (20, 33, 61)
GOLD = (242, 183, 49)

STORIES = [
    (
        "CLIMATE  |  ANTALYA, TURKIYE",
        (39, 122, 72),
        "COP31 Climate Talks End Without a Deal",
        "The Antalya summit closed after record overtime as the EU and about "
        "130 parties rejected a text omitting a fossil-fuel phase-out. "
        "Pacific nations voiced despair.",
    ),
    (
        "UKRAINE  |  DYMER, KYIV REGION",
        (38, 84, 160),
        "Russian Attack on Dymer Kills 11",
        "Rescuers pulled bodies from the rubble of a housing block in the "
        "town north of Kyiv, regional governor Tymur Tkachenko said on Monday.",
    ),
    (
        "SUDAN  |  KHARTOUM",
        (176, 92, 36),
        "Drone Strikes Hit Homes and a U.N. Building",
        "Explosions near the airport from about 2 a.m. destroyed a house "
        "and damaged U.N. premises in a civilian neighbourhood, witnesses said.",
    ),
    (
        "INDONESIA  |  BANTEN",
        (178, 52, 52),
        "Factory Fire Kills 24; About 30 Still Missing",
        "The weekend blaze at a Cikande candy factory may have started "
        "with an air-conditioner short circuit; 29 people were confirmed safe.",
    ),
    (
        "MARKETS  |  GLOBAL",
        (104, 66, 160),
        "AI Sell-Off Shakes Markets as Futures Rebound",
        "After last week's bruising sell-off, U.S. futures bounced while "
        "Asia stayed mixed; Taiwan loosened margin rules to calm selling.",
    ),
    (
        "SPACE  |  MERCURY",
        (24, 124, 138),
        "Japan-Europe Probes Enter Orbit Around Mercury",
        "After an eight-year journey, JAXA's Mio and ESA's MPO will study "
        "Mercury's magnetic field and surface. They separate in December.",
    ),
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def render_bytes() -> bytes:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([0, 0, W, 128], fill=NAVY)
    d.rectangle([0, 128, W, 134], fill=GOLD)
    d.text((48, 26), "World News \u2014 23 November 2026", font=font(BOLD, 43), fill=(255, 255, 255))
    d.text((48, 82), "MONDAY  \u00b7  SIX STORIES FROM AROUND THE WORLD",
           font=font(BOLD, 20), fill=(198, 210, 232))

    # Story cards
    top = 154
    card_h = 132
    gap = 10
    for i, (tag, color, headline, body) in enumerate(STORIES):
        y = top + i * (card_h + gap)
        d.rounded_rectangle([36, y, W - 36, y + card_h], radius=14, fill=CARD)
        d.rounded_rectangle([36, y, 48, y + card_h], radius=6, fill=color)
        x = 68
        d.text((x, y + 12), tag, font=font(BOLD, 17), fill=color)
        d.text((x, y + 34), headline, font=font(BOLD, 27), fill=INK)
        body_lines = wrap(d, body, font(REG, 19), W - 36 - x - 22)
        by = y + 72
        for line in body_lines[:2]:
            d.text((x, by), line, font=font(REG, 19), fill=MUTED)
            by += 25

    # Footer
    fy = top + len(STORIES) * (card_h + gap) + 2
    d.text((48, fy), "Sources: Reuters \u00b7 AFP via The Japan Times \u00b7 Jiji Press via "
                     "The Japan Times \u2014 all dated 23 Nov 2026",
           font=font(REG, 16), fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main() -> None:
    data = render_bytes()
    target = Path("/output/entry.png")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    except OSError:
        target = Path(__file__).resolve().parent / "output" / "entry.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    print(f"wrote {target} ({len(data)} bytes)")


if __name__ == "__main__":
    main()
