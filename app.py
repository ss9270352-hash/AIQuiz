"""
app.py - QuizMaster AI Web Application.

A calm, focused, human-designed study space built with Streamlit.
Converts lecture notes into interactive multiple-choice quizzes, checks answers,
explains mistakes, and provides targeted practice rounds.
"""

import os
import streamlit as st
from typing import Optional

from quiz_logic import (
    Question,
    QuizSession,
    SessionProgressTracker
)
from sample_data import get_sample_quiz, SAMPLE_LECTURE_NOTES
from quiz_generator import (
    generate_quiz_from_notes,
    is_api_configured,
    get_api_credentials,
    AIProviderError
)
from document_parser import extract_text_from_upload, DocumentParserError

# -----------------------------------------------------------------------------
# 1. Page Configuration & Custom CSS (Editorial & Understated Design)
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="QuizMaster AI — Calm Study Space",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
/* Import Clean Serif & Sans Fonts */
@import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

:root {
    --bg-page: #F8F7F3;
    --text-primary: #242522;
    --text-secondary: #5C5D58;
    --text-muted: #82817B;
    --surface-card: #FFFFFF;
    --surface-tint: #FDFCFA;
    --border-subtle: #E3E1D9;
    --border-hover: #C5C2B7;
    --accent-forest: #356B52;
    --accent-forest-hover: #295340;
    --accent-forest-soft: #EBF3EE;
    --accent-terracotta: #A83838;
    --accent-terracotta-soft: #FAF0F0;
    --accent-gold-soft: #F9F6ED;
    --radius-sm: 6px;
    --radius-md: 9px;
    --radius-lg: 12px;
}

/* Background & Body Resets */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-page) !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Center Column Container constraint */
.block-container {
    max-width: 740px !important;
    padding-top: 2rem !important;
    padding-bottom: 4rem !important;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* Hide default streamlit header bar decorations */
header[data-testid="stHeader"] {
    background: transparent !important;
}
#MainMenu, footer {
    visibility: hidden;
}

/* Top App Bar Header */
.qm-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 1.25rem;
    margin-bottom: 1.75rem;
    border-bottom: 1px solid var(--border-subtle);
}
.qm-brand {
    display: flex;
    align-items: center;
    gap: 0.65rem;
    text-decoration: none;
    color: var(--text-primary);
}
.qm-logo-icon {
    width: 26px;
    height: 26px;
    color: var(--accent-forest);
}
.qm-brand-title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.35rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--text-primary);
    line-height: 1;
}
.qm-brand-subtitle {
    font-size: 0.72rem;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-left: 0.15rem;
}
.qm-nav-status {
    font-size: 0.78rem;
    color: var(--text-secondary);
    background: #EFECE4;
    padding: 0.28rem 0.65rem;
    border-radius: 999px;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}

/* Editorial Headings */
h1, .qm-heading-1 {
    font-family: 'Newsreader', Georgia, serif !important;
    font-weight: 500 !important;
    font-size: 2.15rem !important;
    line-height: 1.2 !important;
    letter-spacing: -0.02em !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.4rem !important;
}
h2, .qm-heading-2 {
    font-family: 'Newsreader', Georgia, serif !important;
    font-weight: 500 !important;
    font-size: 1.6rem !important;
    line-height: 1.25 !important;
    letter-spacing: -0.015em !important;
    color: var(--text-primary) !important;
    margin-top: 1.25rem !important;
    margin-bottom: 0.5rem !important;
}
p.qm-lead {
    font-size: 1.02rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 1.5rem;
}

/* Nav Pills Bar */
.qm-tabs-bar {
    display: flex;
    gap: 0.35rem;
    background: #ECE9DF;
    padding: 0.25rem;
    border-radius: var(--radius-md);
    margin-bottom: 1.75rem;
}

/* Cards & Surfaces */
.qm-card {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.4rem 1.5rem;
    margin-bottom: 1.25rem;
}

/* Question Prompt Display */
.qm-question-box {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 1.75rem 1.65rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}
.qm-topic-badge {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent-forest);
    background: var(--accent-forest-soft);
    padding: 0.2rem 0.55rem;
    border-radius: 4px;
    margin-bottom: 0.75rem;
}
.qm-question-text {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 1.45rem;
    line-height: 1.38;
    color: var(--text-primary);
    font-weight: 500;
}

/* Feedback Callout Boxes */
.qm-feedback-correct {
    background: var(--accent-forest-soft);
    border-left: 3px solid var(--accent-forest);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 1.15rem 1.35rem;
    margin: 1.25rem 0;
}
.qm-feedback-incorrect {
    background: var(--accent-terracotta-soft);
    border-left: 3px solid var(--accent-terracotta);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 1.15rem 1.35rem;
    margin: 1.25rem 0;
}
.qm-feedback-title {
    font-weight: 700;
    font-size: 0.95rem;
    margin-bottom: 0.35rem;
}
.qm-feedback-correct .qm-feedback-title {
    color: var(--accent-forest);
}
.qm-feedback-incorrect .qm-feedback-title {
    color: var(--accent-terracotta);
}
.qm-feedback-explanation {
    font-size: 0.92rem;
    line-height: 1.5;
    color: var(--text-primary);
}
.qm-feedback-reference {
    font-size: 0.82rem;
    color: var(--text-secondary);
    font-style: italic;
    margin-top: 0.5rem;
}

/* Primary Button Styling */
div.stButton > button {
    border-radius: var(--radius-sm) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.25rem !important;
    transition: all 0.15s ease-in-out !important;
    border: 1px solid var(--border-subtle) !important;
    background-color: var(--surface-card) !important;
    color: var(--text-primary) !important;
}
div.stButton > button:hover {
    border-color: var(--border-hover) !important;
    background-color: #F3F1EC !important;
    color: var(--text-primary) !important;
}
div.stButton > button[kind="primary"] {
    background-color: var(--accent-forest) !important;
    border-color: var(--accent-forest) !important;
    color: #FFFFFF !important;
}
div.stButton > button[kind="primary"]:hover {
    background-color: var(--accent-forest-hover) !important;
    border-color: var(--accent-forest-hover) !important;
    color: #FFFFFF !important;
}

/* Radio Choice Card Customization */
div[data-testid="stRadio"] > div {
    gap: 0.65rem !important;
}
div[data-testid="stRadio"] label {
    background: var(--surface-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.85rem 1.1rem !important;
    transition: all 0.12s ease !important;
    cursor: pointer !important;
}
div[data-testid="stRadio"] label:hover {
    border-color: var(--border-hover) !important;
    background-color: #FCFBF9 !important;
}

/* Streamlit Inputs */
.stTextArea textarea {
    background-color: var(--surface-card) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 0.92rem !important;
    color: var(--text-primary) !important;
    line-height: 1.55 !important;
}
.stTextArea textarea:focus {
    border-color: var(--accent-forest) !important;
    box-shadow: 0 0 0 1px var(--accent-forest) !important;
}

/* Streamlit Progress Bar */
.stProgress > div > div > div > div {
    background-color: var(--accent-forest) !important;
}
.stProgress > div > div > div {
    background-color: #E2E0D8 !important;
    height: 5px !important;
    border-radius: 999px !important;
}

/* Score Summary Card */
.qm-score-hero {
    text-align: center;
    padding: 2.25rem 1.5rem;
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    margin-bottom: 1.75rem;
}
.qm-score-big {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 3.5rem;
    font-weight: 500;
    line-height: 1;
    color: var(--accent-forest);
    margin-bottom: 0.4rem;
}
.qm-score-caption {
    font-size: 0.98rem;
    color: var(--text-secondary);
    max-width: 440px;
    margin: 0 auto;
    line-height: 1.45;
}

/* Stat Grid */
.qm-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}
.qm-stat-box {
    background: var(--surface-card);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 1rem 0.75rem;
    text-align: center;
}
.qm-stat-num {
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.1;
}
.qm-stat-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 0.25rem;
}

/* Topic Breakdown Pill */
.qm-topic-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.65rem 0.9rem;
    border-bottom: 1px solid #ECEAE2;
    font-size: 0.88rem;
}
.qm-topic-row:last-child {
    border-bottom: none;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# 2. Session State Initialization
# -----------------------------------------------------------------------------

if "quiz_session" not in st.session_state:
    st.session_state.quiz_session: Optional[QuizSession] = None

if "progress_tracker" not in st.session_state:
    st.session_state.progress_tracker = SessionProgressTracker()

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "study"

if "notes_input" not in st.session_state:
    st.session_state.notes_input = ""

if "confirm_exit" not in st.session_state:
    st.session_state.confirm_exit = False

if "last_error" not in st.session_state:
    st.session_state.last_error = None

if "last_warning" not in st.session_state:
    st.session_state.last_warning = None

if "selected_option" not in st.session_state:
    st.session_state.selected_option = None

if "last_upload_key" not in st.session_state:
    st.session_state.last_upload_key = None

if "upload_feedback" not in st.session_state:
    st.session_state.upload_feedback = None


# -----------------------------------------------------------------------------
# 3. Top Navigation Header
# -----------------------------------------------------------------------------

api_ready = is_api_configured()
_, api_provider, _ = get_api_credentials()
status_text = f"AI Connected ({api_provider})" if api_ready else "Sample Mode (Offline Ready)"

st.markdown(
    f"""
    <div class="qm-header">
        <div class="qm-brand">
            <svg class="qm-logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
                <line x1="9" y1="7" x2="15" y2="7"></line>
                <line x1="9" y1="11" x2="13" y2="11"></line>
            </svg>
            <div>
                <span class="qm-brand-title">QuizMaster</span>
                <span class="qm-brand-subtitle">AI Study Space</span>
            </div>
        </div>
        <div class="qm-nav-status">
            <span>●</span>
            <span>{status_text}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Navigation Bar Tabs
nav_cols = st.columns(4)
nav_labels = [
    ("study", "1. Study Notes"),
    ("quiz", "2. Active Quiz"),
    ("results", "3. Results & Practice"),
    ("progress", "4. Progress")
]

for idx, (tab_id, label) in enumerate(nav_labels):
    is_active = (st.session_state.active_nav == tab_id)
    btn_type = "primary" if is_active else "secondary"
    
    # Disable quiz / results tabs if no active session exists
    disabled = False
    if tab_id in ("quiz", "results") and st.session_state.quiz_session is None:
        disabled = True

    if nav_cols[idx].button(label, key=f"nav_btn_{tab_id}", use_container_width=True, type=btn_type, disabled=disabled):
        # If currently in the middle of an uncompleted quiz and leaving, prompt confirm
        current_sess = st.session_state.quiz_session
        if st.session_state.active_nav == "quiz" and current_sess and not current_sess.is_finished and tab_id != "quiz":
            st.session_state.confirm_exit = True
        else:
            st.session_state.active_nav = tab_id
            st.rerun()


# -----------------------------------------------------------------------------
# 4. Workspace View: Study & Create
# -----------------------------------------------------------------------------

if st.session_state.active_nav == "study":
    st.markdown('<h1 class="qm-heading-1">Make your notes work harder.</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="qm-lead">Paste lecture notes, study summaries, or upload a .txt, .pdf, or .pptx file. '
        'QuizMaster will extract key concepts and build an interactive quiz to test your memory.</p>',
        unsafe_allow_html=True
    )

    if st.session_state.last_error:
        st.error(st.session_state.last_error)
        st.session_state.last_error = None

    if st.session_state.last_warning:
        st.warning(st.session_state.last_warning)
        st.session_state.last_warning = None

    # Input method: Paste or Upload
    tab_paste, tab_upload = st.tabs(["Paste Notes", "Upload File (.txt, .pdf, .pptx)"])

    with tab_paste:
        notes_input = st.text_area(
            "Lecture Notes",
            value=st.session_state.notes_input,
            placeholder="Paste your lecture notes, textbook excerpts, or revision summaries here...\nMinimum 50 characters for meaningful question generation.",
            height=200,
            label_visibility="collapsed"
        )
        st.session_state.notes_input = notes_input

        # Character and word count feedback
        char_count = len(notes_input.strip())
        word_count = len(notes_input.strip().split()) if char_count > 0 else 0
        st.caption(f"{char_count:,} characters · {word_count:,} words")

    with tab_upload:
        uploaded_file = st.file_uploader(
            "Upload lecture notes or slides (.txt, .pdf, .pptx)",
            type=["txt", "pdf", "pptx"],
            help="Text files are read directly. PDFs are extracted page by page and "
                 "PowerPoint decks slide by slide, including tables and speaker notes. "
                 "Scanned / image-only PDFs have no text to extract."
        )
        if uploaded_file is not None:
            # Parse each distinct file only once; Streamlit reruns this block
            # on every interaction while the file stays uploaded.
            upload_key = getattr(uploaded_file, "file_id", None) or f"{uploaded_file.name}:{uploaded_file.size}"
            if st.session_state.last_upload_key != upload_key:
                st.session_state.last_upload_key = upload_key
                try:
                    parsed = extract_text_from_upload(uploaded_file.getvalue(), uploaded_file.name)
                    st.session_state.notes_input = parsed.text
                    unit_plural = "s" if parsed.unit_count != 1 else ""
                    st.session_state.upload_feedback = (
                        "success",
                        f"Loaded '{parsed.file_name}' — extracted {parsed.char_count:,} characters "
                        f"from {parsed.unit_count} {parsed.unit_label}{unit_plural}. "
                        "Switch to the Paste Notes tab to review or trim the text before creating your quiz."
                    )
                except DocumentParserError as e:
                    st.session_state.upload_feedback = ("error", str(e))
                except Exception as e:
                    st.session_state.upload_feedback = ("error", f"Could not read uploaded file: {e}")

            if st.session_state.upload_feedback:
                feedback_kind, feedback_msg = st.session_state.upload_feedback
                if feedback_kind == "success":
                    st.success(feedback_msg)
                else:
                    st.error(feedback_msg)

    # Compact Configuration Row
    st.markdown('<h2 class="qm-heading-2">Quiz Settings</h2>', unsafe_allow_html=True)
    cfg_col1, cfg_col2, cfg_col3 = st.columns([1, 1, 1])

    with cfg_col1:
        question_count = st.selectbox(
            "Questions",
            options=[5, 10, 15],
            index=0,
            help="Number of multiple-choice questions to generate."
        )

    with cfg_col2:
        difficulty = st.selectbox(
            "Difficulty",
            options=["Medium", "Easy", "Hard"],
            index=0,
            help="Target difficulty for question formulation."
        )

    with cfg_col3:
        st.selectbox(
            "Format",
            options=["Multiple Choice (4 options)"],
            index=0,
            disabled=True,
            help="Single-answer multiple choice format."
        )

    st.write("") # spacing

    # Action Row
    act_col1, act_col2 = st.columns([1.4, 1])

    with act_col1:
        create_btn = st.button("Create My Quiz", type="primary", use_container_width=True)

    with act_col2:
        sample_btn = st.button("Try Sample Quiz (Offline)", use_container_width=True)

    # Secondary shortcut: Load sample notes into textarea
    st.write("")
    if st.button("Load sample lecture notes into text area", use_container_width=False):
        st.session_state.notes_input = SAMPLE_LECTURE_NOTES
        st.rerun()

    # Handler: Create My Quiz
    if create_btn:
        notes_text = st.session_state.notes_input.strip()
        if not notes_text:
            st.error("Please paste lecture notes or upload a .txt, .pdf, or .pptx file before creating a quiz.")
        elif len(notes_text) < 50:
            st.error("Your notes are too short (minimum 50 characters). Please provide more material so meaningful questions can be created.")
        elif len(notes_text) > 30000:
            st.error("Your notes exceed 30,000 characters. Please shorten or select a specific lecture chapter.")
        elif not is_api_configured():
            st.error(
                "No AI API key is configured. To generate quizzes from custom notes, set GEMINI_API_KEY "
                "or OPENAI_API_KEY in a .env file. Alternatively, click 'Try Sample Quiz (Offline)' to test "
                "the complete experience right now."
            )
        else:
            with st.spinner("Analyzing lecture notes and crafting questions..."):
                try:
                    questions, warning_msg = generate_quiz_from_notes(
                        notes=notes_text,
                        count=question_count,
                        difficulty=difficulty
                    )
                    st.session_state.quiz_session = QuizSession(
                        quiz_id=f"ai_quiz_{os.urandom(4).hex()}",
                        title="Lecture Notes Quiz",
                        questions=questions
                    )
                    st.session_state.last_warning = warning_msg
                    st.session_state.active_nav = "quiz"
                    st.session_state.selected_option = None
                    st.rerun()
                except AIProviderError as e:
                    st.session_state.last_error = str(e)
                    st.rerun()
                except Exception as e:
                    st.session_state.last_error = f"An unexpected error occurred during quiz generation: {e}"
                    st.rerun()

    # Handler: Try Sample Quiz
    if sample_btn:
        sample_questions = get_sample_quiz(count=question_count, difficulty=difficulty)
        st.session_state.quiz_session = QuizSession(
            quiz_id=f"sample_{os.urandom(4).hex()}",
            title="Sample Quiz (Computer Science Fundamentals)",
            questions=sample_questions
        )
        st.session_state.active_nav = "quiz"
        st.session_state.selected_option = None
        st.rerun()

    # Editorial Privacy Footnote
    st.markdown(
        """
        <div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle); font-size: 0.8rem; color: var(--text-muted); line-height: 1.5;">
            <strong>Privacy & Data Handling:</strong> Your lecture notes are processed in memory and sent only to your configured AI provider when generating questions. Notes are not stored on any permanent server or database.
        </div>
        """,
        unsafe_allow_html=True
    )


# -----------------------------------------------------------------------------
# 5. Workspace View: Active Quiz
# -----------------------------------------------------------------------------

elif st.session_state.active_nav == "quiz":
    session: Optional[QuizSession] = st.session_state.quiz_session

    if session is None or session.is_empty:
        st.info("No active quiz found. Please create or start a quiz from the Study screen.")
        if st.button("Go to Study Workspace", type="primary"):
            st.session_state.active_nav = "study"
            st.rerun()
    elif session.is_finished:
        st.session_state.active_nav = "results"
        st.rerun()
    else:
        q: Question = session.current_question
        q_idx = session.current_index
        total_q = session.total_questions

        # Exit confirmation prompt if student clicked Leave
        if st.session_state.confirm_exit:
            st.warning("Are you sure you want to exit? Your progress in this quiz round will be lost.")
            exit_col1, exit_col2 = st.columns([1, 1])
            with exit_col1:
                if st.button("Yes, Exit Quiz", type="secondary", use_container_width=True):
                    st.session_state.quiz_session = None
                    st.session_state.confirm_exit = False
                    st.session_state.active_nav = "study"
                    st.rerun()
            with exit_col2:
                if st.button("Keep Practising", type="primary", use_container_width=True):
                    st.session_state.confirm_exit = False
                    st.rerun()
            st.write("")

        # Slim Progress Bar & Header Meta
        progress_val = (q_idx) / total_q
        st.progress(progress_val)

        meta_col1, meta_col2 = st.columns([2, 1])
        with meta_col1:
            quiz_type_tag = "Practice Mistakes Round" if session.is_retry_round else "Active Quiz"
            st.caption(f"{quiz_type_tag} · Question {q_idx + 1} of {total_q}")
        with meta_col2:
            if st.button("Exit Quiz", key="exit_quiz_btn"):
                st.session_state.confirm_exit = True
                st.rerun()

        # Question Prompt Box
        st.markdown(
            f"""
            <div class="qm-question-box">
                <div class="qm-topic-badge">{q.topic}</div>
                <div class="qm-question-text">{q.prompt}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        is_already_submitted = session.is_submitted.get(q.id, False)

        # Options formatting
        option_keys = ["A", "B", "C", "D"]
        option_labels = [f"{k}.  {q.options.get(k, '')}" for k in option_keys]

        # Determine currently selected or previously answered index
        current_choice = session.user_answers.get(q.id)
        default_index = option_keys.index(current_choice) if current_choice in option_keys else None

        # Display Options
        selected_label = st.radio(
            "Select the best answer:",
            options=option_labels,
            index=default_index,
            disabled=is_already_submitted,
            key=f"radio_q_{q.id}",
            label_visibility="collapsed"
        )

        # Check Answer or Next Question Actions
        st.write("")
        if not is_already_submitted:
            if st.button("Check Answer", type="primary", use_container_width=True):
                if selected_label is None:
                    st.error("Please select an answer option before checking.")
                else:
                    selected_key = selected_label.split(".")[0].strip()
                    session.submit_answer(q.id, selected_key)
                    st.rerun()
        else:
            # Show Feedback Callout
            was_correct = session.is_correct.get(q.id, False)
            chosen_key = session.user_answers.get(q.id, "")
            chosen_text = q.options.get(chosen_key, "")
            correct_key = q.correct_option
            correct_text = q.options.get(correct_key, "")

            if was_correct:
                st.markdown(
                    f"""
                    <div class="qm-feedback-correct">
                        <div class="qm-feedback-title">✓ Correct</div>
                        <div class="qm-feedback-explanation">{q.explanation}</div>
                        {f'<div class="qm-feedback-reference">Source reference: {q.source_reference}</div>' if q.source_reference else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div class="qm-feedback-incorrect">
                        <div class="qm-feedback-title">✕ Incorrect</div>
                        <div class="qm-feedback-explanation">
                            You chose <strong>({chosen_key}) {chosen_text}</strong>.<br>
                            The correct answer is <strong>({correct_key}) {correct_text}</strong>.<br><br>
                            {q.explanation}
                        </div>
                        {f'<div class="qm-feedback-reference">Source reference: {q.source_reference}</div>' if q.source_reference else ''}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # Advance to next question or view results
            is_last_question = (q_idx + 1 >= total_q)
            next_label = "View Quiz Results" if is_last_question else "Next Question →"

            if st.button(next_label, type="primary", use_container_width=True):
                session.next_question()
                if session.is_finished:
                    # Record in progress tracker if not already recorded
                    st.session_state.progress_tracker.record_completed_quiz(session)
                    st.session_state.active_nav = "results"
                st.rerun()


# -----------------------------------------------------------------------------
# 6. Workspace View: Results & Practice Mistakes
# -----------------------------------------------------------------------------

elif st.session_state.active_nav == "results":
    session: Optional[QuizSession] = st.session_state.quiz_session

    if session is None or session.is_empty:
        st.info("No completed quiz results found. Create a quiz to get started.")
        if st.button("Start New Quiz", type="primary"):
            st.session_state.active_nav = "study"
            st.rerun()
    else:
        score = session.score
        total = session.total_questions
        accuracy = session.accuracy_percentage
        incorrect = session.incorrect_count

        # Performance summary message
        if accuracy == 100.0:
            summary_msg = "Outstanding mastery. You answered every question correctly on the first attempt."
        elif accuracy >= 80.0:
            summary_msg = "Strong grasp of the material. Review the couple of questions you missed to reinforce your memory."
        elif accuracy >= 60.0:
            summary_msg = "Good foundation, with a few weak areas that would benefit from targeted practice."
        else:
            summary_msg = "Several core concepts need revision. Practise your mistakes below to solidify understanding."

        # Hero Score Box
        st.markdown(
            f"""
            <div class="qm-score-hero">
                <div class="qm-score-big">{score} / {total}</div>
                <div style="font-weight: 600; font-size: 1.15rem; color: var(--text-primary); margin-bottom: 0.35rem;">
                    {accuracy}% Score
                </div>
                <div class="qm-score-caption">{summary_msg}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Performance Stats Grid
        st.markdown(
            f"""
            <div class="qm-stat-grid">
                <div class="qm-stat-box">
                    <div class="qm-stat-num" style="color: var(--accent-forest);">{score}</div>
                    <div class="qm-stat-label">Correct</div>
                </div>
                <div class="qm-stat-box">
                    <div class="qm-stat-num" style="color: { 'var(--accent-terracotta)' if incorrect > 0 else 'var(--text-muted)' };">{incorrect}</div>
                    <div class="qm-stat-label">To Practise</div>
                </div>
                <div class="qm-stat-box">
                    <div class="qm-stat-num">{total}</div>
                    <div class="qm-stat-label">Total Questions</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Topic Breakdown
        topic_breakdown = session.get_topic_breakdown()
        if topic_breakdown:
            st.markdown('<h2 class="qm-heading-2">Topic Breakdown</h2>', unsafe_allow_html=True)
            topic_rows_html = ""
            for topic, stats in topic_breakdown.items():
                t_total = stats["total"]
                t_correct = stats["correct"]
                t_acc = round((t_correct / t_total) * 100) if t_total > 0 else 0
                topic_rows_html += f"""
                <div class="qm-topic-row">
                    <span style="font-weight: 500;">{topic}</span>
                    <span style="color: var(--text-secondary);">{t_correct}/{t_total} correct ({t_acc}%)</span>
                </div>
                """
            st.markdown(f'<div class="qm-card" style="padding: 0.5rem 1rem;">{topic_rows_html}</div>', unsafe_allow_html=True)

        # Action Buttons
        res_col1, res_col2 = st.columns([1.2, 1])

        with res_col1:
            if incorrect > 0:
                if st.button(f"Practise Mistakes ({incorrect} questions)", type="primary", use_container_width=True):
                    retry_session = session.create_retry_session()
                    if retry_session:
                        st.session_state.quiz_session = retry_session
                        st.session_state.active_nav = "quiz"
                        st.rerun()
            else:
                st.button("No Mistakes to Practise", disabled=True, use_container_width=True)

        with res_col2:
            if st.button("Start New Quiz", use_container_width=True):
                st.session_state.quiz_session = None
                st.session_state.active_nav = "study"
                st.rerun()

        # Expandable Answer Review
        st.write("")
        with st.expander("Review Submitted Questions and Answers", expanded=False):
            for i, q in enumerate(session.questions):
                user_choice = session.user_answers.get(q.id, "None")
                is_right = session.is_correct.get(q.id, False)
                symbol = "✓" if is_right else "✕"
                color = "var(--accent-forest)" if is_right else "var(--accent-terracotta)"

                st.markdown(
                    f"""
                    <div style="margin-bottom: 1.25rem; padding-bottom: 1rem; border-bottom: 1px solid #EFECE4;">
                        <div style="display: flex; gap: 0.5rem; align-items: baseline;">
                            <strong style="color: {color};">{symbol} Q{i+1}:</strong>
                            <span style="font-weight: 500; color: var(--text-primary);">{q.prompt}</span>
                        </div>
                        <div style="font-size: 0.85rem; margin-top: 0.4rem; color: var(--text-secondary);">
                            Your choice: <strong>({user_choice}) {q.options.get(user_choice, '')}</strong> · 
                            Correct: <strong>({q.correct_option}) {q.options.get(q.correct_option, '')}</strong>
                        </div>
                        <div style="font-size: 0.82rem; margin-top: 0.35rem; color: var(--text-primary); background: #FAF9F5; padding: 0.5rem 0.75rem; border-radius: 4px;">
                            {q.explanation}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# -----------------------------------------------------------------------------
# 7. Workspace View: Session Progress
# -----------------------------------------------------------------------------

elif st.session_state.active_nav == "progress":
    tracker: SessionProgressTracker = st.session_state.progress_tracker

    st.markdown('<h1 class="qm-heading-1">Session Progress</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="qm-lead">Review your cumulative performance across all quizzes completed during this study session.</p>',
        unsafe_allow_html=True
    )

    # Big Summary Grid
    st.markdown(
        f"""
        <div class="qm-stat-grid">
            <div class="qm-stat-box">
                <div class="qm-stat-num">{tracker.quizzes_completed}</div>
                <div class="qm-stat-label">Quizzes Completed</div>
            </div>
            <div class="qm-stat-box">
                <div class="qm-stat-num">{tracker.total_questions_answered}</div>
                <div class="qm-stat-label">Questions Answered</div>
            </div>
            <div class="qm-stat-box">
                <div class="qm-stat-num" style="color: var(--accent-forest);">{tracker.overall_accuracy}%</div>
                <div class="qm-stat-label">Overall Accuracy</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Weak Topics Breakdown
    weak_topics = tracker.get_weak_topics()
    st.markdown('<h2 class="qm-heading-2">Topics Needing More Practice</h2>', unsafe_allow_html=True)

    if not weak_topics:
        if tracker.total_questions_answered == 0:
            st.info("No questions answered yet. Complete a quiz to see topic insights.")
        else:
            st.success("You have no weak topics recorded this session! All answered questions were correct.")
    else:
        topic_cards_html = ""
        for item in weak_topics:
            topic_cards_html += f"""
            <div class="qm-topic-row">
                <div>
                    <strong>{item['topic']}</strong>
                    <div style="font-size: 0.76rem; color: var(--text-muted);">{item['incorrect']} missed out of {item['answered']} questions</div>
                </div>
                <span style="font-weight: 600; color: var(--accent-terracotta);">{item['accuracy']}% accuracy</span>
            </div>
            """
        st.markdown(f'<div class="qm-card" style="padding: 0.5rem 1rem;">{topic_cards_html}</div>', unsafe_allow_html=True)

    # Persistence Note
    st.markdown(
        """
        <div style="margin-top: 2.5rem; padding: 1rem 1.25rem; background: #ECEAE2; border-radius: var(--radius-sm); font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5;">
            <strong>Honest Session Persistence:</strong> All progress data shown above is stored in your current browser memory session. If you close this tab or restart the local server, session metrics will reset.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")
    if st.button("Return to Study Workspace", type="primary"):
        st.session_state.active_nav = "study"
        st.rerun()
