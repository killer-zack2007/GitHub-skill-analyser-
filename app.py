import os

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
    """
<style>

.stApp {
    background-color: #08090d;
}

.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 {
    color: white !important;
}

p, label {
    color: #b5bac7 !important;
}

.hero-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 5px;
}

.hero-subtitle {
    text-align: center;
    color: #9da3b2;
    font-size: 16px;
    margin-bottom: 30px;
}

.hero-badge {
    text-align: center;
    color: #a78bfa;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 10px;
}

.score-box {
    background-color: #151620;
    border: 1px solid #292b38;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    min-height: 220px;
}

.score-number {
    font-size: 58px;
    font-weight: 800;
    color: white;
}

.score-text {
    color: #9da3b2;
    font-size: 14px;
}

.profile-title {
    font-size: 25px;
    font-weight: 700;
    color: white;
}

.profile-login {
    color: #858b9a;
    font-size: 14px;
}

.profile-bio {
    color: #b5bac7;
    font-size: 14px;
}

.section-title {
    font-size: 22px;
    font-weight: 700;
    color: white;
    margin-top: 25px;
    margin-bottom: 12px;
}

div[data-testid="stMetric"] {
    background-color: #151620;
    border: 1px solid #292b38;
    padding: 15px;
    border-radius: 15px;
}

div[data-testid="stMetricValue"] {
    color: white;
}

div[data-testid="stMetricLabel"] {
    color: #9da3b2;
}

div[data-testid="stTextInput"] input {
    background-color: #151620;
    color: white;
    border: 1px solid #303342;
    border-radius: 12px;
}

.stButton button {
    border-radius: 12px;
    font-weight: 600;
}

[data-testid="stExpander"] {
    background-color: #111219;
    border: 1px solid #292b38;
    border-radius: 14px;
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

st.markdown(
    '<div class="hero-badge">GITHUB PROFILE INTELLIGENCE</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="hero-title">GitHub Pulse</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero-subtitle">
Analyze GitHub activity, projects, collaboration,
technology and consistency to estimate developer skill level.
</div>
""",
    unsafe_allow_html=True,
)


# ============================================================
# SEARCH
# ============================================================

search_col1, search_col2 = st.columns(
    [5, 1]
)

with search_col1:

    username = st.text_input(
        "GitHub username",
        placeholder="Enter GitHub username",
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

        artifact = joblib.load(
            MODEL_PATH
        )

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
# YEARLY PROJECT DATA
# ============================================================

def build_yearly_project_data(
    repositories,
):

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

        repo_name = (
            repo.get("name")
            or repo.get("full_name")
            or "Unknown"
        )

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
                "Year": int(
                    date.year
                ),
                "Project": str(
                    repo_name
                ),
                "Stars": stars_value,
            }
        )

    if not rows:

        return pd.DataFrame()

    df = pd.DataFrame(
        rows
    )

    return df.sort_values(
        "Date"
    )


# ============================================================
# MAIN ANALYSIS
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
    # FETCH DATA
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
    # VALIDATE API RESPONSE
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
    # PROFILE
    # ========================================================

    if not isinstance(
        user,
        dict,
    ):

        user = {}


    avatar_url = str(
        user.get(
            "avatar_url",
            "",
        )
    )

    profile_name = str(
        user.get(
            "name"
        )
        or username
    )

    profile_bio = str(
        user.get(
            "bio"
        )
        or "No bio available."
    )


    # ========================================================
    # PROFILE SECTION
    # ========================================================

    st.markdown(
        '<div class="section-title">Profile</div>',
        unsafe_allow_html=True,
    )

    profile_col1, profile_col2 = st.columns(
        [1, 4]
    )

    with profile_col1:

        if avatar_url:

            st.image(
                avatar_url,
                width=100,
            )

    with profile_col2:

        st.markdown(
            f'<div class="profile-title">{profile_name}</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="profile-login">@{username}</div>',
            unsafe_allow_html=True,
        )

        st.write(
            profile_bio
        )


    # ========================================================
    # SCORE / SIGNALS / METRICS
    # ========================================================

    score_col, signal_col, metric_col = st.columns(
        [1.1, 2, 1.2]
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
            '<div class="section-title">Overall Score</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
<div class="score-box">
    <div class="score-number">{overall_score}</div>
    <div class="score-text">Score out of 100</div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.write("")

        st.info(
            f"Level: {predicted_level}"
        )


    # ========================================================
    # SIGNALS
    # ========================================================

    with signal_col:

        st.markdown(
            '<div class="section-title">Skill Signals</div>',
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
            height=320,
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

    with metric_col:

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
            '<div class="section-title">Metrics</div>',
            unsafe_allow_html=True,
        )

        st.metric(
            "Public Repositories",
            public_repos,
        )

        st.metric(
            "Followers",
            followers,
        )

        st.metric(
            "Languages",
            languages_count,
        )


    # ========================================================
    # INSIGHTS
    # ========================================================

    st.markdown(
        '<div class="section-title">Insights</div>',
        unsafe_allow_html=True,
    )

    try:

        insight_result = generate_insights(
            features,
            rubric_scores,
        )

        if (
            isinstance(
                insight_result,
                tuple,
            )
            and len(insight_result) >= 2
        ):

            strengths = insight_result[0]
            improvements = insight_result[1]

        else:

            strengths = []
            improvements = []

    except Exception:

        strengths = []
        improvements = []


    insight_col1, insight_col2 = st.columns(
        2
    )


    # ========================================================
    # STRENGTHS
    # ========================================================

    with insight_col1:

        st.subheader(
            "Strengths"
        )

        if strengths:

            for item in strengths:

                st.success(
                    str(item)
                )

        else:

            st.info(
                "No major strengths detected yet."
            )


    # ========================================================
    # IMPROVEMENTS
    # ========================================================

    with insight_col2:

        st.subheader(
            "Areas to Improve"
        )

        if improvements:

            for item in improvements:

                st.warning(
                    str(item)
                )

        else:

            st.info(
                "Keep building and contributing."
            )


    # ========================================================
    # TECHNOLOGY STACK
    # ========================================================

    if (
        isinstance(
            languages,
            dict,
        )
        and languages
    ):

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

                language_chart = px.bar(
                    language_df.sort_values(
                        "Usage"
                    ),
                    x="Usage",
                    y="Language",
                    orientation="h",
                    text="Usage",
                    template="plotly_dark",
                )

                language_chart.update_traces(
                    texttemplate="%{text:.1f}%",
                    textposition="outside",
                )

                language_chart.update_layout(
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
                    language_chart,
                    use_container_width=True,
                    config=PLOTLY_CONFIG,
                )


    # ========================================================
    # PROJECT EVOLUTION
    # ========================================================

    st.markdown(
        '<div class="section-title">Project Evolution</div>',
        unsafe_allow_html=True,
    )

    yearly_df = build_yearly_project_data(
        repositories
    )


    # ========================================================
    # FALLBACK TIMELINE
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

                if pd.isna(
                    date_value
                ):
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


    # ========================================================
    # YEARLY GRAPH
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


        # ----------------------------------------------------
        # PROJECTS PER YEAR
        # ----------------------------------------------------

        st.subheader(
            "Projects Created Per Year"
        )

        yearly_chart = px.line(
            yearly_summary,
            x="Year",
            y="Projects",
            markers=True,
            text="Projects",
            template="plotly_dark",
        )

        yearly_chart.update_traces(
            line=dict(
                width=3,
            ),
            marker=dict(
                size=9,
            ),
            textposition="top center",
        )

        yearly_chart.update_layout(
            height=400,
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
            yearly_chart,
            use_container_width=True,
            config=PLOTLY_CONFIG,
        )


        # ----------------------------------------------------
        # YEARLY STAR GROWTH
        # ----------------------------------------------------

        if yearly_summary["Stars"].sum() > 0:

            st.subheader(
                "Yearly Star Growth"
            )

            stars_chart = px.bar(
                yearly_summary,
                x="Year",
                y="Stars",
                text="Stars",
                template="plotly_dark",
            )

            stars_chart.update_traces(
                textposition="outside"
            )

            stars_chart.update_layout(
                height=350,
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
                stars_chart,
                use_container_width=True,
                config=PLOTLY_CONFIG,
            )


        # ----------------------------------------------------
        # YEARLY SUMMARY
        # ----------------------------------------------------

        summary_col1, summary_col2, summary_col3 = st.columns(
            3
        )

        with summary_col1:

            st.metric(
                "Total Projects",
                int(
                    yearly_summary[
                        "Projects"
                    ].sum()
                ),
            )

        with summary_col2:

            st.metric(
                "Active Years",
                int(
                    yearly_summary[
                        "Year"
                    ].nunique()
                ),
            )

        with summary_col3:

            st.metric(
                "Total Stars",
                int(
                    yearly_summary[
                        "Stars"
                    ].sum()
                ),
            )

    else:

        st.info(
            "Project creation dates are not available for this profile."
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
        "estimate and is not a definitive measure "
        "of programming ability."
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
