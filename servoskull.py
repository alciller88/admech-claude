#!/usr/bin/env python3
"""
servoskull.py — Servo-Cráneo Designatus
Pixel art con Unicode half-block characters + ANSI true color.
⚙ CLASIFICACIÓN: ARCHEOTECH — SOLO MAGOS AUTORIZADOS ⚙
"""

import math

# ═══ ANSI CODES ═══
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

# ═══ CANVAS ═══
W, H = 60, 48  # pixels (renders as 60 chars × 24 lines)
PAD = 10        # centering in 80 cols

# ═══ COLOR PALETTE ═══
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


# ═══ RENDER ENGINE ═══

def _fg(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def _bg(r, g, b):
    return f"\033[48;2;{r};{g};{b}m"

def _c(color, text):
    return f"{color}{text}{RESET}"

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def render(canvas):
    """Render pixel canvas using half-block characters with true color ANSI."""
    lines = []
    for row in range(0, H, 2):
        parts = []
        for col in range(W):
            top = canvas[row][col]
            bot = canvas[row + 1][col] if row + 1 < H else None
            if top is None and bot is None:
                parts.append(" ")
            elif top is None:
                parts.append(_fg(*bot) + "▄")
            elif bot is None:
                parts.append(_fg(*top) + "▀")
            elif top == bot:
                parts.append(_fg(*top) + "█")
            else:
                parts.append(_bg(*top) + _fg(*bot) + "▄")
        line = " " * PAD + "".join(parts) + RESET
        lines.append(line)
    return "\n".join(lines)


# ═══ DRAWING PRIMITIVES ═══

def make_canvas():
    return [[None] * W for _ in range(H)]


def fill_ellipse(c, cx, cy, rx, ry, color):
    y0 = max(0, int(cy - ry - 1))
    y1 = min(H - 1, int(cy + ry + 1))
    x0 = max(0, int(cx - rx - 1))
    x1 = min(W - 1, int(cx + rx + 1))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx if rx > 0 else 0
            dy = (y - cy) / ry if ry > 0 else 0
            if dx * dx + dy * dy <= 1.0:
                c[y][x] = color


def stroke_ellipse(c, cx, cy, rx, ry, color, thickness=1.0):
    """Draw only the outline of an ellipse."""
    y0 = max(0, int(cy - ry - 2))
    y1 = min(H - 1, int(cy + ry + 2))
    x0 = max(0, int(cx - rx - 2))
    x1 = min(W - 1, int(cx + rx + 2))
    inner = 1.0 - thickness / min(rx, ry)
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            dx = (x - cx) / rx if rx > 0 else 0
            dy = (y - cy) / ry if ry > 0 else 0
            d = dx * dx + dy * dy
            if inner * inner <= d <= 1.0:
                c[y][x] = color


def fill_rect(c, x1, y1, x2, y2, color):
    for y in range(max(0, y1), min(H, y2 + 1)):
        for x in range(max(0, x1), min(W, x2 + 1)):
            c[y][x] = color


def fill_trapezoid(c, y_start, y_end, top_half_w, bot_half_w, cx, color,
                   outline_col=None):
    for y in range(max(0, y_start), min(H, y_end + 1)):
        t = (y - y_start) / max(1, y_end - y_start)
        hw = top_half_w + (bot_half_w - top_half_w) * t
        xl = int(cx - hw)
        xr = int(cx + hw)
        for x in range(max(0, xl), min(W, xr + 1)):
            c[y][x] = color
        if outline_col:
            if 0 <= xl < W:
                c[y][xl] = outline_col
            if 0 <= xr < W:
                c[y][xr] = outline_col


# ═══ SKULL BUILDER ═══

CX = 30   # skull center X (in 60-wide canvas)
CY = 15   # cranium center Y


def build_skull(lens_color=None, lens_ring=None, lens_ring2=None,
                cable_glow=None):
    """Build servo-skull pixel canvas."""
    c = make_canvas()

    # ─── CRANIUM (main ellipse) ───
    fill_ellipse(c, CX, CY, 22, 15, OUTLINE)        # outer outline
    fill_ellipse(c, CX, CY, 21, 14, BONE)            # bone fill
    fill_ellipse(c, CX - 3, CY - 6, 14, 7, BONE_HI)  # cranium highlight

    # ─── BROW RIDGE (gold band with cog teeth) ───
    brow_y = 9
    for x in range(CX - 18, CX + 19):
        for y_off in [brow_y, brow_y + 1]:
            if 0 <= x < W and 0 <= y_off < H:
                if c[y_off][x] is not None and c[y_off][x] != OUTLINE:
                    c[y_off][x] = GOLD if y_off == brow_y + 1 else GOLD_DIM
    # Cog teeth extending up from brow
    for x in [CX - 14, CX - 9, CX - 4, CX + 1, CX + 6, CX + 11]:
        for dx in range(3):
            xx = x + dx
            if 0 <= xx < W and c[brow_y - 1][xx] is not None:
                c[brow_y - 1][xx] = GOLD

    # ─── LOWER FACE / JAW ───
    # Wider at cheekbones, tapers to chin
    fill_trapezoid(c, CY + 12, CY + 16, 14, 11, CX, BONE, OUTLINE)
    fill_trapezoid(c, CY + 16, CY + 24, 11, 4, CX, BONE, OUTLINE)

    # ─── METAL PLATING (right side augmentation) ───
    for y in range(H):
        for x in range(W):
            px = c[y][x]
            if px is not None and px not in (OUTLINE, VOID, GOLD, GOLD_DIM):
                if x > CX + 3:
                    t = min(1.0, (x - CX - 3) / 16.0)
                    c[y][x] = lerp(px, METAL, t * 0.6)

    # Metal plate edge (darker seam line)
    for y in range(3, CY + 20):
        x = CX + 4
        if 0 <= y < H and 0 <= x < W:
            if c[y][x] is not None and c[y][x] not in (OUTLINE, VOID, GOLD,
                                                         GOLD_DIM):
                c[y][x] = lerp(c[y][x], METAL_DK, 0.5)

    # Rivets / bolts on metal side
    rivet_positions = [
        (CX + 10, 6), (CX + 15, 8), (CX + 12, 12),
        (CX + 16, 18), (CX + 13, 24), (CX + 10, 28),
    ]
    for rx, ry in rivet_positions:
        if 0 <= rx < W and 0 <= ry < H and c[ry][rx] is not None:
            c[ry][rx] = RIVET

    # Metal plate highlight (subtle bright edge)
    for y in range(4, CY + 18):
        x = CX + 5
        if 0 <= y < H and 0 <= x < W:
            if c[y][x] is not None and c[y][x] not in (OUTLINE, VOID, GOLD,
                                                         GOLD_DIM):
                c[y][x] = lerp(c[y][x], METAL_HI, 0.25)

    # ─── EYE SOCKETS (BIGGER, more prominent) ───
    left_ex, left_ey = CX - 9, CY + 3
    right_ex, right_ey = CX + 9, CY + 3

    # Left eye: organic — deep dark socket with bone rim
    fill_ellipse(c, left_ex, left_ey, 8, 5.5, BONE_DK)
    fill_ellipse(c, left_ex, left_ey, 7, 4.5, OUTLINE)
    fill_ellipse(c, left_ex, left_ey, 6, 3.8, VOID)
    # Subtle highlight on upper-left rim of left socket
    for dx in range(-3, 1):
        yy = left_ey - 4
        xx = left_ex + dx
        if 0 <= xx < W and 0 <= yy < H:
            if c[yy][xx] is not None and c[yy][xx] == BONE_DK:
                c[yy][xx] = lerp(BONE_DK, BONE, 0.4)

    # Right eye: mechanical — metal housing with sensor
    fill_ellipse(c, right_ex, right_ey, 8, 5.5, METAL_DK)
    stroke_ellipse(c, right_ex, right_ey, 8, 5.5, METAL_SH, 1.5)
    fill_ellipse(c, right_ex, right_ey, 6.5, 4.2, VOID)

    # Right eye: concentric auspex lens rings
    if lens_ring2:
        fill_ellipse(c, right_ex, right_ey, 5, 3.2, lens_ring2)
    if lens_ring:
        fill_ellipse(c, right_ex, right_ey, 3.5, 2.3, lens_ring)
    if lens_color:
        fill_ellipse(c, right_ex, right_ey, 2, 1.3, lens_color)
        # Bright center dot
        c[right_ey][right_ex] = (
            min(255, lens_color[0] + 80),
            min(255, lens_color[1] + 80),
            min(255, lens_color[2] + 80),
        )

    # ─── NASAL CAVITY (bigger, more defined) ───
    nose_top = CY + 8
    # Triangular cavity narrowing downward
    for y in range(nose_top, nose_top + 9):
        if y >= H:
            break
        t = (y - nose_top) / 9.0
        hw = max(0, 4.0 * (1.0 - t * 0.6))
        # Outline
        for x in range(int(CX - hw) - 1, int(CX + hw) + 2):
            if 0 <= x < W and c[y][x] is not None:
                if c[y][x] not in (VOID, OUTLINE, METAL_DK):
                    c[y][x] = OUTLINE
        # Void fill
        for x in range(int(CX - hw) + 1, int(CX + hw)):
            if 0 <= x < W:
                c[y][x] = VOID
    # Nasal septum (bone divider)
    for y in range(nose_top, nose_top + 6):
        if 0 <= y < H:
            c[y][CX] = BONE_DK

    # ─── ZYGOMATIC ARCHES (cheekbone shadows) ───
    for y in range(CY + 5, CY + 12):
        t = 1.0 - abs(y - (CY + 8)) / 4.0
        for dx in range(4):
            for side_x in [left_ex - 7 - dx, right_ex + 7 + dx]:
                if 0 <= side_x < W and 0 <= y < H:
                    if c[y][side_x] is not None and c[y][side_x] not in (
                        OUTLINE, VOID
                    ):
                        c[y][side_x] = lerp(c[y][side_x], BONE_SH,
                                            t * 0.35)

    # ─── TEETH (wider, more defined rictus grin) ───
    teeth_y = CY + 17
    teeth_left = CX - 10
    teeth_right = CX + 10
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
                    # Teeth are brighter in center, darker at edges
                    edge_t = abs(tooth_pos - round(tooth_pos)) / 0.5
                    c[y][x] = lerp(TEETH, TEETH_DK, edge_t * 0.3)

    # Upper teeth edge (dark line between skull and teeth)
    for x in range(teeth_left, teeth_right + 1):
        if 0 <= x < W and teeth_y - 1 >= 0:
            if c[teeth_y - 1][x] is not None and c[teeth_y - 1][x] not in (
                OUTLINE, VOID
            ):
                c[teeth_y - 1][x] = lerp(c[teeth_y - 1][x], OUTLINE, 0.6)

    # ─── CABLES / MECHADENDRITES (thicker, curved) ───
    cab_col = cable_glow or CABLE

    # Left cables — 3 bundles curving down from temple
    for bundle in range(3):
        b_offset = bundle * 2 - 2  # -2, 0, 2
        for dy in range(-5, 7):
            y = CY + 3 + dy + bundle
            if 0 <= y < H:
                # Curve: starts horizontal, curves down
                curve = max(0, dy - 1) * 0.5
                intensity = 1.0 - abs(dy) / 8.0
                for dx_inner in range(2):
                    x = int(CX - 22 - b_offset + curve) - dx_inner
                    if 0 <= x < W and c[y][x] is None:
                        c[y][x] = lerp(CABLE_DK, cab_col,
                                       max(0, intensity) * 0.85)

    # Right cables — mirror
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
                        c[y][x] = lerp(CABLE_DK, cab_col,
                                       max(0, intensity) * 0.85)

    # ─── SEGMENTED SPINE (more detailed) ───
    spine_start = CY + 25
    spine_len = 8
    for y in range(spine_start, min(H, spine_start + spine_len)):
        seg = (y - spine_start)
        # Spine tapers slightly
        hw = 2 if seg < 4 else 1
        for dx in range(-hw, hw + 1):
            x = CX + dx
            if 0 <= x < W:
                if seg % 2 == 0:
                    # Vertebra segment
                    if abs(dx) == hw:
                        c[y][x] = METAL_SH
                    else:
                        c[y][x] = METAL
                else:
                    # Joint between segments
                    if abs(dx) <= 1:
                        c[y][x] = METAL_DK

    # ─── MANIPULATOR CLAW ───
    claw_y = spine_start + spine_len
    # Two pincers spreading out
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
        # Center connector
        if dy == 0 and 0 <= y < H:
            c[y][CX] = METAL_SH

    return c


# ═══ FRAME BUILDERS ═══

def get_frame(state="IDLE"):
    frames = {
        "IDLE": _frame_idle,
        "THINKING_1": _frame_thinking_1,
        "THINKING_2": _frame_thinking_2,
        "THINKING_3": _frame_thinking_3,
        "ERROR": _frame_error,
        "SUCCESS": _frame_success,
    }
    return frames.get(state, _frame_idle)()


def _frame_idle():
    canvas = build_skull(lens_color=None, lens_ring=METAL_DK,
                         lens_ring2=METAL_SH)
    art = render(canvas)
    h = _c(GREY_COGIT, f"        {BINHARIC_STATIC}")
    f = _c(GREY_COGIT, f"        {BINHARIC_MARS}")
    s = _c(GREY_COGIT, "     [SERVO-Ω//] STATUS: IDLE — AWAITING COMMAND")
    return f"{h}\n{art}\n{f}\n{s}"


def _frame_thinking_1():
    canvas = build_skull(lens_color=ORANGE, lens_ring=RED_DIM,
                         lens_ring2=(80, 5, 0))
    art = render(canvas)
    h = _c(ORANGE_FORGE, f"    ψ   {BINHARIC_STATIC}   ψ")
    f = _c(ORANGE_FORGE, "      CONSULTANDO AL OMNISSIAH... ψ")
    s = _c(GREY_COGIT, "     [SERVO-Ω//] STATUS: THINKING — OUTER RING")
    return f"{h}\n{art}\n{f}\n{s}"


def _frame_thinking_2():
    canvas = build_skull(lens_color=ORANGE, lens_ring=(255, 80, 0),
                         lens_ring2=RED_DIM)
    art = render(canvas)
    h = _c(ORANGE_FORGE, f"  ψ ψ ψ  {BINHARIC_STATIC}  ψ ψ ψ")
    f = _c(ORANGE_FORGE, "    QUERYING THE MACHINE GOD... ψ  ◉  ◉  ◉")
    s = _c(GREY_COGIT, "     [SERVO-Ω//] STATUS: DEEP QUERY — RINGS EXPAND")
    return f"{h}\n{art}\n{f}\n{s}"


def _frame_thinking_3():
    canvas = build_skull(
        lens_color=(255, 255, 200),
        lens_ring=ORANGE,
        lens_ring2=(255, 80, 0),
        cable_glow=ORANGE,
    )
    art = render(canvas)
    h = _c(BOLD + ORANGE_FORGE, f"ψψψψψ  {BINHARIC_MARS}  ψψψψψ")
    f = _c(BOLD + ORANGE_FORGE, "  ψ NOOSPHERIC LINK — ALL ANIMUS ENGAGED ψ")
    s = _c(ORANGE_FORGE, "     [SERVO-Ω//] STATUS: MAXIMUM — OMNISSIAH SPEAKS")
    return f"{h}\n{art}\n{f}\n{s}"


def _frame_error():
    canvas = build_skull(
        lens_color=(255, 0, 0),
        lens_ring=RED,
        lens_ring2=RED_DARK,
        cable_glow=(160, 0, 0),
    )
    # Tint skull red
    for y in range(H):
        for x in range(W):
            if canvas[y][x] is not None:
                r, g, b = canvas[y][x]
                canvas[y][x] = (min(255, r + 55), max(0, g - 40),
                                max(0, b - 40))
    art = render(canvas)
    h = _c(BOLD + RED_MARS,
           "☠ ☠ ☠  ERR0R C0RRUPT10N 0x00DEAD — SCRAPCODE  ☠ ☠ ☠")
    f = _c(BOLD + RED_MARS,
           " ☠ ¡HEREJÍA DETECTADA! — TECH-HERESY IDENTIFIED ☠")
    s = _c(RED_MARS,
           "     [SERVO-Ω//] STATUS: ☠ ERROR — PURGE REQUIRED ☠")
    return f"{h}\n{art}\n{f}\n{s}"


def _frame_success():
    canvas = build_skull(lens_color=GREEN, lens_ring=GREEN_DIM,
                         lens_ring2=(0, 80, 20))
    # Tint skull golden/green
    for y in range(H):
        for x in range(W):
            if canvas[y][x] is not None:
                r, g, b = canvas[y][x]
                canvas[y][x] = (min(255, r + 15), min(255, g + 22), b)
    art = render(canvas)
    h = _c(BOLD + GOLD_OMNI,
           " ‡ ‡ ‡  LAUS OMNISSIAH — RITE COMPLETE  ‡ ‡ ‡")
    f = _c(BOLD + GOLD_OMNI,
           "⚙ POR EL OMNISSIAH — BY THE WILL OF THE OMNISSIAH ⚙")
    s = _c(GREEN_BIONIC,
           "     [SERVO-Ω//] STATUS: ‡ SUCCESS — CODE SANCTIFIED ‡")
    return f"{h}\n{art}\n{f}\n{s}"


def print_all_frames():
    states = ["IDLE", "THINKING_1", "THINKING_2", "THINKING_3",
              "ERROR", "SUCCESS"]
    for state in states:
        print(f"\n{'═' * 70}")
        print(f"  FRAME: {state}")
        print(f"{'═' * 70}")
        print(get_frame(state))
        print()


if __name__ == "__main__":
    print_all_frames()
