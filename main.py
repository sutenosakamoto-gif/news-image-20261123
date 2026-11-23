#!/usr/bin/env python3
"""World News - 23 November 2026, in one image.

A self-contained renderer: running this program draws a 1024x1024
infographic summarising six world news stories of Monday, 23 November
2026 and writes it as a PNG to /output/entry.png (falling back to
./entry.png when /output is not writable).

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

BG = (13, 20, 36)
PANEL = (24, 34, 56)
PANEL_EDGE = (64, 84, 120)
TITLE = (240, 244, 250)
SUB = (160, 175, 200)
HEADLINE = (235, 240, 248)
DETAIL = (170, 182, 205)
WHITE = (225, 232, 242)
GREY = (120, 134, 158)

# Each story: (number, accent colour, tag, headline, detail, source, motif)
STORIES = [
    ("1", (240, 160, 60), "CLIMATE - ANTALYA, TURKIYE",
     "COP31 talks end without a deal",
     "EU and 130 parties reject a text with no fossil-fuel phase-out",
     "REUTERS", "climate"),
    ("2", (90, 150, 240), "UKRAINE - DYMER, KYIV REGION",
     "Russian attack on Dymer kills 11",
     "Toll rises as rescuers pull another body from the rubble",
     "REUTERS", "house"),
    ("3", (230, 90, 80), "SUDAN - KHARTOUM",
     "Drone strikes hit homes and a U.N. building",
     "Explosions heard near the airport from 2:00 to 4:30 a.m.",
     "AFP / JAPAN TIMES", "drone"),
    ("4", (245, 110, 50), "INDONESIA - BANTEN",
     "Factory fire kills 24; 30 still missing",
     "Weekend blaze at a candy factory in Cikande, Serang regency",
     "REUTERS", "factory"),
    ("5", (80, 200, 140), "MARKETS - GLOBAL",
     "AI sell-off shakes markets; futures rebound",
     "Asia mixed: Taiwan up, South Korea's KOSPI down",
     "REUTERS", "chart"),
    ("6", (170, 130, 240), "SPACE - MERCURY",
     "Japan-Europe probes enter Mercury orbit",
     "BepiColombo's Mio and MPO arrive after an eight-year journey",
     "JIJI / JAPAN TIMES", "orbit"),
]


# ---------------------------------------------------------------- motifs
# Small pictograms, each drawn around a centre point (cx, cy).

def motif_climate(cv, cx, cy):
    # A globe with a crack in it and a red "no deal" slash across.
    cv.ring(cx, cy, 34, (90, 160, 240), 3)
    cv.polyline([(cx - 30, cy + 6), (cx - 12, cy - 2), (cx + 4, cy + 6),
                 (cx + 20, cy - 2), (cx + 31, cy + 4)], (90, 160, 240), 2)
    cv.polyline([(cx - 4, cy - 33), (cx + 3, cy - 14), (cx - 5, cy + 2),
                 (cx + 4, cy + 18), (cx - 2, cy + 33)], (240, 160, 60), 3)
    cv.line(cx - 40, cy + 40, cx + 40, cy - 40, (230, 70, 60), 4)


def motif_house(cv, cx, cy):
    # A house with a cracked wall and an explosion burst beside it.
    cv.rect_outline(cx - 32, cy - 2, 58, 36, WHITE, 3)
    cv.line(cx - 38, cy - 2, cx - 3, cy - 30, WHITE, 3)
    cv.line(cx - 3, cy - 30, cx + 32, cy - 2, WHITE, 3)
    cv.polyline([(cx - 12, cy + 2), (cx - 6, cy + 12), (cx - 13, cy + 20),
                 (cx - 7, cy + 30)], (230, 90, 80), 2)
    cv.fill_rect(cx - 6, cy + 14, 12, 20, (90, 150, 240))
    bx, by = cx + 38, cy - 32
    for dx, dy in ((0, -12), (9, -9), (12, 0), (9, 9), (0, 12),
                   (-9, 9), (-12, 0), (-9, -9)):
        cv.line(bx, by, bx + dx, by + dy, (250, 200, 70), 3)
    cv.fill_circle(bx, by, 4, (250, 200, 70))


def motif_drone(cv, cx, cy):
    # A quadcopter seen from the front, rotors spinning at the corners.
    for dx, dy in ((-30, -20), (30, -20), (-30, 20), (30, 20)):
        cv.line(cx, cy, cx + dx, cy + dy, GREY, 3)
        cv.ring(cx + dx, cy + dy, 8, WHITE, 2)
    cv.fill_rect(cx - 11, cy - 7, 22, 14, WHITE)
    cv.fill_circle(cx, cy + 20, 4, (230, 70, 60))
    cv.line(cx, cy + 7, cx, cy + 16, GREY, 2)


def motif_factory(cv, cx, cy):
    # A factory block with a chimney and flames over the roof.
    cv.fill_rect(cx - 40, cy + 4, 58, 32, GREY)
    cv.fill_rect(cx + 24, cy - 16, 12, 52, GREY)
    cv.polyline([(cx - 40, cy + 4), (cx - 26, cy - 8), (cx - 12, cy + 4),
                 (cx + 2, cy - 8), (cx + 16, cy + 4)], WHITE, 2)
    for fx in (cx - 30, cx - 12, cx + 6):
        cv.fill_triangle(fx - 7, cy - 6, fx + 7, cy - 6, fx, cy - 30,
                         (245, 110, 50))
        cv.fill_triangle(fx - 4, cy - 6, fx + 4, cy - 6, fx, cy - 20,
                         (250, 200, 70))
    cv.fill_rect(cx - 32, cy + 20, 8, 10, (250, 200, 70))
    cv.fill_rect(cx - 16, cy + 20, 8, 10, (250, 200, 70))


def motif_chart(cv, cx, cy):
    # A market line: down hard in red, then rebounding in green.
    cv.line(cx - 44, cy + 30, cx + 46, cy + 30, GREY, 2)
    cv.line(cx - 44, cy + 30, cx - 44, cy - 32, GREY, 2)
    cv.polyline([(cx - 40, cy - 14), (cx - 18, cy + 2), (cx - 2, cy + 20)],
                (230, 80, 70), 3)
    cv.polyline([(cx - 2, cy + 20), (cx + 20, cy - 4), (cx + 42, cy - 24)],
                (80, 210, 140), 3)
    cv.polyline([(cx + 42, cy - 24), (cx + 32, cy - 23), (cx + 41, cy - 14)],
                (80, 210, 140), 3)


def motif_orbit(cv, cx, cy):
    # Mercury with an orbit ring and the two BepiColombo orbiters.
    px, py = cx - 16, cy + 12
    cv.ring(px, py, 44, GREY, 2)
    cv.fill_circle(px, py, 25, (203, 152, 110))
    cv.line(px - 22, py - 6, px + 22, py - 10, (160, 112, 74), 3)
    cv.line(px - 24, py + 8, px + 24, py + 4, (160, 112, 74), 3)
    for sx, sy in ((cx + 28, cy - 28), (cx + 34, cy + 16)):
        cv.fill_rect(sx - 13, sy - 3, 9, 6, (90, 150, 240))
        cv.fill_rect(sx + 4, sy - 3, 9, 6, (90, 150, 240))
        cv.fill_rect(sx - 4, sy - 4, 8, 8, WHITE)


MOTIFS = {
    "climate": motif_climate,
    "house": motif_house,
    "drone": motif_drone,
    "factory": motif_factory,
    "chart": motif_chart,
    "orbit": motif_orbit,
}


# ---------------------------------------------------------------- panels

MARGIN = 24
PANEL_W = 480
PANEL_H = 268
PANEL_GAP = 16
PANELS_TOP = 132
ROW_GAP = 14


def draw_panel(cv, x, y, story):
    number, accent, tag, headline, detail, source, motif = story
    cv.fill_rect(x, y, PANEL_W, PANEL_H, PANEL)
    cv.rect_outline(x, y, PANEL_W, PANEL_H, PANEL_EDGE, 2)

    # Number disc and category tag.
    cv.fill_circle(x + 27, y + 25, 12, accent)
    draw_text(cv, x + 22, y + 18, number, 2, BG)
    draw_text(cv, x + 48, y + 17, tag, 2, accent)

    # Headline, wrapped to leave the right-hand column for the motif.
    lines = wrap_text(headline, 3, PANEL_W - 32 - 128)
    hy = y + 48
    for line_text in lines:
        draw_text(cv, x + 16, hy, line_text, 3, HEADLINE)
        hy += 27

    # Motif pictogram in the right-hand column.
    MOTIFS[motif](cv, x + PANEL_W - 72, y + 96)

    # Detail text under the headline.
    dy = max(hy + 12, y + 160)
    for line_text in wrap_text(detail, 2, PANEL_W - 32):
        draw_text(cv, x + 16, dy, line_text, 2, DETAIL)
        dy += 19

    # Source line at the bottom of the panel.
    draw_text(cv, x + 16, y + PANEL_H - 28, "SOURCE: " + source, 2, SUB)


def render():
    cv = Canvas(WIDTH, HEIGHT, BG)

    # Header: title and date line.
    draw_text_centered(cv, 24, "WORLD NEWS", 7, TITLE)
    draw_text_centered(cv, 84, "MONDAY 23 NOVEMBER 2026", 2, SUB)
    cv.fill_rect(MARGIN, 116, WIDTH - 2 * MARGIN, 3, PANEL_EDGE)

    # Six story panels in a 2x3 grid.
    for i, story in enumerate(STORIES):
        col = i % 2
        row = i // 2
        x = MARGIN + col * (PANEL_W + PANEL_GAP)
        y = PANELS_TOP + row * (PANEL_H + ROW_GAP)
        draw_panel(cv, x, y, story)

    # Footer with the source outlets.
    draw_text_centered(cv, 984,
                       "SOURCES: REUTERS - AFP VIA THE JAPAN TIMES - JIJI PRESS",
                       2, SUB)
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
