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
# PROJECT IMPORTS
# ============================================================

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
    page_icon="G",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    dedent(
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
            padding-top: 2.5rem;
            padding-bottom: 4rem;
        }

        /* ====================================================
           HERO
        ==================================================== */

        .hero {
            text-align: center;
            padding: 25px 10px;
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

        /* ====================================================
           CARDS
        ==================================================== */

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

        /* ====================================================
           SCORE
        ==================================================== */

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

        /* ====================================================
           SECTION
        ==================================================== */

        .section-title {
            color: white;
            font-size: 20px;
            font-weight: 700;
            margin: 22px 0 12px;
        }

        /* ====================================================
           INSIGHTS
        ==================================================== */

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

        /* ====================================================
           METRICS
        ==================================================== */

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

        /* ====================================================
           SEARCH
        ==================================================== */

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

        /* ====================================================
           MOBILE
        ==================================================== */

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
        """
    ),
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    dedent(
        """
        <div class="hero">

            <div class="hero-badge">
                GitHub Profile Intelligence
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
    ),
    unsafe_allow_html=True,
)


# ============================================================
# SEARCH
# ============================================================

search_col1, search_col2 = st.columns([5, 1])

with search_col1:

    username = st.text_input(
        "GitHub username",
        placeholder="e.g. torvalds",
        label_visibility="collapsed",
    )

with search_col2:

    analyze = st.button(
        "Analyze",
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

    if joblib is None:
        return None

    if not os.path.exists(MODEL_PATH):
        return None

    try:

        artifact = joblib.load(MODEL_PATH)

        if not isinstance(
            artifact,
            dict,
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
# PLOTLY CONFIG
# ============================================================

PLOTLY_CONFIG = {
    "displaylogo": False,
    "responsive": True,
    "displayModeBar": False,
}


# ============================================================
# YEARLY PROJECT ANALYSIS
# ============================================================

def build_yearly_project_data(repositories):

    """
    Creates yearly project statistics directly
    from GitHub repository data.

    This does not depend on repository_timeline(),
    so the yearly graph can still work even when
    timeline data is unavailable.
    """

    rows = []

    if not isinstance(
        repositories,
        list,
    ):
        return pd.DataFrame()

    for repo in repositories:

        if not isinstance(
            repo,
            dict,
        ):
            continue

        # ----------------------------------------------------
        # Find repository creation date
        # ----------------------------------------------------

        date_value = (
            repo.get("created_at")
            or repo.get("createdAt")
            or repo.get("date")
        )

        if not date_value:
            continue

        try:

            date = pd.to_datetime(
                date_value,
                errors="coerce",
            )

        except Exception:

            continue

        if pd.isna(date):
            continue

        # ----------------------------------------------------
        # Repository name
        # ----------------------------------------------------

        repo_name = (
            repo.get("name")
            or repo.get("full_name")
            or "Unknown"
        )

        # ----------------------------------------------------
        # Stars
        # ----------------------------------------------------

        stars_value = repo.get(
            "stargazers_count"
        )

        if stars_value is None:
            stars_value = repo.get(
                "stars",
                0,
            )

        try:

            stars_value = int(
                stars_value or 0
            )

        except Exception:

            stars_value = 0

        rows.append(
            {
                "Date": date,
                "Year": int(date.year),
                "Project": str(repo_name),
                "Stars": stars_value,
            }
        )

    if not rows:

        return pd.DataFrame()

    df = pd.DataFrame(rows)

    return df.sort_values(
        "Date"
    )


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
    # VALIDATE BUNDLE
    # ========================================================

    if not isinstance(
        bundle,
        dict,
    ):

        st.error(
            "GitHub API returned invalid data."
        )

        st.stop()


    # ========================================================
    # EXTRACT DATA
    # ========================================================

    try:

        user = bundle.get(
            "user",
            {},
        )

        repositories = bundle.get(
            "repositories",
            [],
        )

        languages = bundle.get(
            "languages",
            {},
        )

        features = extract_features(
            bundle
        )

        if not isinstance(
            features,
            dict,
        ):
            features = {}

        rubric_scores = calculate_score(
            features
        )

        if not isinstance(
            rubric_scores,
            dict,
        ):
            rubric_scores = {}

    except Exception as error:

        st.error(
            f"Analysis failed: {error}"
        )

        st.stop()


    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    artifact = load_model()

    predicted_level = rubric_scores.get(
        "level",
        "Beginner",
    )

    model_used = False

    if artifact is not None:

        try:

            model = artifact["model"]

            feature_names = artifact["features"]

            row = {}

            for feature_name in feature_names:

                row[feature_name] = features.get(
                    feature_name,
                    0,
                )

            X = pd.DataFrame(
                [row]
            )

            prediction = model.predict(
                X
            )

            if len(prediction) > 0:

                predicted_level = str(
                    prediction[0]
                )

                model_used = True

        except Exception:

            predicted_level = rubric_scores.get(
                "level",
                "Beginner",
            )


    # ========================================================
    # PROFILE HEADER
    # ========================================================

    if not isinstance(
        user,
        dict,
    ):
        user = {}

    avatar = html.escape(
        str(
            user.get(
                "avatar_url",
                "",
            )
        ),
        quote=True,
    )

    name = html.escape(
        str(
            user.get(
                "name"
            )
            or username
        )
    )

    safe_username = html.escape(
        username
    )

    bio = html.escape(
        str(
            user.get(
                "bio"
            )
            or "No bio available."
        )
    )

    profile_html = dedent(
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

    st.markdown(
        profile_html,
        unsafe_allow_html=True,
    )


    # ========================================================
    # SCORE + SIGNALS + METRICS
    # ========================================================

    score_col, signals_col, metrics_col = st.columns(
        [1.15, 2, 1.15]
    )


    # ========================================================
    # SCORE
    # ========================================================

    with score_col:

        overall_score = rubric_scores.get(
            "overall_score",
            0,
        )

        try:

            overall_score = int(
                round(
                    float(
                        overall_score
                    )
                )
            )

        except Exception:

            overall_score = 0

        overall_score = max(
            0,
            min(
                100,
                overall_score,
            ),
        )

        st.markdown(
            dedent(
                f"""
                <div class="score-card">

                    <div class="score-number">
                        {overall_score}
                    </div>

                    <div class="score-label">
                        Overall Score / 100
                    </div>

                    <div class="level">
                        {html.escape(
                            str(predicted_level)
                        )}
                    </div>

                </div>
                """
            ),
            unsafe_allow_html=True,
        )


    # ========================================================
    # SIGNALS
    # ========================================================

    with signals_col:

        st.markdown(
            dedent(
                """
                <div class="glass">

                    <div class="section-title">
                        Skill Signals
                    </div>

                </div>
                """
            ),
            unsafe_allow_html=True,
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
                        0,
                    ),
                    rubric_scores.get(
                        "project_score",
                        0,
                    ),
                    rubric_scores.get(
                        "collaboration_score",
                        0,
                    ),
                    rubric_scores.get(
                        "consistency_score",
                        0,
                    ),
                    rubric_scores.get(
                        "community_score",
                        0,
                    ),
                ],
            }
        )

        signal_data["Score"] = pd.to_numeric(
            signal_data["Score"],
            errors="coerce",
        ).fillna(0)

        signal_data["Score"] = signal_data[
            "Score"
        ].clip(
            0,
            100,
        )

        fig = px.bar(
            signal_data,
            x="Score",
            y="Signal",
            orientation="h",
            text="Score",
            template="plotly_dark",
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
                t=10,
                b=10,
            ),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(
                title="Score",
                range=[0, 110],
            ),
            yaxis=dict(
                title="",
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


    # ========================================================
    # METRICS
    # ========================================================

    with metrics_col:

        public_repos = features.get(
            "public_repos",
            0,
        )

        followers = features.get(
            "followers",
            0,
        )

        languages_count = features.get(
            "languages_count",
            0,
        )

        st.markdown(
            dedent(
                f"""
                <div class="glass">

                    <div class="metric-item">

                        <div class="metric-label">
                            PUBLIC REPOS
                        </div>

                        <div class="metric-value">
                            {public_repos}
                        </div>

                    </div>

                    <div class="metric-item">

                        <div class="metric-label">
                            FOLLOWERS
                        </div>

                        <div class="metric-value">
                            {followers}
                        </div>

                    </div>

                    <div class="metric-item">

                        <div class="metric-label">
                            LANGUAGES
                        </div>

                        <div class="metric-value">
                            {languages_count}
                        </div>

                    </div>

                </div>
                """
            ),
            unsafe_allow_html=True,
        )


    # ========================================================
    # INSIGHTS
    # ========================================================

    try:

        insights_result = generate_insights(
            features,
            rubric_scores,
        )

        if (
            isinstance(
                insights_result,
                tuple,
            )
            and len(insights_result) >= 2
        ):

            strengths = insights_result[0]
            improvements = insights_result[1]

        else:

            strengths = []
            improvements = []

    except Exception:

        strengths = []
        improvements = []


    insights_col1, insights_col2 = st.columns(
        2
    )


    # ========================================================
    # STRENGTHS
    # ========================================================

    with insights_col1:

        st.markdown(
            """
            <div class="section-title">
                Strengths
            </div>
            """,
            unsafe_allow_html=True,
        )

        if strengths:

            for item in strengths:

                safe_item = html.escape(
                    str(item)
                )

                st.markdown(
                    f"""
                    <div class="insight">
                        + {safe_item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <div class="insight">
                    No major strengths detected yet.
                </div>
                """,
                unsafe_allow_html=True,
            )


    # ========================================================
    # IMPROVEMENTS
    # ========================================================

    with insights_col2:

        st.markdown(
            """
            <div class="section-title">
                Areas to Improve
            </div>
            """,
            unsafe_allow_html=True,
        )

        if improvements:

            for item in improvements:

                safe_item = html.escape(
                    str(item)
                )

                st.markdown(
                    f"""
                    <div class="insight">
                        -> {safe_item}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        else:

            st.markdown(
                """
                <div class="insight">
                    Keep building and contributing!
                </div>
                """,
                unsafe_allow_html=True,
            )


    # ========================================================
    # TECHNOLOGY STACK
    # ========================================================

    if isinstance(
        languages,
        dict,
    ) and languages:

        st.markdown(
            """
            <div class="section-title">
                Technology Stack
            </div>
            """,
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

        language_df["Bytes"] = pd.to_numeric(
            language_df["Bytes"],
            errors="coerce",
        ).fillna(0)

        language_df = language_df[
            language_df["Bytes"] > 0
        ]

        language_df = (
            language_df
            .sort_values(
                "Bytes",
                ascending=False,
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
                    template="plotly_dark",
                )

                fig.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                )

                fig.update_layout(
                    height=max(
                        300,
                        len(language_df) * 45,
                    ),
                    margin=dict(
                        l=0,
                        r=35,
                        t=10,
                        b=10,
                    ),
                    showlegend=False,
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(
                        title="Usage %",
                        range=[0, 110],
                    ),
                    yaxis=dict(
                        title="",
                    ),
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                )


    # ========================================================
    # PROJECT EVOLUTION
    # ========================================================

    st.markdown(
        """
        <div class="section-title">
            Project Evolution
        </div>
        """,
        unsafe_allow_html=True,
    )


    # ========================================================
    # BUILD YEARLY DATA DIRECTLY
    # ========================================================

    yearly_df = build_yearly_project_data(
        repositories
    )


    # ========================================================
    # FALLBACK TO repository_timeline()
    # ========================================================

    if yearly_df.empty:

        try:

            timeline = repository_timeline(
                repositories
            )

        except Exception:

            timeline = []

        if isinstance(
            timeline,
            list,
        ) and timeline:

            fallback_rows = []

            for item in timeline:

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                date_value = (
                    item.get("date")
                    or item.get("created_at")
                    or item.get("createdAt")
                )

                if not date_value:
                    continue

                try:

                    date_value = pd.to_datetime(
                        date_value,
                        errors="coerce",
                    )

                except Exception:

                    continue

                if pd.isna(date_value):
                    continue

                try:

                    stars = int(
                        item.get(
                            "stars",
                            0,
                        )
                        or 0
                    )

                except Exception:

                    stars = 0

                project_name = (
                    item.get("name")
                    or item.get("full_name")
                    or "Unknown"
                )

                fallback_rows.append(
                    {
                        "Date": date_value,
                        "Year": int(
                            date_value.year
                        ),
                        "Project": str(
                            project_name
                        ),
                        "Stars": stars,
                    }
                )

            if fallback_rows:

                yearly_df = pd.DataFrame(
                    fallback_rows
                )

                yearly_df = yearly_df.sort_values(
                    "Date"
                )


    # ========================================================
    # DRAW YEARLY GRAPH
    # ========================================================

    if not yearly_df.empty:

        yearly_summary = (
            yearly_df
            .groupby("Year")
            .agg(
                Projects=(
                    "Project",
                    "count",
                ),
                Stars=(
                    "Stars",
                    "sum",
                ),
            )
            .reset_index()
        )

        yearly_summary["Year"] = (
            pd.to_numeric(
                yearly_summary["Year"],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

        yearly_summary["Projects"] = (
            pd.to_numeric(
                yearly_summary["Projects"],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

        yearly_summary["Stars"] = (
            pd.to_numeric(
                yearly_summary["Stars"],
                errors="coerce",
            )
            .fillna(0)
            .astype(int)
        )

        yearly_summary = yearly_summary.sort_values(
            "Year"
        )


        # ====================================================
        # YEARLY PROJECT COUNT GRAPH
        # ====================================================

        fig = px.line(
            yearly_summary,
            x="Year",
            y="Projects",
            markers=True,
            text="Projects",
            template="plotly_dark",
        )

        fig.update_traces(
            line=dict(
                width=3,
            ),
            marker=dict(
                size=8,
            ),
            textposition="top center",
        )

        fig.update_layout(
            height=380,
            margin=dict(
                l=0,
                r=0,
                t=20,
                b=20,
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            showlegend=False,
            xaxis=dict(
                title="Year",
                dtick=1,
            ),
            yaxis=dict(
                title="Projects Created",
                rangemode="tozero",
            ),
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


        # ====================================================
        # YEARLY STARS GRAPH
        # ====================================================

        if yearly_summary["Stars"].sum() > 0:

            st.markdown(
                """
                <div class="section-title">
                    Yearly Star Growth
                </div>
                """,
                unsafe_allow_html=True,
            )

            fig_stars = px.bar(
                yearly_summary,
                x="Year",
                y="Stars",
                text="Stars",
                template="plotly_dark",
            )

            fig_stars.update_traces(
                textposition="outside"
            )

            fig_stars.update_layout(
                height=330,
                margin=dict(
                    l=0,
                    r=0,
                    t=20,
                    b=20,
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                xaxis=dict(
                    title="Year",
                    dtick=1,
                ),
                yaxis=dict(
                    title="Stars",
                    rangemode="tozero",
                ),
            )

            st.plotly_chart(
                fig_stars,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )


        # ====================================================
        # YEARLY SUMMARY CARDS
        # ====================================================

        summary_col1, summary_col2, summary_col3 = st.columns(
            3
        )

        with summary_col1:

            total_projects = int(
                yearly_summary["Projects"].sum()
            )

            st.metric(
                "Total Projects",
                total_projects,
            )

        with summary_col2:

            active_years = int(
                yearly_summary["Year"].nunique()
            )

            st.metric(
                "Active Years",
                active_years,
            )

        with summary_col3:

            total_stars = int(
                yearly_summary["Stars"].sum()
            )

            st.metric(
                "Total Stars",
                total_stars,
            )


    else:

        st.markdown(
            dedent(
                """
                <div class="glass">

                    <div style="
                        color:#858a99;
                        font-size:14px;
                        line-height:1.6;
                    ">

                        Project creation dates are not
                        available for this profile yet.

                    </div>

                </div>
                """
            ),
            unsafe_allow_html=True,
        )


    # ========================================================
    # TECHNICAL ANALYSIS
    # ========================================================

    with st.expander(
        "View technical analysis"
    ):

        feature_rows = []

        if isinstance(
            features,
            dict,
        ):

            for feature_name, feature_value in features.items():

                feature_rows.append(
                    {
                        "Feature": str(
                            feature_name
                        ),
                        "Value": feature_value,
                    }
                )

        if feature_rows:

            feature_df = pd.DataFrame(
                feature_rows
            )

            st.dataframe(
                feature_df,
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No technical feature data available."
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
            "Prediction powered by the trained "
            "machine-learning model."
        )

    else:

        st.caption(
            "Prediction currently uses the "
            "activity-based scoring system."
)
