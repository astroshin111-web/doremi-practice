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
    div.stButton > button {
        width: 100%;
        min-height: 140px;
        text-align: left;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        border-radius: 0.9rem;
        background: #f8fafc;
        color: #0f172a;
        white-space: normal;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.empty()

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
    if st.button(
        "📖 계이름\n\n도·레·미를 익혀요\n음의 이름과 높낮이를 연결해 보고, 악보에서 음을 떠올리는 연습을 해요.",
        use_container_width=True,
    ):
        st.switch_page("pages/1_계이름.py")

with col2:
    if st.button(
        "🥁 리듬\n\n박자를 따라가요\n짧게, 길게, 쉬는 박자를 익히며 리듬 감각을 키워요.",
        use_container_width=True,
    ):
        st.switch_page("pages/2_리듬.py")

with col3:
    if st.button(
        "🎺 연주\n\n직접 소리를 내요\n보고 듣고 따라 하며, 내 연주가 맞는지 바로 확인해요.",
        use_container_width=True,
    ):
        st.switch_page("pages/3_연주.py")

st.subheader("오늘의 연습 루틴", divider="gray")
st.markdown("1. 먼저 계이름으로 음의 이름을 익혀요.")
st.markdown("2. 그다음 리듬으로 박자를 따라 해요.")
st.markdown("3. 마지막으로 연주 페이지에서 직접 해 보며 확인해요.")

st.caption("작은 성공이 쌓이면, 음악을 더 자신 있게 만날 수 있어요.")
# score_renderer.py
import matplotlib; matplotlib.use("Agg")
import numpy as np, matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Circle

# ================= 공용 데이터 모델 =================
STEP = {"C":0,"D":1,"E":2,"F":3,"G":4,"A":5,"B":6}
DUR_BEATS = {"whole":4.0,"half":2.0,"quarter":1.0,"eighth":0.5,"sixteenth":0.25}
FLAGS = {"eighth":1,"sixteenth":2}
CLEF_REF = {"treble":30, "bass":18}   # 오선 맨 아랫줄 diatonic step (E4 / G2)

def note_to_y(pitch, clef):
    """계이름 -> 오선 y좌표. 선 간격=0.5, 한 계이름=0.25"""
    n = int(pitch[-1])*7 + STEP[pitch[0]]
    return (n - CLEF_REF[clef]) * 0.25

# ================= 박자 기반 마디 분할 =================
def split_measures(notes, beats_per_measure):
    """음길이 값을 누적해 마디로 나눈다."""
    measures=[[]]; acc=0.0
    for nt in notes:
        b = DUR_BEATS[nt["duration"]]
        if acc + b > beats_per_measure + 1e-9:   # 넘치면 새 마디
            measures.append([]); acc=0.0
        measures[-1].append(nt); acc += b
        if abs(acc - beats_per_measure) < 1e-9:  # 딱 채우면 마디 마감
            measures.append([]); acc=0.0
    if measures and not measures[-1]: measures.pop()
    return measures

# ================= 자리표 (벡터 작도) =================
def _bez(pts,n=48):
    pts=np.array(pts,float); t=np.linspace(0,1,n)[:,None]; p0,p1,p2,p3=pts
    return ((1-t)**3)*p0+3*((1-t)**2)*t*p1+3*(1-t)*t**2*p2+t**3*p3

def draw_treble(ax,cx,u=0.5):
    gy=1*u; s=u/0.5; P=lambda x,y:[cx+x*s,gy+y*s]
    curve=np.vstack([_bez([P(0.5,3.5),P(0.15,4.1),P(-0.55,3.7),P(-0.4,3.0)]),
        _bez([P(-0.4,3.0),P(-0.3,2.5),P(0.55,2.4),P(0.6,1.7)]),
        _bez([P(0.6,1.7),P(0.65,0.9),P(-0.95,0.95),P(-0.9,0.05)]),
        _bez([P(-0.9,0.05),P(-0.85,-0.7),P(0.35,-0.75),P(0.35,0.05)]),
        _bez([P(0.35,0.05),P(0.35,0.6),P(-0.35,0.65),P(-0.3,0.15)]),
        _bez([P(-0.3,0.15),P(-0.27,-0.15),P(0.1,-0.1),P(0.1,0.1)])])
    stem=[P(0.5,3.5),P(0.5,-2.4)]
    tail=_bez([P(0.5,-2.4),P(0.5,-2.9),P(-0.35,-2.85),P(-0.3,-2.25)])
    ax.plot(curve[:,0],curve[:,1],'k',lw=2.2,solid_capstyle='round')
    ax.plot([stem[0][0],stem[1][0]],[stem[0][1],stem[1][1]],'k',lw=2.2)
    ax.plot(tail[:,0],tail[:,1],'k',lw=2.2,solid_capstyle='round')
    ax.add_patch(Circle(P(-0.3,-2.05),0.13*s,color='k'))

def draw_bass(ax,cx,u=0.5):
    fy=3*u; s=u/0.5; P=lambda x,y:[cx+x*s,fy+y*s]
    body=np.vstack([_bez([P(-0.5,0.9),P(0.6,1.25),P(1.2,0.6),P(1.15,-0.1)]),
                    _bez([P(1.15,-0.1),P(1.1,-1.1),P(0.2,-1.7),P(-0.7,-1.75)])])
    head=_bez([P(-0.5,0.9),P(-1.0,0.8),P(-1.05,0.15),P(-0.55,0.05)])
    ax.plot(body[:,0],body[:,1],'k',lw=2.4,solid_capstyle='round')
    ax.plot(head[:,0],head[:,1],'k',lw=2.4,solid_capstyle='round')
    for d in [P(1.55,0.5),P(1.55,-0.5)]: ax.add_patch(Circle(d,0.12*s,color='k'))

# ================= 음표 =================
def draw_note(ax,x,pitch,duration,clef,u=0.5):
    r=u/0.5; y=note_to_y(pitch,clef)*r; top=4*u; step=u
    filled=duration in("quarter","eighth","sixteenth"); has_stem=duration!="whole"
    yy=-step                                   # 아래 덧줄
    while yy>=y-1e-6:
        ax.add_line(Line2D([x-0.28,x+0.28],[yy,yy],color='k',lw=1.2)); yy-=step
    yy=top+step                                # 위 덧줄
    while yy<=y+1e-6:
        ax.add_line(Line2D([x-0.28,x+0.28],[yy,yy],color='k',lw=1.2)); yy+=step
    ax.add_patch(Ellipse((x,y),0.34*r,0.26*r,angle=-20,
                 facecolor='k' if filled else 'white',edgecolor='k',lw=1.5,zorder=3))
    if has_stem:
        up=y<2*u; sx=x+0.16*r if up else x-0.16*r
        sy2=y+1.6*u if up else y-1.6*u
        ax.add_line(Line2D([sx,sx],[y,sy2],color='k',lw=1.5,zorder=2))
        for i in range(FLAGS.get(duration,0)):
            fy=sy2-i*0.3*r
            ax.plot([sx,sx+0.3*r],[fy,fy-0.4*r] if up else [fy,fy+0.4*r],'k',lw=1.5)

# ================= 전체 악보 렌더링 =================
def render_score(notes, clef="treble", time_sig=(4,4), title=""):
    bpm = time_sig[0]*(4/time_sig[1])          # 한 마디 박자수(4분음표 환산)
    measures = split_measures(notes, bpm)
    u=0.5; x0=0.3; clef_w=1.6; ts_w=0.9; note_gap=0.85; pad=0.5
    x=x0+clef_w+ts_w; positions=[]; barlines=[]
    for m in measures:
        for nt in m: positions.append((x,nt)); x+=note_gap
        x+=pad; barlines.append(x-pad*0.5)
    total_w=x+0.3; top=4*u
    fig,ax=plt.subplots(figsize=(min(16,total_w*0.9),2.4))
    for i in range(5): ax.add_line(Line2D([x0,total_w-0.2],[i*u,i*u],color='k',lw=1.1))
    ax.add_line(Line2D([x0,x0],[0,top],color='k',lw=1.4))          # 시작선
    (draw_treble if clef=="treble" else draw_bass)(ax,x0+0.7,u)    # 자리표
    tsx=x0+clef_w+0.3                                              # 박자표
    ax.text(tsx,top*0.75,str(time_sig[0]),ha='center',va='center',fontsize=20,fontweight='bold')
    ax.text(tsx,top*0.25,str(time_sig[1]),ha='center',va='center',fontsize=20,fontweight='bold')
    for xx,nt in positions: draw_note(ax,xx,nt["pitch"],nt["duration"],clef,u)
    for i,bx in enumerate(barlines):                              # 마디선
        if i==len(barlines)-1:                                    # 종료선(굵게)
            ax.add_line(Line2D([bx-0.05,bx-0.05],[0,top],color='k',lw=1.2))
            ax.add_line(Line2D([bx+0.02,bx+0.02],[0,top],color='k',lw=3.2))
        else:
            ax.add_line(Line2D([bx,bx],[0,top],color='k',lw=1.3))
    ax.set_xlim(0,total_w); ax.set_ylim(-2.2,4.2); ax.set_aspect('equal'); ax.axis('off')
    if title: ax.set_title(title,fontsize=12)
    plt.tight_layout(); return fig, measures
