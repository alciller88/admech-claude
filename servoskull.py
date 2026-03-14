#!/usr/bin/env python3
"""
servoskull.py — Servo-Craneo Designatus
Pixel art con Unicode half-block characters + ANSI true color.
Supports full-size (standalone) and compact (sidebar) modes.
"""

# === ANSI CODES ===
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREY_COGIT = "\033[90m"
GOLD_OMNI = "\033[93m"
GREEN_BIONIC = "\033[92m"
RED_MARS = "\033[31m"
ORANGE_FORGE = "\033[33m"
BONE_SACRED = "\033[97m"

BINHARIC_MARS = "01001101 01000001 01010010 01010011"
BINHARIC_STATIC = "10110100 01011010 11001001 00110110"

# === COLOR PALETTE ===
BONE = (225, 210, 185)
BONE_HI = (250, 242, 225)
BONE_SH = (185, 168, 142)
BONE_DK = (135, 118, 95)
OUTLINE = (72, 60, 45)
VOID = (3, 3, 5)
METAL = (162, 167, 178)
METAL_HI = (195, 200, 210)
METAL_SH = (118, 123, 135)
METAL_DK = (68, 73, 86)
RED = (225, 18, 0)
RED_DIM = (155, 10, 0)
RED_DARK = (90, 5, 0)
ORANGE = (255, 130, 20)
GOLD = (255, 205, 0)
GOLD_DIM = (188, 150, 0)
GREEN = (0, 225, 55)
GREEN_DIM = (0, 155, 35)
CABLE = (78, 83, 95)
CABLE_DK = (42, 47, 58)
TEETH = (245, 242, 235)
TEETH_DK = (200, 195, 182)
RIVET = (100, 105, 118)


# === RENDER ENGINE ===

def _fg(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def _bg(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

def _c(color, text):
    return f"{color}{text}{RESET}"

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render(canvas, pad=0):
    """Render pixel canvas using half-block characters with true color ANSI."""
    h = len(canvas)
    w = len(canvas[0]) if h > 0 else 0
    lines = []
    for row in range(0, h, 2):
        parts = []
        for col in range(w):
            top = canvas[row][col]
            bot = canvas[row + 1][col] if row + 1 < h else None
            if top is None and bot is None:
                parts.append(" ")
            elif top is None:
                parts.append(_fg(*bot) + "\u2584")
            elif bot is None:
                parts.append(_fg(*top) + "\u2580")
            elif top == bot:
                parts.append(_fg(*top) + "\u2588")
            else:
                parts.append(_bg(*top) + _fg(*bot) + "\u2584")
        line = " " * pad + "".join(parts) + RESET
        lines.append(line)
    return "\n".join(lines)


# === DRAWING PRIMITIVES ===

def make_canvas(w, h):
    return [[None] * w for _ in range(h)]


def fill_ellipse(c, cx, cy, rx, ry, color):
    h, w = len(c), len(c[0])
    y0 = max(0, int(cy - ry - 1))
    y1 = min(h - 1, int(cy + ry + 1))
    x0 = max(0, int(cx - rx - 1))
    x1 = min(w - 1, int(cx + rx + 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx if rx > 0 else 0
            dy = (y - cy) / ry if ry > 0 else 0
            if dx * dx + dy * dy <= 1.0:
                c[y][x] = color


def stroke_ellipse(c, cx, cy, rx, ry, color, thickness=1.0):
    h, w = len(c), len(c[0])
    y0 = max(0, int(cy - ry - 2))
    y1 = min(h - 1, int(cy + ry + 2))
    x0 = max(0, int(cx - rx - 2))
    x1 = min(w - 1, int(cx + rx + 2))
    inner = 1.0 - thickness / min(rx, ry)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx if rx > 0 else 0
            dy = (y - cy) / ry if ry > 0 else 0
            d = dx * dx + dy * dy
            if inner * inner <= d <= 1.0:
                c[y][x] = color


def fill_rect(c, x1, y1, x2, y2, color):
    h, w = len(c), len(c[0])
    for y in range(max(0, y1), min(h, y2 + 1)):
        for x in range(max(0, x1), min(w, x2 + 1)):
            c[y][x] = color


def fill_trapezoid(c, y_start, y_end, top_hw, bot_hw, cx, color,
                   outline_col=None):
    h, w = len(c), len(c[0])
    for y in range(max(0, y_start), min(h, y_end + 1)):
        t = (y - y_start) / max(1, y_end - y_start)
        hw = top_hw + (bot_hw - top_hw) * t
        xl = int(cx - hw)
        xr = int(cx + hw)
        for x in range(max(0, xl), min(w, xr + 1)):
            c[y][x] = color
        if outline_col:
            if 0 <= xl < w:
                c[y][xl] = outline_col
            if 0 <= xr < w:
                c[y][xr] = outline_col


def set_px(c, x, y, color):
    h, w = len(c), len(c[0])
    if 0 <= x < w and 0 <= y < h:
        c[y][x] = color


# ============================================================
#  COMPACT SKULL (28 x 24 pixels → 28 chars x 12 lines)
#  For sidebar monitor in tmux right pane
# ============================================================

def build_compact(lens_color=None, lens_ring=None, lens_ring2=None,
                  cable_glow=None):
    W, H = 28, 24
    CX, CY = 14, 7
    c = make_canvas(W, H)

    # --- CRANIUM ---
    fill_ellipse(c, CX, CY, 12, 7, OUTLINE)
    fill_ellipse(c, CX, CY, 11, 6, BONE)
    fill_ellipse(c, CX - 2, CY - 3, 7, 3, BONE_HI)

    # --- BROW RIDGE ---
    brow_y = 4
    for x in range(CX - 9, CX + 10):
        for y_off in (brow_y, brow_y + 1):
            if 0 <= x < W and 0 <= y_off < H:
                if c[y_off][x] is not None and c[y_off][x] not in (OUTLINE,):
                    c[y_off][x] = GOLD if y_off == brow_y + 1 else GOLD_DIM
    # Cog teeth
    for x in [CX - 7, CX - 3, CX + 1, CX + 5]:
        for dx in range(2):
            xx = x + dx
            if 0 <= xx < W and brow_y - 1 >= 0:
                if c[brow_y - 1][xx] is not None:
                    c[brow_y - 1][xx] = GOLD

    # --- METAL PLATING (right side) ---
    for y in range(H):
        for x in range(W):
            px = c[y][x]
            if px is not None and px not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                if x > CX + 2:
                    t = min(1.0, (x - CX - 2) / 9.0)
                    c[y][x] = lerp(px, METAL, t * 0.65)
    # Seam line
    for y in range(2, CY + 12):
        if 0 <= y < H and 0 <= CX + 3 < W:
            px = c[y][CX + 3]
            if px is not None and px not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                c[y][CX + 3] = lerp(px, METAL_DK, 0.5)
    # Rivets
    for rx, ry in [(CX + 7, 4), (CX + 9, 7), (CX + 8, 11), (CX + 7, 15)]:
        if 0 <= rx < W and 0 <= ry < H and c[ry][rx] is not None:
            c[ry][rx] = RIVET

    # --- LEFT EYE (organic) ---
    lex, ley = CX - 5, CY + 2
    fill_ellipse(c, lex, ley, 4, 2.8, BONE_DK)
    fill_ellipse(c, lex, ley, 3.2, 2.2, OUTLINE)
    fill_ellipse(c, lex, ley, 2.5, 1.7, VOID)

    # --- RIGHT EYE (sensor) ---
    rex, rey = CX + 5, CY + 2
    fill_ellipse(c, rex, rey, 4, 2.8, METAL_DK)
    stroke_ellipse(c, rex, rey, 4, 2.8, METAL_SH, 1.2)
    fill_ellipse(c, rex, rey, 3, 2, VOID)
    if lens_ring2:
        fill_ellipse(c, rex, rey, 2.3, 1.5, lens_ring2)
    if lens_ring:
        fill_ellipse(c, rex, rey, 1.5, 1.0, lens_ring)
    if lens_color:
        fill_ellipse(c, rex, rey, 0.8, 0.6, lens_color)
        set_px(c, rex, rey, (
            min(255, lens_color[0] + 80),
            min(255, lens_color[1] + 80),
            min(255, lens_color[2] + 80),
        ))

    # --- NASAL CAVITY ---
    nose_top = CY + 5
    for y in range(nose_top, min(H, nose_top + 4)):
        t = (y - nose_top) / 4.0
        hw = max(0, 2.0 * (1.0 - t * 0.5))
        for x in range(int(CX - hw) - 1, int(CX + hw) + 2):
            if 0 <= x < W and c[y][x] is not None:
                if c[y][x] not in (VOID, OUTLINE, METAL_DK):
                    c[y][x] = OUTLINE
        for x in range(int(CX - hw) + 1, int(CX + hw)):
            if 0 <= x < W:
                c[y][x] = VOID
        set_px(c, CX, y, BONE_DK)

    # --- LOWER FACE / JAW ---
    fill_trapezoid(c, CY + 8, CY + 10, 8, 6, CX, BONE, OUTLINE)
    fill_trapezoid(c, CY + 10, CY + 14, 6, 2, CX, BONE, OUTLINE)

    # --- TEETH ---
    teeth_y = CY + 10
    teeth_l, teeth_r = CX - 6, CX + 6
    for y in range(teeth_y, min(H, teeth_y + 3)):
        for x in range(teeth_l, teeth_r + 1):
            if 0 <= x < W and c[y][x] is not None and c[y][x] != OUTLINE:
                pos = (x - teeth_l) / 2.0
                in_gap = abs(pos - round(pos)) < 0.18
                if in_gap:
                    c[y][x] = OUTLINE
                else:
                    edge = abs(pos - round(pos)) / 0.5
                    c[y][x] = lerp(TEETH, TEETH_DK, edge * 0.3)

    # --- CABLES ---
    cab = cable_glow or CABLE
    for bundle in range(2):
        for dy in range(-3, 5):
            y = CY + 2 + dy + bundle
            if 0 <= y < H:
                curve = max(0, dy) * 0.4
                xl = int(CX - 13 + curve)
                xr = int(CX + 13 - curve)
                intensity = max(0, 1.0 - abs(dy) / 5.0)
                col = lerp(CABLE_DK, cab, intensity * 0.8)
                if 0 <= xl < W and c[y][xl] is None:
                    c[y][xl] = col
                if 0 <= xr < W and c[y][xr] is None:
                    c[y][xr] = col

    # --- SPINE ---
    sp_start = min(CY + 15, H - 4)
    for y in range(sp_start, min(H, sp_start + 4)):
        seg = y - sp_start
        for dx in (-1, 0, 1):
            x = CX + dx
            if 0 <= x < W:
                c[y][x] = METAL if seg % 2 == 0 else METAL_DK

    return c


# ============================================================
#  FULL-SIZE SKULL (60 x 48 pixels → 60 chars x 24 lines)
#  For standalone display
# ============================================================

def build_full(lens_color=None, lens_ring=None, lens_ring2=None,
               cable_glow=None):
    W, H = 60, 48
    CX, CY = 30, 15
    c = make_canvas(W, H)

    # --- CRANIUM ---
    fill_ellipse(c, CX, CY, 22, 15, OUTLINE)
    fill_ellipse(c, CX, CY, 21, 14, BONE)
    fill_ellipse(c, CX - 3, CY - 6, 14, 7, BONE_HI)

    # --- BROW RIDGE ---
    brow_y = 9
    for x in range(CX - 18, CX + 19):
        for y_off in [brow_y, brow_y + 1]:
            if 0 <= x < W and 0 <= y_off < H:
                if c[y_off][x] is not None and c[y_off][x] != OUTLINE:
                    c[y_off][x] = GOLD if y_off == brow_y + 1 else GOLD_DIM
    for x in [CX - 14, CX - 9, CX - 4, CX + 1, CX + 6, CX + 11]:
        for dx in range(3):
            xx = x + dx
            if 0 <= xx < W and c[brow_y - 1][xx] is not None:
                c[brow_y - 1][xx] = GOLD

    # --- LOWER FACE / JAW ---
    fill_trapezoid(c, CY + 12, CY + 16, 14, 11, CX, BONE, OUTLINE)
    fill_trapezoid(c, CY + 16, CY + 24, 11, 4, CX, BONE, OUTLINE)

    # --- METAL PLATING ---
    for y in range(H):
        for x in range(W):
            px = c[y][x]
            if px is not None and px not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                if x > CX + 3:
                    t = min(1.0, (x - CX - 3) / 16.0)
                    c[y][x] = lerp(px, METAL, t * 0.6)
    for y in range(3, CY + 20):
        x = CX + 4
        if 0 <= y < H and 0 <= x < W:
            if c[y][x] is not None and c[y][x] not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                c[y][x] = lerp(c[y][x], METAL_DK, 0.5)
    for rx, ry in [(CX+10,6),(CX+15,8),(CX+12,12),(CX+16,18),(CX+13,24),(CX+10,28)]:
        if 0 <= rx < W and 0 <= ry < H and c[ry][rx] is not None:
            c[ry][rx] = RIVET
    for y in range(4, CY + 18):
        x = CX + 5
        if 0 <= y < H and 0 <= x < W:
            if c[y][x] is not None and c[y][x] not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                c[y][x] = lerp(c[y][x], METAL_HI, 0.25)

    # --- EYE SOCKETS ---
    left_ex, left_ey = CX - 9, CY + 3
    right_ex, right_ey = CX + 9, CY + 3

    fill_ellipse(c, left_ex, left_ey, 8, 5.5, BONE_DK)
    fill_ellipse(c, left_ex, left_ey, 7, 4.5, OUTLINE)
    fill_ellipse(c, left_ex, left_ey, 6, 3.8, VOID)
    for dx in range(-3, 1):
        yy = left_ey - 4
        xx = left_ex + dx
        if 0 <= xx < W and 0 <= yy < H:
            if c[yy][xx] is not None and c[yy][xx] == BONE_DK:
                c[yy][xx] = lerp(BONE_DK, BONE, 0.4)

    fill_ellipse(c, right_ex, right_ey, 8, 5.5, METAL_DK)
    stroke_ellipse(c, right_ex, right_ey, 8, 5.5, METAL_SH, 1.5)
    fill_ellipse(c, right_ex, right_ey, 6.5, 4.2, VOID)
    if lens_ring2:
        fill_ellipse(c, right_ex, right_ey, 5, 3.2, lens_ring2)
    if lens_ring:
        fill_ellipse(c, right_ex, right_ey, 3.5, 2.3, lens_ring)
    if lens_color:
        fill_ellipse(c, right_ex, right_ey, 2, 1.3, lens_color)
        c[right_ey][right_ex] = (
            min(255, lens_color[0] + 80),
            min(255, lens_color[1] + 80),
            min(255, lens_color[2] + 80),
        )

    # --- NASAL CAVITY ---
    nose_top = CY + 8
    for y in range(nose_top, nose_top + 9):
        if y >= H:
            break
        t = (y - nose_top) / 9.0
        hw = max(0, 4.0 * (1.0 - t * 0.6))
        for x in range(int(CX - hw) - 1, int(CX + hw) + 2):
            if 0 <= x < W and c[y][x] is not None:
                if c[y][x] not in (VOID, OUTLINE, METAL_DK):
                    c[y][x] = OUTLINE
        for x in range(int(CX - hw) + 1, int(CX + hw)):
            if 0 <= x < W:
                c[y][x] = VOID
        if 0 <= y < H:
            set_px(c, CX, y, BONE_DK)

    # --- ZYGOMATIC ARCHES ---
    for y in range(CY + 5, CY + 12):
        t = 1.0 - abs(y - (CY + 8)) / 4.0
        for dx in range(4):
            for side_x in [left_ex - 7 - dx, right_ex + 7 + dx]:
                if 0 <= side_x < W and 0 <= y < H:
                    if c[y][side_x] is not None and c[y][side_x] not in (OUTLINE, VOID):
                        c[y][side_x] = lerp(c[y][side_x], BONE_SH, t * 0.35)

    # --- TEETH ---
    teeth_y = CY + 17
    teeth_left, teeth_right = CX - 10, CX + 10
    num_teeth = 10
    tooth_width = (teeth_right - teeth_left) / num_teeth
    for y in range(teeth_y, teeth_y + 4):
        if y >= H:
            break
        for x in range(teeth_left, teeth_right + 1):
            if 0 <= x < W and c[y][x] is not None and c[y][x] != OUTLINE:
                tooth_pos = (x - teeth_left) / tooth_width
                in_gap = abs(tooth_pos - round(tooth_pos)) < 0.15
                if in_gap:
                    c[y][x] = OUTLINE
                else:
                    edge_t = abs(tooth_pos - round(tooth_pos)) / 0.5
                    c[y][x] = lerp(TEETH, TEETH_DK, edge_t * 0.3)
    for x in range(teeth_left, teeth_right + 1):
        if 0 <= x < W and teeth_y - 1 >= 0:
            if c[teeth_y - 1][x] is not None and c[teeth_y - 1][x] not in (OUTLINE, VOID):
                c[teeth_y - 1][x] = lerp(c[teeth_y - 1][x], OUTLINE, 0.6)

    # --- CABLES ---
    cab_col = cable_glow or CABLE
    for bundle in range(3):
        b_offset = bundle * 2 - 2
        for dy in range(-5, 7):
            y = CY + 3 + dy + bundle
            if 0 <= y < H:
                curve = max(0, dy - 1) * 0.5
                intensity = 1.0 - abs(dy) / 8.0
                for dx_inner in range(2):
                    x = int(CX - 22 - b_offset + curve) - dx_inner
                    if 0 <= x < W and c[y][x] is None:
                        c[y][x] = lerp(CABLE_DK, cab_col, max(0, intensity) * 0.85)
    for bundle in range(3):
        b_offset = bundle * 2 - 2
        for dy in range(-5, 7):
            y = CY + 3 + dy + bundle
            if 0 <= y < H:
                curve = max(0, dy - 1) * 0.5
                intensity = 1.0 - abs(dy) / 8.0
                for dx_inner in range(2):
                    x = int(CX + 22 + b_offset - curve) + dx_inner
                    if 0 <= x < W and c[y][x] is None:
                        c[y][x] = lerp(CABLE_DK, cab_col, max(0, intensity) * 0.85)

    # --- SPINE ---
    spine_start = CY + 25
    for y in range(spine_start, min(H, spine_start + 8)):
        seg = y - spine_start
        hw = 2 if seg < 4 else 1
        for dx in range(-hw, hw + 1):
            x = CX + dx
            if 0 <= x < W:
                if seg % 2 == 0:
                    c[y][x] = METAL_SH if abs(dx) == hw else METAL
                elif abs(dx) <= 1:
                    c[y][x] = METAL_DK

    # --- MANIPULATOR CLAW ---
    claw_y = spine_start + 8
    for dy in range(3):
        y = claw_y + dy
        if y >= H:
            break
        spread = 2 + dy * 2
        for dx in range(-1, 2):
            xl = CX - spread + dx
            xr = CX + spread + dx
            if 0 <= xl < W:
                c[y][xl] = METAL_DK if dx == 0 else METAL_SH
            if 0 <= xr < W:
                c[y][xr] = METAL_DK if dx == 0 else METAL_SH
        if dy == 0 and 0 <= y < H:
            set_px(c, CX, y, METAL_SH)

    return c


# ============================================================
#  FRAME BUILDERS — compact=True for sidebar, False for full
# ============================================================

def get_frame(state="IDLE", compact=False):
    frames = {
        "IDLE": _frame_idle,
        "THINKING": _frame_thinking,
        "THINKING_1": _frame_thinking,
        "THINKING_2": _frame_thinking_2,
        "THINKING_3": _frame_thinking_3,
        "ERROR": _frame_error,
        "SUCCESS": _frame_success,
    }
    builder = frames.get(state, _frame_idle)
    return builder(compact=compact)


def _frame_idle(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(lens_color=None, lens_ring=METAL_DK, lens_ring2=METAL_SH)
    return render(canvas, pad=pad)


def _frame_thinking(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(lens_color=ORANGE, lens_ring=RED_DIM, lens_ring2=(80, 5, 0))
    return render(canvas, pad=pad)


def _frame_thinking_2(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(lens_color=ORANGE, lens_ring=(255, 80, 0), lens_ring2=RED_DIM)
    return render(canvas, pad=pad)


def _frame_thinking_3(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(
        lens_color=(255, 255, 200), lens_ring=ORANGE,
        lens_ring2=(255, 80, 0), cable_glow=ORANGE,
    )
    return render(canvas, pad=pad)


def _frame_error(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(
        lens_color=(255, 0, 0), lens_ring=RED,
        lens_ring2=RED_DARK, cable_glow=(160, 0, 0),
    )
    h = len(canvas)
    w = len(canvas[0]) if h > 0 else 0
    for y in range(h):
        for x in range(w):
            if canvas[y][x] is not None:
                r, g, b = canvas[y][x]
                canvas[y][x] = (min(255, r + 55), max(0, g - 40), max(0, b - 40))
    return render(canvas, pad=pad)


def _frame_success(compact=False):
    build = build_compact if compact else build_full
    pad = 1 if compact else 10
    canvas = build(lens_color=GREEN, lens_ring=GREEN_DIM, lens_ring2=(0, 80, 20))
    h = len(canvas)
    w = len(canvas[0]) if h > 0 else 0
    for y in range(h):
        for x in range(w):
            if canvas[y][x] is not None:
                r, g, b = canvas[y][x]
                canvas[y][x] = (min(255, r + 15), min(255, g + 22), b)
    return render(canvas, pad=pad)


# ============================================================
#  STANDALONE TEST
# ============================================================

def print_all_frames():
    for mode_name, compact in [("FULL", False), ("COMPACT", True)]:
        for state in ["IDLE", "THINKING", "THINKING_2", "THINKING_3", "ERROR", "SUCCESS"]:
            print(f"\n{'=' * 50}")
            print(f"  {mode_name} — {state}")
            print(f"{'=' * 50}")
            print(get_frame(state, compact=compact))
            print()


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "compact":
        for state in ["IDLE", "THINKING", "THINKING_2", "THINKING_3", "ERROR", "SUCCESS"]:
            print(f"\n  === {state} ===")
            print(get_frame(state, compact=True))
    else:
        print_all_frames()
