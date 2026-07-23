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
import streamlit as st
import random
from score_renderer import render_score, DUR_BEATS   # 앞서 만든 렌더러 재사용

st.set_page_config(page_title="계이름 연습", page_icon="🎼", layout="wide")

# ==================== 계이름 변환 ====================
# 답: 한글(도레미) / 영어(CDEF) 모두 허용
KOR = {"C":"도","D":"레","E":"미","F":"파","G":"솔","A":"라","B":"시"}
# 입력 정규화용: 사용자가 무엇을 쳐도 알파벳 음이름으로 통일
ANY_TO_LETTER = {
    "도":"C","레":"D","미":"E","파":"F","솔":"G","라":"A","시":"B",
    "c":"C","d":"D","e":"E","f":"F","g":"G","a":"A","b":"B",
    "C":"C","D":"D","E":"E","F":"F","G":"G","A":"A","B":"B",
}
DUR_KOR = {"whole":"온음표","half":"2분음표","quarter":"4분음표",
           "eighth":"8분음표","sixteenth":"16분음표"}

POOL = ["C4","D4","E4","F4","G4","A4","B4","C5"]
DURS = ["quarter","half","eighth","whole"]

def make_question(n_measures):
    """각 마디를 정확히 4박으로 채우는 문제 생성 (음길이 혼합)"""
    notes = []
    for _ in range(n_measures):
        acc = 0.0
        while acc < 4.0 - 1e-9:
            d = random.choice([x for x in DURS if DUR_BEATS[x] <= 4.0 - acc])
            notes.append({"pitch": random.choice(POOL), "duration": d})
            acc += DUR_BEATS[d]
    return notes

def parse_answer(text):
    """'도레미' / 'C D E' / 'cde' 등 어떤 형식이든 알파벳 리스트로 변환"""
    tokens = [t for t in text.replace(",", " ").split()] if any(
        c.isspace() or c == "," for c in text) else list(text)
    result = []
    for tok in tokens:
        tok = tok.strip()
        if not tok:
            continue
        # 여러 글자가 붙어온 경우(예: 'CDE') 한 글자씩 처리
        for ch in ([tok] if len(tok) == 1 or tok in ANY_TO_LETTER else list(tok)):
            key = ch if ch in ANY_TO_LETTER else ch.upper()
            if key in ANY_TO_LETTER:
                result.append(ANY_TO_LETTER[key])
    return result

# ==================== 세션 상태 ====================
if "q_notes" not in st.session_state:
    st.session_state.q_notes = make_question(2)
    st.session_state.checked = False
    st.session_state.score = 0
    st.session_state.tries = 0

# ==================== 헤더 ====================
st.title("🎼 계이름 연습")
st.write("악보의 음표를 **왼쪽부터 순서대로** 읽어, 계이름을 적어보세요.")
st.caption("한글(도레미…) 또는 영어(C D E F…) 어느 쪽으로 써도 됩니다. "
           "음표 길이는 온음표·2분·4분·8분음표가 섞여 나옵니다.")

top1, top2 = st.columns([3, 1])
with top1:
    n_measures = st.slider("문제 길이(마디 수)", 1, 4, 2)
with top2:
    if st.session_state.tries:
        st.metric("점수", f"{st.session_state.score} / {st.session_state.tries}")

st.divider()

notes = st.session_state.q_notes

# ==================== 문제 악보 (높은음자리표 포함) ====================
st.subheader("문제 악보")
fig, measures = render_score(notes, clef="treble", time_sig=(4, 4))
st.pyplot(fig)

# 음길이 힌트(어떤 음표가 나왔는지 안내)
st.caption("나온 음표 길이: " +
           " · ".join(DUR_KOR[n["duration"]] for n in notes))

st.divider()

# ==================== 정답 입력 ====================
correct_letters = [n["pitch"][0] for n in notes]           # 예: ['E','C','G']
correct_kor = [KOR[c] for c in correct_letters]

st.write(f"이 악보에는 음이 **{len(notes)}개** 있습니다. 순서대로 적어주세요.")
answer = st.text_input(
    "계이름 입력 (예: 도레미파  또는  C D E F)",
    key="note_answer",
    placeholder="예) 도레미파  /  CDEF")

b1, b2 = st.columns(2)
with b1:
    if st.button("✅ 정답 확인", type="primary"):
        st.session_state.tries += 1
        user_letters = parse_answer(answer)
        if user_letters == correct_letters:
            st.session_state.score += 1
            st.success("정답입니다! 잘했어요 🎉")
            st.balloons()
        else:
            st.error("아쉬워요. 다시 한 번 볼까요?")
            # 정답 대조 표시(학습용)
            st.markdown("**정답:** " +
                        "  ".join(f"{k}({l})" for k, l in
                                  zip(correct_kor, correct_letters)))
            if user_letters:
                st.markdown("**내 답:** " + "  ".join(user_letters))
with b2:
    if st.button("➡️ 다음 문제"):
        st.session_state.q_notes = make_question(n_measures)
        st.session_state.note_answer = ""
        st.rerun()

# ==================== 하단 ====================
st.divider()
if st.button("← 메인으로 돌아가기"):
    st.switch_page("app.py")
