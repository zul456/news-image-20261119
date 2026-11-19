#!/usr/bin/env python3
"""Draw the front page of Thursday 19 November 2026 in one image.

Deterministic: no network, no randomness, no timestamps. Running this
program twice writes byte-identical PNGs. Output goes to
$MAKEFUN_OUTPUT_DIR/entry.png (or ./entry.png when unset).
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 38, 74)
GOLD = (200, 162, 74)
WHITE = (255, 255, 255)
GREY = (110, 108, 100)
LIGHT_GREY = (214, 208, 194)

FONT_DIR = os.environ.get("MAKEFUN_FONT_DIR", "/usr/share/fonts/truetype/dejavu")


def load_font(name, size):
    """Try a DejaVu file first, fall back to Pillow's bundled font."""
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except Exception:
        return ImageFont.load_default(size=size)


def serif_bold(size):
    return load_font("DejaVuSerif-Bold.ttf", size)


def sans(size):
    return load_font("DejaVuSans.ttf", size)


def sans_bold(size):
    return load_font("DejaVuSans-Bold.ttf", size)


def wrap(draw, text, font, max_width):
    """Greedy word wrap returning a list of lines that fit max_width."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_spaced(draw, xy, text, font, fill, spacing=3):
    """Draw text with extra letter spacing (for kickers)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x


def draw_icon(draw, kind, cx, cy, color):
    """Small geometric motif for a story panel, centred on (cx, cy)."""
    if kind == "summit":
        # Three leaders at one table: three circles over a table line.
        for i, c in enumerate(((176, 42, 48), (200, 162, 74), (36, 86, 166))):
            draw.ellipse([cx - 52 + i * 34, cy - 26, cx - 28 + i * 34, cy - 2], fill=c)
        draw.rectangle([cx - 58, cy + 2, cx + 58, cy + 8], fill=INK)
        draw.rectangle([cx - 52, cy + 8, cx - 46, cy + 22], fill=INK)
        draw.rectangle([cx + 46, cy + 8, cx + 52, cy + 22], fill=INK)
    elif kind == "gulf":
        # Drone arcs over a sea line.
        draw.arc([cx - 44, cy - 34, cx + 44, cy + 30], start=200, end=340, fill=color, width=3)
        for dx, dy in ((-30, -18), (0, -30), (30, -18)):
            draw.ellipse([cx + dx - 5, cy + dy - 5, cx + dx + 5, cy + dy + 5], fill=color)
        draw.rectangle([cx - 48, cy + 18, cx + 48, cy + 22], fill=color)
    elif kind == "markets":
        # Rising bar chart.
        bars = (12, 22, 32, 44)
        for i, h in enumerate(bars):
            x0 = cx - 44 + i * 23
            draw.rectangle([x0, cy + 22 - h, x0 + 15, cy + 22], fill=color)
    elif kind == "bridge":
        # Suspension bridge: deck, towers, cables.
        draw.line([cx - 48, cy + 16, cx + 48, cy + 16], fill=color, width=4)
        for tx in (-38, 38):
            draw.line([cx + tx, cy - 26, cx + tx, cy + 16], fill=color, width=4)
        draw.line([cx - 38, cy - 26, cx, cy + 16], fill=color, width=3)
        draw.line([cx + 38, cy - 26, cx, cy + 16], fill=color, width=3)
    elif kind == "justice":
        # Scales of justice.
        draw.line([cx, cy - 28, cx, cy + 22], fill=color, width=3)
        draw.line([cx - 34, cy - 22, cx + 34, cy - 22], fill=color, width=3)
        for sx in (-34, 34):
            draw.line([cx + sx, cy - 22, cx + sx - 12, cy + 2], fill=color, width=2)
            draw.line([cx + sx, cy - 22, cx + sx + 12, cy + 2], fill=color, width=2)
            draw.arc([cx + sx - 12, cy - 4, cx + sx + 12, cy + 14], start=0, end=180, fill=color, width=2)
    elif kind == "euro":
        # Euro coin: ring with a euro sign.
        draw.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=color, width=4)
        draw.text((cx - 11, cy - 20), "\u20ac", font=sans_bold(36), fill=color)


STORIES = [
    dict(
        kicker="SUMMIT  \u00b7  SHENZHEN",
        color=(176, 42, 48),
        icon="summit",
        headline="Trump, Xi and Putin hold first three-way summit",
        summary=("The leaders of the US, China and Russia meet in Shenzhen on the "
                 "APEC sidelines \u2014 the first talks of the three together. "
                 "Ukraine tops the agenda."),
        source="REUTERS",
    ),
    dict(
        kicker="THE GULF",
        color=(15, 107, 92),
        icon="gulf",
        headline="Iran fires drones at US bases in Kuwait and Bahrain",
        summary=("Overnight strikes follow a US attack on a missile site on Iran\u2019s "
                 "Qeshm Island; Gulf defences intercepted the drones."),
        source="REUTERS",
    ),
    dict(
        kicker="MARKETS",
        color=(46, 107, 46),
        icon="markets",
        headline="Anthropic starts trading after record $81.3bn IPO",
        summary=("Shares debut on Nasdaq as ANT at $83, valuing the Claude maker "
                 "at about $1.5 trillion, a record IPO."),
        source="BLOOMBERG",
    ),
    dict(
        kicker="UKRAINE",
        color=(36, 86, 166),
        icon="bridge",
        headline="Crimean Bridge hit for a third time in a week",
        summary=("An overnight strike halts traffic again, days after a 227-metre "
                 "road section fell into the Kerch Strait."),
        source="DEUTSCHE WELLE",
    ),
    dict(
        kicker="JUSTICE  \u00b7  THE HAGUE",
        color=(107, 63, 160),
        icon="justice",
        headline="World court to rule today on Rohingya genocide case",
        summary=("The ICJ delivers its verdict on whether Myanmar committed "
                 "genocide \u2014 a first for a state."),
        source="HUMAN RIGHTS WATCH",
    ),
    dict(
        kicker="EUROPE  \u00b7  BRUSSELS",
        color=(20, 38, 74),
        icon="euro",
        headline="EU proposes \u20ac45bn loan for Ukraine",
        summary=("Brussels would lend Kyiv up to \u20ac45 billion for 2027, to be repaid "
                 "only if Russia pays war reparations."),
        source="REUTERS",
    ),
]


def draw_card(draw, box, story, headline_size, summary_size, max_summary_lines=3):
    x0, y0, x1, y1 = box
    draw.rectangle([x0, y0, x1, y1], fill=WHITE, outline=LIGHT_GREY, width=2)
    draw.rectangle([x0, y0, x0 + 8, y1], fill=story["color"])
    pad = 24
    tx = x0 + pad + 8
    # Kicker.
    draw_spaced(draw, (tx, y0 + 16), story["kicker"], sans_bold(15), story["color"], spacing=2)
    # Headline.
    hfont = serif_bold(headline_size)
    lines = wrap(draw, story["headline"], hfont, x1 - tx - 130)
    y = y0 + 44
    for line in lines:
        draw.text((tx, y), line, font=hfont, fill=INK)
        y += headline_size + 4
    # Summary, truncated so it never reaches the source tag.
    sfont = sans(summary_size)
    full = wrap(draw, story["summary"], sfont, x1 - tx - 16)
    limit = y1 - 34
    room = max(0, (limit - y - 6) // (summary_size + 4))
    keep = min(max_summary_lines, room)
    slines = full[:keep]
    if len(full) > len(slines) and slines:
        slines[-1] = slines[-1].rstrip() + " \u2026"
    y += 6
    for line in slines:
        draw.text((tx, y), line, font=sfont, fill=(60, 58, 52))
        y += summary_size + 4
    # Source tag, bottom left.
    draw.text((tx, y1 - 26), "SOURCE: " + story["source"], font=sans_bold(12), fill=GREY)
    # Icon, top right.
    draw_icon(draw, story["icon"], x1 - 62, y0 + 52, story["color"])


def main():
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # --- Masthead ---
    draw.rectangle([0, 0, W, 150], fill=NAVY)
    draw_spaced(draw, (28, 20), "THE WORLD IN ONE PAGE", sans_bold(17), GOLD, spacing=4)
    draw.text((28, 48), "Thursday 19 November 2026", font=serif_bold(54), fill=WHITE)
    draw.text((28, 116), "Six stories that defined the day",
              font=sans(19), fill=(205, 210, 225))
    draw.line([28, 142, W - 28, 142], fill=GOLD, width=2)

    # --- Lead story (summit), full width ---
    draw_card(draw, (28, 164, 996, 372), STORIES[0], 33, 18)

    # --- Grid: stories 2-5, two columns x two rows ---
    grid = [(28, 386, 498, 584), (526, 386, 996, 584),
            (28, 598, 498, 796), (526, 598, 996, 796)]
    for box, story in zip(grid, STORIES[1:5]):
        draw_card(draw, box, story, 21, 14, max_summary_lines=2)

    # --- Bottom strip: story 6 (EU loan), full width ---
    draw_card(draw, (28, 810, 996, 962), STORIES[5], 24, 16)

    # --- Footer ---
    draw.text((W // 2, 978),
              "Sources: Reuters  \u00b7  Associated Press  \u00b7  The Guardian  \u00b7  "
              "Deutsche Welle  \u00b7  Human Rights Watch  \u00b7  Bloomberg",
              font=sans(13), fill=GREY, anchor="ma")
    draw.text((W // 2, 998), "Drawn by a program; no photograph used.",
              font=sans(13), fill=GREY, anchor="ma")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    os.makedirs(out_dir, exist_ok=True)
    img.save(os.path.join(out_dir, "entry.png"), format="PNG")


if __name__ == "__main__":
    main()
