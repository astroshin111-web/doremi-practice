import streamlit as st

st.set_page_config(page_title="계이름 연습", page_icon="🎼")

st.title("📖 계이름 연습")
st.write("악보를 보고 음의 이름을 적어보세요. 도부터 시까지 한글로 써 보세요.")

questions = [
    {"label": "도", "answer": "도", "positions": [2, 3, 1, 4, 2, 5, 3, 6]},
    {"label": "레", "answer": "레", "positions": [4, 2, 5, 3, 6, 4, 7, 5]},
    {"label": "미", "answer": "미", "positions": [3, 5, 2, 6, 4, 7, 5, 8]},
    {"label": "파", "answer": "파", "positions": [5, 4, 6, 3, 7, 5, 8, 6]},
    {"label": "솔", "answer": "솔", "positions": [6, 7, 5, 8, 6, 9, 7, 10]},
    {"label": "라", "answer": "라", "positions": [8, 6, 9, 7, 10, 8, 11, 9]},
    {"label": "시", "answer": "시", "positions": [7, 9, 6, 10, 8, 11, 9, 12]},
]

if "index" not in st.session_state:
    st.session_state.index = 0

current = questions[st.session_state.index]

st.subheader("문제")
st.write("아래 악보는 4분음표 길이로 제시됩니다.")

staff = """
<div style="font-family: serif; font-size: 32px; line-height: 1.1; margin: 1rem 0; padding: 1rem; border: 1px solid #cbd5e1; border-radius: 0.75rem; background: #fffdf7;">
  <div style="margin-bottom: 0.2rem;">𝄞</div>
  <div style="display: flex; align-items: center; gap: 6px;">
    <span>║</span><span>║</span><span>║</span><span>║</span><span>║</span>
  </div>
  <div style="display: flex; align-items: center; gap: 6px; margin-top: 4px;">
    <span>♩</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span><span style="margin-left: 8px;">●</span>
  </div>
</div>
"""

st.markdown(staff, unsafe_allow_html=True)

st.write(f"이 음의 이름은 무엇일까요? : {current['label']}")

answer = st.text_input("음의 이름을 한글로 적어보세요", key="note_answer")

if st.button("정답 확인"):
    if answer.strip() == current["answer"]:
        st.success("정답입니다! 잘했어요.")
    else:
        st.error(f"아쉬워요. 정답은 {current['answer']}입니다.")

if st.button("다음 문제"):
    st.session_state.index = (st.session_state.index + 1) % len(questions)
    st.session_state.note_answer = ""
    st.rerun()
