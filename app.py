import os
import html
from textwrap import dedent

import pandas as pd
import plotly.express as px
import streamlit as st

# joblib is optional
try:
    import joblib
except ImportError:
    joblib = None

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

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

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
   CARDS
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
   SCORE
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
   SECTION
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
   SEARCH
============================================================ */

div[data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.08);
    color: white;
    border-radius: 12px;
}

div[data-testid="stTextInput"] input:focus {
    border-color: rgba(167,139,250,0.6);
    box-shadow: 0 0 0 1px rgba(167,139,250,0.2);
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

footer {
    visibility: hidden;
}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# HTML HELPER
# ============================================================

def render_html(content):
    """
    Render HTML safely through Streamlit Markdown.

    Removes problematic blank lines and indentation
    that can cause Streamlit to interpret HTML as
    a Markdown code block.
    """

    cleaned = dedent(content).strip()

    # Remove blank lines inside HTML blocks
    cleaned = "\n".join(
        line for line in cleaned.splitlines()
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
        <div class="hero-badge">◈ GitHub Profile Intelligence</div>
        <h1>GitHub <span>Pulse</span></h1>
        <p>Analyze GitHub activity, projects, collaboration and technology signals to estimate a developer's skill level.</p>
    </div>
    """
)


# ============================================================
# SEARCH
# ============================================================

col1, col2 = st.columns([5, 1])

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

    if not os.path.exists(MODEL_PATH):
        return None

    try:

        artifact = joblib.load(MODEL_PATH)

        if not isinstance(artifact, dict):
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

        # Safety fallback
        if not isinstance(rubric_scores, dict):
            rubric_scores = {}

    except Exception as error:

        st.error(
            f"Analysis failed: {error}"
        )

        st.stop()


    # ========================================================
    # SAFE SCORE CALCULATION
    # ========================================================

    signal_scores = [
        float(
            rubric_scores.get(
                "activity_score",
                0
            ) or 0
        ),
        float(
            rubric_scores.get(
                "project_score",
                0
            ) or 0
        ),
        float(
            rubric_scores.get(
                "collaboration_score",
                0
            ) or 0
        ),
        float(
            rubric_scores.get(
                "consistency_score",
                0
            ) or 0
        ),
        float(
            rubric_scores.get(
                "community_score",
                0
            ) or 0
        )
    ]

    existing_score = rubric_scores.get(
        "overall_score",
        0
    )

    try:
        existing_score = float(
            existing_score or 0
        )
    except Exception:
        existing_score = 0

    # If analyzer returns 0 but individual signals exist,
    # calculate a weighted average fallback.
    if existing_score <= 0 and any(
        score > 0 for score in signal_scores
    ):

        overall_score = round(
            sum(signal_scores) / len(signal_scores)
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
    # MODEL PREDICTION
    # ========================================================

    artifact = load_model()

    model_used = False

    if artifact is not None:

        try:

            model = artifact["model"]

            feature_names = artifact["features"]

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

            prediction = model.predict(X)

            if len(prediction) > 0:

                predicted_level = str(
                    prediction[0]
                )

                model_used = True

        except Exception:

            model_used = False


    # ========================================================
    # PROFILE HEADER
    # ========================================================

    avatar = html.escape(
        str(
            user.get(
                "avatar_url",
                ""
            )
        ),
        quote=True
    )

    name = html.escape(
        str(
            user.get(
                "name"
            ) or username
        )
    )

    safe_username = html.escape(
        username
    )

    bio = html.escape(
        str(
            user.get(
                "bio"
            ) or "No bio available."
        )
    )

    render_html(
        f"""
        <div class="glass">
            <div class="profile-card">
                <img class="profile-avatar" src="{avatar}" alt="GitHub avatar">
                <div>
                    <div class="profile-name">{name}</div>
                    <div class="profile-login">@{safe_username}</div>
                    <div class="profile-bio">{bio}</div>
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


    # ========================================================
    # SCORE
    # ========================================================

    with col1:

        render_html(
            f"""
            <div class="score-card">
                <div class="score-number">{overall_score}</div>
                <div class="score-label">Overall Score / 100</div>
                <div class="level">{html.escape(str(predicted_level))}</div>
            </div>
            """
        )


    # ========================================================
    # SIGNALS
    # ========================================================

    with col2:

        render_html(
            """
            <div class="glass">
                <div class="section-title">Skill Signals</div>
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
                    "Community"
                ],
                "Score": signal_scores
            }
        )

        fig = px.bar(
            signal_data,
            x="Score",
            y="Signal",
            orientation="h",
            range_x=[0, 100],
            text="Score",
            template="plotly_dark"
        )

        fig.update_traces(
            texttemplate="%{text:.0f}",
            textposition="outside"
        )

        fig.update_layout(
            height=300,
            margin=dict(
                l=0,
                r=30,
                t=10,
                b=10
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Score",
                range=[0, 110]
            ),
            yaxis=dict(
                title=""
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True
            }
        )


    # ========================================================
    # METRICS
    # ========================================================

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
                <div class="metric-item">
                    <div class="metric-label">PUBLIC REPOS</div>
                    <div class="metric-value">{public_repos}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">FOLLOWERS</div>
                    <div class="metric-value">{followers}</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">LANGUAGES</div>
                    <div class="metric-value">{languages_count}</div>
                </div>
            </div>
            """
        )


    # ========================================================
    # INSIGHTS
    # ========================================================

    try:

        strengths, improvements = generate_insights(
            features,
            rubric_scores
        )

    except Exception:

        strengths = []
        improvements = []


    col1, col2 = st.columns(2)


    # ========================================================
    # STRENGTHS
    # ========================================================

    with col1:

        render_html(
            """
            <div class="section-title">✦ Strengths</div>
            """
        )

        if strengths:

            for item in strengths:

                safe_item = html.escape(
                    str(item)
                )

                render_html(
                    f"""
                    <div class="insight">✓ {safe_item}</div>
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


    # ========================================================
    # IMPROVEMENTS
    # ========================================================

    with col2:

        render_html(
            """
            <div class="section-title">↗ Areas to Improve</div>
            """
        )

        if improvements:

            for item in improvements:

                safe_item = html.escape(
                    str(item)
                )

                render_html(
                    f"""
                    <div class="insight">→ {safe_item}</div>
                    """
                )

        else:

            render_html(
                """
                <div class="insight">
                    Keep building and contributing!
                </div>
                """
            )


    # ========================================================
    # TECHNOLOGY STACK
    # ========================================================

    if languages:

        render_html(
            """
            <div class="section-title">
                Technology Stack
            </div>
            """
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

        language_df = language_df[
            language_df["Bytes"] > 0
        ]

        language_df = (
            language_df
            .sort_values(
                "Bytes",
                ascending=False
            )
            .head(10)
        )

        if not language_df.empty:

            total_bytes = language_df[
                "Bytes"
            ].sum()

            if total_bytes > 0:

                language_df["Usage"] = (
                    language_df["Bytes"]
                    / total_bytes
                    * 100
                )

                fig = px.bar(
                    language_df.sort_values(
                        "Usage"
                    ),
                    x="Usage",
                    y="Language",
                    orientation="h",
                    text="Usage",
                    template="plotly_dark"
                )

                fig.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside"
                )

                fig.update_layout(
                    height=max(
                        300,
                        len(language_df) * 45
                    ),
                    margin=dict(
                        l=0,
                        r=35,
                        t=10,
                        b=10
                    ),
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(
                        title="Usage %",
                        range=[0, 110]
                    ),
                    yaxis=dict(
                        title=""
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        "displaylogo": False,
                        "responsive": True
                    }
                )


# ========================================================
# PROJECT EVOLUTION / YEARLY ANALYSIS
# ========================================================

timeline = []

try:

    timeline = repository_timeline(
        repositories
    )

except Exception:

    timeline = []


timeline_rows = []

if timeline:

    for item in timeline:

        try:

            date_value = item.get(
                "date"
            )

            project_name = item.get(
                "name",
                "Unknown"
            )

            stars_value = item.get(
                "stars",
                0
            )

            timeline_rows.append(
                {
                    "Date": date_value,
                    "Project": project_name,
                    "Stars": max(
                        0,
                        int(stars_value or 0)
                    )
                }
            )

        except Exception:

            continue


# ========================================================
# YEARLY PROJECT ANALYSIS
# ========================================================

if timeline_rows:

    timeline_df = pd.DataFrame(
        timeline_rows
    )

    # Convert dates safely
    timeline_df["Date"] = pd.to_datetime(
        timeline_df["Date"],
        errors="coerce"
    )

    # Remove invalid dates
    timeline_df = timeline_df.dropna(
        subset=["Date"]
    )

    if not timeline_df.empty:

        # -----------------------------------------------
        # Extract year
        # -----------------------------------------------

        timeline_df["Year"] = (
            timeline_df["Date"]
            .dt.year
            .astype(int)
        )

        # -----------------------------------------------
        # Group projects by year
        # -----------------------------------------------

        yearly_df = (
            timeline_df
            .groupby("Year")
            .agg(
                Projects=("Project", "count"),
                Stars=("Stars", "sum")
            )
            .reset_index()
        )

        yearly_df = yearly_df.sort_values(
            "Year"
        )

        # -----------------------------------------------
        # Section title
        # -----------------------------------------------

        render_html(
            """
            <div class="section-title">
                Project Evolution
            </div>
            """
        )

        # -----------------------------------------------
        # Yearly project chart
        # -----------------------------------------------

        fig = px.bar(
            yearly_df,
            x="Year",
            y="Projects",
            text="Projects",
            hover_data={
                "Year": True,
                "Projects": True,
                "Stars": True
            },
            template="plotly_dark"
        )

        fig.update_traces(
            texttemplate="%{text}",
            textposition="outside"
        )

        fig.update_layout(
            height=380,

            margin=dict(
                l=0,
                r=10,
                t=20,
                b=10
            ),

            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",

            showlegend=False,

            xaxis=dict(
                title="Year",
                dtick=1,
                type="linear"
            ),

            yaxis=dict(
                title="Projects Created",
                rangemode="tozero"
            ),

            hoverlabel=dict(
                bgcolor="#151821",
                font_size=12
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displaylogo": False,
                "responsive": True
            }
        )

        # -----------------------------------------------
        # Yearly summary
        # -----------------------------------------------

        summary_cols = st.columns(
            min(4, len(yearly_df))
        )

        recent_years = (
            yearly_df
            .sort_values(
                "Year",
                ascending=False
            )
            .head(4)
        )

        for index, (_, row) in enumerate(
            recent_years.iterrows()
        ):

            if index >= len(summary_cols):
                break

            with summary_cols[index]:

                render_html(
                    f"""
                    <div class="glass" style="text-align:center;">
                        <div class="metric-label">
                            {int(row["Year"])}
                        </div>

                        <div class="metric-value">
                            {int(row["Projects"])}
                        </div>

                        <div style="
                            color:#858a99;
                            font-size:11px;
                            margin-top:5px;
                        ">
                            Projects
                        </div>
                    </div>
                    """
                )

    else:

        render_html(
            """
            <div class="section-title">
                Project Evolution
            </div>

            <div class="glass">
                <div style="
                    color:#858a99;
                    font-size:14px;
                ">
                    Project evolution data is not available
                    for this profile yet.
                </div>
            </div>
            """
        )

else:

    render_html(
        """
        <div class="section-title">
            Project Evolution
        </div>

        <div class="glass">
            <div style="
                color:#858a99;
                font-size:14px;
            ">
                Project evolution data is not available
                for this profile yet.
            </div>
        </div>
        """
    )


# ========================================================
# TECHNICAL ANALYSIS
# ========================================================
    with st.expander(
        "View technical analysis"
    ):

        feature_rows = []

        for key, value in features.items():

            feature_rows.append(
                {
                    "Feature": key,
                    "Value": value
                }
            )

        feature_df = pd.DataFrame(
            feature_rows
        )

        st.dataframe(
            feature_df,
            use_container_width=True,
            hide_index=True
        )


    # ========================================================
    # FOOTER
    # ========================================================

    st.divider()

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
