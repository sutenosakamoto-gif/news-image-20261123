#!/usr/bin/env python3
"""World News - 23 November 2026, in one image (v2: newspaper front page).

A self-contained renderer: running this program draws a 1024x1024
broadsheet-style front page summarising thirty world news stories of
Monday, 23 November 2026 and writes it as a PNG to /output/entry.png
(falling back to ./entry.png when /output is not writable).

Only the Python standard library is used (zlib/struct for the PNG
encoding).  All drawing - including the bitmap font - is implemented
here, so the output is byte-identical on every run.  No network.
"""

import os
import struct
import zlib
from math import hypot

# ---------------------------------------------------------------- canvas

WIDTH = 1024
HEIGHT = 1024


class Canvas:
    """A tiny RGB framebuffer with just the primitives we need."""

    def __init__(self, width, height, colour):
        self.w = width
        self.h = height
        self.px = bytearray(bytes(colour) * (width * height))

    def set_px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            if 0 <= yy < self.h:
                x0 = max(0, x)
                x1 = min(self.w, x + w)
                if x0 < x1:
                    i = (yy * self.w + x0) * 3
                    self.px[i:i + (x1 - x0) * 3] = bytes(colour) * (x1 - x0)

    def rect_outline(self, x, y, w, h, colour, t=2):
        self.fill_rect(x, y, w, t, colour)
        self.fill_rect(x, y + h - t, w, t, colour)
        self.fill_rect(x, y, t, h, colour)
        self.fill_rect(x + w - t, y, t, h, colour)

    def fill_circle(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if hypot(xx - cx, yy - cy) <= r:
                    self.set_px(xx, yy, colour)

    def ring(self, cx, cy, r, colour, t=3):
        for yy in range(cy - r - t, cy + r + t + 1):
            for xx in range(cx - r - t, cx + r + t + 1):
                if abs(hypot(xx - cx, yy - cy) - r) <= t / 2.0:
                    self.set_px(xx, yy, colour)

    def line(self, x0, y0, x1, y1, colour, t=1):
        # Bresenham, optionally thickened by stamping small squares.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.fill_rect(x0 - t // 2, y0 - t // 2, t, t, colour)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polyline(self, points, colour, t=2):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            self.line(ax, ay, bx, by, colour, t)

    def fill_triangle(self, ax, ay, bx, by, cx, cy, colour):
        def edge(px, py, qx, qy, rx, ry):
            return (px - qx) * (ry - qy) - (py - qy) * (rx - qx)

        minx = max(0, min(ax, bx, cx))
        maxx = min(self.w - 1, max(ax, bx, cx))
        miny = max(0, min(ay, by, cy))
        maxy = min(self.h - 1, max(ay, by, cy))
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                d1 = edge(xx, yy, ax, ay, bx, by)
                d2 = edge(xx, yy, bx, by, cx, cy)
                d3 = edge(xx, yy, cx, cy, ax, ay)
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or \
                        (d1 <= 0 and d2 <= 0 and d3 <= 0):
                    self.set_px(xx, yy, colour)


# ------------------------------------------------------------------ font
# A 5x7 bitmap font.  Each glyph is seven rows of five pixels; '#' is ink.

FONT = {
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    '2': (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '$': (".###.", "#.#.#", "#.#..", ".###.", "..#.#", "#.#.#", ".###."),
    '%': ("##..#", "#.#.#", "##.#.", "...#.", "..#..", ".#.##", "#..##"),
}


def text_width(text, scale):
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def draw_text(cv, x, y, text, scale, colour):
    text = text.upper()
    for i, ch in enumerate(text):
        glyph = FONT.get(ch, FONT[' '])
        gx = x + i * 6 * scale
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == '#':
                    cv.fill_rect(gx + col * scale, y + row * scale,
                                 scale, scale, colour)
    return text_width(text, scale)


def draw_text_centered(cv, y, text, scale, colour):
    x = (cv.w - text_width(text, scale)) // 2
    draw_text(cv, x, y, text, scale, colour)


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    current = ""
    for word in text.upper().split():
        trial = word if not current else current + " " + word
        if text_width(trial, scale) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------- layout
# Broadsheet front page: cream paper, black ink, one red accent.

PAPER = (247, 241, 226)
PANEL_BG = (253, 250, 241)
INK = (18, 18, 20)
RED = (178, 32, 38)
FAINT = (96, 90, 78)
RULE = (18, 18, 20)

# The three lead stories: (tag, headline, detail, giant, motif)
LEADS = [
    ("MARKETS - GLOBAL",
     "NVIDIA LEAPS AS HUANG RETURNS AS CEO",
     "SHARES SOAR AFTER THE AI SELL-OFF; NASDAQ UP 6.5%",
     "+31%", "chart"),
    ("CLIMATE - ANTALYA",
     "COP31 TALKS END WITHOUT A DEAL",
     "130+ PARTIES REJECT A TEXT WITH NO FOSSIL-FUEL PHASE-OUT",
     "130+", "globe"),
    ("DISASTER - INDONESIA",
     "CANDY FACTORY FIRE KILLS 24 WORKERS",
     "ABOUT 30 PEOPLE STILL MISSING AFTER THE WEEKEND BLAZE",
     "24", "flame"),
]

# Ten medium stories: (tag, headline line 1, headline line 2)
MEDIUM = [
    ("EUROPE - REUTERS", "DYMER, UKRAINE: RUSSIAN ATTACK",
     "KILLS 11 AS RESCUERS SEARCH RUBBLE"),
    ("AFRICA - AFP", "KHARTOUM, SUDAN: DRONE STRIKES HIT",
     "HOMES AND A U.N. BUILDING"),
    ("EUROPE - AP", "LIBYA: UKRAINE SINKS RUSSIAN",
     "WARSHIP IN NAVAL DRONE ATTACK"),
    ("EUROPE - REUTERS", "GERMANY: BOMB THREATS SENT TO",
     "ABOUT 450 SCHOOLS BY EMAIL"),
    ("N. AMERICA - AP", "U.S. HOUSE: DEMOCRATS CLINCH",
     "258-SEAT MAJORITY, BEST SINCE 1992"),
    ("AFRICA - REUTERS", "CONGO HALTS COBALT EXPORTS",
     "AGAIN TO LIFT WEAK PRICES"),
    ("EUROPE - REUTERS", "SPAIN: COURT CLEARS CATALAN",
     "LEADER PUIGDEMONT TO RETURN"),
    ("MIDDLE EAST - REUTERS", "SYRIA: U.S. DISCUSSES TRAINING",
     "SYRIAN FORCES IN DEMINING"),
    ("WORLD SPORT - AP", "FIFA PICKS U.S.-LED BID FOR 2031",
     "WOMEN'S WORLD CUP; UK GETS 2035"),
    ("SPACE - JIJI", "MERCURY: JAPAN-EUROPE PROBES",
     "ENTER ORBIT AFTER 8 YEARS"),
]

# Seventeen more stories, one line each, for the "also" list.
ALSO = [
    "N. KOREA MAY SHUT SWISS OFFICE",
    "CZECH + HUNGARY REJECT EU BUDGET",
    "RUSSIA: $576M KALININGRAD FERRIES",
    "EU PROPOSES NEW RUSSIA SANCTIONS",
    "EU SIGNS TRADE DEAL WITH INDONESIA",
    "CROWDSTRIKE BUYS ZSCALER FOR $44BN",
    "HONDA RECALLS 810,000 VEHICLES",
    "FBI PROBES CRIME DATABASE HACK",
    "REP. GOMEZ RESIGNS: ETHICS REPORT",
    "DELTA FAULT DELAYS HOLIDAY FLIGHTS",
    "VERSTAPPEN WINS LAS VEGAS GP",
    "SKUBAL AGREES RECORD $450M METS DEAL",
    "GOLD REBOUNDS NEARLY 5%",
    "CANADA, QATAR INK INVESTMENT PACT",
    "CHINA: DEATH SENTENCE FOR SPY OFFICIAL",
    "9 SHOT AT CALIFORNIA CONCERT",
    "BELGIUM FLIGHTS GROUNDED BY STRIKE",
]


# ---------------------------------------------------------------- motifs
# Bold pictograms for the three lead panels, drawn around (cx, cy).

def motif_chart(cv, cx, cy):
    # A market line crashing, then rebounding steeply in red.
    cv.line(cx - 42, cy + 30, cx + 44, cy + 30, INK, 3)
    cv.line(cx - 42, cy + 30, cx - 42, cy - 30, INK, 3)
    cv.polyline([(cx - 38, cy - 16), (cx - 16, cy + 4), (cx - 2, cy + 20)],
                INK, 4)
    cv.polyline([(cx - 2, cy + 20), (cx + 18, cy - 6), (cx + 40, cy - 26)],
                RED, 5)
    cv.polyline([(cx + 40, cy - 26), (cx + 29, cy - 25), (cx + 39, cy - 15)],
                RED, 4)


def motif_globe(cv, cx, cy):
    # A globe with a crack, and a red slash: the talks failed.
    cv.ring(cx, cy, 32, INK, 4)
    cv.polyline([(cx - 28, cy + 6), (cx - 11, cy - 2), (cx + 4, cy + 6),
                 (cx + 19, cy - 2), (cx + 29, cy + 4)], INK, 3)
    cv.polyline([(cx - 3, cy - 31), (cx + 3, cy - 13), (cx - 4, cy + 3),
                 (cx + 3, cy + 17), (cx - 2, cy + 31)], RED, 4)
    cv.line(cx - 38, cy + 38, cx + 38, cy - 38, RED, 5)


def motif_flame(cv, cx, cy):
    # A factory block with flames over the roof.
    cv.fill_rect(cx - 40, cy + 6, 56, 30, INK)
    cv.fill_rect(cx + 24, cy - 12, 12, 48, INK)
    for fx in (cx - 28, cx - 10, cx + 8):
        cv.fill_triangle(fx - 8, cy - 2, fx + 8, cy - 2, fx, cy - 32, RED)
    cv.fill_rect(cx - 30, cy + 20, 9, 10, PAPER)
    cv.fill_rect(cx - 14, cy + 20, 9, 10, PAPER)


MOTIFS = {"chart": motif_chart, "globe": motif_globe, "flame": motif_flame}


# ---------------------------------------------------------------- panels

MARGIN = 20
CONTENT_W = WIDTH - 2 * MARGIN  # 984


def draw_lead(cv, x, y, w, h, story):
    tag, headline, detail, giant, motif = story
    cv.fill_rect(x, y, w, h, PANEL_BG)
    cv.rect_outline(x, y, w, h, RULE, 2)
    cv.fill_rect(x, y, w, 7, RED)

    draw_text(cv, x + 14, y + 16, tag, 2, RED)

    hy = y + 40
    for line_text in wrap_text(headline, 3, w - 28):
        draw_text(cv, x + 14, hy, line_text, 3, INK)
        hy += 27

    dy = y + 124
    for line_text in wrap_text(detail, 2, w - 28):
        draw_text(cv, x + 14, dy, line_text, 2, FAINT)
        dy += 18

    # The giant key number, bottom left; motif at bottom right.
    draw_text(cv, x + 14, y + h - 62, giant, 8, RED)
    MOTIFS[motif](cv, x + w - 62, y + h - 48)


def draw_medium(cv, x, y, w, h, story):
    tag, line1, line2 = story
    cv.fill_rect(x, y, w, h, PANEL_BG)
    cv.rect_outline(x, y, w, h, RULE, 1)
    cv.fill_rect(x, y, 6, h, RED)
    draw_text(cv, x + 14, y + 6, tag, 2, RED)
    draw_text(cv, x + 14, y + 24, line1, 2, INK)
    draw_text(cv, x + 14, y + 42, line2, 2, INK)


def render():
    cv = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead: red rules, the title, then the date in huge type.
    cv.fill_rect(MARGIN, 14, CONTENT_W, 4, RED)
    cv.fill_rect(MARGIN, 22, CONTENT_W, 2, RULE)
    draw_text_centered(cv, 30, "THE DAILY WORLD", 8, INK)
    draw_text_centered(cv, 94, "MONDAY 23 NOVEMBER 2026", 5, RED)
    draw_text_centered(cv, 138,
                       "30 STORIES - 7 REGIONS - ALL REPORTED 23 NOV 2026 (UTC)",
                       2, FAINT)
    cv.fill_rect(MARGIN, 158, CONTENT_W, 4, RULE)

    # Three lead stories across the top.
    lead_y, lead_h, lead_w, lead_gap = 172, 240, 320, 12
    for i, story in enumerate(LEADS):
        draw_lead(cv, MARGIN + i * (lead_w + lead_gap), lead_y,
                  lead_w, lead_h, story)

    # Ten medium stories, two columns of five.
    med_y, med_h, med_w, med_gap = 424, 62, 486, 12
    for i, story in enumerate(MEDIUM):
        col, row = i % 2, i // 2
        draw_medium(cv, MARGIN + col * (med_w + med_gap),
                    med_y + row * (med_h + 6), med_w, med_h, story)

    # The rest of the day as a compact one-line list.
    list_y = 424 + 5 * med_h + 4 * 6 + 14  # 772
    draw_text(cv, MARGIN, list_y, "ALSO ON 23 NOVEMBER", 3, INK)
    cv.fill_rect(MARGIN, list_y + 26, CONTENT_W, 3, RED)
    item_y = list_y + 38
    half = (len(ALSO) + 1) // 2
    for i, item in enumerate(ALSO):
        col, row = (0, i) if i < half else (1, i - half)
        x = MARGIN + col * (med_w + med_gap)
        y = item_y + row * 16
        cv.fill_rect(x, y + 3, 7, 7, RED)
        draw_text(cv, x + 14, y, item, 2, INK)

    # Footer: the date check.
    foot_y = item_y + half * 16 + 8
    cv.fill_rect(MARGIN, foot_y, CONTENT_W, 3, RULE)
    draw_text_centered(cv, foot_y + 10,
                       "DATE CHECK: EVERY STORY ABOVE WAS REPORTED ON "
                       "MONDAY 23 NOVEMBER 2026", 2, INK)
    draw_text_centered(cv, foot_y + 28,
                       "SOURCES: REUTERS - AP - AFP - BBC - DOW JONES - JIJI PRESS",
                       2, FAINT)
    cv.fill_rect(MARGIN, foot_y + 50, CONTENT_W, 4, RED)
    return cv


# -------------------------------------------------------------- PNG file

def encode_png(cv):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    raw = bytearray()
    stride = cv.w * 3
    for yy in range(cv.h):
        raw.append(0)  # filter type 0 (None) for every scanline
        raw += cv.px[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    data = encode_png(render())
    try:
        os.makedirs("/output", exist_ok=True)
        path = "/output/entry.png"
        with open(path, "wb") as fh:
            fh.write(data)
    except OSError:
        path = "./entry.png"
        with open(path, "wb") as fh:
            fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
