"""Genera las 40 skins (5 facciones x 8 roles) proyectando los píxeles reales de las láminas
de referencia sobre el layout de piel humanoide 64x64 de Minecraft.

uso: python3 -I tools/gen_textures.py [--preview DIR]
"""
import sys, os, random
import numpy as np
from PIL import Image, ImageEnhance
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sprites import ROLES, FACTIONS, cells, foreground_mask, bbox_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "src/main/resources/assets/factionlands/textures/entity")

# proporciones medidas a ojo sobre las láminas (fracciones de la altura H del sprite)
#   hf: fin de la cabeza   tf: fin del torso   bw: ancho total del cuerpo   hw: ancho de la cabeza
PROPS = {
    "troll":  dict(hf=0.25, tf=0.62, bw=0.62, hw=0.27, thr=60, hat=False),
    "knight": dict(hf=0.21, tf=0.62, bw=0.46, hw=0.19, thr=60),
    "elf":    dict(hf=0.20, tf=0.60, bw=0.44, hw=0.18, thr=48),
    "dwarf":  dict(hf=0.36, tf=0.80, bw=0.95, hw=0.50, thr=60, beard=True),
    "human":  dict(hf=0.21, tf=0.60, bw=0.46, hw=0.19, thr=60),
}


def mean_color(img):
    a = np.asarray(img.convert("RGB")).reshape(-1, 3).mean(axis=0)
    return tuple(int(v) for v in a)


def shade(c, f):
    return tuple(max(0, min(255, int(v * f))) for v in c)


def rows_mean(img, w, h):
    """cada fila = color medio de la fila (para costados/espalda)."""
    a = np.asarray(img.convert("RGB").resize((8, h), Image.BOX)).astype(float).mean(axis=1)
    out = Image.new("RGB", (w, h))
    for y in range(h):
        out.paste(tuple(int(v) for v in a[y]), (0, y, w, y + 1))
    return out


def solid(w, h, c):
    return Image.new("RGB", (w, h), c)


def paste_box(tex, fx, fy, w, h, d, front, back, right, left, top, bottom):
    tex.paste(front, (fx, fy))
    tex.paste(right, (fx - d, fy))
    tex.paste(left, (fx + w, fy))
    tex.paste(back, (fx + w + d, fy))
    tex.paste(top, (fx, fy - d))
    tex.paste(bottom, (fx + w, fy - d))


def grab(sheet_cell, box, size):
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    x0 = max(0, x0); y0 = max(0, y0)
    x1 = min(sheet_cell.width, max(x1, x0 + 1)); y1 = min(sheet_cell.height, max(y1, y0 + 1))
    img = sheet_cell.crop((x0, y0, x1, y1)).convert("RGB").resize(size, Image.BOX)
    img = ImageEnhance.Contrast(img).enhance(1.15)
    return ImageEnhance.Color(img).enhance(1.12)


def regions(p, cx, top, H):
    hw = p["hw"] * H; W = p["bw"] * H
    y_h1 = top + p["hf"] * H
    y_t1 = top + p["tf"] * H
    y_end = top + 0.97 * H
    head = (cx - hw / 2, top, cx + hw / 2, y_h1)
    torso = (cx - 0.28 * W, y_h1, cx + 0.28 * W, y_t1)
    arm_l = (cx - 0.50 * W, y_h1 + 0.01 * H, cx - 0.27 * W, y_t1 + 0.02 * H)   # izq. de la imagen = brazo DERECHO del mob
    arm_r = (cx + 0.27 * W, y_h1 + 0.01 * H, cx + 0.50 * W, y_t1 + 0.02 * H)
    leg_l = (cx - 0.30 * W, y_t1, cx, y_end)
    leg_r = (cx, y_t1, cx + 0.30 * W, y_end)
    return head, torso, arm_l, arm_r, leg_l, leg_r


def figure(sheet, box, p):
    cell = sheet.crop(box)
    m = foreground_mask(cell, p["thr"])
    x0, y0, x1, y1 = bbox_of(m)
    H = (y1 - y0) * 0.96  # descuenta la sombra del suelo
    ys, xs = np.where(m[int(y0 + 0.35 * H):int(y0 + 0.6 * H)])
    cx = xs.mean() if len(xs) else (x0 + x1) / 2
    return cell, cx, y0, H


def build_skin(cell, cx, top, H, p, rng):
    tex = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    head_b, torso_b, arm_r_b, arm_l_b, leg_r_b, leg_l_b = regions(p, cx, top, H)

    # --- cabeza ---
    head = grab(cell, head_b, (8, 8))
    hair = mean_color(head.crop((0, 0, 8, 3)))
    skin_low = mean_color(head.crop((0, 5, 8, 8)))
    hw = head_b[2] - head_b[0]
    side_r = grab(cell, (head_b[0], head_b[1], head_b[0] + hw * 0.25, head_b[3]), (8, 8))
    side_l = grab(cell, (head_b[2] - hw * 0.25, head_b[1], head_b[2], head_b[3]), (8, 8))
    back = solid(8, 8, shade(hair, 0.9))
    back.paste(solid(8, 3, shade(skin_low, 0.55)), (0, 5))
    paste_box(tex, 8, 8, 8, 8, 8, head, back, shade_img(side_r, 0.9), shade_img(side_l, 0.9),
              solid(8, 8, hair), solid(8, 8, shade(skin_low, 0.7)))

    # --- torso ---
    torso = grab(cell, torso_b, (8, 12))
    tw = torso_b[2] - torso_b[0]
    ts_r = grab(cell, (torso_b[0], torso_b[1], torso_b[0] + tw * 0.2, torso_b[3]), (4, 12))
    ts_l = grab(cell, (torso_b[2] - tw * 0.2, torso_b[1], torso_b[2], torso_b[3]), (4, 12))
    tback = shade_img(rows_mean(torso, 8, 12), 0.82)
    paste_box(tex, 20, 20, 8, 12, 4, torso, tback, shade_img(ts_r, 0.9), shade_img(ts_l, 0.9),
              solid(8, 4, mean_color(torso.crop((0, 0, 8, 2)))), solid(8, 4, shade(mean_color(torso.crop((0, 9, 8, 12))), 0.6)))

    # --- brazos ---
    for (fx, fy, b) in ((44, 20, arm_r_b), (36, 52, arm_l_b)):
        arm = grab(cell, b, (4, 12))
        side = rows_mean(arm, 4, 12)
        paste_box(tex, fx, fy, 4, 12, 4, arm, shade_img(arm, 0.82), shade_img(side, 0.9), shade_img(side, 0.9),
                  solid(4, 4, mean_color(arm.crop((0, 0, 4, 2)))), solid(4, 4, shade(mean_color(arm.crop((0, 9, 4, 12))), 0.8)))

    # --- piernas ---
    for (fx, fy, b) in ((4, 20, leg_r_b), (20, 52, leg_l_b)):
        leg = grab(cell, b, (4, 12))
        side = rows_mean(leg, 4, 12)
        paste_box(tex, fx, fy, 4, 12, 4, leg, shade_img(leg, 0.82), shade_img(side, 0.9), shade_img(side, 0.9),
                  solid(4, 4, mean_color(leg.crop((0, 0, 4, 2)))), solid(4, 4, shade(mean_color(leg.crop((0, 9, 4, 12))), 0.6)))
    if p.get("hat", True):
        beard = None
        if p.get("beard"):
            beard = mean_color(grab(cell, (cx - 0.09 * H, top + 0.30 * H, cx + 0.09 * H, top + 0.46 * H), (2, 2)))
        hat_layer(tex, hair, beard, rng)
    return tex


def hat_layer(tex, hair, beard, rng):
    """Segunda capa de la cabeza (UV en 32,0): volumen de pelo/casco y barba."""
    def px(x, y, c, j=10):
        k = rng.randint(-j, j)
        tex.putpixel((x, y), (max(0, min(255, c[0] + k)), max(0, min(255, c[1] + k)), max(0, min(255, c[2] + k)), 255))
    for x in range(8):                      # techo (40,0)
        for y in range(8):
            px(40 + x, y, hair)
    for x in range(8):                      # espalda (56,8)
        for y in range(8):
            px(56 + x, 8 + y, shade(hair, 0.9))
    for y in range(5):                      # costados (32,8) y (48,8)
        for x in range(8):
            px(32 + x, 8 + y, shade(hair, 0.95))
            px(48 + x, 8 + y, shade(hair, 0.95))
    for x in range(8):                      # flequillo / ala (40,8)
        for y in range(2):
            px(40 + x, 8 + y, hair)
    if beard:
        for y in range(4, 8):
            for x in range(8):
                if y == 4 and x in (0, 7):
                    continue
                if y == 7 and x in (0, 7):
                    continue
                px(40 + x, 8 + y, shade(beard, 1.0 - 0.06 * (y - 4)), 14)
        for y in range(5, 8):
            for x in range(0, 4):
                px(32 + x + 4, 8 + y, shade(beard, 0.85))   # lado derecho, junto a la cara
                px(48 + x, 8 + y, shade(beard, 0.85))        # lado izquierdo


def shade_img(img, f):
    a = np.asarray(img.convert("RGB")).astype(float) * f
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGB")


def preview_front(tex, scale=10):
    """reconstruye la vista frontal desde la skin, para compararla con la lámina original."""
    t = tex.convert("RGB")
    W, H = 20 * scale, 32 * scale
    out = Image.new("RGB", (W, H), (235, 225, 205))
    def put(src_box, dst_xy, size):
        part = t.crop(src_box).resize((size[0] * scale, size[1] * scale), Image.NEAREST)
        out.paste(part, (dst_xy[0] * scale, dst_xy[1] * scale))
    put((8, 8, 16, 16), (6, 0), (8, 8))
    hat = tex.crop((40, 8, 48, 16)).resize((8 * scale, 8 * scale), Image.NEAREST)
    out.paste(hat, (6 * scale, 0), hat)
    put((20, 20, 28, 32), (6, 8), (8, 12))
    put((44, 20, 48, 32), (2, 8), (4, 12))
    put((36, 52, 40, 64), (14, 8), (4, 12))
    put((4, 20, 8, 32), (6, 20), (4, 12))
    put((20, 52, 24, 64), (10, 20), (4, 12))
    return out


def main():
    preview_dir = None
    if "--preview" in sys.argv:
        preview_dir = sys.argv[sys.argv.index("--preview") + 1]
        os.makedirs(preview_dir, exist_ok=True)
    for f in FACTIONS:
        sheet = Image.open(os.path.join(ROOT, f"tools/reference/chars_{f}.png")).convert("RGB")
        p = PROPS[f]
        os.makedirs(os.path.join(OUT, f), exist_ok=True)
        pv = Image.new("RGB", (8 * 200, 2 * 320), (255, 255, 255)) if preview_dir else None
        for i, box in cells(sheet):
            cell, cx, top, H = figure(sheet, box, p)
            tex = build_skin(cell, cx, top, H, p, random.Random(f"{f}-{ROLES[i]}"))
            tex.save(os.path.join(OUT, f, f"{ROLES[i]}.png"))
            if pv:
                orig = cell.crop((int(cx - 0.45 * H), int(top), int(cx + 0.45 * H), int(top + H)))
                orig = orig.resize((int(200), int(200 * orig.height / max(1, orig.width))))
                pv.paste(orig.crop((0, 0, 200, 320)), (i * 200, 0))
                pv.paste(preview_front(tex), (i * 200, 320))
        if pv:
            pv.save(os.path.join(preview_dir, f"preview_{f}.png"))
    print("texturas escritas en", OUT)


if __name__ == "__main__":
    main()
