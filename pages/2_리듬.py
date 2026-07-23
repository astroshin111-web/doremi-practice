import random
import wave
from io import BytesIO
from fractions import Fraction

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse
from score_renderer import DUR_BEATS

st.set_page_config(page_title="리듬 연습", page_icon="🥁")

st.title("🥁 리듬 연습")
st.write("음표 덧셈 문제를 보고, 총 박 수를 숫자로 직접 입력해 보세요.")

# 문제에서 사용할 음표 데이터
NOTE_DATA = [
    {"symbol": "♩", "beats": Fraction(1, 1)},   # 4분음표
    {"symbol": "♪", "beats": Fraction(1, 2)},   # 8분음표(개별 표기)
    {"symbol": "𝅘𝅥𝅯", "beats": Fraction(1, 4)},   # 16분음표(개별 표기)
    {"symbol": "♪.", "beats": Fraction(3, 4)},  # 점8분음표
    {"symbol": "𝅗𝅥", "beats": Fraction(2, 1)},   # 2분음표
]

RHYTHM_NOTES = {
    "whole": {"beats": Fraction(4, 1)},
    "half": {"beats": Fraction(2, 1)},
    "quarter": {"beats": Fraction(1, 1)},
    "eighth": {"beats": Fraction(1, 2)},
}


LEVEL_CONFIG = [
    {"count": (3, 3), "pool": [0, 1]},          # 4분, 8분
    {"count": (3, 4), "pool": [0, 1, 3]},       # + 점8분
    {"count": (3, 4), "pool": [0, 1, 2, 3]},    # + 16분
    {"count": (4, 5), "pool": [0, 1, 2, 3]},    # 음표 수 증가
    {"count": (4, 5), "pool": [0, 1, 2, 3, 4]}, # + 2분
]


def generate_question(level: int) -> dict:
    config = LEVEL_CONFIG[min(level - 1, len(LEVEL_CONFIG) - 1)]
    min_count, max_count = config["count"]
    count = random.randint(min_count, max_count)
    note_pool = [NOTE_DATA[idx] for idx in config["pool"]]
    notes = [random.choice(note_pool) for _ in range(count)]
    total = sum((note["beats"] for note in notes), start=Fraction(0, 1))
    return {
        "notes": notes,
        "answer": total,
    }


RHYTHM2_LEVEL_CONFIG = [
    ["quarter", "eighth"],
    ["quarter", "eighth", "half"],
    ["quarter", "eighth", "half", "whole"],
    ["quarter", "eighth", "half", "whole"],
    ["quarter", "eighth", "half", "whole"],
]


def draw_rhythm_note(ax, x: float, duration: str):
    """score_renderer.py의 음표 도형 스타일을 리듬 한 줄보에 맞게 사용한다."""
    y = 0.02
    head_width = 0.34
    head_height = 0.26
    is_filled = duration in ["quarter", "eighth"]
    has_stem = duration != "whole"

    head = Ellipse(
        (x, y),
        width=head_width,
        height=head_height,
        angle=-20,
        facecolor="black" if is_filled else "white",
        edgecolor="black",
        lw=1.6,
        zorder=3,
    )
    ax.add_patch(head)

    if has_stem:
        stem_x = x + 0.16
        stem_top_y = 0.62
        ax.add_line(Line2D([stem_x, stem_x], [y, stem_top_y], color="black", lw=1.5, zorder=2))

        if duration == "eighth":
            ax.plot(
                [stem_x, stem_x + 0.30],
                [stem_top_y, stem_top_y - 0.36],
                color="black",
                lw=1.5,
                solid_capstyle="round",
            )


def make_measure_durations(level: int, beats_per_measure: float) -> list[str]:
    allowed = RHYTHM2_LEVEL_CONFIG[min(level - 1, len(RHYTHM2_LEVEL_CONFIG) - 1)]
    durations = []
    remaining = beats_per_measure

    while remaining > 1e-9:
        candidates = [d for d in allowed if DUR_BEATS[d] <= remaining + 1e-9]
        duration = random.choice(candidates)
        durations.append(duration)
        remaining -= DUR_BEATS[duration]

    return durations


def generate_rhythm2_question(level: int, n_measures: int, beats_per_measure: float, time_sig: tuple[int, int]) -> dict:
    # 여러 종류 음표가 보이도록 패턴 다양성을 보장한다.
    pattern = []
    for _ in range(n_measures):
        pattern.extend(make_measure_durations(level, beats_per_measure))

    for _ in range(8):
        if len(set(pattern)) >= 2:
            break
        pattern = []
        for _ in range(n_measures):
            pattern.extend(make_measure_durations(level, beats_per_measure))

    beats = [DUR_BEATS[d] for d in pattern]
    return {
        "durations": pattern,
        "beats": beats,
        "n_measures": n_measures,
        "beats_per_measure": beats_per_measure,
        "time_sig": time_sig,
    }


def render_rhythm_line(durations: list[str], n_measures: int, beats_per_measure: float):
    total_beats = n_measures * beats_per_measure
    x_margin = 0.6
    width = total_beats + x_margin * 2

    fig, ax = plt.subplots(figsize=(min(14, max(7, total_beats * 1.3)), 2.2))
    ax.add_line(Line2D([x_margin, width - x_margin], [0, 0], color="black", lw=1.6))

    for i in range(n_measures + 1):
        x = x_margin + i * beats_per_measure
        ax.add_line(Line2D([x, x], [-0.28, 0.28], color="black", lw=2.0 if i in [0, n_measures] else 1.2))

    t = 0.0
    for duration in durations:
        beat_len = DUR_BEATS[duration]
        x = x_margin + t + (beat_len / 2)
        draw_rhythm_note(ax, x, duration)
        t += beat_len

    ax.set_xlim(0, width)
    ax.set_ylim(-0.8, 0.8)
    ax.axis("off")
    plt.tight_layout()
    return fig


def decode_wav_to_mono_float(wav_bytes: bytes):
    with wave.open(BytesIO(wav_bytes), "rb") as wf:
        channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    if sample_width == 1:
        arr = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        arr = (arr - 128.0) / 128.0
    elif sample_width == 2:
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sample_width == 4:
        arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError("지원하지 않는 WAV 포맷입니다.")

    if channels > 1:
        arr = arr.reshape(-1, channels).mean(axis=1)

    return arr, sample_rate


def detect_onsets(audio: np.ndarray, sr: int):
    if len(audio) < sr * 0.2:
        return np.array([])

    frame_size = 1024
    hop = 256
    n_frames = 1 + (len(audio) - frame_size) // hop
    if n_frames <= 2:
        return np.array([])

    energy = np.empty(n_frames, dtype=np.float32)
    for i in range(n_frames):
        start = i * hop
        frame = audio[start:start + frame_size]
        energy[i] = float(np.mean(frame * frame))

    diff = np.diff(energy, prepend=energy[0])
    flux = np.maximum(diff, 0.0)
    smooth = np.convolve(flux, np.ones(5, dtype=np.float32) / 5.0, mode="same")

    threshold = float(np.median(smooth) + np.std(smooth) * 1.3)
    min_dist = max(1, int((0.10 * sr) / hop))

    peaks = []
    last = -10**9
    for i in range(1, len(smooth) - 1):
        if smooth[i] > threshold and smooth[i] >= smooth[i - 1] and smooth[i] >= smooth[i + 1]:
            if i - last >= min_dist:
                peaks.append(i)
                last = i

    peak_times = np.array(peaks, dtype=np.float32) * (hop / sr)
    return peak_times


def _normalize_intervals(intervals: np.ndarray):
    total = float(np.sum(intervals))
    if total <= 1e-9:
        return None
    return intervals / total


def _ratio_text(intervals: np.ndarray):
    min_val = float(np.min(intervals))
    if min_val <= 1e-9:
        return "-"
    values = np.round(intervals / min_val, 2)
    return ":".join(f"{v:g}" for v in values)


def _best_onset_window(onsets: np.ndarray, expected_count: int, expected_norm: np.ndarray):
    """여러 타격이 잡힌 경우, 기대 비율과 가장 가까운 연속 구간을 선택한다."""
    if len(onsets) == expected_count:
        return onsets

    best = None
    best_mae = float("inf")
    for start in range(0, len(onsets) - expected_count + 1):
        window = onsets[start:start + expected_count]
        intervals = np.diff(window)
        norm = _normalize_intervals(intervals)
        if norm is None:
            continue
        mae = float(np.mean(np.abs(norm - expected_norm)))
        if mae < best_mae:
            best_mae = mae
            best = window

    return best if best is not None else onsets[:expected_count]


def judge_rhythm_clap(wav_bytes: bytes, expected_beats: list[float]):
    audio, sr = decode_wav_to_mono_float(wav_bytes)
    onsets = detect_onsets(audio, sr)

    expected_count = len(expected_beats)
    if expected_count < 2:
        return False, "문제 데이터 오류: 음표 수가 너무 적습니다."

    if len(onsets) < expected_count:
        return False, f"박수 개수가 부족해요. 감지된 타격 {len(onsets)}회 / 예상 {expected_count}회"

    expected_intervals = np.array(expected_beats[:-1], dtype=np.float32)
    expected_norm = _normalize_intervals(expected_intervals)
    if expected_norm is None:
        return False, "문제 데이터 오류: 비교할 리듬 간격이 없습니다."

    if len(onsets) > expected_count:
        onsets = _best_onset_window(onsets, expected_count, expected_norm)

    observed_intervals = np.diff(onsets)
    observed_norm = _normalize_intervals(observed_intervals)
    if observed_norm is None:
        return False, "리듬을 판정하기 어렵습니다. 다시 녹음해 주세요."

    mae = float(np.mean(np.abs(observed_norm - expected_norm)))
    max_err = float(np.max(np.abs(observed_norm - expected_norm)))

    expected_ratio = _ratio_text(expected_intervals)
    observed_ratio = _ratio_text(observed_intervals)

    # 평균 오차 + 최대 오차를 함께 보아 박자 구조를 더 엄격히 본다.
    is_correct = mae <= 0.13 and max_err <= 0.22
    if is_correct:
        return True, (
            "정답입니다! "
            f"기대 비율 {expected_ratio}, 연주 비율 {observed_ratio} "
            f"(평균 오차 {mae:.3f})"
        )
    return False, (
        "오답입니다. 리듬 간격 비율이 달라요. "
        f"기대 비율 {expected_ratio}, 연주 비율 {observed_ratio} "
        f"(평균 오차 {mae:.3f})"
    )


if "rhythm_level" not in st.session_state:
    st.session_state.rhythm_level = 1

if "rhythm_question_no" not in st.session_state:
    st.session_state.rhythm_question_no = 1

if "rhythm_question" not in st.session_state:
    st.session_state.rhythm_question = generate_question(st.session_state.rhythm_level)

if "rhythm2_level" not in st.session_state:
    st.session_state.rhythm2_level = 1

if "rhythm2_time_sig" not in st.session_state:
    st.session_state.rhythm2_time_sig = "4/4"

if st.session_state.rhythm2_time_sig not in ["2/4", "3/4", "4/4"]:
    st.session_state.rhythm2_time_sig = "4/4"


def rebuild_rhythm2_question():
    numerator, denominator = map(int, st.session_state.rhythm2_time_sig.split("/"))
    beats_per_measure = numerator * (4 / denominator)
    st.session_state.rhythm2_question = generate_rhythm2_question(
        st.session_state.rhythm2_level,
        2,
        beats_per_measure,
        (numerator, denominator),
    )

if "rhythm2_question" not in st.session_state:
    rebuild_rhythm2_question()

required_keys = {"durations", "beats", "n_measures", "beats_per_measure", "time_sig"}
if not required_keys.issubset(st.session_state.rhythm2_question.keys()):
    rebuild_rhythm2_question()

current = st.session_state.rhythm_question
answer_key = f"rhythm_answer_text_{st.session_state.rhythm_question_no}"

st.subheader("문제 1")
st.write("아래처럼 더해서 `=` 오른쪽 값(박 수)을 구하세요.")
st.caption(f"난이도 {st.session_state.rhythm_level} / {len(LEVEL_CONFIG)}")

parts = []
for idx, note in enumerate(current["notes"]):
    parts.append(
        f"<span style='display:inline-block;font-size:2.2rem;margin:0 0.2rem;padding:0.2rem 0.45rem;"
        "border:1px solid #e5e7eb;border-radius:0.45rem;min-width:2.5rem;text-align:center;'>"
        f"{note['symbol']}</span>"
    )
    if idx < len(current["notes"]) - 1:
        parts.append("<span style='font-size:2rem;margin:0 0.1rem;'>+</span>")

parts.append("<span style='font-size:2rem;margin-left:0.2rem;'>= ?</span>")
st.markdown(f"<div style='margin:1rem 0;'>{''.join(parts)}</div>", unsafe_allow_html=True)

answer_text = st.text_input(
    "정답(박 수)을 숫자로 입력하세요. 예: 1.5, 2.75",
    key=answer_key,
)

if st.button("정답 확인"):
    try:
        user_answer = Fraction(answer_text.strip())
        if user_answer == current["answer"]:
            st.success("맞았습니다!")
        else:
            st.info(f"아쉽습니다. 정답은 {float(current['answer']):g} 박입니다.")
    except (ValueError, ZeroDivisionError):
        st.warning("숫자 형태로 입력해 주세요. 예: 1.5 또는 2.75")

if st.button("다음 문제"):
    st.session_state.rhythm_level = min(
        st.session_state.rhythm_level + 1,
        len(LEVEL_CONFIG),
    )
    st.session_state.rhythm_question_no += 1
    st.session_state.rhythm_question = generate_question(st.session_state.rhythm_level)
    st.rerun()

st.divider()

st.subheader("문제 2")
st.write("아래 리듬 악보를 손뼉으로 연주한 뒤, 녹음 또는 WAV 파일 업로드로 제출하세요.")
st.caption(f"문제 2 난이도 {st.session_state.rhythm2_level} / {len(RHYTHM2_LEVEL_CONFIG)}")
st.caption("문제 2는 항상 2마디로 제시됩니다.")

time_sig = st.selectbox(
    "박자 선택",
    options=["2/4", "3/4", "4/4"],
    index=["2/4", "3/4", "4/4"].index(st.session_state.rhythm2_time_sig),
    key="rhythm2_time_sig_select",
)

if time_sig != st.session_state.rhythm2_time_sig:
    st.session_state.rhythm2_time_sig = time_sig
    numerator, denominator = map(int, time_sig.split("/"))
    beats_per_measure = numerator * (4 / denominator)
    st.session_state.rhythm2_question = generate_rhythm2_question(
        st.session_state.rhythm2_level,
        2,
        beats_per_measure,
        (numerator, denominator),
    )
    st.rerun()

rhythm2 = st.session_state.rhythm2_question
rhythm2_fig = render_rhythm_line(
    rhythm2["durations"],
    rhythm2["n_measures"],
    rhythm2["beats_per_measure"],
)
st.pyplot(rhythm2_fig)

st.write("녹음 버튼")
recorded_audio = st.audio_input("손뼉 리듬 녹음")
uploaded_audio = st.file_uploader("또는 WAV 파일 업로드", type=["wav"], key="rhythm2_upload")

submit_col, next_col = st.columns(2)

with submit_col:
    if st.button("문제 2 채점", type="primary"):
        audio_bytes = None
        if recorded_audio is not None:
            audio_bytes = recorded_audio.getvalue()
        elif uploaded_audio is not None:
            audio_bytes = uploaded_audio.read()

        if audio_bytes is None:
            st.warning("먼저 녹음하거나 WAV 파일을 업로드해 주세요.")
        else:
            try:
                ok, message = judge_rhythm_clap(audio_bytes, rhythm2["beats"])
                if ok:
                    st.success(message)
                else:
                    st.error(message)
            except Exception:
                st.error("오디오를 읽는 중 오류가 발생했습니다. WAV 형식으로 다시 시도해 주세요.")

with next_col:
    if st.button("문제 2 다음 문제"):
        st.session_state.rhythm2_level = min(
            st.session_state.rhythm2_level + 1,
            len(RHYTHM2_LEVEL_CONFIG),
        )
        numerator, denominator = map(int, st.session_state.rhythm2_time_sig.split("/"))
        beats_per_measure = numerator * (4 / denominator)
        st.session_state.rhythm2_question = generate_rhythm2_question(
            st.session_state.rhythm2_level,
            2,
            beats_per_measure,
            (numerator, denominator),
        )
        st.rerun()
