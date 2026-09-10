import os
import html
from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# OPTIONAL JOBLIB
# ============================================================

try:
    import joblib
except ImportError:
    joblib = None


# ============================================================
# PROJECT MODULES
# ============================================================

from src.github_api import get_profile_bundle

from src.analyzer import (
    extract_features,
    calculate_score,
    repository_timeline,
    generate_insights
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GitHub Pulse",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

/* ============================================================
   GLOBAL
============================================================ */

html,
body,
[class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(120, 80, 255, 0.14),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(0, 210, 255, 0.10),
            transparent 30%
        ),
        #08090d;
}

.block-container {
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}


/* ============================================================
   HERO
============================================================ */

.hero {
    text-align: center;
    padding: 25px 10px 25px 10px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 999px;
    background: rgba(255,255,255,0.04);
    font-size: 13px;
    color: #a9adba;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 52px;
    line-height: 1.05;
    font-weight: 800;
    letter-spacing: -2px;
    margin: 0;
    color: white;
}

.hero h1 span {
    background: linear-gradient(
        90deg,
        #a78bfa,
        #60a5fa
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #8f94a3;
    font-size: 16px;
    max-width: 650px;
    margin: 16px auto 0;
    line-height: 1.7;
}


/* ============================================================
   GLASS CARDS
============================================================ */

.glass {
    background: rgba(255,255,255,0.045);

    border: 1px solid rgba(255,255,255,0.08);

    border-radius: 22px;

    padding: 24px;

    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);

    margin-bottom: 18px;
}


/* ============================================================
   PROFILE
============================================================ */

.profile-card {
    display: flex;
    gap: 20px;
    align-items: center;
}

.profile-avatar {
    width: 80px;
    height: 80px;

    min-width: 80px;

    border-radius: 50%;

    border: 2px solid rgba(255,255,255,0.12);

    object-fit: cover;
}

.profile-name {
    font-size: 24px;

    font-weight: 700;

    color: white;
}

.profile-login {
    color: #858a99;

    font-size: 14px;

    margin-top: 2px;
}

.profile-bio {
    color: #a9adba;

    margin-top: 8px;

    font-size: 13px;

    line-height: 1.5;
}


/* ============================================================
   SCORE CARD
============================================================ */

.score-card {
    text-align: center;

    padding: 35px 20px;

    border-radius: 22px;

    background:
        linear-gradient(
            145deg,
            rgba(167,139,250,0.12),
            rgba(96,165,250,0.06)
        );

    border: 1px solid rgba(167,139,250,0.16);

    min-height: 270px;

    display: flex;

    flex-direction: column;

    justify-content: center;
}

.score-number {
    font-size: 64px;

    font-weight: 800;

    color: white;

    line-height: 1;
}

.score-label {
    margin-top: 10px;

    color: #a9adba;

    font-size: 14px;
}

.level {
    display: inline-block;

    align-self: center;

    margin-top: 18px;

    padding: 8px 15px;

    border-radius: 999px;

    background: rgba(255,255,255,0.07);

    color: white;

    font-size: 13px;

    font-weight: 600;
}


/* ============================================================
   SECTION TITLES
============================================================ */

.section-title {
    color: white;

    font-size: 20px;

    font-weight: 700;

    margin: 22px 0 12px;
}


/* ============================================================
   INSIGHTS
============================================================ */

.insight {
    padding: 13px 16px;

    margin: 8px 0;

    border-radius: 14px;

    background: rgba(255,255,255,0.04);

    border: 1px solid rgba(255,255,255,0.06);

    color: #d5d7de;

    font-size: 14px;

    line-height: 1.5;
}


/* ============================================================
   METRICS
============================================================ */

.metric-label {
    color: #858a99;

    font-size: 12px;

    margin-bottom: 5px;

    letter-spacing: 0.5px;
}

.metric-value {
    color: white;

    font-size: 25px;

    font-weight: 700;
}

.metric-item {
    margin-bottom: 22px;
}

.metric-item:last-child {
    margin-bottom: 0;
}


/* ============================================================
   SEARCH INPUT
============================================================ */

div[data-testid="stTextInput"] input {

    background: rgba(255,255,255,0.06);

    border: 1px solid rgba(255,255,255,0.08);

    color: white;

    border-radius: 12px;
}

div[data-testid="stTextInput"] input:focus {

    border-color: rgba(167,139,250,0.6);

    box-shadow:
        0 0 0 1px
        rgba(167,139,250,0.2);
}


/* ============================================================
   BUTTON
============================================================ */

div[data-testid="stButton"] button {

    border-radius: 12px;

    font-weight: 600;
}


/* ============================================================
   MOBILE
============================================================ */

@media (max-width: 768px) {

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;

        padding-top: 1.5rem;
    }

    .hero {

        padding-top: 15px;
    }

    .hero h1 {

        font-size: 38px;

        letter-spacing: -1px;
    }

    .hero p {

        font-size: 14px;
    }

    .profile-card {

        gap: 14px;
    }

    .profile-avatar {

        width: 64px;

        height: 64px;

        min-width: 64px;
    }

    .profile-name {

        font-size: 19px;
    }

    .score-number {

        font-size: 52px;
    }

    .glass {

        padding: 18px;

        border-radius: 18px;
    }
}


/* ============================================================
   HIDE STREAMLIT FOOTER
============================================================ */

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HTML RENDER HELPER
# ============================================================

def render_html(content):
    """
    Render custom HTML safely.

    Removes problematic indentation and blank lines
    that can cause Streamlit to display HTML as text.
    """

    cleaned = dedent(content).strip()

    cleaned = "\n".join(
        line
        for line in cleaned.splitlines()
        if line.strip()
    )

    st.markdown(
        cleaned,
        unsafe_allow_html=True
    )


# ============================================================
# HERO
# ============================================================

render_html(
    """
    <div class="hero">

        <div class="hero-badge">
            ◈ GitHub Profile Intelligence
        </div>

        <h1>
            GitHub <span>Pulse</span>
        </h1>

        <p>
            Analyze GitHub activity, projects,
            collaboration and technology signals
            to estimate a developer's skill level.
        </p>

    </div>
    """
)


# ============================================================
# SEARCH
# ============================================================

col1, col2 = st.columns(
    [5, 1]
)

with col1:

    username = st.text_input(
        "GitHub username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed"
    )

with col2:

    analyze = st.button(
        "Analyze →",
        use_container_width=True,
        type="primary"
    )


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "github_skill_model.joblib"
)


def load_model():

    if joblib is None:
        return None

    if not os.path.exists(
        MODEL_PATH
    ):
        return None

    try:

        artifact = joblib.load(
            MODEL_PATH
        )

        if not isinstance(
            artifact,
            dict
        ):
            return None

        if "model" not in artifact:
            return None

        if "features" not in artifact:
            return None

        return artifact

    except Exception:

        return None


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # ========================================================
    # VALIDATE USERNAME
    # ========================================================

    if not username.strip():

        st.warning(
            "Please enter a GitHub username."
        )

        st.stop()

    username = username.strip()


    # ========================================================
    # FETCH GITHUB DATA
    # ========================================================

    with st.spinner(
        "Scanning GitHub profile..."
    ):

        try:

            bundle = get_profile_bundle(
                username
            )

        except Exception as error:

            st.error(
                f"Unable to analyze this profile: {error}"
            )

            st.stop()


    # ========================================================
    # EXTRACT DATA
    # ========================================================

    try:

        user = bundle.get(
            "user",
            {}
        )

        repositories = bundle.get(
            "repositories",
            []
        )

        languages = bundle.get(
            "languages",
            {}
        )

        features = extract_features(
            bundle
        )

        rubric_scores = calculate_score(
            features
        )

        if not isinstance(
            rubric_scores,
            dict
        ):

            rubric_scores = {}

    except Exception as error:

        st.error(
            f"Analysis failed: {error}"
        )

        st.stop()


    # ========================================================
    # SAFE SIGNAL VALUES
    # ========================================================

    def safe_number(
        value,
        default=0
    ):

        try:

            return float(
                value or default
            )

        except Exception:

            return float(
                default
            )


    activity_score = safe_number(
        rubric_scores.get(
            "activity_score",
            0
        )
    )

    project_score = safe_number(
        rubric_scores.get(
            "project_score",
            0
        )
    )

    collaboration_score = safe_number(
        rubric_scores.get(
            "collaboration_score",
            0
        )
    )

    consistency_score = safe_number(
        rubric_scores.get(
            "consistency_score",
            0
        )
    )

    community_score = safe_number(
        rubric_scores.get(
            "community_score",
            0
        )
    )


    # ========================================================
    # OVERALL SCORE
    # ========================================================

    existing_score = safe_number(
        rubric_scores.get(
            "overall_score",
            0
        )
    )

    signal_scores = [
        activity_score,
        project_score,
        collaboration_score,
        consistency_score,
        community_score
    ]


    # If calculate_score() doesn't provide a usable
    # overall score, calculate a fallback from signals.

    if (
        existing_score <= 0
        and any(
            score > 0
            for score in signal_scores
        )
    ):

        overall_score = round(
            sum(signal_scores)
            / len(signal_scores)
        )

    else:

        overall_score = round(
            max(
                0,
                min(
                    100,
                    existing_score
                )
            )
        )


    # ========================================================
    # LEVEL
    # ========================================================

    predicted_level = rubric_scores.get(
        "level"
    )

    if not predicted_level:

        if overall_score < 40:

            predicted_level = "Beginner"

        elif overall_score < 70:

            predicted_level = "Intermediate"

        else:

            predicted_level = "Advanced"


    # ========================================================
    # MACHINE LEARNING MODEL
    # ========================================================

    artifact = load_model()

    model_used = False

    if artifact is not None:

        try:

            model = artifact[
                "model"
            ]

            feature_names = artifact[
                "features"
            ]

            row = {}

            for feature
