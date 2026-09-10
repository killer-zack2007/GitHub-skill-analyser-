import argparse
import os
import time

import pandas as pd
import requests
from dotenv import load_dotenv

from src.github_api import get_profile_bundle
from src.analyzer import extract_features


load_dotenv()


def search_users(
    query="type:user",
    pages=1,
    per_page=10
):

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if token:
        headers["Authorization"] = (
            f"Bearer {token}"
        )

    users = []

    for page in range(1, pages + 1):

        response = requests.get(
            "https://api.github.com/search/users",
            headers=headers,
            params={
                "q": query,
                "page": page,
                "per_page": per_page
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        users.extend(
            data.get("items", [])
        )

        if len(data.get("items", [])) < per_page:
            break

    return users


def collect_dataset(
    query,
    pages,
    per_page,
    output
):

    users = search_users(
        query=query,
        pages=pages,
        per_page=per_page
    )

    rows = []

    print(
        f"Found {len(users)} users."
    )

    for index, user in enumerate(users, 1):

        username = user.get("login")

        print(
            f"[{index}/{len(users)}] "
            f"Collecting {username}..."
        )

        try:

            bundle = get_profile_bundle(
                username
            )

            features = extract_features(
                bundle
            )

            features["username"] = username

            rows.append(features)

            time.sleep(0.5)

        except Exception as error:

            print(
                f"Skipped {username}: {error}"
            )

    if not rows:

        raise RuntimeError(
            "No data was collected."
        )

    dataframe = pd.DataFrame(rows)

    os.makedirs(
        os.path.dirname(output)
        or ".",
        exist_ok=True
    )

    dataframe.to_csv(
        output,
        index=False
    )

    print(
        f"\nDataset saved to: {output}"
    )

    print(
        f"Rows collected: {len(dataframe)}"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "Collect GitHub profile features"
        )
    )

    parser.add_argument(
        "--query",
        default="type:user"
    )

    parser.add_argument(
        "--pages",
        type=int,
        default=1
    )

    parser.add_argument(
        "--per-page",
        type=int,
        default=10
    )

    parser.add_argument(
        "--output",
        default="data/raw/github_users.csv"
    )

    args = parser.parse_args()

    collect_dataset(
        query=args.query,
        pages=args.pages,
        per_page=args.per_page,
        output=args.output
  )
