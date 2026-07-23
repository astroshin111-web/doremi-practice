import streamlit as st
from score_audio import synthesize_score
from score_renderer import note_to_y, render_score

st.set_page_config(page_title="연주 게임", page_icon="🎺")

st.title("🎺 연주 게임")
st.write("아래 악보처럼 순서대로 연주해 보세요. 버튼을 눌러 4개의 음을 선택한 뒤, 정답을 확인해 보세요.")

questions = [
    {"label": "문제 1", "answer": ["도", "레", "미", "파"], "hint": "도에서 파로 올라갑니다."},
    {"label": "문제 2", "answer": ["미", "레", "도", "레"], "hint": "처음과 끝이 비슷한 음입니다."},
    {"label": "문제 3", "answer": ["파", "솔", "미", "레"], "hint": "높은 음에서 낮은 음으로 내려갑니다."},
    {"label": "문제 4", "answer": ["도", "미", "솔", "도"], "hint": "도에서 시작해 위로 올라가 다시 도로 돌아옵니다."},
]

NOTE_SCALE = ["도", "레", "미", "파", "솔", "라", "시"]
NOTE_TO_PITCH_BY_CLEF = {
    "treble": {
        "도": "C4",
        "레": "D4",
        "미": "E4",
        "파": "F4",
        "솔": "G4",
        "라": "A4",
        "시": "B4",
    },
    "bass": {
        "도": "C3",
        "레": "D3",
        "미": "E3",
        "파": "F3",
        "솔": "G3",
        "라": "A3",
        "시": "B3",
    },
}

if "index" not in st.session_state:
    st.session_state.index = 0

if "played_notes" not in st.session_state:
    st.session_state.played_notes = []

if "feedback" not in st.session_state:
    st.session_state.feedback = None

if "last_note_audio" not in st.session_state:
    st.session_state.last_note_audio = None

if "play_clef" not in st.session_state:
    st.session_state.play_clef = "treble"


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


def build_note_audio(note_name, clef):
    pitch = NOTE_TO_PITCH_BY_CLEF[clef][note_name]
    return synthesize_score(
        [{"pitch": pitch, "duration": "eighth"}],
        tempo=220,
    )


def build_score_notes(answer_notes, clef):
    mapping = NOTE_TO_PITCH_BY_CLEF[clef]
    return [{"pitch": mapping[note], "duration": "quarter"} for note in answer_notes]


current = questions[st.session_state.index]
expected_answer = current["answer"]

clef_label = st.selectbox(
    "음자리표 선택",
    options=["높은음자리표", "낮은음자리표"],
    index=0 if st.session_state.play_clef == "treble" else 1,
)
selected_clef = "treble" if clef_label == "높은음자리표" else "bass"
st.session_state.play_clef = selected_clef

st.subheader(current["label"])
score_notes = build_score_notes(current["answer"], selected_clef)
fig, _ = render_score(score_notes, clef=selected_clef, time_sig=(4, 4), title="")

# 연주 페이지에서는 악보 위/아래 여백을 줄여 화면 밀도를 높인다.
ax = fig.axes[0]
note_ys = [note_to_y(n["pitch"], selected_clef) for n in score_notes]
content_y_min = min(0.0, min(note_ys, default=0.0))
content_y_max = max(2.0, max(note_ys, default=2.0))
ax.set_ylim(content_y_min - 0.8, content_y_max + 0.8)
fig.subplots_adjust(top=0.90, bottom=0.20)

st.pyplot(fig)

st.write("연주 패드")
notes = ["도", "레", "미", "파", "솔", "라", "시"]

cols = st.columns(4)
for idx, note in enumerate(notes):
    if cols[idx % 4].button(note, key=f"note_{st.session_state.index}_{note}"):
        st.session_state.last_note_audio = build_note_audio(note, selected_clef)
        if len(st.session_state.played_notes) < 4:
            st.session_state.played_notes.append(note)
            st.session_state.feedback = None
        else:
            st.warning("4개의 음만 선택할 수 있어요.")

if st.session_state.last_note_audio:
    st.audio(st.session_state.last_note_audio, format="audio/wav", autoplay=True)

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

