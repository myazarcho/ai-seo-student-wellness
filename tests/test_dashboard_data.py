from __future__ import annotations

import importlib.util
from pathlib import Path

import pandas as pd
import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "11-dashboard" / "app.py"

spec = importlib.util.spec_from_file_location("dashboard_app", APP_PATH)
dashboard_app = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(dashboard_app)


def test_project_csv_files_exist() -> None:
    assert dashboard_app.KEYWORD_FILE.exists()
    assert dashboard_app.CALENDAR_FILE.exists()
    assert dashboard_app.ARTICLES_FILE.exists()


def test_keyword_csv_has_required_columns() -> None:
    data = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )

    assert dashboard_app.REQUIRED_KEYWORD_COLUMNS.issubset(data.columns)
    assert len(data) == 30


def test_calendar_csv_has_required_columns() -> None:
    data = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )

    assert dashboard_app.REQUIRED_CALENDAR_COLUMNS.issubset(data.columns)
    assert len(data) == 8


def test_articles_csv_has_required_columns() -> None:
    data = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
        required_value_columns=dashboard_app.ARTICLE_REQUIRED_VALUE_COLUMNS,
        unique_columns=dashboard_app.ARTICLE_UNIQUE_COLUMNS,
    )

    assert dashboard_app.REQUIRED_ARTICLE_COLUMNS.issubset(data.columns)
    assert len(data) == 9


def test_missing_required_column_raises_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "broken.csv"
    csv_path.write_text("Keyword,Topic\nexample keyword,Example topic\n")

    with pytest.raises(dashboard_app.DataValidationError):
        dashboard_app.read_project_csv(csv_path, {"Keyword", "Priority"})


def test_missing_csv_file_raises_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing.csv"

    with pytest.raises(dashboard_app.DataValidationError, match="Missing required file"):
        dashboard_app.read_project_csv(csv_path, {"Keyword"})


def test_empty_csv_file_raises_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("")

    with pytest.raises(dashboard_app.DataValidationError, match="is empty"):
        dashboard_app.read_project_csv(csv_path, {"Keyword"})


def test_header_only_csv_raises_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "header-only.csv"
    csv_path.write_text("Keyword,Topic\n")

    with pytest.raises(dashboard_app.DataValidationError, match="has no data rows"):
        dashboard_app.read_project_csv(csv_path, {"Keyword", "Topic"})


def test_missing_required_values_raise_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "missing-values.csv"
    csv_path.write_text("Keyword,Topic\nassignment planning,\n")

    with pytest.raises(
        dashboard_app.DataValidationError,
        match="missing required value",
    ):
        dashboard_app.read_project_csv(
            csv_path,
            {"Keyword", "Topic"},
            required_value_columns={"Keyword", "Topic"},
        )


def test_duplicate_keywords_raise_validation_error(tmp_path: Path) -> None:
    csv_path = tmp_path / "duplicate-keywords.csv"
    csv_path.write_text(
        "Keyword,Topic\n"
        "assignment planning,Assignment Management\n"
        " Assignment Planning ,Assignment Management\n"
    )

    with pytest.raises(dashboard_app.DataValidationError, match="duplicate value"):
        dashboard_app.read_project_csv(
            csv_path,
            {"Keyword", "Topic"},
            unique_columns={"Keyword"},
        )


def test_filter_keywords_searches_multiple_public_fields() -> None:
    data = pd.DataFrame(
        {
            "Keyword": ["assignment plan", "exam help"],
            "Topic": ["Assignment Management", "Exams and Presentations"],
            "Search Intent": ["Problem-solving", "Support-seeking"],
            "Priority": ["High", "Medium"],
            "Safety Level": ["Low", "Medium"],
            "Suggested Content Type": ["Checklist article", "Supportive guide"],
        }
    )

    filtered = dashboard_app.filter_keywords(
        data=data,
        topics=["Assignment Management", "Exams and Presentations"],
        intents=["Problem-solving", "Support-seeking"],
        priorities=["High", "Medium"],
        safety_levels=["Low", "Medium"],
        query="supportive",
    )

    assert filtered["Keyword"].tolist() == ["exam help"]


def test_filter_keywords_handles_screenshot_search_case() -> None:
    data = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )

    filtered = dashboard_app.filter_keywords(
        data=data,
        topics=["Assignment Management"],
        intents=["Problem-solving"],
        priorities=["Primary", "High", "Medium"],
        safety_levels=["Low", "Medium"],
        query="how to manage multiple assignmen",
    )

    assert filtered["Keyword"].tolist() == [
        "how to manage multiple assignment deadlines"
    ]


def test_summary_metrics_are_built_from_source_data() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )

    metrics = dashboard_app.build_summary_metrics(keywords, calendar)

    assert metrics["keywords"] == 30
    assert metrics["planned_articles"] == 8
    assert metrics["topics"] >= 1
    assert metrics["medium_safety"] >= 1


def test_public_topic_cards_include_student_support_areas() -> None:
    titles = {card["title"] for card in dashboard_app.public_topic_cards()}

    assert {
        "Deadlines",
        "Academic stress",
        "Time management",
        "Exams",
        "Presentations",
        "University support",
        "International student life",
    }.issubset(titles)


@pytest.mark.parametrize(
    ("query", "expected_topic"),
    [
        ("I have too many deadlines", "Assignment Management"),
        ("I feel nervous about a presentation", "Presentations"),
        ("I cannot organize my study time", "Time Management"),
        ("I do not know who to ask for help", "University Support"),
        ("I am worried about exams and revision", "Exams"),
        ("I am an international student trying to manage daily life", "International Students"),
    ],
)
def test_match_support_topic_handles_chat_prompts(
    query: str,
    expected_topic: str,
) -> None:
    assert dashboard_app.match_support_topic(query) == expected_topic


def test_match_support_topic_returns_none_for_unmatched_query() -> None:
    assert dashboard_app.match_support_topic("banana bicycle volcano") is None


def test_build_chat_response_is_short_and_actionable() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    response = dashboard_app.build_chat_response(
        "I have too many deadlines next week",
        keywords,
        calendar,
        articles,
    )

    assert response["topic"] == "Assignment Management"
    assert response["is_fallback"] is False
    assert "Next action" in response["message"]
    assert "Create my plan" in response["actions"]


def test_build_chat_response_fallback_suggests_topics() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    response = dashboard_app.build_chat_response(
        "banana bicycle volcano",
        keywords,
        calendar,
        articles,
    )

    assert response["is_fallback"] is True
    assert response["topic"] is None
    assert "deadlines" in response["suggested_topics"]
    assert "Find university support" in response["actions"]


def test_recommend_support_matches_deadline_query() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    results = dashboard_app.recommend_support(
        "I have too many deadlines next week",
        keywords,
        calendar,
        articles,
    )

    assert results
    assert results[0]["topic"] == "Assignment Management"
    assert "deadline" in results[0]["title"].lower()
    assert "summary" in results[0]
    assert "intent" in results[0]
    assert "safety_level" in results[0]


def test_recommend_support_matches_exam_query() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    results = dashboard_app.recommend_support(
        "exam stress and study plan",
        keywords,
        calendar,
        articles,
    )

    assert any(result["topic"] == "Exams" for result in results[:3])


def test_recommend_support_matches_university_support_query() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    results = dashboard_app.recommend_support(
        "how do I ask my professor for help",
        keywords,
        calendar,
        articles,
    )

    assert results
    assert results[0]["topic"] == "University Support"


def test_recommend_support_returns_empty_for_unrelated_query() -> None:
    keywords = dashboard_app.read_project_csv(
        dashboard_app.KEYWORD_FILE,
        dashboard_app.REQUIRED_KEYWORD_COLUMNS,
    )
    calendar = dashboard_app.read_project_csv(
        dashboard_app.CALENDAR_FILE,
        dashboard_app.REQUIRED_CALENDAR_COLUMNS,
    )
    articles = dashboard_app.read_project_csv(
        dashboard_app.ARTICLES_FILE,
        dashboard_app.REQUIRED_ARTICLE_COLUMNS,
    )

    results = dashboard_app.recommend_support(
        "banana bicycle volcano",
        keywords,
        calendar,
        articles,
    )

    assert results == []
