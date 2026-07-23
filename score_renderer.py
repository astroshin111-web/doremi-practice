import matplotlib
matplotlib.use("Agg")

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Circle


def _configure_korean_font():
    """fonts 폴더의 Noto Sans KR을 matplotlib 기본 폰트로 등록한다."""
    fonts_dir = Path(__file__).resolve().parent / "fonts"
    regular_path = fonts_dir / "NotoSansKR-Regular.ttf"
    all_noto_fonts = sorted(fonts_dir.glob("NotoSansKR-*.ttf"))

    for font_path in all_noto_fonts:
        font_manager.fontManager.addfont(str(font_path))

    if regular_path.exists():
        font_name = font_manager.FontProperties(fname=str(regular_path)).get_name()
        plt.rcParams["font.family"] = font_name
        plt.rcParams["axes.unicode_minus"] = False


_configure_korean_font()

# =========================
# 기본 데이터
# =========================
STEP_MAP = {
    "C": 0,
    "D": 1,
    "E": 2,
    "F": 3,
    "G": 4,
    "A": 5,
    "B": 6,
}

DUR_BEATS = {
    "whole": 4.0,
    "half": 2.0,
    "quarter": 1.0,
    "eighth": 0.5,
    "sixteenth": 0.25,
}

FLAG_COUNT = {
    "eighth": 1,
    "sixteenth": 2,
}

# 높은음자리표: 맨 아래줄 E4
# 낮은음자리표: 맨 아래줄 G2
CLEF_BOTTOM_REFERENCE = {
    "treble": 30,
    "bass": 18,
}


# =========================
# 음 높이 계산
# =========================
def _pitch_to_step_number(pitch: str) -> int:
    """
    예:
    C4 -> 28
    D4 -> 29
    E4 -> 30
    """
    step = pitch[0].upper()
    octave = int(pitch[-1])
    return octave * 7 + STEP_MAP[step]


def note_to_y(pitch: str, clef: str = "treble") -> float:
    """
    오선 y 좌표 계산
    - 한 줄 간격 = 0.5
    - 계이름 한 칸 이동 = 0.25
    """
    note_value = _pitch_to_step_number(pitch)
    bottom_ref = CLEF_BOTTOM_REFERENCE[clef]
    return (note_value - bottom_ref) * 0.25


# =========================
# 베지어 곡선 유틸
# =========================
def _bezier_curve(points, n=50):
    points = np.array(points, dtype=float)
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = points
    curve = (
        ((1 - t) ** 3) * p0
        + 3 * ((1 - t) ** 2) * t * p1
        + 3 * (1 - t) * (t ** 2) * p2
        + (t ** 3) * p3
    )
    return curve


# =========================
# 자리표 그리기
# =========================
def draw_treble_clef(ax, center_x, unit=0.5):
    """
    학습용 높은음자리표
    """
    base_y = 1 * unit
    # 악보 대비 큰 편이라 높은음자리표만 절반 크기로 축소
    scale = (unit / 0.5) * 0.5

    def P(x, y):
        return [center_x + x * scale, base_y + y * scale]

    curve = np.vstack([
        _bezier_curve([P(0.5, 3.5), P(0.15, 4.1), P(-0.55, 3.7), P(-0.4, 3.0)]),
        _bezier_curve([P(-0.4, 3.0), P(-0.3, 2.5), P(0.55, 2.4), P(0.6, 1.7)]),
        _bezier_curve([P(0.6, 1.7), P(0.65, 0.9), P(-0.95, 0.95), P(-0.9, 0.05)]),
        _bezier_curve([P(-0.9, 0.05), P(-0.85, -0.7), P(0.35, -0.75), P(0.35, 0.05)]),
        _bezier_curve([P(0.35, 0.05), P(0.35, 0.6), P(-0.35, 0.65), P(-0.3, 0.15)]),
        _bezier_curve([P(-0.3, 0.15), P(-0.27, -0.15), P(0.1, -0.1), P(0.1, 0.1)]),
    ])

    stem_top = P(0.5, 3.5)
    stem_bottom = P(0.5, -2.4)

    tail = _bezier_curve([
        P(0.5, -2.4),
        P(0.5, -2.9),
        P(-0.35, -2.85),
        P(-0.3, -2.25),
    ])

    ax.plot(curve[:, 0], curve[:, 1], color="black", lw=2.2, solid_capstyle="round")
    ax.plot(
        [stem_top[0], stem_bottom[0]],
        [stem_top[1], stem_bottom[1]],
        color="black",
        lw=2.2,
    )
    ax.plot(tail[:, 0], tail[:, 1], color="black", lw=2.2, solid_capstyle="round")
    ax.add_patch(Circle(P(-0.3, -2.05), 0.13 * scale, color="black"))


def draw_bass_clef(ax, center_x, unit=0.5):
    """
    학습용 낮은음자리표
    """
    base_y = 3 * unit
    # 기존보다 약 40% 축소
    scale = (unit / 0.5) * 0.6

    def P(x, y):
        return [center_x + x * scale, base_y + y * scale]

    body = np.vstack([
        _bezier_curve([P(-0.5, 0.9), P(0.6, 1.25), P(1.2, 0.6), P(1.15, -0.1)]),
        _bezier_curve([P(1.15, -0.1), P(1.1, -1.1), P(0.2, -1.7), P(-0.7, -1.75)]),
    ])
    head = _bezier_curve([P(-0.5, 0.9), P(-1.0, 0.8), P(-1.05, 0.15), P(-0.55, 0.05)])

    ax.plot(body[:, 0], body[:, 1], color="black", lw=2.4, solid_capstyle="round")
    ax.plot(head[:, 0], head[:, 1], color="black", lw=2.4, solid_capstyle="round")

    ax.add_patch(Circle(P(1.55, 0.5), 0.12 * scale, color="black"))
    ax.add_patch(Circle(P(1.55, -0.5), 0.12 * scale, color="black"))


# =========================
# 마디 분할
# =========================
def split_measures(notes, beats_per_measure=4.0):
    """
    notes: [{"pitch":"C4", "duration":"quarter"}, ...]
    박자 길이에 맞추어 마디로 분리
    """
    measures = []
    current_measure = []
    acc = 0.0

    for note in notes:
        beats = DUR_BEATS[note["duration"]]

        if acc + beats > beats_per_measure + 1e-9:
            if current_measure:
                measures.append(current_measure)
            current_measure = [note]
            acc = beats
        else:
            current_measure.append(note)
            acc += beats

        if abs(acc - beats_per_measure) < 1e-9:
            measures.append(current_measure)
            current_measure = []
            acc = 0.0

    if current_measure:
        measures.append(current_measure)

    return measures


# =========================
# 음표 그리기
# =========================
def draw_note(ax, x, pitch, duration, clef="treble", unit=0.5):
    y = note_to_y(pitch, clef)
    scale = unit / 0.5
    line_step = unit
    top_staff_y = 4 * unit

    filled = duration in ["quarter", "eighth", "sixteenth"]
    has_stem = duration != "whole"

    # 덧줄 아래
    ledger_y = -line_step
    while ledger_y >= y - 1e-9:
        ax.add_line(Line2D([x - 0.28, x + 0.28], [ledger_y, ledger_y], color="black", lw=1.2))
        ledger_y -= line_step

    # 덧줄 위
    ledger_y = top_staff_y + line_step
    while ledger_y <= y + 1e-9:
        ax.add_line(Line2D([x - 0.28, x + 0.28], [ledger_y, ledger_y], color="black", lw=1.2))
        ledger_y += line_step

    # 음표 머리
    head = Ellipse(
        (x, y),
        width=0.34 * scale,
        height=0.26 * scale,
        angle=-20,
        facecolor="black" if filled else "white",
        edgecolor="black",
        lw=1.5,
        zorder=3,
    )
    ax.add_patch(head)

    # 기둥
    if has_stem:
        stem_up = y < 2 * unit
        stem_x = x + 0.16 * scale if stem_up else x - 0.16 * scale
        stem_end_y = y + 1.6 * unit if stem_up else y - 1.6 * unit

        ax.add_line(Line2D([stem_x, stem_x], [y, stem_end_y], color="black", lw=1.5, zorder=2))

        # 꼬리
        for i in range(FLAG_COUNT.get(duration, 0)):
            flag_y = stem_end_y - i * 0.3 * scale
            if stem_up:
                ax.plot(
                    [stem_x, stem_x + 0.3 * scale],
                    [flag_y, flag_y - 0.4 * scale],
                    color="black",
                    lw=1.5,
                )
            else:
                ax.plot(
                    [stem_x, stem_x + 0.3 * scale],
                    [flag_y, flag_y + 0.4 * scale],
                    color="black",
                    lw=1.5,
                )


# =========================
# 전체 악보 렌더링
# =========================
def render_score(notes, clef="treble", time_sig=(4, 4), title=""):
    """
    notes: [{"pitch":"C4", "duration":"quarter"}, ...]
    clef: "treble" or "bass"
    time_sig: (4,4), (3,4) 등
    반환값: (fig, measures)
    """
    numerator, denominator = time_sig
    beats_per_measure = numerator * (4 / denominator)

    measures = split_measures(notes, beats_per_measure=beats_per_measure)

    unit = 0.5
    left_margin = 0.3
    clef_width = 1.6
    time_width = 0.9
    note_gap = 0.85
    measure_padding = 0.5

    positions = []
    barlines = []

    x = left_margin + clef_width + time_width

    for measure in measures:
        for note in measure:
            positions.append((x, note))
            x += note_gap
        x += measure_padding
        barlines.append(x - measure_padding * 0.5)

    total_width = x + 0.3
    top_staff_y = 4 * unit

    fig_width = min(16, max(8, total_width * 0.9))
    fig, ax = plt.subplots(figsize=(fig_width, 2.6))

    # 오선
    for i in range(5):
        y = i * unit
        ax.add_line(Line2D([left_margin, total_width - 0.2], [y, y], color="black", lw=1.1))

    # 시작선
    ax.add_line(Line2D([left_margin, left_margin], [0, top_staff_y], color="black", lw=1.4))

    # 자리표
    clef_x = left_margin + 0.7
    if clef == "treble":
        draw_treble_clef(ax, clef_x, unit=unit)
    else:
        draw_bass_clef(ax, clef_x, unit=unit)

    # 박자표
    ts_x = left_margin + clef_width + 0.3
    ax.text(ts_x, top_staff_y * 0.75, str(numerator),
            ha="center", va="center", fontsize=20, fontweight="bold")
    ax.text(ts_x, top_staff_y * 0.25, str(denominator),
            ha="center", va="center", fontsize=20, fontweight="bold")

    # 음표
    for x_pos, note in positions:
        draw_note(
            ax,
            x=x_pos,
            pitch=note["pitch"],
            duration=note["duration"],
            clef=clef,
            unit=unit,
        )

    # 마디선
    for i, bar_x in enumerate(barlines):
        if i == len(barlines) - 1:
            ax.add_line(Line2D([bar_x - 0.05, bar_x - 0.05], [0, top_staff_y], color="black", lw=1.2))
            ax.add_line(Line2D([bar_x + 0.02, bar_x + 0.02], [0, top_staff_y], color="black", lw=3.2))
        else:
            ax.add_line(Line2D([bar_x, bar_x], [0, top_staff_y], color="black", lw=1.3))

    ax.set_xlim(0, total_width)
    ax.set_ylim(-2.2, 4.3)
    ax.set_aspect("equal")
    ax.axis("off")

    if title:
        ax.set_title(title, fontsize=12)

    plt.tight_layout()
    return fig, measures


if __name__ == "__main__":
    notes = [
        {"pitch": "C4", "duration": "quarter"},
        {"pitch": "D4", "duration": "quarter"},
        {"pitch": "E4", "duration": "quarter"},
        {"pitch": "F4", "duration": "quarter"},
    ]
    fig, measures = render_score(notes, title="Sample Score")
    output_path = "score_render.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight", facecolor="white")
    print(f"Saved {output_path}")
    print(f"Measures: {len(measures)}")
