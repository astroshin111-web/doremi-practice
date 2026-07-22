import streamlit as st

st.set_page_config(page_title="리듬 연습", page_icon="🥁")

st.title("🥁 리듬 연습")
st.write("화면에 보이는 음표들을 보고, 총 음길이를 숫자로 계산해 보세요.")

questions = [
    {"label": "혼합 1", "notes": ["♬", "♫", "♩"], "answer": 1.75, "explain": "16분음표 1개(0.25) + 8분음표 1개(0.5) + 4분음표 1개(1) = 1.75박"},
    {"label": "혼합 2", "notes": ["♫", "♪.", "♩"], "answer": 2.25, "explain": "8분음표 1개(0.5) + 점8분음표 1개(0.75) + 4분음표 1개(1) = 2.25박"},
    {"label": "혼합 3", "notes": ["♬", "♩", "♩"], "answer": 2.25, "explain": "16분음표 1개(0.25) + 4분음표 2개(2) = 2.25박"},
    {"label": "혼합 4", "notes": ["♫", "♩", "♩", "♬"], "answer": 2.75, "explain": "8분음표 1개(0.5) + 4분음표 2개(2) + 16분음표 1개(0.25) = 2.75박"},
    {"label": "혼합 5", "notes": ["♪.", "♩", "♩"], "answer": 2.75, "explain": "점8분음표 1개(0.75) + 4분음표 2개(2) = 2.75박"},
    {"label": "혼합 6", "notes": ["♬", "♫", "♪."], "answer": 1.5, "explain": "16분음표 1개(0.25) + 8분음표 1개(0.5) + 점8분음표 1개(0.75) = 1.5박"},
]

if "index" not in st.session_state:
    st.session_state.index = 0

current = questions[st.session_state.index]

st.subheader("문제")
st.write("아래 음표들의 총 길이를 박 수로 계산하세요.")

notes_html = "".join([
    f"<span style='display: inline-block; font-size: 2rem; margin: 0 0.35rem 0.35rem 0; padding: 0.2rem 0.4rem; border: 1px solid #e5e7eb; border-radius: 0.4rem; min-width: 2.3rem; text-align: center;'>{note}</span>"
    for note in current["notes"]
])
st.markdown(f"<div style='font-size: 2rem; margin: 1rem 0;'>{notes_html}</div>", unsafe_allow_html=True)

answer = st.number_input("박 수로 답을 적으세요 (예: 0.25, 1.75)", min_value=0.0, value=0.0, step=0.25, key="rhythm_answer")

if st.button("정답 확인"):
    if abs(float(answer) - float(current["answer"])) < 1e-9:
        st.success("맞았습니다!")
    else:
        st.info("아쉽습니다. 다시 한 번 생각해 보세요.")

if st.button("다음 문제"):
    st.session_state.index = (st.session_state.index + 1) % len(questions)
    st.session_state.rhythm_answer = 0
    st.rerun()
