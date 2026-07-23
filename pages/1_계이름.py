import random

import streamlit as st

from score_audio import synthesize_score
from score_renderer import DUR_BEATS, render_score

st.set_page_config(page_title="계이름 학습", page_icon="🎼", layout="wide")

KOR = {
    "C": "도",
    "D": "레",
    "E": "미",
    "F": "파",
    "G": "솔",
    "A": "라",
    "B": "시",
}

ANY_TO_LETTER = {
    "도": "C", "레": "D", "미": "E", "파": "F", "솔": "G", "라": "A", "시": "B",
    "c": "C", "d": "D", "e": "E", "f": "F", "g": "G", "a": "A", "b": "B",
    "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "A": "A", "B": "B",
}

DUR_KOR = {
    "whole": "온음표",
    "half": "2분음표",
    "quarter": "4분음표",
    "eighth": "8분음표",
    "sixteenth": "16분음표",
}

POOL = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
DURS = ["whole", "half", "quarter", "eighth"]


def make_question(n_measures=2):
    """각 마디가 4박을 채우도록 랜덤 문제를 만든다."""
    notes = []
    for _ in range(n_measures):
        acc = 0.0
        while acc < 4.0 - 1e-9:
            candidates = [d for d in DURS if DUR_BEATS[d] <= 4.0 - acc]
            duration = random.choice(candidates)
            notes.append({"pitch": random.choice(POOL), "duration": duration})
            acc += DUR_BEATS[duration]
    return notes


def parse_answer(text):
    """도레미 / C D E / cde 형식을 모두 알파벳 음이름 리스트로 바꾼다."""
    text = text.strip()
    if not text:
        return []

    if " " in text or "," in text:
        tokens = text.replace(",", " ").split()
    else:
        tokens = list(text)

    result = []
    for token in tokens:
        if token in ANY_TO_LETTER:
            result.append(ANY_TO_LETTER[token])
        elif len(token) > 1:
            for ch in token:
                if ch in ANY_TO_LETTER:
                    result.append(ANY_TO_LETTER[ch])
    return result


if "pitch_notes" not in st.session_state:
    st.session_state.pitch_notes = make_question(2)
if "pitch_score" not in st.session_state:
    st.session_state.pitch_score = 0
if "pitch_tries" not in st.session_state:
    st.session_state.pitch_tries = 0

st.title("🎼 계이름 학습")
st.write("악보를 보고 계이름을 읽어보세요. 필요하면 문제 악보를 소리로 재생할 수 있습니다.")

left, right = st.columns([3, 1])
with left:
    n_measures = st.slider("문제 길이(마디 수)", 1, 4, 2, key="pitch_measures")
with right:
    st.metric("점수", f"{st.session_state.pitch_score} / {st.session_state.pitch_tries}")

notes = st.session_state.pitch_notes

st.subheader("문제 악보")
fig, _ = render_score(notes, clef="treble", time_sig=(4, 4), title="계이름 문제")
st.pyplot(fig)
st.caption("나온 음표 길이: " + " · ".join(DUR_KOR[n["duration"]] for n in notes))

play_col, tempo_col = st.columns([1, 2])
with tempo_col:
    tempo = st.slider("재생 속도(BPM)", 50, 160, 90, 5, key="pitch_tempo")
with play_col:
    if st.button("▶ 문제 악보 재생", use_container_width=True):
        audio_bytes = synthesize_score(notes, tempo=tempo)
        st.audio(audio_bytes, format="audio/wav", autoplay=True)

st.divider()

correct_letters = [n["pitch"][0] for n in notes]
correct_kor = [KOR[x] for x in correct_letters]

answer = st.text_input("계이름 입력 (예: 도레미 / CDE)", key="pitch_answer")

c1, c2 = st.columns(2)
with c1:
    if st.button("✅ 정답 확인", type="primary"):
        st.session_state.pitch_tries += 1
        user = parse_answer(answer)
        if user == correct_letters:
            st.session_state.pitch_score += 1
            st.success("정답입니다!")
            st.balloons()
        else:
            st.error("오답입니다.")
            st.write("정답:", " - ".join(correct_kor), f"({' '.join(correct_letters)})")

with c2:
    if st.button("➡️ 다음 문제"):
        st.session_state.pitch_notes = make_question(n_measures)
        st.session_state.pitch_answer = ""
        st.rerun()

st.divider()
if st.button("← 메인으로 돌아가기"):
    st.switch_page("streamlit_app.py")
