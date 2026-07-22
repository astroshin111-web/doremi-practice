import streamlit as st

st.set_page_config(page_title="연주 게임", page_icon="🎺")

st.title("🎺 연주 게임")
st.write("아래 악보처럼 순서대로 연주해 보세요. 버튼을 눌러 4개의 음을 선택한 뒤, 정답을 확인해 보세요.")

questions = [
    {"label": "문제 1", "answer": ["도", "레", "미", "파"], "positions": [2, 1, 0, 1], "hint": "도에서 파로 올라갑니다."},
    {"label": "문제 2", "answer": ["미", "레", "도", "레"], "positions": [3, 2, 1, 2], "hint": "처음과 끝이 비슷한 음입니다."},
    {"label": "문제 3", "answer": ["파", "솔", "미", "레"], "positions": [1, 3, 2, 4], "hint": "높은 음에서 낮은 음으로 내려갑니다."},
    {"label": "문제 4", "answer": ["도", "미", "솔", "도"], "positions": [2, 0, 2, 4], "hint": "도에서 시작해 위로 올라가 다시 도로 돌아옵니다."},
]

if "index" not in st.session_state:
    st.session_state.index = 0

if "played_notes" not in st.session_state:
    st.session_state.played_notes = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None


def reset_round():
    st.session_state.played_notes = []
    st.session_state.feedback = None


def render_staff(positions):
    staff_lines = [30, 50, 70, 90, 110]
    note_x_positions = [90, 180, 270, 360]
    svg_parts = [
        '<svg width="430" height="140" viewBox="0 0 430 140" xmlns="http://www.w3.org/2000/svg">',
        '<rect x="0" y="0" width="430" height="140" rx="12" fill="#fffdf8" stroke="#e5e7eb" />',
    ]

    for y in staff_lines:
        svg_parts.append(f'<line x1="40" y1="{y}" x2="390" y2="{y}" stroke="#111827" stroke-width="1.5" />')

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

st.subheader(current["label"])
st.write(f"힌트: {current['hint']}")

st.write("문제 악보")
st.markdown(f"<div style='margin: 0.5rem 0 1rem 0;'>{render_staff(current['positions'])}</div>", unsafe_allow_html=True)

st.write("연주 패드")
notes = ["도", "레", "미", "파", "솔", "라", "시"]

cols = st.columns(4)
for idx, note in enumerate(notes):
    if cols[idx % 4].button(note, key=f"note_{st.session_state.index}_{note}"):
        if len(st.session_state.played_notes) < 4:
            st.session_state.played_notes.append(note)
            st.session_state.feedback = None
        else:
            st.warning("4개의 음만 선택할 수 있어요.")

st.write("")
st.write("지금까지 연주한 음")
if st.session_state.played_notes:
    st.info(" → ".join(st.session_state.played_notes))
else:
    st.info("아직 연주한 음이 없습니다. 버튼을 눌러 보세요.")

st.write("")
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("연주 완료"):
        if len(st.session_state.played_notes) != 4:
            st.warning("4개의 음을 모두 선택해 주세요.")
        elif st.session_state.played_notes == current["answer"]:
            st.success("정답입니다! 악보와 똑같이 연주했어요.")
            st.session_state.feedback = "correct"
        else:
            st.info("아쉽습니다. 다시 한 번 생각해 보세요.")
            st.session_state.feedback = "wrong"

with col2:
    if st.button("다음 문제"):
        st.session_state.index = (st.session_state.index + 1) % len(questions)
        reset_round()

if st.session_state.feedback == "wrong":
    st.write("정답 악보")
    st.write(" → ".join(current["answer"]))

