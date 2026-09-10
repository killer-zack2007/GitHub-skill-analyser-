import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.github.com"

TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def github_get(endpoint, params=None):
    url = f"{BASE_URL}{endpoint}"

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=20
    )

    if response.status_code == 404:
        raise ValueError("GitHub user or resource not found.")

    if response.status_code == 403:
        raise ValueError(
            "GitHub API rate limit reached. Please try again later."
        )

    if not response.ok:
        raise ValueError(
            f"GitHub API error: {response.status_code}"
        )

    return response.json()


def get_user(username):
    return github_get(f"/users/{username}")


def get_repositories(username, max_pages=4, per_page=100):
    repositories = []

    for page in range(1, max_pages + 1):

        data = github_get(
            f"/users/{username}/repos",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "updated",
                "direction": "desc",
                "type": "owner"
            }
        )

        if not data:
            break

        repositories.extend(data)

        if len(data) < per_page:
            break

    return repositories


def get_public_events(username, max_pages=3):
    events = []

    for page in range(1, max_pages + 1):

        data = github_get(
            f"/users/{username}/events/public",
            params={
                "page": page,
                "per_page": 100
            }
        )

        if not data:
            break

        events.extend(data)

        if len(data) < 100:
            break

    return events


def get_languages(repo_full_name):
    try:
        return github_get(
            f"/repos/{repo_full_name}/languages"
        )
    except ValueError:
        return {}


def get_profile_bundle(username):

    user = get_user(username)

    repositories = get_repositories(username)

    events = get_public_events(username)

    languages = {}

    # Limit language requests to avoid unnecessary API usage
    for repo in repositories[:30]:

        repo_name = repo.get("full_name")

        if not repo_name:
            continue

        repo_languages = get_languages(repo_name)

        for language, bytes_count in repo_languages.items():

            languages[language] = (
                languages.get(language, 0) + bytes_count
            )

    return {
        "user": user,
        "repositories": repositories,
        "events": events,
        "languages": languages
    }


def parse_github_date(date_string):

    if not date_string:
        return None

    try:
        return datetime.fromisoformat(
            date_string.replace("Z", "+00:00")
        )
    except ValueError:
        return None


def days_since(date_string):

    date = parse_github_date(date_string)

    if date is None:
        return 0

    now = datetime.now(timezone.utc)

    return max(
        0,
        (now - date).days
                             )
