import os
import html
import textwrap

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

from src.github_api import get_profile_bundle
from src.analyzer import (
    extract_features,
    calculate_score,
    repository_timeline,
    generate_insights,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="GitHub Pulse",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def render_html(content):
    """
    Render HTML safely without Streamlit treating
    indented HTML as a code block.
    """
    st.markdown(
        textwrap.dedent(content).strip(),
        unsafe_allow_html=True,
    )


def safe_text(value, fallback=""):
    """Safely convert text for HTML."""
    if value is None:
        return fallback

    return html.escape(str(value))


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
<style>

@import url(
    'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);


/* ==============================
   GLOBAL
   ============================== */

html,
body,
[class*="css"] {
    font-family: "Inter", sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 8% 8%,
            rgba(120, 80, 255, 0.15),
            transparent 30%
        ),
        radial-gradient(
            circle at 92% 15%,
            rgba(0, 210, 255, 0.10),
            transparent 30%
        ),
        #08090d;
}


/* ==============================
   MAIN CONTAINER
   ============================== */

.block-container {
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 4rem;
}


/* ==============================
   HERO
   ============================== */

.hero {
    text-align: center;
    padding: 25px 10px 28px 10px;
}

.hero-badge {
    display: inline-block;
    padding: 7px 14px;
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.04);
    color: #a9adba;
    font-size: 12px;
    font-weight: 500;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 54px;
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
    font-size: 15px;
    max-width: 680px;
    margin: 16px auto 0;
    line-height: 1.7;
}


/* ==============================
   SEARCH
   ============================== */

div[data-testid="stTextInput"] input {
    background: rgba(255, 255, 255, 0.055);
    border: 1px solid rgba(255, 255, 255, 0.09);
    color: white;
    border-radius: 12px;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(167, 139, 250, 0.55);
    box-shadow: 0 0 0 1px rgba(167, 139, 250, 0.25);
}


/* ==============================
   BUTTON
   ============================== */

.stButton > button {
    border-radius: 12px;
    border: none;
    min-height: 42px;
    font-weight: 700;
}


/* ==============================
   GLASS CARDS
   ============================== */

.glass {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 24px;
    backdrop-filter: blur(16px);
    margin-bottom: 18px;
}


/* ==============================
   PROFILE CARD
   ============================== */

.profile-card {
    display: flex;
    align-items: center;
    gap: 18px;
}

.profile-avatar {
    width: 76px;
    height: 76px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid rgba(255, 255, 255, 0.12);
}

.profile-name {
    color: white;
    font-size: 24px;
    font-weight: 700;
}

.profile-login {
    color: #858a99;
    font-size: 13px;
    margin-top: 2px;
}

.profile-bio {
    color: #a9adba;
    margin-top: 8px;
    font-size: 13px;
    line-height: 1.5;
}


/* ==============================
   SCORE CARD
   ============================== */

.score-card {
    text-align: center;
    padding: 32px 18px;
    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(167, 139, 250, 0.13),
            rgba(96, 165, 250, 0.06)
        );

    border: 1px solid rgba(167, 139, 250, 0.16);
}

.score-number {
    font-size: 58px;
    font-weight: 800;
    color: white;
    line-height: 1;
}

.score-label {
    margin-top: 9px;
    color: #a9adba;
    font-size: 13px;
}

.level {
    display: inline-block;
    margin-top: 17px;
    padding: 7px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.07);
    color: white;
    font-size: 12px;
    font-weight: 600;
}


/* ==============================
   SECTION TITLES
   ============================== */

.section-title {
    color: white;
    font-size: 19px;
    font-weight: 700;
    margin: 24px 0 12px;
}


/* ==============================
   INSIGHTS
   ============================== */

.insight {
    padding: 12px 15px;
    margin: 8px 0;
    border-radius: 13px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    color: #d5d7de;
    font-size: 13px;
    line-height: 1.5;
}


/* ==============================
   METRICS
   ============================== */

.metric-label {
    color: #858a99;
    font-size: 11px;
    font-weight: 600;
    margin-bottom: 5px;
    letter-spacing: 0.5px;
}

.metric-value {
    color: white;
    font-size: 24px;
    font-weight: 700;
}


/* ==============================
   MOBILE
   ============================== */

@media (max-width: 768px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        padding-top: 1.5rem;
    }

    .hero {
        padding-top: 10px;
    }

    .hero h1 {
        font-size: 39px;
        letter-spacing: -1.5px;
    }

    .hero p {
        font-size: 13px;
    }

    .glass {
        padding: 18px;
        border-radius: 16px;
    }

    .profile-avatar {
        width: 62px;
        height: 62px;
    }

    .profile-name {
        font-size: 19px;
    }

    .score-number {
        font-size: 48px;
    }
}


/* ==============================
   FOOTER
   ============================== */

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True,
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

col1, col2 = st.columns([4, 1])

with col1:
    username = st.text_input(
        "GitHub username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed",
    )

with col2:
    analyze = st.button(
        "Analyze →",
        use_container_width=True,
        type="primary",
    )


# ============================================================
# MODEL
# ============================================================

MODEL_PATH = os.path.join(
    "models",
    "github_skill_model.joblib",
)


def load_model():

    if not os.path.exists(MODEL_PATH):
        return None

    try:
        artifact = joblib.load(MODEL_PATH)
        return artifact

    except Exception:
        return None


# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # -----------------------------------------
    # VALIDATE USERNAME
    # -----------------------------------------

    if not username.strip():

        st.warning(
            "Please enter a GitHub username."
        )

        st.stop()

    username = username.strip()


    # -----------------------------------------
    # FETCH GITHUB DATA
    # -----------------------------------------

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


    # -----------------------------------------
    # GET DATA
    # -----------------------------------------

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

    except Exception as error:

        st.error(
            f"Invalid GitHub data received: {error}"
        )

        st.stop()


    # -----------------------------------------
    # FEATURE EXTRACTION
    # -----------------------------------------

    try:

        features = extract_features(
            bundle
        )

        rubric_scores = calculate_score(
            features
        )

    except Exception as error:

        st.error(
            f"Feature analysis failed: {error}"
        )

        st.stop()


    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    artifact = load_model()

    predicted_level = rubric_scores.get(
        "level",
        "Beginner"
    )

    model_used = False

    if artifact is not None:

        try:

            model = artifact["model"]

            feature_names = artifact[
                "features"
            ]

            row = {}

            for feature in feature_names:

                row[feature] = features.get(
                    feature,
                    0
                )

            X = pd.DataFrame(
                [row],
                columns=feature_names
            )

            predicted_level = model.predict(
                X
            )[0]

            model_used = True

        except Exception:

            predicted_level = rubric_scores.get(
                "level",
                "Beginner"
            )

            model_used = False


    # ========================================================
    # PROFILE
    # ========================================================

    avatar = safe_text(
        user.get(
            "avatar_url",
            ""
        )
    )

    name = safe_text(
        user.get(
            "name"
        ) or username
    )

    safe_username = safe_text(
        username
    )

    bio = safe_text(
        user.get(
            "bio"
        ) or "No bio available."
    )


    render_html(
        f"""
        <div class="glass">

            <div class="profile-card">

                <img
                    class="profile-avatar"
                    src="{avatar}"
                    alt="GitHub avatar"
                >

                <div>

                    <div class="profile-name">
                        {name}
                    </div>

                    <div class="profile-login">
                        @{safe_username}
                    </div>

                    <div class="profile-bio">
                        {bio}
                    </div>

                </div>

            </div>

        </div>
        """
    )


    # ========================================================
    # SCORE + SIGNALS + METRICS
    # ========================================================

    col1, col2, col3 = st.columns(
        [1.15, 2, 1.15]
    )


    # --------------------------------------------------------
    # SCORE
    # --------------------------------------------------------

    with col1:

        overall_score = rubric_scores.get(
            "overall_score",
            0
        )

        render_html(
            f"""
            <div class="score-card">

                <div class="score-number">
                    {overall_score}
                </div>

                <div class="score-label">
                    Overall Score / 100
                </div>

                <div class="level">
                    {safe_text(predicted_level)}
                </div>

            </div>
            """
        )


    # --------------------------------------------------------
    # SIGNALS
    # --------------------------------------------------------

    with col2:

        render_html(
            """
            <div class="glass">

                <div class="section-title">
                    Skill Signals
                </div>

            </div>
            """
        )

        signal_data = pd.DataFrame(
            {
                "Signal": [
                    "Activity",
                    "Projects",
                    "Collaboration",
                    "Consistency",
                    "Community",
                ],

                "Score": [
                    rubric_scores.get(
                        "activity_score",
                        0
                    ),

                    rubric_scores.get(
                        "project_score",
                        0
                    ),

                    rubric_scores.get(
                        "collaboration_score",
                        0
                    ),

                    rubric_scores.get(
                        "consistency_score",
                        0
                    ),

                    rubric_scores.get(
                        "community_score",
                        0
                    ),
                ],
            }
        )

        fig = px.bar(
            signal_data,
            x="Score",
            y="Signal",
            orientation="h",
            range_x=[0, 100],
            template="plotly_dark",
            text="Score",
        )

        fig.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside",
        )

        fig.update_layout(
            height=300,
            margin=dict(
                l=0,
                r=30,
                t=5,
                b=5,
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                showgrid=False,
                range=[0, 110],
            ),
            yaxis=dict(
                showgrid=False,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )


    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

    with col3:

        public_repos = features.get(
            "public_repos",
            0
        )

        followers = features.get(
            "followers",
            0
        )

        languages_count = features.get(
            "languages_count",
            0
        )

        render_html(
            f"""
            <div class="glass">

                <div class="metric-label">
                    PUBLIC REPOS
                </div>

                <div class="metric-value">
                    {public_repos}
                </div>

                <br>

                <div class="metric-label">
                    FOLLOWERS
                </div>

                <div class="metric-value">
                    {followers}
                </div>

                <br>

                <div class="metric-label">
                    LANGUAGES
                </div>

                <div class="metric-value">
                    {languages_count}
                </div>

            </div>
            """
        )


    # ========================================================
    # INSIGHTS
    # ========================================================

    try:

        strengths, improvements = (
            generate_insights(
                features,
                rubric_scores
            )
        )

    except Exception:

        strengths = []
        improvements = []


    col1, col2 = st.columns(2)


    # --------------------------------------------------------
    # STRENGTHS
    # --------------------------------------------------------

    with col1:

        st.markdown(
            '<div class="section-title">✦ Strengths</div>',
            unsafe_allow_html=True,
        )

        if strengths:

            for item in strengths:

                render_html(
                    f"""
                    <div class="insight">
                        ✓ {safe_text(item)}
                    </div>
                    """
                )

        else:

            render_html(
                """
                <div class="insight">
                    No major strengths detected yet.
                </div>
                """
            )


    # --------------------------------------------------------
    # IMPROVEMENTS
    # --------------------------------------------------------

    with col2:

        st.markdown(
            '<div class="section-title">↗ Areas to Improve</div>',
            unsafe_allow_html=True,
        )

        if improvements:

            for item in improvements:

                render_html(
                    f"""
                    <div class="insight">
                        → {safe_text(item)}
                    </div>
                    """
                )

        else:

            render_html(
                """
                <div class="insight">
                    No major improvement areas detected.
                </div>
                """
            )


    # ========================================================
    # TECHNOLOGY STACK
    # ========================================================

    if languages:

        st.markdown(
            '<div class="section-title">Technology Stack</div>',
            unsafe_allow_html=True,
        )

        language_df = pd.DataFrame(
            {
                "Language": list(
                    languages.keys()
                ),

                "Bytes": list(
                    languages.values()
                ),
            }
        )


        # Convert bytes to numeric values
        language_df["Bytes"] = pd.to_numeric(
            language_df["Bytes"],
            errors="coerce"
        ).fillna(0)


        language_df = (
            language_df
            .sort_values(
                "Bytes",
                ascending=False
            )
            .head(10)
        )


        total_bytes = language_df[
            "Bytes"
        ].sum()


        if total_bytes > 0:

            language_df["Percentage"] = (
                language_df["Bytes"]
                / total_bytes
                * 100
            )

        else:

            language_df["Percentage"] = 0


        language_df["Label"] = (
            language_df["Language"]
            + "  "
            + language_df["Percentage"]
            .round(1)
            .astype(str)
            + "%"
        )


        fig = px.bar(
            language_df,
            x="Percentage",
            y="Language",
            orientation="h",
            range_x=[0, 100],
            text="Percentage",
            template="plotly_dark",
        )

        fig.update_traces(
            texttemplate="%{text:.1f}%",
            textposition="outside",
        )

        fig.update_layout(
            height=max(
                300,
                len(language_df) * 45
            ),
            margin=dict(
                l=0,
                r=45,
                t=10,
                b=10,
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Usage %",
                showgrid=False,
            ),
            yaxis=dict(
                title="",
                showgrid=False,
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False,
            },
        )


    # ========================================================
    # PROJECT EVOLUTION
    # ========================================================

    try:

        timeline = repository_timeline(
            repositories
        )

    except Exception:

        timeline = []


    if timeline:

        st.markdown(
            '<div class="section-title">Project Evolution</div>',
            unsafe_allow_html=True,
        )


        timeline_df = pd.DataFrame(
            {
                "Date": [
                    item.get(
                        "date"
                    )
                    for item in timeline
                ],

                "Project": [
                    item.get(
                        "name",
                        "Repository"
                    )
                    for item in timeline
                ],

                "Stars": [
                    item.get(
                        "stars",
                        0
                    )
                    for item in timeline
                ],
            }
        )


        timeline_df["Date"] = pd.to_datetime(
            timeline_df["Date"],
            errors="coerce"
        )

        timeline_df["Stars"] = pd.to_numeric(
            timeline_df["Stars"],
            errors="coerce"
        ).fillna(0)


        timeline_df = timeline_df.dropna(
            subset=["Date"]
        )


        if not timeline_df.empty:

            fig = px.scatter(
                timeline_df,
                x="Date",
                y="Stars",
                hover_name="Project",
                size="Stars",
                template="plotly_dark",
            )

            fig.update_layout(
                height=380,
                margin=dict(
                    l=0,
                    r=10,
                    t=10,
                    b=10,
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(
                    showgrid=False,
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor="rgba(255,255,255,0.06)",
                ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                },
            )

        else:

            st.info(
                "Not enough repository timeline data available."
            )


    else:

        st.info(
            "No repository timeline data available for this profile."
        )


    # ========================================================
    # TECHNICAL ANALYSIS
    # ========================================================

    with st.expander(
        "View technical analysis"
    ):

        feature_df = pd.DataFrame(
            {
                "Feature": list(
                    features.keys()
                ),

                "Value": list(
                    features.values()
                ),
            }
        )

        st.dataframe(
            feature_df,
            use_container_width=True,
            hide_index=True,
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.markdown("---")

    st.caption(
        "GitHub Pulse provides an activity-based "
        "estimate, not a definitive measure of "
        "programming ability."
    )

    if model_used:

        st.caption(
            "✦ Prediction powered by the trained "
            "machine-learning model."
        )

    else:

        st.caption(
            "✦ Prediction currently uses the "
            "activity-based scoring system."
    )
