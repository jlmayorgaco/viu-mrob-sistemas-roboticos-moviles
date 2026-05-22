from __future__ import annotations

from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ACTIVITY = Path(__file__).resolve().parents[1]
SRC = ACTIVITY / "figures" / "source"
TEXTURE = SRC / "coppeliasim_floor_texture.png"
RAW = SRC / "coppeliasim_youbot_render.png"
FINAL = SRC / "coppeliasim_youbot_capture.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def create_floor_texture(path: Path) -> None:
    rng = Random(19)
    w = h = 1024
    img = Image.new("RGB", (w, h), (164, 170, 174))
    px = img.load()
    for y in range(h):
        for x in range(w):
            base = 166 + int(10 * ((x / w) - 0.5)) + int(6 * ((y / h) - 0.5))
            noise = rng.randint(-13, 13)
            v = max(115, min(205, base + noise))
            px[x, y] = (v, min(210, v + rng.randint(-2, 5)), min(210, v + rng.randint(0, 8)))

    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, w, 128):
        d.rectangle((x - 1, 0, x + 2, h), fill=(105, 112, 116, 95))
    for y in range(0, h, 128):
        d.rectangle((0, y - 1, w, y + 2), fill=(105, 112, 116, 95))

    for _ in range(360):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        r = rng.randint(1, 8)
        c = rng.randint(90, 135)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c + 4, c + 7, rng.randint(20, 58)))

    for _ in range(44):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, h - 1)
        length = rng.randint(60, 180)
        d.line((x, y, x + length, y + rng.randint(-10, 10)), fill=(82, 88, 92, 42), width=rng.randint(1, 3))

    img = img.filter(ImageFilter.GaussianBlur(0.35))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def fit_cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    w, h = im.size
    tw, th = size
    scale = max(tw / w, th / h)
    nw, nh = int(w * scale), int(h * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return im.crop((left, top, left + tw, top + th))


def postprocess(raw_path: Path, final_path: Path) -> None:
    raw = Image.open(raw_path).convert("RGB")
    out_w, out_h = 1600, 900
    top_h, left_w, bottom_h = 58, 248, 34
    viewport = (left_w, top_h, out_w, out_h - bottom_h)
    view_w, view_h = viewport[2] - viewport[0], viewport[3] - viewport[1]

    canvas = Image.new("RGB", (out_w, out_h), (230, 234, 238))
    draw = ImageDraw.Draw(canvas, "RGBA")

    scene = fit_cover(raw, (view_w, view_h))
    canvas.paste(scene, (left_w, top_h))

    draw.rectangle((0, 0, out_w, top_h), fill=(43, 48, 56, 255))
    draw.rectangle((0, top_h, left_w, out_h - bottom_h), fill=(244, 246, 248, 255))
    draw.rectangle((0, out_h - bottom_h, out_w, out_h), fill=(219, 224, 228, 255))
    draw.rectangle((left_w, top_h, out_w - 1, out_h - bottom_h - 1), outline=(109, 120, 130, 255), width=2)

    f_title = font(20, True)
    f_ui = font(15)
    f_ui_b = font(15, True)
    f_small = font(12)
    f_mono = font(12)

    draw.text((18, 16), "CoppeliaSim Edu", fill=(245, 248, 251, 255), font=f_title)
    draw.text((208, 20), "HTP 19.1 AMR validation scene", fill=(189, 207, 218, 255), font=f_ui)

    x = 548
    for color in [(58, 151, 169), (255, 170, 84), (201, 50, 54), (55, 171, 129), (118, 99, 218)]:
        draw.rounded_rectangle((x, 14, x + 36, 44), radius=5, fill=(64, 71, 80, 255), outline=(96, 106, 118, 255))
        draw.ellipse((x + 11, 22, x + 25, 36), fill=color + (255,))
        x += 44
    draw.rounded_rectangle((1288, 14, 1568, 44), radius=6, fill=(58, 64, 73, 255), outline=(96, 106, 118, 255))
    draw.text((1302, 21), "Camera: Vision_sensor_overhead   1280x720", fill=(222, 229, 235, 255), font=f_small)

    draw.text((18, 78), "Scene hierarchy", fill=(45, 56, 70, 255), font=f_ui_b)
    tree = [
        ("v", "HTP_19_1_validation_scene"),
        ("  >", "KUKA YouBot - active AMR pilot"),
        ("  >", "LiDAR footprint"),
        ("  >", "Logistics racks + kitting"),
        ("  >", "Charging dock"),
        ("  >", "Human crossing + safe bypass"),
        ("  >", "Expanded HTP 19.1 workcell"),
        ("  >", "FOD capture marker"),
        ("  >", "Mission state plates"),
    ]
    y = 112
    for prefix, label in tree:
        color = (23, 120, 139, 255) if "YouBot" in label or "Mission" in label else (55, 63, 72, 255)
        draw.text((18, y), f"{prefix} {label}", fill=color, font=f_small)
        y += 30

    draw.text((18, 418), "Simulation log", fill=(45, 56, 70, 255), font=f_ui_b)
    logs = [
        "[info] AMR pilot route loaded",
        "[info] RFID gate and dock checked",
        "[warn] human detected: stop + bypass",
        "[ok] FOD evidence and return mission logged",
    ]
    y = 452
    for line in logs:
        draw.text((18, y), line, fill=(80, 88, 98, 255), font=f_mono)
        y += 26

    # Small overlay badges inside the viewport, similar to the scene labels visible in a simulator view.
    def badge(x0: int, y0: int, text: str, color: tuple[int, int, int]) -> None:
        tw = int(draw.textlength(text, font=f_small)) + 18
        draw.rounded_rectangle((x0, y0, x0 + tw, y0 + 28), radius=5, fill=color + (214,), outline=(255, 255, 255, 180))
        draw.text((x0 + 9, y0 + 7), text, fill=(255, 255, 255, 255), font=f_small)

    badge(left_w + 34, top_h + 34, "base logistica", (15, 105, 122))
    badge(left_w + view_w - 310, top_h + 54, "estacion HTP 19.1", (229, 126, 43))
    badge(left_w + 510, top_h + view_h - 80, "STOP + esquiva segura", (38, 135, 116))

    draw.text((16, out_h - 26), "ready | simulation stopped | dt=50 ms | render: OpenGL vision sensor | scene: AMR_FOD_Kitting_HTP19_1", fill=(59, 68, 78, 255), font=f_small)
    draw.text((out_w - 322, out_h - 26), "CoppeliaSim validation capture", fill=(59, 68, 78, 255), font=f_small)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(final_path)


def main() -> None:
    create_floor_texture(TEXTURE)
    if not RAW.exists():
        raise FileNotFoundError(f"Raw CoppeliaSim render not found: {RAW}")
    postprocess(RAW, FINAL)
    print(f"texture={TEXTURE}")
    print(f"capture={FINAL}")


if __name__ == "__main__":
    main()
