from datetime import datetime, timezone
import math


FEATURE_NAMES = [
    "public_repos",
    "followers",
    "following",
    "public_gists",
    "account_age_days",
    "original_repos",
    "active_repos",
    "total_stars",
    "total_forks",
    "open_issues",
    "watchers",
    "total_repo_size_kb",
    "average_repo_size_kb",
    "languages_count",
    "recent_public_events",
    "recent_push_events",
    "recent_pr_events",
    "recent_issue_events",
    "recent_review_events",
    "latest_repo_update_days",
]


def safe_number(value):

    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def days_since(date_string):

    if not date_string:
        return 0

    try:
        date = datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )

        now = datetime.now(timezone.utc)

        return max(
            0,
            (now - date).days
        )

    except ValueError:
        return 0


def extract_features(bundle):

    user = bundle.get("user", {})
    repositories = bundle.get("repositories", [])
    events = bundle.get("events", [])
    languages = bundle.get("languages", {})

    original_repos = 0
    active_repos = 0

    total_stars = 0
    total_forks = 0
    open_issues = 0
    watchers = 0

    total_repo_size = 0

    latest_update_days = None

    for repo in repositories:

        if not repo.get("fork", False):
            original_repos += 1

        if repo.get("archived", False) is False:
            active_repos += 1

        total_stars += safe_number(
            repo.get("stargazers_count")
        )

        total_forks += safe_number(
            repo.get("forks_count")
        )

        open_issues += safe_number(
            repo.get("open_issues_count")
        )

        watchers += safe_number(
            repo.get("watchers_count")
        )

        total_repo_size += safe_number(
            repo.get("size")
        )

        update_days = days_since(
            repo.get("updated_at")
        )

        if latest_update_days is None:
            latest_update_days = update_days
        else:
            latest_update_days = min(
                latest_update_days,
                update_days
            )

    if latest_update_days is None:
        latest_update_days = 0

    recent_events = 0
    push_events = 0
    pr_events = 0
    issue_events = 0
    review_events = 0

    for event in events:

        event_date = event.get("created_at")

        age = days_since(event_date)

        if age <= 90:

            recent_events += 1

            event_type = event.get("type", "")

            if event_type == "PushEvent":
                push_events += 1

            elif event_type in [
                "PullRequestEvent"
            ]:
                pr_events += 1

            elif event_type in [
                "IssuesEvent"
            ]:
                issue_events += 1

            elif event_type in [
                "PullRequestReviewEvent"
            ]:
                review_events += 1

    created_days_ago = days_since(
        user.get("created_at")
    )

    feature_data = {

        "public_repos": int(
            safe_number(user.get("public_repos"))
        ),

        "followers": int(
            safe_number(user.get("followers"))
        ),

        "following": int(
            safe_number(user.get("following"))
        ),

        "public_gists": int(
            safe_number(user.get("public_gists"))
        ),

        "account_age_days": int(
            created_days_ago
        ),

        "original_repos": original_repos,

        "active_repos": active_repos,

        "total_stars": int(total_stars),

        "total_forks": int(total_forks),

        "open_issues": int(open_issues),

        "watchers": int(watchers),

        "total_repo_size_kb": int(
            total_repo_size
        ),

        "average_repo_size_kb": (
            round(
                total_repo_size / len(repositories),
                2
            )
            if repositories
            else 0
        ),

        "languages_count": len(languages),

        "recent_public_events": recent_events,

        "recent_push_events": push_events,

        "recent_pr_events": pr_events,

        "recent_issue_events": issue_events,

        "recent_review_events": review_events,

        "latest_repo_update_days": int(
            latest_update_days
        ),
    }

    return feature_data


def clamp(value, minimum=0, maximum=100):

    return max(
        minimum,
        min(maximum, value)
    )


def logarithmic_score(value, maximum):

    if value <= 0:
        return 0

    return clamp(
        (math.log1p(value) /
         math.log1p(maximum)) * 100
    )


def calculate_score(features):

    # -------------------------
    # ACTIVITY SCORE
    # -------------------------

    push_score = logarithmic_score(
        features["recent_push_events"],
        100
    )

    event_score = logarithmic_score(
        features["recent_public_events"],
        150
    )

    activity_score = (
        push_score * 0.65 +
        event_score * 0.35
    )

    # -------------------------
    # PROJECT SCORE
    # -------------------------

    repo_score = logarithmic_score(
        features["original_repos"],
        30
    )

    star_score = logarithmic_score(
        features["total_stars"],
        100
    )

    fork_score = logarithmic_score(
        features["total_forks"],
        50
    )

    project_score = (
        repo_score * 0.45 +
        star_score * 0.35 +
        fork_score * 0.20
    )

    # -------------------------
    # COLLABORATION SCORE
    # -------------------------

    pr_score = logarithmic_score(
        features["recent_pr_events"],
        30
    )

    issue_score = logarithmic_score(
        features["recent_issue_events"],
        30
    )

    review_score = logarithmic_score(
        features["recent_review_events"],
        20
    )

    collaboration_score = (
        pr_score * 0.40 +
        issue_score * 0.30 +
        review_score * 0.30
    )

    # -------------------------
    # CONSISTENCY SCORE
    # -------------------------

    if features["latest_repo_update_days"] <= 30:
        consistency_score = 100

    elif features["latest_repo_update_days"] <= 90:
        consistency_score = 75

    elif features["latest_repo_update_days"] <= 180:
        consistency_score = 50

    elif features["latest_repo_update_days"] <= 365:
        consistency_score = 30

    else:
        consistency_score = 10

    # -------------------------
    # COMMUNITY SCORE
    # -------------------------

    followers_score = logarithmic_score(
        features["followers"],
        500
    )

    community_score = followers_score

    # -------------------------
    # FINAL SCORE
    # -------------------------

    overall = (
        activity_score * 0.30 +
        project_score * 0.25 +
        collaboration_score * 0.20 +
        consistency_score * 0.15 +
        community_score * 0.10
    )

    overall = round(
        clamp(overall),
        1
    )

    if overall < 40:
        level = "Beginner"

    elif overall < 70:
        level = "Intermediate"

    else:
        level = "Advanced"

    return {
        "overall_score": overall,
        "activity_score": round(activity_score, 1),
        "project_score": round(project_score, 1),
        "collaboration_score": round(
            collaboration_score,
            1
        ),
        "consistency_score": round(
            consistency_score,
            1
        ),
        "community_score": round(
            community_score,
            1
        ),
        "level": level,
    }


def repository_timeline(repositories):

    timeline = []

    for repo in repositories:

        created_at = repo.get("created_at")

        if not created_at:
            continue

        try:
            date = datetime.fromisoformat(
                created_at.replace(
                    "Z",
                    "+00:00"
                )
            )

            timeline.append({
                "date": date,
                "name": repo.get(
                    "name",
                    "Unknown"
                ),
                "stars": repo.get(
                    "stargazers_count",
                    0
                )
            })

        except ValueError:
            continue

    timeline.sort(
        key=lambda item: item["date"]
    )

    return timeline


def generate_insights(features, scores):

    strengths = []
    improvements = []

    if scores["activity_score"] >= 65:
        strengths.append(
            "Strong recent GitHub activity"
        )
    else:
        improvements.append(
            "Increase regular coding activity"
        )

    if scores["project_score"] >= 65:
        strengths.append(
            "Good project-building signals"
        )
    else:
        improvements.append(
            "Build and maintain more original projects"
        )

    if scores["collaboration_score"] >= 60:
        strengths.append(
            "Good collaboration signals"
        )
    else:
        improvements.append(
            "Participate more in issues and pull requests"
        )

    if features["languages_count"] >= 4:
        strengths.append(
            "Good exposure to multiple technologies"
        )
    elif features["languages_count"] <= 1:
        improvements.append(
            "Explore another relevant programming language"
        )

    if features["total_stars"] >= 20:
        strengths.append(
            "Projects are receiving community attention"
        )

    if features["recent_push_events"] < 5:
        improvements.append(
            "Maintain a more consistent commit pattern"
        )

    if not strengths:
        strengths.append(
            "You have an active starting point to build on"
        )

    if not improvements:
        improvements.append(
            "Continue improving project quality and consistency"
        )

    return strengths, improvements
