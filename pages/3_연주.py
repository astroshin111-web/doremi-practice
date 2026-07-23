import streamlit as st
from score_audio import synthesize_score

st.set_page_config(page_title="연주 게임", page_icon="🎺")

st.title("🎺 연주 게임")
st.write("아래 악보처럼 순서대로 연주해 보세요. 버튼을 눌러 4개의 음을 선택한 뒤, 정답을 확인해 보세요.")

questions = [
    {"label": "문제 1", "answer": ["도", "레", "미", "파"], "positions": [2, 1, 0, 1], "hint": "도에서 파로 올라갑니다."},
    {"label": "문제 2", "answer": ["미", "레", "도", "레"], "positions": [3, 2, 1, 2], "hint": "처음과 끝이 비슷한 음입니다."},
    {"label": "문제 3", "answer": ["파", "솔", "미", "레"], "positions": [1, 3, 2, 4], "hint": "높은 음에서 낮은 음으로 내려갑니다."},
    {"label": "문제 4", "answer": ["도", "미", "솔", "도"], "positions": [2, 0, 2, 4], "hint": "도에서 시작해 위로 올라가 다시 도로 돌아옵니다."},
]

# 높은음자리표 기준: 가장 상단 칸(pos=3)이 "미"
NOTE_SCALE = ["도", "레", "미", "파", "솔", "라", "시"]
NOTE_TO_PITCH = {
    "도": "C4",
    "레": "D4",
    "미": "E4",
    "파": "F4",
    "솔": "G4",
    "라": "A4",
    "시": "B4",
}


def position_to_note(pos):
    return NOTE_SCALE[(pos - 1) % 7]

if "index" not in st.session_state:
    st.session_state.index = 0

if "played_notes" not in st.session_state:
    st.session_state.played_notes = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "last_note_audio" not in st.session_state:
    st.session_state.last_note_audio = None


def reset_round():
    st.session_state.played_notes = []
    st.session_state.feedback = None


def remove_last_note():
    if st.session_state.played_notes:
        st.session_state.played_notes.pop()
    st.session_state.feedback = None


def clear_played_notes():
    st.session_state.played_notes = []
    st.session_state.feedback = None


def build_note_audio(note_name):
    pitch = NOTE_TO_PITCH[note_name]
    return synthesize_score(
        [{"pitch": pitch, "duration": "eighth"}],
        tempo=220,
    )


def render_staff(positions):
    staff_lines = [30, 50, 70, 90, 110]
    note_x_positions = [130, 205, 280, 355]
    svg_parts = [
        '<svg width="430" height="140" viewBox="0 0 430 140" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="430" height="140" rx="12" fill="#fffdf8" stroke="#e5e7eb" />',
    ]

    for y in staff_lines:
        svg_parts.append(f'<line x1="40" y1="{y}" x2="390" y2="{y}" stroke="#111827" stroke-width="1.5" />')

    # 높은음자리표(G clef)를 단순화한 벡터 형태로 추가
    svg_parts.append(
        '<path d="M78 28 '
        'C66 30, 60 42, 65 52 '
        'C71 65, 88 66, 92 54 '
        'C96 41, 81 36, 73 46 '
        'C66 55, 69 71, 82 76 '
        'C95 82, 108 73, 107 59 '
        'C106 44, 95 31, 81 31 '
        'L85 116" '
        'fill="none" stroke="#111827" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" />'
    )
    svg_parts.append('<circle cx="77" cy="96" r="5" fill="#111827" />')

    for idx, pos in enumerate(positions):
        x = note_x_positions[idx]
        y = 70 - pos * 10
        svg_parts.append(
            f'<ellipse cx="{x}" cy="{y}" rx="12" ry="8" fill="#111827" transform="rotate(-20 {x} {y})" />'
        )
        svg_parts.append(f'<line x1="{x + 10}" y1="{y}" x2="{x + 10}" y2="{y - 36}" stroke="#111827" stroke-width="2" />')

    svg_parts.append('</svg>')
    return "".join(svg_parts)


current = questions[st.session_state.index]
expected_answer = [position_to_note(pos) for pos in current["positions"]]

st.subheader(current["label"])
st.write(f"힌트: {current['hint']}")

st.write("문제 악보")
st.markdown(f"<div style='margin: 0.5rem 0 1rem 0;'>{render_staff(current['positions'])}</div>", unsafe_allow_html=True)

st.write("연주 패드")
notes = ["도", "레", "미", "파", "솔", "라", "시"]

cols = st.columns(4)
for idx, note in enumerate(notes):
    if cols[idx % 4].button(note, key=f"note_{st.session_state.index}_{note}"):
        st.session_state.last_note_audio = build_note_audio(note)
        if len(st.session_state.played_notes) < 4:
            st.session_state.played_notes.append(note)
            st.session_state.feedback = None
        else:
            st.warning("4개의 음만 선택할 수 있어요.")

if st.session_state.last_note_audio:
    st.audio(st.session_state.last_note_audio, format="audio/wav", autoplay=True)

st.write("")
st.write("지금까지 연주한 음")
if st.session_state.played_notes:
    st.info(" → ".join(st.session_state.played_notes))
else:
    st.info("아직 연주한 음이 없습니다. 버튼을 눌러 보세요.")

edit_col1, edit_col2 = st.columns(2)
with edit_col1:
    if st.button("↩️ 마지막 음 지우기", use_container_width=True):
        remove_last_note()
        st.rerun()
with edit_col2:
    if st.button("🧹 전체 지우기", use_container_width=True):
        clear_played_notes()
        st.rerun()

st.write("")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("연주 완료"):
        if len(st.session_state.played_notes) != 4:
            st.warning("4개의 음을 모두 선택해 주세요.")
        elif st.session_state.played_notes == expected_answer:
            st.success("정답입니다! 악보와 똑같이 연주했어요.")
            st.session_state.feedback = "correct"
        else:
            st.info("아쉽습니다. 아래에서 음을 지우고 다시 입력해 보세요.")
            st.session_state.feedback = "wrong"

with col2:
    if st.button("다음 문제"):
        st.session_state.index = (st.session_state.index + 1) % len(questions)
        reset_round()

if st.session_state.feedback == "wrong":
    st.write("정답 악보")
    st.write(" → ".join(expected_answer))

