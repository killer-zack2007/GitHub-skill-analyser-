import argparse
import os

import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report
)
from sklearn.model_selection import train_test_split


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


def train_model(
    csv_path,
    output_path
):

    dataframe = pd.read_csv(
        csv_path
    )

    if "skill_level" not in dataframe.columns:

        raise ValueError(
            "CSV must contain a "
            "'skill_level' column."
        )

    if len(dataframe) < 30:

        raise ValueError(
            "At least 30 labelled rows "
            "are recommended."
        )

    dataframe = dataframe.dropna(
        subset=["skill_level"]
    )

    missing_columns = [
        column
        for column in FEATURE_NAMES
        if column not in dataframe.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing feature columns: "
            + ", ".join(missing_columns)
        )

    X = dataframe[
        FEATURE_NAMES
    ]

    y = dataframe[
        "skill_level"
    ]

    if y.nunique() < 2:

        raise ValueError(
            "The dataset needs at least "
            "two skill-level classes."
        )

    stratify_value = y

    try:

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42,
                stratify=stratify_value
            )
        )

    except ValueError:

        X_train, X_test, y_train, y_test = (
            train_test_split(
                X,
                y,
                test_size=0.2,
                random_state=42
            )
        )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=2,
        n_jobs=-1
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    print(
        f"\nAccuracy: {accuracy:.3f}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    os.makedirs(
        os.path.dirname(output_path)
        or ".",
        exist_ok=True
    )

    artifact = {
        "model": model,
        "features": FEATURE_NAMES
    }

    joblib.dump(
        artifact,
        output_path
    )

    print(
        f"\nModel saved to: {output_path}"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--csv",
        default="data/processed/"
                "github_labeled.csv"
    )

    parser.add_argument(
        "--output",
        default="models/"
                "github_skill_model.joblib"
    )

    args = parser.parse_args()

    train_model(
        csv_path=args.csv,
        output_path=args.output
  )
