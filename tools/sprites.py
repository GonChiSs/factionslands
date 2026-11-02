"""Segmentación de personajes en las láminas de referencia (4x2 celdas)."""
import numpy as np
from PIL import Image, ImageFilter

ROLES = ["leader", "lumberjack", "mason", "smith", "warrior", "archer", "scout", "mystic"]
FACTIONS = ["troll", "knight", "elf", "dwarf", "human"]


def cells(sheet):
    w, h = sheet.size
    cw, ch = w // 4, h // 2
    for i in range(8):
        c, r = i % 4, i // 4
        yield i, (c * cw, r * ch, (c + 1) * cw, (r + 1) * ch)


def foreground_mask(cell_rgb, thr):
    arr = np.asarray(cell_rgb.convert("RGB")).astype(int)
    h, w, _ = arr.shape
    border = np.concatenate([arr[:12].reshape(-1, 3), arr[-12:].reshape(-1, 3),
                             arr[:, :12].reshape(-1, 3), arr[:, -12:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    dist = np.abs(arr - bg).sum(axis=2)
    m = (dist > thr).astype(np.uint8) * 255
    mi = Image.fromarray(m).filter(ImageFilter.MedianFilter(9))
    return np.asarray(mi) > 0


def bbox_of(mask, inset=0.04):
    h, w = mask.shape
    m = mask.copy()
    # ignora el borde de la celda (marcos, marcas de registro)
    ih, iw = int(h * inset), int(w * inset)
    m[:ih] = False; m[-ih:] = False; m[:, :iw] = False; m[:, -iw:] = False
    rows = np.where(m.sum(axis=1) >= 4)[0]
    cols = np.where(m.sum(axis=0) >= 4)[0]
    return cols.min(), rows.min(), cols.max() + 1, rows.max() + 1
