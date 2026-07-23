import random
from fractions import Fraction

import streamlit as st

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


if "rhythm_level" not in st.session_state:
    st.session_state.rhythm_level = 1

if "rhythm_question_no" not in st.session_state:
    st.session_state.rhythm_question_no = 1

if "rhythm_question" not in st.session_state:
    st.session_state.rhythm_question = generate_question(st.session_state.rhythm_level)

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
