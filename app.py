import os
os.environ["TRANSFORMERS_VERBOSITY"] = "error"

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from rag_chain import build_chain

load_dotenv()

SAMPLE_QUESTIONS = [
    "Why is my mobile internet so slow?",
    "My calls keep dropping — what should I do?",
    "How do I activate international roaming?",
    "Why is my bill higher than usual this month?",
    "My phone shows SIM not detected after a restart",
    "How do I enable Wi-Fi calling?",
    "I was charged for roaming but had a bundle active",
    "How do I unlock my phone for another network?",
]

st.set_page_config(
    page_title="Telecom Support Chat",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(245, 197, 24, 0.06), transparent 32rem),
                #0b0b0c;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 5.5rem;
            padding-bottom: 6rem;
        }

        .stApp, .stApp p, .stApp span, .stApp label, .stApp li {
            color: #eceef0;
        }

        /* ── Sidebar ───────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: #000000;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] * {
            color: #f2f2ef;
        }

        .sb-title {
            font-weight: 800;
            font-size: 1.15rem;
            letter-spacing: -0.02em;
            margin: 0;
        }

        .sb-title span {
            color: #f5c518;
        }

        .sb-caption {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            color: #8b8f96;
            letter-spacing: 0.02em;
        }

        .sb-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.68rem;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: #f5c518;
            margin: 0 0 0.15rem;
        }

        .sb-subtext {
            font-size: 0.78rem;
            color: #8b8f96;
            margin: 0 0 0.6rem;
        }

        [data-testid="stSidebar"] .stButton > button {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.09);
            color: #eceef0;
            border-radius: 8px;
            min-height: 2.7rem;
            text-align: left;
            justify-content: flex-start;
            white-space: normal;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.78rem;
            transition: all 0.15s ease;
        }

        [data-testid="stSidebar"] .stButton > button::before {
            content: "> ";
            color: #f5c518;
        }

        [data-testid="stSidebar"] .stButton > button:hover {
            background: #f5c518;
            border-color: #f5c518;
            color: #0b0b0c;
        }

        [data-testid="stSidebar"] .stButton > button:hover::before {
            color: #0b0b0c;
        }

        [data-testid="stSidebar"] hr {
            border-color: rgba(255, 255, 255, 0.08);
        }

        /* ── Hero ──────────────────────────────────────────────── */
        .hero {
            background: #000000;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 30px 70px rgba(0, 0, 0, 0.55);
        }

        .hero-chrome {
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.65rem 1.1rem;
            background: #111214;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }

        .hero-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }

        .hero-tab {
            margin-left: 0.35rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: #9aa0a6;
            background: rgba(255, 255, 255, 0.05);
            padding: 0.28rem 0.7rem;
            border-radius: 6px;
        }

        .hero-body {
            padding: 2.5rem 2.25rem 2.75rem;
        }

        .hero-eyebrow {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.16em;
            color: #f5c518;
            margin: 0 0 0.9rem;
        }

        .hero h1 {
            font-weight: 800;
            letter-spacing: -0.03em;
            line-height: 1.02;
            font-size: clamp(2rem, 4vw, 3.15rem);
            color: #f5f5f2;
            margin: 0 0 1rem;
        }

        .hero h1 mark {
            background: black;
            color: #f5c518;
            padding: 0 0.22em;
            border-radius: 4px;
        }

        .hero p {
            max-width: 660px;
            margin: 0;
            color: #9aa0a6;
            font-size: 1.03rem;
            line-height: 1.6;
        }

        /* ── Feature strip ─────────────────────────────────────── */
        .feature-strip {
            background: linear-gradient(135deg, #f6ca2e 0%, #f2b929 100%);
            border-radius: 14px;
            padding: 1.4rem;
            margin: 1.1rem 0 1.5rem;
        }

        .metric-row {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.8rem;
        }

        .info-card {
            background: #ffffff;
            border: 1px solid rgba(0, 0, 0, 0.12);
            border-radius: 10px;
            padding: 1rem 1.05rem;
        }

        .info-card .icon {
            width: 28px;
            height: 28px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 7px;
            background: #0b0b0c;
            margin-bottom: 0.65rem;
        }

        .info-card strong {
            display: block;
            color: #111214;
            font-size: 0.94rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            letter-spacing: -0.01em;
        }

        .info-card span {
            color: #55575c;
            font-size: 0.84rem;
        }

        /* ── Chat ──────────────────────────────────────────────── */
        [data-testid="stChatMessage"] {
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background: #131417;
            box-shadow: none;
        }

        [data-testid="stChatMessage"] p,
        [data-testid="stChatMessage"] li,
        [data-testid="stChatMessage"] span {
            color: #eceef0;
        }

        [data-testid="stBottom"],
        [data-testid="stBottom"] > div,
        [data-testid="stBottomBlockContainer"],
        [data-testid="stBottomBlockContainer"] > div {
            background: transparent !important;
        }

        [data-testid="stBottomBlockContainer"] {
            padding-top: 0.5rem !important;
            padding-bottom: 1.5rem !important;
        }

        [data-testid="stChatInput"] {
            background: transparent !important;
            width: 100% !important;
            margin: 0 auto !important;
        }

        [data-testid="stChatInput"] > div {
            background: #000000 !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            border-radius: 999px !important;
            display: flex !important;
            align-items: center !important;
            overflow: hidden !important;
            padding: 0 0.3rem 0 0 !important;
        }

        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] > div *:not(button):not(button *) {
            background: #000000 !important;
            background-color: #000000 !important;
        }

        [data-testid="stChatInput"] div {
            box-shadow: none !important;
        }

        [data-testid="stChatInput"] textarea {
            background: transparent !important;
            border: none !important;
            color: #f2f2ef !important;
            padding: 0.85rem 1rem !important;
            flex: 1 !important;
            font-size: 1.3rem !important;
            min-height: 44px !important;
            resize: none !important;
            line-height: 1.4 !important;
          
        }

        [data-testid="stChatInput"] textarea:focus {
            box-shadow: none !important;
        }

        [data-testid="stChatInput"] > div:focus-within {
            border-color: #f5c518 !important;
            box-shadow: 0 0 0 1px #f5c518 !important;
        }

        [data-testid="stChatInput"] button {
            background: #f5c518;
            border-radius: 50% !important;
            width: 30px !important;
            height: 30px !important;
            min-width: 28px !important;
            min-height: 28px !important;
            flex-shrink: 0 !important;
            margin-right: 0.3rem !important;
        }

        [data-testid="stChatInput"] button svg {
            fill: #0b0b0c !important;
            width: 28px !important;
            height: 28px !important;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-top: 1rem;
            }

            .hero-body {
                padding: 1.5rem 1.35rem 1.85rem;
            }

            .metric-row {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource
def get_chain():
    return build_chain()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sb-title">Telecom <span>Support</span></p>', unsafe_allow_html=True)
    st.markdown('<p class="sb-caption">RAG assistant · powered by Groq</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown('<p class="sb-eyebrow">Ask your AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sb-subtext">Send a common support question.</p>', unsafe_allow_html=True)
    for q in SAMPLE_QUESTIONS:
        if st.button(q, use_container_width=True):
            st.session_state.pending_question = q

    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []

# Click-outside-to-close: clicking anywhere in the main content area
# collapses the sidebar by triggering Streamlit's own collapse button.
# The native collapse arrow keeps working as-is. Falls back through a
# few selector variants since Streamlit's internal test-ids differ
# across versions.
components.html(
    """
    <script>
    (function() {
        const doc = window.parent.document;

        function findMain() {
            return (
                doc.querySelector('[data-testid="stMain"]') ||
                doc.querySelector('[data-testid="stAppViewContainer"] section.main') ||
                doc.querySelector('section.main')
            );
        }

        function findSidebar() {
            return doc.querySelector('[data-testid="stSidebar"]');
        }

        function findCollapseButton() {
            const selectors = [
                '[data-testid="stSidebarCollapseButton"] button',
                '[data-testid="stSidebarCollapseButton"]',
                '[data-testid="stSidebarHeader"] button',
                '[data-testid="stSidebar"] button[kind="headerNoPadding"]',
                '[data-testid="stSidebar"] button[aria-label*="close" i]',
                '[data-testid="stSidebar"] button[aria-label*="collapse" i]'
            ];
            for (const sel of selectors) {
                const el = doc.querySelector(sel);
                if (el) return el;
            }
            return null;
        }

        function attach() {
            const mainContent = findMain();
            const sidebar = findSidebar();
            if (!mainContent || !sidebar) return;
            if (mainContent.dataset.outsideCloseAttached) return;
            mainContent.dataset.outsideCloseAttached = "true";

            mainContent.addEventListener('click', function(e) {
                const sb = findSidebar();
                if (!sb) return;
                const isVisible = sb.offsetWidth > 0 && sb.offsetHeight > 0;
                if (!isVisible) return;

                const collapseBtn = findCollapseButton();
                if (collapseBtn) {
                    collapseBtn.click();
                }
            });
        }

        attach();
        const observer = new MutationObserver(attach);
        observer.observe(doc.body, { childList: true, subtree: true });
    })();
    </script>
    """,
    height=0,
)

# ── Main ─────────────────────────────────────────────────────────────────
st.markdown(
    """
    <section class="hero">
        <div class="hero-chrome">
            <span class="hero-dot" style="background:#ff5f57;"></span>
            <span class="hero-dot" style="background:#febc2e;"></span>
            <span class="hero-dot" style="background:#28c840;"></span>
            <span class="hero-tab">telecom-support · ai care</span>
        </div>
        <div class="hero-body">
            <p class="hero-eyebrow">Telecom Support / RAG Assistant</p>
            <h1>Customer Care <mark>Assistant</mark></h1>
            <p>Get grounded answers for mobile data, billing, SIM issues, roaming, Wi-Fi calling, and device support using your telecom knowledge base.</p>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="feature-strip">
        <div class="metric-row">
            <div class="info-card">
                <div class="icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f5c518" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <ellipse cx="12" cy="5" rx="8" ry="3"></ellipse>
                        <path d="M4 5v6c0 1.66 3.58 3 8 3s8-1.34 8-3V5"></path>
                        <path d="M4 11v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6"></path>
                    </svg>
                </div>
                <strong>Knowledge sources</strong>
                <span>FAQ, resolved tickets, and PDF guide</span>
            </div>
            <div class="info-card">
                <div class="icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f5c518" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                    </svg>
                </div>
                <strong>Answer style</strong>
                <span>Support-focused and context-aware</span>
            </div>
            <div class="info-card">
                <div class="icon">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#f5c518" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                </div>
                <strong>Best for</strong>
                <span>Connectivity, billing, SIM, and roaming</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# Resolve question from chat input or sidebar button click
question = st.chat_input("Describe your issue…")
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        chain = get_chain()
        response = st.write_stream(chain.stream(question))

    st.session_state.messages.append({"role": "assistant", "content": response})