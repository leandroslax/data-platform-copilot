from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path("/Users/leandrosantos/Downloads/data-platform-copilot")
OUT = ROOT / "docs/assets/novadrive-dashboard.png"

W, H = 1600, 960

FONT_CANDIDATES = {
    "bold": [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial Bold.ttf",
    ],
    "regular": [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ],
}

CARD = "#121C31"
CARD_2 = "#0F1729"
STROKE = "#213759"
TEXT = "#F3F6FB"
MUTED = "#9FB2CD"
ACCENT = "#49B7FF"
GREEN = "#4CE0B3"
GOLD = "#FFCF5A"
RED = "#FF7A7A"
PURPLE = "#9F7CFF"
ORANGE = "#FF9A5A"
BG_TOP = (11, 18, 32)
BG_BOTTOM = (19, 29, 50)


TOP_10_DEALERSHIPS = [
    ("Belo Horizonte", "MG", 87.017),
    ("Sao Paulo Centro", "SP", 72.436),
    ("Sao Paulo", "SP", 66.804),
    ("Salvador", "BA", 66.167),
    ("Curitiba", "PR", 46.506),
    ("Rio Centro", "RJ", 43.495),
    ("Rio de Janeiro", "RJ", 42.193),
    ("Porto Alegre", "RS", 40.262),
    ("Campo Grande", "MS", 27.989),
    ("Teresina", "PI", 27.874),
]

STATE_SHARE = [
    ("SP", 26.7, ACCENT),
    ("MG", 16.7, GREEN),
    ("RJ", 16.5, PURPLE),
    ("BA", 12.7, GOLD),
    ("PR", 8.9, ORANGE),
    ("Others", 18.5, "#7FD3FF"),
]

SELLERS = [
    ("Felipe Souza", "RJ Centro", 43.5),
    ("Luciana Freitas", "Rio de Janeiro", 42.2),
    ("Gabriela Santos", "Porto Alegre", 40.3),
    ("Roberto Carlos", "Campo Grande", 27.9),
]

CITY_MARKERS = [
    ("Belo Horizonte", "MG", 340, 235, 22),
    ("Sao Paulo Centro", "SP", 305, 315, 20),
    ("Sao Paulo", "SP", 318, 325, 18),
    ("Salvador", "BA", 390, 205, 18),
    ("Curitiba", "PR", 285, 360, 15),
    ("Rio Centro", "RJ", 350, 292, 14),
    ("Rio de Janeiro", "RJ", 340, 300, 13),
    ("Porto Alegre", "RS", 255, 415, 13),
    ("Campo Grande", "MS", 250, 300, 11),
    ("Teresina", "PI", 360, 120, 11),
]


def font(kind: str, size: int):
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def rr(draw: ImageDraw.ImageDraw, box, fill=CARD, outline=STROKE, radius=24, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_width: int, max_size: int, min_size: int = 11, bold: bool = True):
    kind = "bold" if bold else "regular"
    for size in range(max_size, min_size - 1, -1):
        f = font(kind, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_width:
            return f
    return font(kind, min_size)


def build_dashboard():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGBA", (W, H), "#0B1220")
    d = ImageDraw.Draw(img)

    for y in range(H):
        ratio = y / H
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio)
        d.line((0, y, W, y), fill=(r, g, b))

    d.ellipse((-140, -90, 420, 360), fill=(33, 55, 95, 70))
    d.ellipse((1180, 560, 1760, 1160), fill=(21, 43, 72, 60))

    f_title = font("bold", 42)
    f_h2 = font("bold", 22)
    f_h3 = font("bold", 18)
    f_big = font("bold", 30)
    f_med = font("regular", 16)
    f_small = font("regular", 14)
    f_tiny = font("regular", 12)

    d.text((60, 46), "NOVADRIVE EXECUTIVE DASHBOARD", font=f_title, fill=TEXT)
    d.text(
        (60, 96),
        "BigQuery Gold metrics, regional footprint, seller performance and hourly pipeline health",
        font=f_med,
        fill=MUTED,
    )

    kpis = [
        ("2.75M", "Total sales records (Silver)", GREEN),
        ("29", "Dealerships in Gold mart", ACCENT),
        ("54", "Top sellers tracked", GOLD),
        ("1h", "Airflow refresh cadence", RED),
    ]
    for i, (value, desc, color) in enumerate(kpis):
        x = 60 + i * 380
        rr(d, (x, 140, x + 340, 240), fill=CARD_2)
        d.ellipse((x + 24, 162, x + 46, 184), fill=color)
        d.text((x + 60, 156), value, font=f_big, fill=TEXT)
        d.text((x + 60, 196), desc, font=f_small, fill=MUTED)

    rr(d, (60, 280, 670, 860))
    d.text((88, 310), "Brazil Revenue Coverage", font=f_h2, fill=TEXT)
    d.text((88, 342), "Top Novadrive dealerships positioned on a Brazil market map", font=f_small, fill=MUTED)

    mx1, my1 = 125, 395
    # More recognizable Brazil silhouette for presentation use.
    brazil = [
        (250, 12), (320, 24), (386, 46), (438, 82), (474, 122), (494, 168),
        (488, 208), (510, 246), (500, 286), (476, 326), (450, 362), (420, 396),
        (384, 424), (346, 412), (314, 430), (272, 420), (234, 386), (196, 370),
        (160, 330), (134, 286), (128, 242), (140, 196), (136, 154), (158, 116),
        (192, 82), (224, 48),
    ]
    coast = [(mx1 + x, my1 + y) for x, y in brazil]
    d.polygon(coast, fill="#1A2742", outline="#3B6096")
    d.text((mx1 + 218, my1 + 220), "BRAZIL", font=f_h3, fill="#4A628B")

    for city, uf, x, y, r in CITY_MARKERS:
        cx, cy = mx1 + x, my1 + y
        d.ellipse((cx - r * 1.8, cy - r * 1.8, cx + r * 1.8, cy + r * 1.8), fill=(73, 183, 255, 45))
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACCENT, outline="white", width=2)
        d.text((cx + r + 8, cy - 7), uf, font=f_small, fill=TEXT)

    legend_y = 750
    for i, (color, text) in enumerate([(ACCENT, "Revenue hotspot"), (GREEN, "Sales density"), (GOLD, "High-volume city")]):
        x = 92 + i * 170
        d.ellipse((x, legend_y, x + 16, legend_y + 16), fill=color)
        d.text((x + 26, legend_y - 1), text, font=f_tiny, fill=MUTED)

    rr(d, (710, 280, 1540, 540))
    d.text((738, 310), "Top Dealerships by Revenue", font=f_h2, fill=TEXT)
    d.text((738, 342), "Gold mart: faturamento_por_concessionaria", font=f_small, fill=MUTED)

    chart_x1, chart_x2 = 930, 1485
    chart_y1, chart_y2 = 390, 505
    for i in range(6):
        x = chart_x1 + i * (chart_x2 - chart_x1) / 5
        d.line((x, chart_y1, x, chart_y2), fill="#213759", width=1)
        if i < 5:
            d.text((x - 8, chart_y2 + 8), f"{i * 20}B", font=f_tiny, fill=MUTED)

    top5 = TOP_10_DEALERSHIPS[:5]
    for idx, (name, uf, value) in enumerate(top5):
        y = 387 + idx * 26
        d.text((760, y), f"{name} ({uf})", font=f_small, fill=TEXT)
        width = int((value / 90.0) * (chart_x2 - chart_x1 - 10))
        d.rounded_rectangle((chart_x1, y + 2, chart_x1 + width, y + 20), radius=9, fill=GOLD)
        d.text((chart_x1 + width + 8, y), f"{value:.1f}B", font=f_small, fill=TEXT)

    rr(d, (710, 570, 1110, 860))
    d.text((738, 600), "Pipeline Throughput", font=f_h2, fill=TEXT)
    d.text((738, 632), "Hourly load growth and data freshness trend", font=f_small, fill=MUTED)
    px1, py1, px2, py2 = 750, 680, 1070, 820
    for i in range(6):
        y = py1 + i * (py2 - py1) / 5
        d.line((px1, y, px2, y), fill="#213759", width=1)
    values = [18, 26, 23, 31, 29, 37, 34, 42, 39, 47]
    points = []
    for i, value in enumerate(values):
        x = px1 + i * (px2 - px1) / (len(values) - 1)
        y = py2 - (value / 50) * (py2 - py1)
        points.append((x, y))
    d.polygon([(px1, py2)] + points + [(px2, py2)], fill=(76, 224, 179, 45))
    d.line(points, fill=GREEN, width=4)
    for x, y in points:
        d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=GREEN)
    for i, tick in enumerate(["08h", "10h", "12h", "14h", "16h"]):
        x = px1 + i * (px2 - px1) / 4
        d.text((x - 10, py2 + 8), tick, font=f_tiny, fill=MUTED)
    d.text((750, 840), "Incremental rows observed between hourly runs", font=f_tiny, fill=MUTED)

    rr(d, (1130, 570, 1540, 860))
    d.text((1158, 600), "Regional Mix and Seller Leaders", font=f_h2, fill=TEXT)
    d.text((1158, 632), "State mix based on top-10 dealership revenue", font=f_small, fill=MUTED)

    cx, cy = 1260, 735
    outer, inner = 90, 52
    start = -90
    for state, pct, color in STATE_SHARE:
        end = start + pct / 100 * 360
        d.pieslice((cx - outer, cy - outer, cx + outer, cy + outer), start, end, fill=color)
        start = end
    d.ellipse((cx - inner, cy - inner, cx + inner, cy + inner), fill=CARD)
    d.text((cx - 24, cy - 12), "Mix", font=f_h3, fill=TEXT)

    ly = 676
    for state, pct, color in STATE_SHARE:
        d.ellipse((1370, ly + 2, 1384, ly + 16), fill=color)
        d.text((1394, ly), f"{state}  {pct:.1f}%", font=f_small, fill=TEXT)
        ly += 26

    ly = 792
    for idx, (name, city, revenue) in enumerate(SELLERS, 1):
        d.text((1160, ly), f"{idx}.", font=f_h3, fill=GOLD)
        d.text((1186, ly - 2), name, font=f_small, fill=TEXT)
        d.text((1330, ly - 2), city, font=f_tiny, fill=MUTED)
        d.text((1450, ly - 2), f"{revenue:.1f}B", font=f_small, fill=GREEN)
        ly += 28

    rr(d, (60, 892, 1540, 938), fill="#111A2D", outline="#223A60", radius=18, width=1)
    d.text(
        (88, 904),
        "Architecture: PostgreSQL → Airflow Docker → GCS Bronze + BigQuery Bronze → BigQuery Silver → BigQuery Gold → FastAPI / Chat",
        font=f_small,
        fill=MUTED,
    )

    img.convert("RGB").save(OUT, quality=95)
    print(OUT)


if __name__ == "__main__":
    build_dashboard()
