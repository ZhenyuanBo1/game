"""
Run: python3 generate_textures.py
Generates custom textures for RougelikeShooter (enemy skin, ally skin, buff icons).
"""

import math, random, os
from PIL import Image, ImageDraw, ImageFilter, ImageChops

OUT_CHARS = "Textures/Characters"
OUT_ICONS = "Textures/BuffIcons"
SIZE      = 512
ICON_SZ   = 256

random.seed(42)

os.makedirs(OUT_CHARS, exist_ok=True)
os.makedirs(OUT_ICONS, exist_ok=True)


# ─── helpers ────────────────────────────────────────────────────────────────

def add_noise(img: Image.Image, strength=18, seed=0) -> Image.Image:
    rng = random.Random(seed)
    w, h = img.size
    mode = img.mode
    noise = Image.new(mode, (w, h))
    pn = noise.load()
    for y in range(h):
        for x in range(w):
            v = max(-strength, min(strength, int(rng.gauss(0, strength * 0.5))))
            if mode == "RGB":
                r, g, b = img.getpixel((x, y))
                pn[x, y] = (max(0,min(255,r+v)), max(0,min(255,g+v)), max(0,min(255,b+v)))
            else:
                pn[x, y] = max(0, min(255, img.getpixel((x, y)) + v))
    return noise


def gradient_overlay(img: Image.Image, top_alpha=50, bottom_alpha=0) -> Image.Image:
    """Add a top-white highlight via pixel-level blending (no broken alpha draw)."""
    w, h = img.size
    result = img.copy().convert("RGB")
    pr = result.load()
    for y in range(h):
        t = 1 - y / h
        a = (top_alpha * t + bottom_alpha * (1 - t)) / 255
        r0, g0, b0 = pr[0, y] if img.mode != "L" else (pr[0, y],) * 3
        for x in range(w):
            if img.mode == "RGB":
                r, g, b = pr[x, y]
                pr[x, y] = (
                    min(255, int(r + (255 - r) * a)),
                    min(255, int(g + (255 - g) * a)),
                    min(255, int(b + (255 - b) * a)),
                )
    return result


# ─── Demon skin (512×512 RGB) ────────────────────────────────────────────────

def make_demon_skin():
    img = Image.new("RGB", (SIZE, SIZE), (55, 5, 5))
    draw = ImageDraw.Draw(img)
    rng  = random.Random(1)

    # Scale plates — dark ellipses
    for _ in range(240):
        cx = rng.randint(0, SIZE)
        cy = rng.randint(0, SIZE)
        rx = rng.randint(10, 38)
        ry = rng.randint(6, 20)
        c  = rng.randint(18, 52)
        draw.ellipse([cx-rx, cy-ry, cx+rx, cy+ry], fill=(c, 2, 2))

    # Lava cracks — orange/yellow glowing lines
    for _ in range(80):
        x, y = rng.randint(0, SIZE), rng.randint(0, SIZE)
        pts = [(x, y)]
        for _ in range(rng.randint(5, 14)):
            x += rng.randint(-20, 20)
            y += rng.randint(-20, 20)
            pts.append((x, y))
        glow = rng.choice([(230, 80, 0), (255, 130, 10), (210, 40, 0)])
        draw.line(pts, fill=glow, width=rng.randint(1, 3))

    # Bright crack cores
    for _ in range(40):
        x, y = rng.randint(10, SIZE-10), rng.randint(10, SIZE-10)
        pts = [(x, y)]
        for _ in range(rng.randint(3, 8)):
            x += rng.randint(-12, 12)
            y += rng.randint(-12, 12)
            pts.append((x, y))
        draw.line(pts, fill=(255, 210, 60), width=1)

    # Subtle noise
    img = add_noise(img, 14, seed=7)

    img.save(f"{OUT_CHARS}/T_Demon_Skin_D.png")
    print(f"  T_Demon_Skin_D.png  ({SIZE}×{SIZE})")

    # Roughness map
    rough = Image.new("L", (SIZE, SIZE), 185)
    rd = ImageDraw.Draw(rough)
    rng2 = random.Random(3)
    for _ in range(80):
        x, y = rng2.randint(0, SIZE), rng2.randint(0, SIZE)
        pts = [(x, y)]
        for _ in range(rng2.randint(3, 9)):
            x += rng2.randint(-18, 18); y += rng2.randint(-18, 18)
            pts.append((x, y))
        rd.line(pts, fill=55, width=2)
    rough.save(f"{OUT_CHARS}/T_Demon_Skin_M.png")
    print(f"  T_Demon_Skin_M.png")


# ─── Human/Ally soldier skin (512×512 RGB) ───────────────────────────────────

def make_human_skin():
    img  = Image.new("RGB", (SIZE, SIZE), (52, 62, 42))
    draw = ImageDraw.Draw(img)
    rng  = random.Random(5)

    panels = [(38, 46, 32), (62, 72, 50), (45, 54, 38), (70, 80, 56)]
    for row in range(0, SIZE, 80):
        for col in range(0, SIZE, 80):
            c = rng.choice(panels)
            # main panel fill
            draw.rectangle([col+4, row+4, col+76, row+76], fill=c)
            # highlight top/left
            draw.line([(col+4,row+4),(col+76,row+4)],    fill=(95,108,78), width=2)
            draw.line([(col+4,row+4),(col+4, row+76)],   fill=(95,108,78), width=2)
            # shadow bottom/right
            draw.line([(col+4,row+76),(col+76,row+76)],  fill=(22,28,16), width=2)
            draw.line([(col+76,row+4),(col+76,row+76)],  fill=(22,28,16), width=2)

    # Rivets
    for row in range(40, SIZE, 80):
        for col in range(40, SIZE, 80):
            draw.ellipse([col-5,row-5,col+5,row+5],
                         fill=(25,32,20), outline=(98,112,82), width=1)

    # Wear scratches
    for _ in range(50):
        x, y = rng.randint(0, SIZE), rng.randint(0, SIZE)
        draw.line([(x,y),(x+rng.randint(-28,28), y+rng.randint(-4,4))],
                  fill=(78,90,62), width=1)

    img = add_noise(img, 15, seed=9)
    img.save(f"{OUT_CHARS}/T_Human_Ally_D.png")
    print(f"  T_Human_Ally_D.png  ({SIZE}×{SIZE})")

    rough = Image.new("L", (SIZE, SIZE), 155)
    rough.save(f"{OUT_CHARS}/T_Human_Ally_M.png")
    print(f"  T_Human_Ally_M.png")


# ─── Buff icon helpers ────────────────────────────────────────────────────────

def make_icon_base(bg_rgb, border_rgb) -> tuple:
    """Returns (Image, ImageDraw) with solid rounded background — no broken alpha."""
    img  = Image.new("RGBA", (ICON_SZ, ICON_SZ), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    r    = 30
    # solid fill rounded rect
    draw.rounded_rectangle([4, 4, ICON_SZ-4, ICON_SZ-4],
                           radius=r, fill=(*bg_rgb, 255), outline=(*border_rgb, 255), width=6)
    # manual top highlight via pixel blend (safe)
    px = img.load()
    for y in range(6, ICON_SZ-6):
        t = max(0.0, 1 - y / (ICON_SZ * 0.45))
        for x in range(6, ICON_SZ-6):
            if px[x, y][3] == 255:
                ro, go, bo, ao = px[x, y]
                blend = t * 0.18
                px[x, y] = (
                    min(255, int(ro + (255-ro)*blend)),
                    min(255, int(go + (255-go)*blend)),
                    min(255, int(bo + (255-bo)*blend)),
                    255,
                )
    return img, ImageDraw.Draw(img)


def solid(rgb): return (*rgb, 255)   # helper: add full alpha


def icon_bullet(draw, cx, cy, s):
    # tip
    draw.ellipse([cx-s//5, cy-s//2, cx+s//5, cy-s//6],   fill=solid((225,225,200)))
    # casing
    draw.rectangle([cx-s//5, cy-s//6, cx+s//5, cy+s//3],  fill=solid((185,160,75)))
    # rim
    draw.rectangle([cx-s//4, cy+s//3-4, cx+s//4, cy+s//3+4], fill=solid((120,100,40)))

def icon_shield(draw, cx, cy, s, color=(120,160,255)):
    pts = [cx, cy-s//2, cx+s//2, cy-s//6, cx+s//2, cy+s//4,
           cx, cy+s//2, cx-s//2, cy+s//4, cx-s//2, cy-s//6]
    draw.polygon(pts, fill=solid(color), outline=solid((220,235,255)), width=3)
    draw.line([(cx, cy-s//3),(cx, cy+s//5)], fill=solid((220,235,255)), width=s//12)

def icon_heart(draw, cx, cy, s, color=(240,60,80)):
    r = s // 3
    draw.ellipse([cx-r-r//2, cy-r, cx-r//4, cy+r//2],    fill=solid(color))
    draw.ellipse([cx+r//4,   cy-r, cx+r+r//2, cy+r//2],  fill=solid(color))
    draw.polygon([cx-r-r//2, cy,  cx+r+r//2, cy,  cx, cy+r+r//4], fill=solid(color))

def icon_sword(draw, cx, cy, s, color=(220,225,235)):
    # blade
    bw = max(4, s//8)
    draw.rectangle([cx-bw//2, cy-s//2, cx+bw//2, cy+s//4], fill=solid(color))
    # edge glint
    draw.line([(cx-bw//2, cy-s//2),(cx-bw//2, cy+s//4)], fill=solid((255,255,255)), width=1)
    # guard
    draw.rectangle([cx-s//3, cy+s//4-3, cx+s//3, cy+s//4+6],  fill=solid((185,145,55)))
    # handle
    draw.rectangle([cx-s//14, cy+s//4+6, cx+s//14, cy+s//2],   fill=solid((130,90,35)))

def icon_clock(draw, cx, cy, s, color=(160,210,255)):
    draw.ellipse([cx-s//2, cy-s//2, cx+s//2, cy+s//2],
                 outline=solid(color), width=max(4, s//10), fill=solid((30,50,80)))
    draw.line([(cx, cy), (cx, cy-s//3)],        fill=solid(color), width=max(3,s//12))
    draw.line([(cx, cy), (cx+s//4, cy+s//8)],   fill=solid((255,200,100)), width=max(2,s//14))
    draw.ellipse([cx-3,cy-3,cx+3,cy+3],         fill=solid((255,255,255)))

def icon_lightning(draw, cx, cy, s, color=(255,225,50)):
    pts = [cx+s//5, cy-s//2,
           cx-s//8, cy-s//10,
           cx+s//8, cy-s//10,
           cx-s//5, cy+s//2,
           cx+s//8, cy+s//8,
           cx-s//8, cy+s//8]
    draw.polygon(pts, fill=solid(color), outline=solid((255,255,180)), width=2)

def icon_reload(draw, cx, cy, s, color=(120,240,190)):
    steps = 240
    for i in range(steps):
        angle = math.radians(i * 360 / steps - 110)
        ro = s // 2
        ri = ro - max(6, s//8)
        cos_a, sin_a = math.cos(angle), math.sin(angle)
        x0, y0 = cx + int(ri*cos_a), cy + int(ri*sin_a)
        x1, y1 = cx + int(ro*cos_a), cy + int(ro*sin_a)
        draw.line([(x0,y0),(x1,y1)], fill=solid(color), width=2)
    # arrowhead
    ae = math.radians(-110)
    ax = cx + int(s//2 * math.cos(ae))
    ay = cy + int(s//2 * math.sin(ae))
    draw.polygon([ax-6,ay-8, ax+8,ay, ax-6,ay+8], fill=solid(color))

def icon_person(draw, cx, cy, s, color=(170,220,170)):
    hr = s // 5
    # head
    draw.ellipse([cx-hr, cy-s//2, cx+hr, cy-s//2+hr*2], fill=solid(color))
    # torso
    draw.rectangle([cx-s//5, cy-s//2+hr*2, cx+s//5, cy+s//8], fill=solid(color))
    # legs
    w = max(3, s//10)
    draw.line([(cx, cy+s//8),(cx-s//6, cy+s//2)], fill=solid(color), width=w)
    draw.line([(cx, cy+s//8),(cx+s//6, cy+s//2)], fill=solid(color), width=w)
    # arms
    draw.line([(cx, cy-s//8),(cx-s//3, cy+s//10)], fill=solid(color), width=w)
    draw.line([(cx, cy-s//8),(cx+s//3, cy+s//10)], fill=solid(color), width=w)


BUFF_DEFS = [
    # (name,            bg_rgb,        border_rgb,      draw_fn,       label_color)
    ("AddBullet",       (18, 35, 95),  (70, 130, 255),  icon_bullet,   (70,130,255)),
    ("Ally",            (18, 72, 28),  (70, 190, 90),   icon_person,   (70,190,90)),
    ("AttackShield",    (90, 45, 8),   (245, 155, 45),  icon_shield,   (245,155,45)),
    ("IncreaseDamage",  (90, 12, 12),  (245, 65, 45),   icon_sword,    (245,65,45)),
    ("RecoverHP",       (12, 72, 28),  (70, 210, 110),  icon_heart,    (70,210,110)),
    ("ReduceReloadTime",(12, 55, 75),  (70, 195, 230),  icon_reload,   (70,195,230)),
    ("SlowdownCircle",  (18, 18, 75),  (110, 110, 245), icon_clock,    (110,110,245)),
    ("TempShield",      (75, 65, 8),   (235, 205, 45),  icon_lightning,(235,205,45)),
]


def make_buff_icons():
    cx = cy = ICON_SZ // 2
    s  = ICON_SZ // 2 - 28

    for name, bg, border, draw_fn, _ in BUFF_DEFS:
        img, draw = make_icon_base(bg, border)
        draw_fn(draw, cx, cy, s)
        fname = f"{OUT_ICONS}/T_Icon_{name}.png"
        img.save(fname)
        print(f"  {fname}  ({ICON_SZ}×{ICON_SZ})")


# ─── run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Generating character textures...")
    make_demon_skin()
    make_human_skin()
    print("Generating buff icons...")
    make_buff_icons()
    print("All done.")
