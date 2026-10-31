import re
import streamlit as st
from pipeline import run_research_pipeline

# ---------- page setup ----------
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; max-width: 1100px;}
    .hero-title {font-size: 2.4rem; font-weight: 800; margin-bottom: 0;}
    .hero-sub {font-size: 1.05rem; opacity: 0.7; margin-bottom: 1.5rem;}
    div.stButton > button {border-radius: 10px; font-weight: 600;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- session state ----------
if "result" not in st.session_state:
    st.session_state.result = None
if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""
if "topic_input" not in st.session_state:
    st.session_state.topic_input = ""


def set_topic(t: str):
    st.session_state.topic_input = t


def extract_score(feedback: str):
    m = re.search(r"Score:\s*(\d+(?:\.\d+)?)\s*/\s*10", feedback)
    return m.group(1) if m else None


# ---------- sidebar ----------
with st.sidebar:
    st.header("🧠 How it works")
    st.markdown(
        """
        **1. 🔍 Search agent**
        Finds relevant sources with Tavily.

        **2. 📄 Reader agent**
        Scrapes the best page with BeautifulSoup.

        **3. ✍️ Writer chain**
        Turns the research into a structured report.

        **4. 🧐 Critic chain**
        Scores the report and suggests improvements.
        """
    )
    st.divider()
    st.caption("Built with LangChain, Groq, Tavily and Streamlit")
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.result = None
        st.session_state.last_topic = ""
        st.rerun()

# ---------- header ----------
st.markdown('<p class="hero-title">🔬 AI Research Agent</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-sub">Enter any topic and a team of AI agents will search, read, write and review a research report for you.</p>',
    unsafe_allow_html=True,
)

# ---------- input ----------
col_input, col_btn = st.columns([5, 1], vertical_alignment="bottom")
with col_input:
    topic = st.text_input(
        "Research topic",
        key="topic_input",
        placeholder="e.g. Impact of solid state batteries on the EV industry",
    )
with col_btn:
    run = st.button("🚀 Research", type="primary", use_container_width=True)

st.caption("Try an example:")
examples = [
    "Future of quantum computing",
    "Impact of AI on Indian IT jobs",
    "Solid state batteries explained",
]
ex_cols = st.columns(len(examples))
for col, ex in zip(ex_cols, examples):
    col.button(ex, on_click=set_topic, args=(ex,), use_container_width=True)

# ---------- run pipeline ----------
if run:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        st.session_state.result = None
        with st.status("Starting the agents...", expanded=True) as status:

            def progress(step, msg):
                st.write(f"**Step {step}/4** - {msg}")
                status.update(label=f"Step {step}/4: {msg}")

            try:
                st.session_state.result = run_research_pipeline(topic.strip(), progress=progress)
                st.session_state.last_topic = topic.strip()
                status.update(label="Research complete!", state="complete", expanded=False)
            except Exception as e:
                status.update(label="Something went wrong", state="error")
                st.error(f"{type(e).__name__}: {e}")

# ---------- results ----------
result = st.session_state.result
if result:
    st.divider()
    st.subheader(f"Results for: {st.session_state.last_topic}")

    score = extract_score(result["feedback"])
    m1, m2, m3 = st.columns(3)
    m1.metric("Critic score", f"{score}/10" if score else "N/A")
    m2.metric("Report length", f"{len(result['report'].split())} words")
    m3.metric("Sources scraped", "1")

    tab_report, tab_critic, tab_search, tab_scrape = st.tabs(
        ["📝 Report", "🧐 Critic review", "🔍 Search results", "📄 Scraped content"]
    )

    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_critic:
        st.markdown(result["feedback"])

    with tab_search:
        st.markdown(result["search_results"])

    with tab_scrape:
        st.markdown(result["scraped_content"])