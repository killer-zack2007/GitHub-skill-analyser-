from pathlib import Path
from html import escape

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from src.github_api import get_profile_bundle

from src.analyzer import (
    extract_features,
    calculate_score,
    repository_timeline,
    generate_insights
)


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="GitHub Pulse",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
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
        padding-top: 3rem;
        padding-bottom: 4rem;
    }

    .hero {
        text-align: center;
        padding: 30px 10px 20px 10px;
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

    .glass {
        background: rgba(255,255,255,0.045);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 22px;
        padding: 24px;
        backdrop-filter: blur(16px);
        margin-bottom: 18px;
    }

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
        margin-top: 18px;
        padding: 8px 15px;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        color: white;
        font-size: 13px;
        font-weight: 600;
    }

    .section-title {
        color: white;
        font-size: 20px;
        font-weight: 700;
        margin: 22px 0 12px;
    }

    .insight {
        padding: 13px 16px;
        margin: 8px 0;
        border-radius: 14px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        color: #d5d7de;
        font-size: 14px;
    }

    .profile-name {
        font-size: 24px;
        font-weight: 700;
        color: white;
    }

    .profile-login {
        color: #858a99;
        font-size: 14px;
    }

    .metric-label {
        color: #858a99;
        font-size: 12px;
        margin-bottom: 5px;
    }

    .metric-value {
        color: white;
        font-size: 25px;
        font-weight: 700;
    }

    footer {
        visibility: hidden;
    }

    /* Streamlit button */

    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Mobile responsiveness */

    @media (max-width: 768px) {

        .block-container {
            padding-top: 1.5rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero h1 {
            font-size: 40px;
        }

        .hero p {
            font-size: 14px;
        }

        .score-number {
            font-size: 50px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# HERO
# ==========================================

hero_html = """
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

# Use st.html instead of st.markdown
# to ensure the HTML is rendered correctly.
st.html(hero_html)


# ==========================================
# SEARCH
# ==========================================

col1, col2 = st.columns([4, 1])

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


# ==========================================
# MODEL PATH
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "github_skill_model.joblib"
)


# ==========================================
# MODEL LOADING
# ==========================================

def load_model():

    if not MODEL_PATH.exists():
        return None

    try:

        artifact = joblib.load(
            MODEL_PATH
        )

        return artifact

    except Exception:

        return None


# ==========================================
# ANALYSIS
# ==========================================

if analyze:

    # --------------------------------------
    # Validate username
    # --------------------------------------

    if not username.strip():

        st.warning(
            "Please enter a GitHub username."
        )

        st.stop()

    username = username.strip()


    # --------------------------------------
    # Fetch GitHub data
    # --------------------------------------

    with st.spinner(
        "Scanning GitHub profile..."
    ):

        try:

            bundle = get_profile_bundle(
                username
            )

        except Exception as error:

            st.error(
                str(error)
            )

            st.stop()


    # --------------------------------------
    # Extract data
    # --------------------------------------

    user = bundle["user"]

    repositories = bundle[
        "repositories"
    ]

    languages = bundle[
        "languages"
    ]


    # --------------------------------------
    # Feature extraction
    # --------------------------------------

    features = extract_features(
        bundle
    )


    # --------------------------------------
    # Activity-based score
    # --------------------------------------

    rubric_scores = calculate_score(
        features
    )


    # ======================================
    # MODEL PREDICTION
    # ======================================

    artifact = load_model()

    predicted_level = rubric_scores[
        "level"
    ]

    model_used = False


    if artifact is not None:

        try:

            model = artifact["model"]

            feature_names = artifact[
                "features"
            ]

            X = pd.DataFrame(
                [
                    {
                        feature: features[
                            feature
                        ]
                        for feature in feature_names
                    }
                ]
            )

            predicted_level = model.predict(
                X
            )[0]

            model_used = True

        except Exception:

            predicted_level = (
                rubric_scores["level"]
            )


    # ======================================
    # PROFILE HEADER
    # ======================================

    avatar = escape(
        user.get(
            "avatar_url",
            ""
        )
    )

    name = escape(
        user.get(
            "name"
        ) or username
    )

    safe_username = escape(
        username
    )

    bio = escape(
        user.get(
            "bio"
        ) or "No bio available."
    )


    profile_html = f"""
    <div class="glass">

        <div style="
            display:flex;
            gap:20px;
            align-items:center;
        ">

            <img
                src="{avatar}"
                width="80"
                height="80"
                style="
                    border-radius:50%;
                    border:2px solid
                    rgba(255,255,255,0.12);
                    object-fit:cover;
                "
            >

            <div>

                <div class="profile-name">
                    {name}
                </div>

                <div class="profile-login">
                    @{safe_username}
                </div>

                <div style="
                    color:#a9adba;
                    margin-top:8px;
                    font-size:13px;
                ">
                    {bio}
                </div>

            </div>

        </div>

    </div>
    """

    st.markdown(
        profile_html,
        unsafe_allow_html=True
    )


    # ======================================
    # SCORE + SIGNALS + METRICS
    # ======================================

    col1, col2, col3 = st.columns(
        [1.2, 2, 1.2]
    )


    # --------------------------------------
    # Overall Score
    # --------------------------------------

    with col1:

        st.markdown(
            f"""
            <div class="score-card">

                <div class="score-number">
                    {rubric_scores["overall_score"]}
                </div>

                <div class="score-label">
                    Overall Score / 100
                </div>

                <div class="level">
                    {escape(str(predicted_level))}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # --------------------------------------
    # Skill Signals
    # --------------------------------------

    with col2:

        st.markdown(
            '<div class="glass">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            'Skill Signals'
            '</div>',
            unsafe_allow_html=True
        )


        signal_data = pd.DataFrame(
            {
                "Signal": [
                    "Activity",
                    "Projects",
                    "Collaboration",
                    "Consistency",
                    "Community"
                ],

                "Score": [
                    rubric_scores[
                        "activity_score"
                    ],

                    rubric_scores[
                        "project_score"
                    ],

                    rubric_scores[
                        "collaboration_score"
                    ],

                    rubric_scores[
                        "consistency_score"
                    ],

                    rubric_scores[
                        "community_score"
                    ]
                ]
            }
        )


        fig = px.bar(
            signal_data,
            x="Score",
            y="Signal",
            orientation="h",
            range_x=[0, 100],
            template="plotly_dark"
        )


        fig.update_layout(
            height=270,

            margin=dict(
                l=0,
                r=0,
                t=10,
                b=10
            ),

            showlegend=False,

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )


    # --------------------------------------
    # Metrics
    # --------------------------------------

    with col3:

        st.markdown(
            f"""
            <div class="glass">

                <div class="metric-label">
                    PUBLIC REPOS
                </div>

                <div class="metric-value">
                    {features["public_repos"]}
                </div>

                <br>

                <div class="metric-label">
                    FOLLOWERS
                </div>

                <div class="metric-value">
                    {features["followers"]}
                </div>

                <br>

                <div class="metric-label">
                    LANGUAGES
                </div>

                <div class="metric-value">
                    {features["languages_count"]}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )


    # ======================================
    # INSIGHTS
    # ======================================

    strengths, improvements = (
        generate_insights(
            features,
            rubric_scores
        )
    )


    col1, col2 = st.columns(2)


    # --------------------------------------
    # Strengths
    # --------------------------------------

    with col1:

        st.markdown(
            '<div class="section-title">'
            '✦ Strengths'
            '</div>',
            unsafe_allow_html=True
        )


        for item in strengths:

            safe_item = escape(
                str(item)
            )

            st.markdown(
                f"""
                <div class="insight">
                    ✓ {safe_item}
                </div>
                """,
                unsafe_allow_html=True
            )


    # --------------------------------------
    # Improvements
    # --------------------------------------

    with col2:

        st.markdown(
            '<div class="section-title">'
            '↗ Areas to Improve'
            '</div>',
            unsafe_allow_html=True
        )


        for item in improvements:

            safe_item = escape(
                str(item)
            )

            st.markdown(
                f"""
                <div class="insight">
                    → {safe_item}
                </div>
                """,
                unsafe_allow_html=True
            )


    # ======================================
    # LANGUAGES
    # ======================================

    if languages:

        st.markdown(
            '<div class="section-title">'
            'Technology Stack'
            '</div>',
            unsafe_allow_html=True
        )


        language_df = pd.DataFrame(
            {
                "Language": list(
                    languages.keys()
                ),

                "Bytes": list(
                    languages.values()
                )
            }
        )


        language_df = (
            language_df
            .sort_values(
                "Bytes",
                ascending=False
            )
            .head(10)
        )


        fig = px.bar(
            language_df,
            x="Language",
            y="Bytes",
            template="plotly_dark"
        )


        fig.update_layout(
            height=330,

            margin=dict(
                l=0,
                r=0,
                t=10,
                b=10
            ),

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ======================================
    # PROJECT EVOLUTION
    # ======================================

    timeline = repository_timeline(
        repositories
    )


    if timeline:

        st.markdown(
            '<div class="section-title">'
            'Project Evolution'
            '</div>',
            unsafe_allow_html=True
        )


        timeline_df = pd.DataFrame(
            {
                "Date": [
                    item["date"]
                    for item in timeline
                ],

                "Project": [
                    item["name"]
                    for item in timeline
                ],

                "Stars": [
                    item["stars"]
                    for item in timeline
                ]
            }
        )


        fig = px.scatter(
            timeline_df,
            x="Date",
            y="Stars",
            hover_name="Project",
            size="Stars",
            template="plotly_dark"
        )


        fig.update_layout(
            height=380,

            margin=dict(
                l=0,
                r=0,
                t=10,
                b=10
            ),

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ======================================
    # RAW FEATURES
    # ======================================

    with st.expander(
        "View technical analysis"
    ):

        feature_df = pd.DataFrame(
            {
                "Feature": features.keys(),
                "Value": features.values()
            }
        )


        st.dataframe(
            feature_df,
            use_container_width=True,
            hide_index=True
        )


    # ======================================
    # FOOTER
    # ======================================

    st.caption(
        "GitHub Pulse provides an activity-based "
        "estimate, not a definitive measure of "
        "programming ability."
    )


    if model_used:

        st.caption(
            "Prediction powered by the trained "
            "machine-learning model."
        )

    else:

        st.caption(
            "Prediction currently uses the "
            "activity-based scoring system."
    )
