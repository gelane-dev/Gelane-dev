"""Gera os SVGs do profile README de gelane-dev.

    python scripts/generate.py

Saída em assets/:
  contributions.svg  -> gráfico de contribuições (raspado da página pública)
  avatar.svg         -> avatar convertido em ASCII colorido
  neofetch.svg       -> card estilo neofetch com informações do perfil

Dependência: Pillow. Sem token: usa só páginas públicas do GitHub.
"""

from __future__ import annotations

import datetime as dt
import html
import base64
import io
import os
import re
import urllib.request
from collections import Counter
from pathlib import Path

from PIL import Image, ImageEnhance

USER = "gelane-dev"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

FONT = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,'Liberation Mono',monospace"

# Paleta: tinta de mangá + azul do perfil + dourado do pôr do sol do avatar
BG = "#0b1220"
PANEL = "#0f1828"
BORDER = "#1f2b40"
INK = "#e6edf7"
MUTED = "#6b7a93"
BLUE = "#2e9ef7"
CYAN = "#6dd5fa"
GOLD = "#f4b860"
GREEN = "#7ee787"
PINK = "#ff8fb1"
LEVELS = ["#152033", "#123d66", "#1b6fb8", "#2e9ef7", "#8be3ff"]


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme-generator"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def window(width: int, height: int, title: str, body: str, extra_style: str = "") -> str:
    """Janela de terminal com os três botões."""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<style>
text{{font-family:{FONT}}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes blink{{50%{{opacity:0}}}}
.cursor{{animation:blink 1s steps(1) infinite}}
{extra_style}
</style>
<rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10" fill="{PANEL}" stroke="{BORDER}"/>
<path d="M0.5 30 V10.5 a10 10 0 0 1 10 -10 H{width-10.5} a10 10 0 0 1 10 10 V30 Z" fill="#131f33"/>
<line x1="0.5" y1="30" x2="{width-0.5}" y2="30" stroke="{BORDER}"/>
<circle cx="18" cy="15.5" r="5" fill="#ff5f57"/><circle cx="34" cy="15.5" r="5" fill="#febc2e"/><circle cx="50" cy="15.5" r="5" fill="#28c840"/>
<text x="{width/2}" y="19.5" text-anchor="middle" font-size="11" fill="{MUTED}">{esc(title)}</text>
{body}
</svg>
"""


# ---------------------------------------------------------------- contribuições

def contributions() -> str:
    page = fetch(f"https://github.com/users/{USER}/contributions").decode("utf-8")
    cells = re.findall(r'data-date="(\d{4}-\d{2}-\d{2})" id="([^"]+)" data-level="(\d)"', page)
    counts = {}
    for cid, label in re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]*)</tool-tip>', page):
        m = re.match(r"(\d+) contribution", label)
        counts[cid] = int(m.group(1)) if m else 0

    days = sorted((dt.date.fromisoformat(d), int(lvl), counts.get(cid, 0)) for d, cid, lvl in cells)
    total = sum(c for _, _, c in days)
    first = days[0][0]
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # domingo

    cell, gap = 11, 3
    left, top = 44, 62
    weeks = (days[-1][0] - start).days // 7 + 1
    width = left + weeks * (cell + gap) + 24
    height = top + 7 * (cell + gap) + 46

    rects, months = [], []
    seen_month = None
    for day, lvl, cnt in days:
        w = (day - start).days // 7
        r = (day.weekday() + 1) % 7
        x, y = left + w * (cell + gap), top + r * (cell + gap)
        delay = w * 0.025 + r * 0.01
        title = f"{cnt} em {day:%d/%m/%Y}"
        rects.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2.5" fill="{LEVELS[lvl]}" '
            f'style="animation-delay:{delay:.2f}s"><title>{title}</title></rect>'
        )
        if day.day <= 7 and day.month != seen_month and r == 0:
            seen_month = day.month
            name = "Jan Fev Mar Abr Mai Jun Jul Ago Set Out Nov Dez".split()[day.month - 1]
            months.append(f'<text x="{x}" y="{top-10}" font-size="10" fill="{MUTED}">{name}</text>')

    wd = "".join(
        f'<text x="{left-10}" y="{top + r*(cell+gap) + 9}" font-size="10" fill="{MUTED}" text-anchor="end">{n}</text>'
        for r, n in ((1, "Seg"), (3, "Qua"), (5, "Sex"))
    )
    legend_x = width - 24 - 5 * (cell + gap) - 70
    ly = height - 22
    legend = f'<text x="{legend_x}" y="{ly+9}" font-size="10" fill="{MUTED}">menos</text>' + "".join(
        f'<rect x="{legend_x + 36 + i*(cell+gap)}" y="{ly}" width="{cell}" height="{cell}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(LEVELS)
    ) + f'<text x="{legend_x + 40 + 5*(cell+gap)}" y="{ly+9}" font-size="10" fill="{MUTED}">mais</text>'

    body = (
        "".join(months) + wd + '<g class="cells">' + "".join(rects) + "</g>"
        + f'<text x="{left}" y="{ly+9}" font-size="12" fill="{INK}" font-weight="700">'
        f'<tspan fill="{CYAN}">{total}</tspan> contribuições no último ano</text>'
        + legend
    )
    style = ".cells rect{opacity:0;animation:in .4s ease-out forwards}"
    return window(width, height, "Gelane-Dev@github ~ $ ./contributions.sh", body, style)


# ---------------------------------------------------------------- avatar ASCII

RAMP = " .:-=+*#%@"


def tone(r: int, g: int, b: int) -> str:
    """Quantiza a cor do pixel para a paleta do perfil."""
    mx, mn = max(r, g, b), min(r, g, b)
    sat = (mx - mn) / mx if mx else 0
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if sat > 0.28 and r > b and lum > 70:
        return GOLD if lum > 150 else "#c98a3a"  # pôr do sol / folhagem quente
    if sat > 0.22 and g >= r and lum > 50:
        return "#5f8f6a"  # folhagem
    if lum > 200:
        return INK
    if lum > 140:
        return CYAN
    return BLUE


def avatar() -> str:
    img = Image.open(io.BytesIO(fetch(f"https://github.com/{USER}.png?size=460"))).convert("RGB")
    img = ImageEnhance.Contrast(img).enhance(1.35)
    cols, rows = 84, 46
    small = img.resize((cols, rows), Image.LANCZOS)
    gray = small.convert("L")

    fs, cw, lh = 7.2, 4.4, 8.2
    width = 420
    ox = (width - cols * cw) / 2
    oy = 48
    lines = []
    for y in range(rows):
        runs, cur, buf = [], None, ""
        for x in range(cols):
            lum = gray.getpixel((x, y))
            ch = RAMP[min(len(RAMP) - 1, lum * len(RAMP) // 256)]
            color = tone(*small.getpixel((x, y))) if ch != " " else cur
            if color != cur and buf:
                runs.append((cur, buf))
                buf = ""
            cur = color
            buf += ch
        runs.append((cur, buf))
        spans = "".join(f'<tspan fill="{c}">{esc(t)}</tspan>' for c, t in runs)
        lines.append(
            f'<text x="{ox:.1f}" y="{oy + y*lh:.1f}" font-size="{fs}" xml:space="preserve" '
            f'textLength="{cols*cw:.1f}" lengthAdjust="spacing" style="animation-delay:{y*0.035:.2f}s">{spans}</text>'
        )
    height = int(oy + rows * lh + 34)
    footer = (
        f'<line x1="0.5" y1="{height-30}" x2="{width-0.5}" y2="{height-30}" stroke="{BORDER}"/>'
        f'<text x="16" y="{height-11}" font-size="11" fill="{MUTED}">Gelane-Dev@github ~ $ '
        f'<tspan fill="{INK}">whoami</tspan>  <tspan fill="{GOLD}">Leonardo Gelane</tspan>'
        f'<tspan class="cursor" fill="{CYAN}"> ▍</tspan></text>'
    )
    style = ".art text{opacity:0;animation:in .3s ease-out forwards}"
    body = '<g class="art">' + "".join(lines) + "</g>" + footer
    return window(width, height, "Gelane-Dev@github ~ $ ./whoami.sh", body, style)


# ---------------------------------------------------------------- card API

SERIF = "'EB Garamond',Garamond,Georgia,'Times New Roman',serif"

NEOFETCH = [
    ("rows", [
        ("Agora", "Dev Full Stack · foco em Backend"),
        ("Busca", "Estágio em desenvolvimento"),
        ("Edu", "ADS @ Gran Faculdade ('26 – cursando)"),
        ("Local", "Rio de Janeiro, RJ"),
    ]),
    ("Stack", [
        ("Backend", "Python, FastAPI, Django, Flask"),
        ("Dados", "PostgreSQL, SQLite, SQLAlchemy, Alembic"),
        ("Frontend", "React, React Native (Expo), TypeScript"),
        ("IA / Visão", "LLMs, Agentes, OpenCV, DeepFace"),
        ("DevOps", "Docker, Docker Compose, pytest, Git"),
    ]),
    ("Destaques", [
        "5 projetos com APIs REST, JWT e controle de acesso",
        "FitFlow — projeto solo com 136 commits",
        "Mel — assistente com IA e function calling",
        "Ex-soldado do Exército Brasileiro (logística)",
    ]),
    ("Links", [
        ("Portfólio", "gelane-dev.vercel.app"),
        ("GitHub", "gelane-dev"),
        ("LinkedIn", "in/leonardo-gelane-222973258"),
        ("Instagram", "leonardo.gelane"),
    ] + ([("Email", os.environ["PROFILE_EMAIL"])] if os.environ.get("PROFILE_EMAIL") else [])),
]


def neofetch(height: int) -> str:
    width, x0, xv = 420, 22, 118
    lh, fs = 15.5, 12
    parts, i = [], 0
    y = 58

    def line(content: str) -> None:
        nonlocal i
        parts.append(
            f'<text class="ln" x="{x0}" y="{y:.1f}" font-size="{fs}" '
            f'style="animation-delay:{0.2 + i*0.05:.2f}s">{content}</text>'
        )
        i += 1

    line(f'<tspan fill="{CYAN}" font-weight="700">gelane</tspan>'
         f'<tspan fill="{INK}" font-weight="700">@github</tspan>')
    parts.append(f'<line x1="{x0}" y1="{y+7}" x2="{x0+92}" y2="{y+7}" stroke="{BORDER}"/>')
    y += lh + 4

    for title, items in NEOFETCH:
        if title != "rows":
            y += 8
            line(f'<tspan fill="{GREEN}" font-weight="700">— {esc(title)}</tspan>')
            parts.append(f'<line x1="{x0}" y1="{y+6}" x2="{width-x0}" y2="{y+6}" stroke="{BORDER}"/>')
            y += lh + 2
        for it in items:
            if isinstance(it, tuple):
                k, v = it
                parts.append(
                    f'<text class="ln" x="{xv}" y="{y:.1f}" font-size="{fs}" fill="#aab6c8" '
                    f'style="animation-delay:{0.2 + i*0.05:.2f}s">{esc(v)}</text>'
                )
                line(f'<tspan fill="{INK}" font-weight="700">{esc(k)}</tspan>')
            else:
                line(f'<tspan fill="{GREEN}">•</tspan><tspan fill="#aab6c8">  {esc(it)}</tspan>')
            y += lh

    style = f".ln{{font-family:{SERIF};opacity:0;animation:in .25s ease-out forwards}}"
    return window(width, height, "Gelane-Dev@github ~ $ neofetch", "".join(parts), style)


# ---------------------------------------------------------------- botões de link

BUTTONS = [
    ("portfolio", "portfólio", "gelane-dev.vercel.app", CYAN),
    ("linkedin", "linkedin", "in/leonardo-gelane", BLUE),
    ("instagram", "instagram", "@leonardo.gelane", PINK),
    ("email", "email", "enviar mensagem", GOLD),
]


# Logos oficiais das marcas (Simple Icons, CC0), viewBox 24x24
ICONS = {
    "linkedin": ('#0a66c2', "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"),
    "instagram": ('url(#ig)', "M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667.072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21.319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382.896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419.419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381.419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"),
    "email": ('#ea4335', "M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 0 1 0 19.366V5.457c0-2.023 2.309-3.178 3.927-1.964L5.455 4.64 12 9.548l6.545-4.91 1.528-1.145C21.69 2.28 24 3.434 24 5.457z"),
}

IG_GRADIENT = ('<defs><radialGradient id="ig" cx="30%" cy="107%" r="150%">'
               '<stop offset="0" stop-color="#fdf497"/><stop offset=".05" stop-color="#fdf497"/>'
               '<stop offset=".45" stop-color="#fd5949"/><stop offset=".6" stop-color="#d6249f"/>'
               '<stop offset=".9" stop-color="#285aeb"/></radialGradient></defs>')


def icon_svg(name: str, color: str) -> str:
    """Logo da marca; no portfólio, o avatar em pixel art (assets/eu_2d.png) recortado em círculo."""
    if name == "portfolio":
        data = base64.b64encode((OUT / "eu_2d.png").read_bytes()).decode()
        return (
            '<defs><clipPath id="me"><circle cx="26" cy="27" r="12"/></clipPath></defs>'
            f'<image x="14" y="15" width="24" height="24" clip-path="url(#me)" style="image-rendering:pixelated" '
            f'href="data:image/png;base64,{data}"/>'
            f'<circle cx="26" cy="27" r="12" fill="none" stroke="{color}" stroke-width="1.5"/>'
        )
    fill, d = ICONS[name]
    grad = IG_GRADIENT if name == "instagram" else ""
    return f'{grad}<path transform="translate(14 16) scale(.917)" fill="{fill}" d="{d}"/>'


def button(name: str, label: str, sub: str, color: str) -> str:
    w, h = 200, 54
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<style>text{{font-family:{FONT}}}</style>
<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="9" fill="{PANEL}" stroke="{BORDER}"/>
<rect x="0.5" y="12" width="3" height="{h-24}" rx="1.5" fill="{color}"/>
{icon_svg(name, color)}
<text x="45" y="23" font-size="12" font-weight="700"><tspan fill="{MUTED}">$ open </tspan><tspan fill="{INK}">{esc(label)}</tspan></text>
<text x="45" y="40" font-size="10.5" fill="{color}">{esc(sub)}</text>
<text x="{w-14}" y="23" font-size="13" fill="{MUTED}" text-anchor="end">↗</text>
</svg>
"""


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for name, label, sub, color in BUTTONS:
        (OUT / f"btn-{name}.svg").write_text(button(name, label, sub, color), encoding="utf-8")
    (OUT / "contributions.svg").write_text(contributions(), encoding="utf-8")
    av = avatar()
    (OUT / "avatar.svg").write_text(av, encoding="utf-8")
    h = int(re.search(r'height="(\d+)"', av).group(1))
    (OUT / "neofetch.svg").write_text(neofetch(h), encoding="utf-8")
    print("ok:", ", ".join(p.name for p in OUT.glob("*.svg")))


if __name__ == "__main__":
    main()
