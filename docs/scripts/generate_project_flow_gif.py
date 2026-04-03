from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


W, H = 1800, 980
ROOT = Path("/Users/leandrosantos/Downloads/data-platform-copilot")
OUT = ROOT / "docs/assets/project-flow-readme-faithful.gif"
PREVIEW = ROOT / "docs/assets/project-flow-readme-faithful-preview.png"

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

BG = "#121A2F"
PANEL = "#121B30"
PANEL_STROKE = "#2B4066"
TEXT = "#F5F7FB"
SUBTEXT = "#D3DCEB"
MUTED = "#B5C1D9"
BRONZE = "#BF7727"
SILVER = "#C3CDD8"
GOLD = "#FFD66C"
PATH = "#68A5E0"
SIDE = "#5B8AC7"
GREEN = "#61F3BA"
CYAN = "#58C7FF"
YELLOW = "#FFD166"


def load_font(kind: str, size: int):
    for path in FONT_CANDIDATES[kind]:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    width: int,
    max_size: int,
    min_size: int = 12,
    kind: str = "bold",
):
    for size in range(max_size, min_size - 1, -1):
        font = load_font(kind, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= width:
            return font
    return load_font(kind, min_size)


def rounded_rect(draw: ImageDraw.ImageDraw, box, fill: str, outline: str, radius: int = 24):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def interpolate(seg, t: float):
    (x1, y1), (x2, y2) = seg
    return x1 + (x2 - x1) * t, y1 + (y2 - y1) * t


def draw_box_text(draw: ImageDraw.ImageDraw, spec: dict):
    x, y = spec["x"], spec["y"]
    inner_w = spec["w"] - 44
    eyebrow_font = load_font("bold", 14)
    body_font = load_font("regular", spec.get("body_size", 16))
    title_kind = spec.get("title_kind", "bold")
    title_fill = spec.get("title_fill", TEXT)
    eyebrow_fill = spec.get("eyebrow_fill", "#DCE6F6")
    body_fill = spec.get("body_fill", SUBTEXT)

    draw.text((x + 22, y + 22), spec["eyebrow"], font=eyebrow_font, fill=eyebrow_fill)

    cur_y = y + 56
    for line in spec["title"]:
        font = fit_font(draw, line, inner_w, spec.get("title_max", 26), spec.get("title_min", 16), title_kind)
        draw.text((x + 22, cur_y), line, font=font, fill=title_fill)
        cur_y = draw.textbbox((x + 22, cur_y), line, font=font)[3] + 4

    for line in spec["body"]:
        font = fit_font(draw, line, inner_w, spec.get("body_size", 16), 11, "regular")
        draw.text((x + 22, cur_y + 8), line, font=font, fill=body_fill)
        cur_y = draw.textbbox((x + 22, cur_y + 8), line, font=font)[3]


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)

    boxes = {
        "postgres": {"x": 80, "y": 290, "w": 260, "h": 138},
        "airflow": {"x": 400, "y": 290, "w": 300, "h": 138},
        "gcs": {"x": 790, "y": 170, "w": 320, "h": 150},
        "bq_bronze": {"x": 790, "y": 410, "w": 320, "h": 165},
        "bq_silver": {"x": 1180, "y": 280, "w": 340, "h": 152},
        "bq_gold": {"x": 1580, "y": 280, "w": 210, "h": 152},
        "databricks": {"x": 80, "y": 690, "w": 450, "h": 138},
        "react": {"x": 1180, "y": 690, "w": 180, "h": 138},
        "fastapi": {"x": 1410, "y": 690, "w": 180, "h": 138},
        "chat": {"x": 1640, "y": 690, "w": 180, "h": 138},
    }

    main_segments = [
        ((340, 359), (400, 359)),
        ((700, 359), (790, 245)),
        ((700, 359), (790, 492)),
        ((1110, 245), (1180, 356)),
        ((1110, 492), (1180, 356)),
        ((1520, 356), (1580, 356)),
        ((1685, 432), (1685, 690)),
    ]
    product_segments = [
        ((1580, 356), (1500, 759)),
        ((1580, 356), (1685, 759)),
    ]
    meta_segments = [
        ((530, 759), (1180, 759)),
        ((1360, 759), (1410, 759)),
        ((1590, 759), (1640, 759)),
    ]

    frames = []
    for i in range(24):
        im = Image.new("RGBA", (W, H), BG)
        draw = ImageDraw.Draw(im)

        draw.ellipse((-120, -120, 470, 380), fill="#22335C")
        draw.ellipse((1430, 560, 2010, 1140), fill="#1A2F49")

        title_font = load_font("bold", 58)
        sub_font = load_font("regular", 26)
        sec_font = load_font("bold", 26)
        footer_font = load_font("regular", 18)

        draw.text((82, 50), "DATA PLATFORM COPILOT", font=title_font, fill=TEXT)
        draw.text(
            (82, 122),
            "Pipeline principal atual da Novadrive e trilha lateral de metadados do produto",
            font=sub_font,
            fill=MUTED,
        )
        draw.text((105, 250), "Fluxo principal Novadrive", font=sec_font, fill=TEXT)
        draw.text((105, 640), "Metadados e exploração", font=sec_font, fill=TEXT)
        draw.text((1180, 640), "Camada de produto", font=sec_font, fill=TEXT)

        for key in ["postgres", "airflow", "databricks", "react", "fastapi", "chat"]:
            b = boxes[key]
            rounded_rect(draw, (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), PANEL, PANEL_STROKE)
        for key in ["gcs", "bq_bronze"]:
            b = boxes[key]
            rounded_rect(draw, (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), BRONZE, "#E39A3F")
        for key in ["bq_silver"]:
            b = boxes[key]
            rounded_rect(draw, (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), SILVER, "#D5DEE7")
        for key in ["bq_gold"]:
            b = boxes[key]
            rounded_rect(draw, (b["x"], b["y"], b["x"] + b["w"], b["y"] + b["h"]), GOLD, "#FFE18A")

        specs = [
            {
                **boxes["postgres"],
                "eyebrow": "SOURCE",
                "title": ["PostgreSQL"],
                "body": ["Novadrive transacional"],
            },
            {
                **boxes["airflow"],
                "eyebrow": "ORCHESTRATION",
                "title": ["Airflow local"],
                "body": ["Runtime Docker da DAG"],
            },
            {
                **boxes["gcs"],
                "eyebrow": "BRONZE",
                "title": ["GCS Bronze"],
                "body": ["Arquivos brutos JSONL"],
            },
            {
                **boxes["bq_bronze"],
                "eyebrow": "BRONZE",
                "title": ["BigQuery", "Bronze"],
                "body": ["Landing bruto no warehouse"],
            },
            {
                **boxes["bq_silver"],
                "eyebrow": "SILVER",
                "eyebrow_fill": "#4C5D73",
                "title_fill": "#1E2736",
                "body_fill": "#39485D",
                "title": ["BigQuery", "Silver"],
                "body": ["silver_novadrive.vendas"],
                "title_max": 21,
                "body_size": 14,
            },
            {
                **boxes["bq_gold"],
                "eyebrow": "GOLD",
                "eyebrow_fill": "#4C5D73",
                "title_fill": "#1E2736",
                "body_fill": "#39485D",
                "title": ["BigQuery", "Gold"],
                "body": ["KPI e consumo", "analítico"],
                "title_max": 19,
                "body_size": 14,
            },
            {
                **boxes["databricks"],
                "eyebrow": "METADATA",
                "title": ["Databricks", "Unity Catalog"],
                "body": ["Datasets, owner e colunas"],
                "title_max": 22,
            },
            {
                **boxes["react"],
                "eyebrow": "PRODUCT",
                "title": ["React UI"],
                "body": ["Frontend demo"],
                "title_max": 18,
            },
            {
                **boxes["fastapi"],
                "eyebrow": "PRODUCT",
                "title": ["FastAPI"],
                "body": ["Cloud Run"],
                "title_max": 18,
            },
            {
                **boxes["chat"],
                "eyebrow": "PRODUCT",
                "title": ["Chat"],
                "body": ["Q&A e exploração"],
                "title_max": 18,
            },
        ]

        for spec in specs:
            draw_box_text(draw, spec)

        for seg in main_segments:
            draw.line(seg, fill=PATH, width=5)
        for seg in meta_segments + product_segments:
            draw.line(seg, fill=SIDE, width=3)

        dots = [
            (main_segments[0], GREEN, 0.00),
            (main_segments[1], CYAN, 0.18),
            (main_segments[3], CYAN, 0.36),
            (main_segments[4], GREEN, 0.54),
            (main_segments[5], YELLOW, 0.72),
            (main_segments[6], CYAN, 0.90),
            (meta_segments[0], CYAN, 0.32),
            (product_segments[1], CYAN, 0.50),
        ]
        for seg, color, phase in dots:
            x, y = interpolate(seg, ((i / 24) + phase) % 1.0)
            r = 10 if color != YELLOW else 9
            draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

        draw.rounded_rectangle((82, 885, 1718, 925), radius=20, fill="#14223B", outline="#28436D", width=1)
        draw.ellipse((96, 895, 118, 917), fill=GREEN)
        draw.text(
            (132, 894),
            "Fluxo principal: PostgreSQL → Airflow → GCS Bronze + BigQuery Bronze → BigQuery Silver → BigQuery Gold → FastAPI / Chat / Frontend Demo",
            font=footer_font,
            fill="#D8E1EF",
        )

        frames.append(im.convert("P", palette=Image.ADAPTIVE))

    frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=120, loop=0, optimize=False)
    frames[0].convert("RGBA").save(PREVIEW)
    print(OUT)
    print(OUT.stat().st_size)
    print(PREVIEW)


if __name__ == "__main__":
    main()
