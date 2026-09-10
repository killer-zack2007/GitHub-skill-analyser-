from pathlib import Path
import sys

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.analyzer import (
    extract_features,
    generate_insights,
    repository_timeline,
    score_features,
)
from src.github_api import GitHubAPIError, get_profile_bundle


st.set_page_config(
    page_title="GitHub Pulse",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: Inter, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(120, 90, 255, .12), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(0, 220, 190, .08), transparent 25%),
            #08090d;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .brand {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #f5f7ff;
    }

    .hero {
        padding: 3.5rem 0 2rem;
    }

    .eyebrow {
        display: inline-block;
        padding: .35rem .65rem;
        border: 1px solid rgba(255,255,255,.12);
        border-radius: 999px;
        color: #b9c0d4;
        font-size: .78rem;
        letter-spacing: .08em;
        text-transform: uppercase;
        background: rgba(255,255,255,.035);
    }

    .hero h1 {
        font-family: "Space Grotesk", sans-serif;
        font-size: clamp(2.8rem, 7vw, 5.8rem);
        line-height: .94;
        letter-spacing: -.065em;
        margin: 1rem 0;
        color: #fff;
    }

    .hero p {
        max-width: 650px;
        color: #9da5b8;
        font-size: 1.05rem;
        line-height: 1.7;
    }

    .glass {
        border: 1px solid rgba(255,255,255,.10);
        background: rgba(255,255,255,.045);
        backdrop-filter: blur(16px);
        border-radius: 22px;
        padding: 1.4rem;
        box-shadow: 0 20px 70px rgba(0,0,0,.22);
    }

    .score {
        font-family: "Space Grotesk", sans-serif;
        font-size: 4.5rem;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -.07em;
        color: #fff;
    }

    .level {
        color: #aeb6ca;
        font-size: .82rem;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-top: .55rem;
    }

    .muted {
        color: #8f98ac;
    }

    .section-title {
        font-family: "Space Grotesk", sans-serif;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 1.8rem 0 .8rem;
        color: #fff;
    }

    .insight {
        border: 1px solid rgba(255,255,255,.08);
        background: rgba(255,255,255,.035);
        padding: .9rem 1rem;
        border-radius: 14px;
        margin: .5rem 0;
        color: #dce1ee;
    }

    div[data-testid="stMetric"] {
        border: 1px solid rgba(255,255,255,.08);
        background: rgba(255,255,255,.035);
        padding: 1rem;
        border-radius: 16px;
    }

    div[data-testid="stTextInput"] input {
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.14);
        border-radius: 14px;
        color: #fff;
        padding: .8rem 1rem;
    }

    .stButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,.14);
        padding: .72rem 1rem;
        font-weight: 700;
        background: #fff;
        color: #08090d;
    }

    .footer {
        margin-top: 4rem;
        padding-top: 1.2rem;
        border-top: 1px solid rgba(255,255,255,.08);
        color: #70788b;
        font-size: .82rem;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="brand">◈ GitHub Pulse</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <span class="eyebrow">Developer intelligence · public GitHub data</span>
        <h1>See the signal<br>behind your GitHub.</h1>
        <p>
            Analyze public GitHub activity, projects, languages and
            collaboration patterns in one clean dashboard.
            The result is an activity-based estimate, not a measure
            of actual programming ability.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("analyze_form"):
    col1, col2 = st.columns([4, 1])

    with col1:
        username = st.text_input(
            "GitHub username",
            placeholder="e.g. octocat",
            label_visibility="collapsed",
        )

    with col2:
        submitted = st.form_submit_button("Analyze →")

if submitted:
    username = username.strip()

    if not username:
        st.warning("Enter a GitHub username first.")
        st.stop()

    with st.spinner("Reading public GitHub signals..."):
        try:
            bundle = get_profile_bundle(username)
        except GitHubAPIError as exc:
            st.error(str(exc))
            st.stop()

    features = extract_features(bundle)
    rule_scores = score_features(features)

    model_path = ROOT / "models" / "github_skill_model.joblib"
    ml_prediction = None

    if model_path.exists():
        try:
            artifact = joblib.load(model_path)
            model = artifact["model"]
            model_features = artifact["features"]

            row = pd.DataFrame(
                [
                    {
                        feature: features.get(feature, 0)
                        for feature in model_features
                    }
                ]
            )

            ml_prediction = str(model.predict(row)[0])
        except Exception:
            ml_prediction = None

    user = bundle["user"]
    repos = bundle["repos"]
    timeline = repository_timeline(repos)

    display_level = ml_prediction or rule_scores["level"]
    method = "ML model" if ml_prediction else "activity rubric"

    strengths, improvements = generate_insights(
        features,
        rule_scores,
    )

    st.markdown(
        '<div class="section-title">Profile snapshot</div>',
        unsafe_allow_html=True,
    )

    profile_col, score_col = st.columns([2.3, 1])

    with profile_col:
        avatar = user.get("avatar_url", "")
        name = user.get("name") or user.get("login", username)
        bio = user.get("bio") or "No public bio."

        st.markdown(
            f"""
            <div class="glass">
                <div style="display:flex;gap:18px;align-items:center;">
                    <img src="{avatar}" width="76" height="76"
                         style="border-radius:20px;border:1px solid rgba(255,255,255,.12);">
                    <div>
                        <div style="font-size:1.45rem;font-weight:800;color:#fff;">
                            {name}
                        </div>
                        <div class="muted">
                            @{user.get('login', username)}
                        </div>
                        <div style="margin-top:8px;color:#aab2c5;">
                            {bio}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with score_col:
        st.markdown(
            f"""
            <div class="glass">
                <div class="score">{rule_scores['overall']:.0f}</div>
                <div class="level">
                    {display_level} · {method}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="section-title">At a glance</div>',
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Repositories", int(features["original_repos"]))
    m2.metric("Followers", int(features["followers"]))
    m3.metric("Stars", int(features["total_stars"]))
    m4.metric("Languages", int(features["languages_count"]))
    m5.metric("Recent events", int(features["recent_public_events"]))

    st.markdown(
        '<div class="section-title">Skill signals</div>',
        unsafe_allow_html=True,
    )

    signal_cols = st.columns(5)

    signals = [
        ("Activity", rule_scores["activity"]),
        ("Projects", rule_scores["project"]),
        ("Collaboration", rule_scores["collaboration"]),
        ("Consistency", rule_scores["consistency"]),
        ("Community", rule_scores["community"]),
    ]

    for col, (label, value) in zip(signal_cols, signals):
        with col:
            st.metric(label, f"{value:.0f}/100")

    left, right = st.columns(2)

    with left:
        st.markdown(
            '<div class="section-title">Strengths</div>',
            unsafe_allow_html=True,
        )

        for item in strengths:
            st.markdown(
                f'<div class="insight">✦ {item}</div>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            '<div class="section-title">Areas to improve</div>',
            unsafe_allow_html=True,
        )

        for item in improvements:
            st.markdown(
                f'<div class="insight">↗ {item}</div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">Project evolution</div>',
        unsafe_allow_html=True,
    )

    if not timeline.empty:
        chart = px.line(
            timeline,
            x="date",
            y="cumulative_projects",
            markers=True,
            hover_data=["repository", "stars"],
        )

        chart.update_layout(
            height=380,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#aab2c5"),
            xaxis_title=None,
            yaxis_title="Cumulative original repositories",
        )

        st.plotly_chart(
            chart,
            use_container_width=True,
        )

        st.caption(
            "This timeline shows repository creation activity. "
            "It is a proxy for project growth, not a direct measurement "
            "of skill growth."
        )
    else:
        st.info(
            "Not enough public repository history to draw the timeline."
        )

    st.markdown(
        '<div class="section-title">Language footprint</div>',
        unsafe_allow_html=True,
    )

    languages = bundle["languages"]

    if languages:
        lang_df = (
            pd.DataFrame(
                {
                    "language": list(languages.keys()),
                    "bytes": list(languages.values()),
                }
            )
            .sort_values("bytes", ascending=False)
            .head(10)
        )

        fig = px.bar(
            lang_df,
            x="bytes",
            y="language",
            orientation="h",
        )

        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#aab2c5"),
            xaxis_title="Code bytes detected by GitHub",
            yaxis_title=None,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )
    else:
        st.info(
            "No language data was returned for the analyzed repositories."
        )

    with st.expander("Technical feature data"):
        feature_df = pd.DataFrame(
            [
                {
                    "feature": key,
                    "value": (
                        round(value, 3)
                        if isinstance(value, float)
                        else value
                    ),
                }
                for key, value in features.items()
            ]
        )

        st.dataframe(
            feature_df,
            use_container_width=True,
            hide_index=True,
        )

st.markdown(
    """
    <div class="footer">
        GitHub Pulse · Python · Streamlit · GitHub API · Public activity only
    </div>
    """,
    unsafe_allow_html=True,
)
