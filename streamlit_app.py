import streamlit as st
from pathlib import Path

st.set_page_config(
    page_title="도레미 연습",
    page_icon="🎼",
    layout="wide",
)

st.markdown(
    """
    <style>
    .hero-box {
        background: linear-gradient(135deg, #6c63ff 0%, #38bdf8 100%);
        padding: 1.8rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }
    .card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 0.9rem;
        padding: 1rem;
        height: 100%;
        color: #334155;
    }
    .card p {
        color: #334155;
        line-height: 1.6;
        margin: 0.35rem 0 0 0;
    }
    .small-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("🎵 도레미 연습")
    st.caption("악보를 보고 소리를 떠올리는 힘을 길러줘요")
    st.page_link("pages/1_계이름.py", label="📖 계이름")
    st.page_link("pages/2_리듬.py", label="🥁 리듬")
    st.page_link("pages/3_연주.py", label="🎺 연주")

st.markdown(
    """
    <div class="hero-box">
        <h1>음악이 처음이어도 괜찮아요</h1>
        <p>악보를 봐도 음이 바로 떠오르지 않아도 괜찮아요. 천천히 따라 하며 자신감을 키워봐요.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.success("오늘의 목표: 악보를 보고 음을 떠올리고, 직접 연주해 보며 맞는지 틀리는지 확인해요.")
st.write("이 앱은 악보를 읽는 것이 익숙하지 않은 중학생도 재미있게 연습할 수 있도록 만들었습니다. 작은 성공을 반복하면 음감과 독보 능력이 함께 자라나요.")

st.subheader("이 앱에서 무엇을 할 수 있나요?", divider="gray")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="card">
            <div style="font-size: 1.15rem; font-weight: 600; margin: 0.35rem 0 0.4rem 0; color: #0f172a;">도·레·미를 익혀요</div>
            <p>음의 이름과 높낮이를 연결해 보고, 악보에서 음을 떠올리는 연습을 해요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="card">
            <div class="small-title">🥁 리듬</div>
            <div style="font-size: 1.15rem; font-weight: 600; margin: 0.35rem 0 0.4rem 0; color: #0f172a;">박자를 따라가요</div>
            <p>짧게, 길게, 쉬는 박자를 익히며 리듬 감각을 키워요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="card">
            <div class="small-title">🎺 연주</div>
            <div style="font-size: 1.15rem; font-weight: 600; margin: 0.35rem 0 0.4rem 0; color: #0f172a;">직접 소리를 내요</div>
            <p>보고 듣고 따라 하며, 내 연주가 맞는지 바로 확인해요.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.subheader("오늘의 연습 루틴", divider="gray")
st.markdown("1. 먼저 계이름으로 음의 이름을 익혀요.")
st.markdown("2. 그다음 리듬으로 박자를 따라 해요.")
st.markdown("3. 마지막으로 연주 페이지에서 직접 해 보며 확인해요.")

st.caption("작은 성공이 쌓이면, 음악을 더 자신 있게 만날 수 있어요.")
