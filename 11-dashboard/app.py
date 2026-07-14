from __future__ import annotations

import base64
import re
from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KEYWORD_FILE = PROJECT_ROOT / "05-keyword-research" / "keyword-research.csv"
CALENDAR_FILE = PROJECT_ROOT / "09-content-calendar" / "content-calendar.csv"
ARTICLES_FILE = PROJECT_ROOT / "articles.csv"
ARTICLE_DRAFT_FILE = PROJECT_ROOT / "07-first-article" / "article-draft.md"
SEO_EVALUATION_FILE = PROJECT_ROOT / "08-evaluation" / "seo-evaluation.md"
SAFETY_EVALUATION_FILE = PROJECT_ROOT / "08-evaluation" / "safety-evaluation.md"
CONTENT_STRATEGY_FILE = PROJECT_ROOT / "06-content-strategy" / "content-strategy.md"
AI_WORKFLOW_FILE = PROJECT_ROOT / "10-ai-workflow" / "ai-workflow.md"
PROMPT_LIBRARY_FILE = PROJECT_ROOT / "10-ai-workflow" / "prompt-library.md"
CHARACTER_FILE = PROJECT_ROOT / "assets" / "mira-character.png"

REQUIRED_KEYWORD_COLUMNS = {
    "Keyword",
    "Topic",
    "Search Intent",
    "Priority",
    "Safety Level",
    "Suggested Content Type",
}

REQUIRED_CALENDAR_COLUMNS = {
    "Week",
    "Article Title",
    "Primary Keyword",
    "Content Pillar",
    "Search Intent",
    "Content Type",
    "Priority",
    "Safety Level",
    "Status",
}

REQUIRED_ARTICLE_COLUMNS = {
    "title",
    "summary",
    "topic",
    "intent",
    "safety_level",
    "source_keyword",
    "status",
}

KEYWORD_UNIQUE_COLUMNS = {"Keyword"}
ARTICLE_UNIQUE_COLUMNS = {"title"}
KEYWORD_REQUIRED_VALUE_COLUMNS = REQUIRED_KEYWORD_COLUMNS
CALENDAR_REQUIRED_VALUE_COLUMNS = REQUIRED_CALENDAR_COLUMNS
ARTICLE_REQUIRED_VALUE_COLUMNS = REQUIRED_ARTICLE_COLUMNS

PRIORITY_ORDER = ["Primary", "High", "Medium", "Low"]
SAFETY_ORDER = ["Low", "Medium", "High"]

PUBLIC_NAVIGATION = [
    "Home",
    "Explore Support",
    "Assignment Planner",
    "Articles",
    "University Support",
    "About and Safety",
    "Admin Dashboard",
]

QUICK_PROMPTS = [
    "Help me organize three assignments due next week",
    "Help me prepare for a university presentation",
    "Help me plan a realistic study schedule",
    "Help me decide who to ask for university support",
]

QUICK_PROMPT_ICONS = [
    ":material/auto_awesome:",
    ":material/co_present:",
    ":material/edit_calendar:",
    ":material/support_agent:",
]

CHAT_ACTION_ROUTES = {
    "Create a plan": "Assignment Planner",
    "Create my plan": "Assignment Planner",
    "Show checklist": "Explore Support",
    "Read full guide": "Articles",
    "Find university support": "University Support",
}

CHAT_TOPIC_OPENINGS = {
    "Assignment Management": "That sounds like a lot to manage at once.",
    "Academic Stress": "That sounds heavy, and it makes sense to want a steadier next step.",
    "Time Management": "It can be frustrating when time feels scattered.",
    "Exams": "Exam preparation can feel much easier once the next step is visible.",
    "Presentations": "Presentation nerves are common, especially when the task still feels vague.",
    "University Support": "It is completely okay to ask for help when the next step is unclear.",
    "International Students": "Studying in a new country can add extra layers to everyday university work.",
}

PUBLIC_TOPIC_CARDS = [
    {
        "title": "Deadlines",
        "topic": "Assignment Management",
        "summary": "Sort several assignments into a clearer next step.",
        "terms": ["deadline", "deadlines", "assignment", "assignments", "due", "prioritize"],
        "steps": [
            "Write every deadline in one list.",
            "Estimate how much work each task needs.",
            "Choose one small task to start today.",
        ],
    },
    {
        "title": "Academic stress",
        "topic": "Academic Stress",
        "summary": "Find practical ways to handle study pressure without big promises.",
        "terms": ["stress", "overwhelmed", "burnout", "pressure", "workload"],
        "steps": [
            "Name what is creating the most pressure.",
            "Separate urgent work from work that can wait.",
            "Ask for support if pressure feels hard to manage alone.",
        ],
    },
    {
        "title": "Time management",
        "topic": "Time Management",
        "summary": "Build a realistic weekly plan around classes, rest, and study.",
        "terms": ["time", "schedule", "routine", "weekly", "procrastinating", "blocking"],
        "steps": [
            "Block fixed commitments first.",
            "Add short study blocks for priority tasks.",
            "Leave buffer time for delays and rest.",
        ],
    },
    {
        "title": "Exams",
        "topic": "Exams",
        "summary": "Prepare for exams with steady planning instead of all-nighters.",
        "terms": ["exam", "exams", "test", "study plan", "all nighter", "revision"],
        "steps": [
            "List exam dates and main topics.",
            "Start with the hardest or highest-value topic.",
            "Plan review breaks instead of one long session.",
        ],
    },
    {
        "title": "Presentations",
        "topic": "Presentations",
        "summary": "Break presentation preparation into smaller, calmer steps.",
        "terms": ["presentation", "presenting", "slides", "speaking", "anxiety"],
        "steps": [
            "Write the main point of the presentation.",
            "Prepare a simple slide outline.",
            "Practice once with notes before polishing.",
        ],
    },
    {
        "title": "University support",
        "topic": "University Support",
        "summary": "Understand who to contact when academic work feels unclear.",
        "terms": [
            "professor",
            "adviser",
            "advisor",
            "support office",
            "counselling",
            "counseling",
            "help",
            "ask for help",
            "who to ask",
        ],
        "steps": [
            "Identify whether the question is about a course, planning, or wellbeing.",
            "Contact the most relevant university service.",
            "Use a short message that explains the problem and what help you need.",
        ],
    },
    {
        "title": "International student life",
        "topic": "International Students",
        "summary": "Find practical support for study, communication, and life abroad.",
        "terms": ["international", "abroad", "homesick", "lonely", "japan", "friends"],
        "steps": [
            "Choose one practical issue to solve first.",
            "Look for university or department support channels.",
            "Plan one small connection or communication step this week.",
        ],
    },
]

TOPIC_BY_PUBLIC_TITLE = {card["title"]: card["topic"] for card in PUBLIC_TOPIC_CARDS}
PUBLIC_TERMS_BY_TOPIC = {
    card["topic"]: set(card["terms"] + [card["title"], card["topic"]])
    for card in PUBLIC_TOPIC_CARDS
}


class DataValidationError(ValueError):
    """Raised when a project CSV is missing or does not match the app schema."""


class ContentFileError(ValueError):
    """Raised when a supporting markdown file cannot be loaded."""


def normalize_required_values(data: pd.DataFrame, columns: set[str]) -> pd.DataFrame:
    """Strip required string values so blank cells are easy to validate."""
    normalized = data.copy()
    for column in columns:
        if column in normalized.columns and pd.api.types.is_object_dtype(normalized[column]):
            normalized[column] = normalized[column].astype("string").str.strip()
    return normalized


def find_missing_required_values(data: pd.DataFrame, columns: set[str]) -> dict[str, int]:
    """Count missing or blank values for required columns."""
    missing_counts: dict[str, int] = {}
    for column in sorted(columns):
        missing = data[column].isna()
        if pd.api.types.is_string_dtype(data[column]):
            missing = missing | data[column].str.strip().eq("")
        count = int(missing.sum())
        if count:
            missing_counts[column] = count
    return missing_counts


def find_duplicate_values(data: pd.DataFrame, columns: set[str]) -> dict[str, list[str]]:
    """Find duplicate values in columns that should be unique."""
    duplicates: dict[str, list[str]] = {}
    for column in sorted(columns):
        normalized = data[column].astype("string").str.strip().str.casefold()
        duplicate_mask = normalized.notna() & normalized.duplicated(keep=False)
        if duplicate_mask.any():
            values = sorted(data.loc[duplicate_mask, column].astype(str).str.strip().unique())
            duplicates[column] = values
    return duplicates


def validate_project_csv(
    data: pd.DataFrame,
    file_name: str,
    required_columns: set[str],
    required_value_columns: set[str] | None = None,
    unique_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Validate the schema and row-level quality of a project CSV."""
    data = data.copy()
    data.columns = data.columns.str.replace("\ufeff", "", regex=False).str.strip()

    missing_columns = sorted(required_columns.difference(data.columns))
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise DataValidationError(
            f"{file_name} is missing required column(s): {missing}"
        )

    if data.empty:
        raise DataValidationError(f"{file_name} has no data rows.")

    required_value_columns = required_value_columns or required_columns
    unique_columns = unique_columns or set()
    data = normalize_required_values(data, required_value_columns)

    missing_values = find_missing_required_values(data, required_value_columns)
    if missing_values:
        details = ", ".join(
            f"{column} ({count})" for column, count in missing_values.items()
        )
        raise DataValidationError(
            f"{file_name} has missing required value(s): {details}"
        )

    duplicates = find_duplicate_values(data, unique_columns)
    if duplicates:
        details = ", ".join(
            f"{column}: {', '.join(values[:3])}" for column, values in duplicates.items()
        )
        raise DataValidationError(
            f"{file_name} has duplicate value(s) that must be unique: {details}"
        )

    return data


def read_project_csv(
    file_path: Path,
    required_columns: set[str],
    required_value_columns: set[str] | None = None,
    unique_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Read a project CSV and validate its required columns."""
    if not file_path.exists():
        raise DataValidationError(f"Missing required file: {file_path}")

    try:
        data = pd.read_csv(file_path, encoding="utf-8-sig")
    except pd.errors.EmptyDataError as error:
        raise DataValidationError(f"{file_path.name} is empty.") from error
    except pd.errors.ParserError as error:
        raise DataValidationError(
            f"{file_path.name} could not be parsed as a CSV file."
        ) from error

    return validate_project_csv(
        data=data,
        file_name=file_path.name,
        required_columns=required_columns,
        required_value_columns=required_value_columns,
        unique_columns=unique_columns,
    )


def read_markdown_file(file_path: Path) -> str:
    """Read a markdown file used by the public dashboard."""
    if not file_path.exists():
        raise ContentFileError(f"Missing supporting file: {file_path}")

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        raise ContentFileError(f"{file_path.name} is empty.")

    return text


@st.cache_data(ttl="1h", max_entries=8, show_spinner=False)
def load_project_csv(
    file_path: Path,
    required_columns: set[str],
    required_value_columns: set[str] | None = None,
    unique_columns: set[str] | None = None,
) -> pd.DataFrame:
    """Cached wrapper around project CSV loading."""
    return read_project_csv(
        file_path,
        required_columns,
        required_value_columns=required_value_columns,
        unique_columns=unique_columns,
    )


@st.cache_data(ttl="1h", max_entries=8, show_spinner=False)
def load_markdown_content(file_path: Path) -> str:
    """Cached wrapper around markdown loading."""
    return read_markdown_file(file_path)


@st.cache_data(ttl="1h", max_entries=4, show_spinner=False)
def load_image_data_url(file_path: Path) -> str:
    """Load a local PNG as a data URL for HTML rendering."""
    if not file_path.exists():
        raise ContentFileError(f"Missing image file: {file_path}")

    encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def count_values(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return a descending count table for a categorical column."""
    if data.empty:
        return pd.DataFrame({column: [], "Count": []})

    return (
        data.groupby(column, dropna=False)
        .size()
        .reset_index(name="Count")
        .sort_values(["Count", column], ascending=[False, True])
    )


def filter_keywords(
    data: pd.DataFrame,
    topics: list[str],
    intents: list[str],
    priorities: list[str],
    safety_levels: list[str],
    query: str,
) -> pd.DataFrame:
    """Filter keyword rows by sidebar selections and a text search."""
    filtered = data.copy()

    filters = {
        "Topic": topics,
        "Search Intent": intents,
        "Priority": priorities,
        "Safety Level": safety_levels,
    }

    for column, selected_values in filters.items():
        if selected_values:
            filtered = filtered[filtered[column].isin(selected_values)]

    if query.strip():
        searchable_columns = [
            "Keyword",
            "Topic",
            "Search Intent",
            "Suggested Content Type",
        ]
        search_blob = filtered[searchable_columns].apply(
            lambda row: " ".join(row.astype(str)),
            axis=1,
        )
        filtered = filtered[
            search_blob.str.contains(query.strip(), case=False, na=False)
        ]

    return filtered.reset_index(drop=True)


def normalize_text(value: str) -> str:
    """Normalize public search text for deterministic matching."""
    return re.sub(r"[^a-z0-9\s]", " ", str(value).casefold()).strip()


def public_topic_cards() -> list[dict[str, object]]:
    """Return public-facing topic card definitions."""
    return PUBLIC_TOPIC_CARDS


def calendar_title_for_keyword(keyword: str, calendar_data: pd.DataFrame) -> str:
    """Find a public article title for a keyword when calendar data has one."""
    matches = calendar_data[
        calendar_data["Primary Keyword"].astype(str).str.casefold()
        == str(keyword).casefold()
    ]
    if matches.empty:
        return str(keyword).capitalize()
    return str(matches.iloc[0]["Article Title"])


def action_steps_for_topic(topic: str) -> list[str]:
    """Return public next steps for a support topic."""
    for card in PUBLIC_TOPIC_CARDS:
        if card["topic"] == topic:
            return list(card["steps"])
    return [
        "Write down what feels unclear right now.",
        "Choose one small next step.",
        "Ask a university contact for guidance if you feel stuck.",
    ]


def match_support_topic(query: str) -> str | None:
    """Match a natural-language query to a public support topic."""
    normalized_query = normalize_text(query)
    if not normalized_query:
        return None

    query_terms = set(normalized_query.split())
    best_topic: str | None = None
    best_score = 0

    for card in PUBLIC_TOPIC_CARDS:
        topic = str(card["topic"])
        searchable_terms = {
            normalize_text(term)
            for term in [card["title"], topic, *list(card["terms"])]
        }
        score = 0

        for term in searchable_terms:
            if not term:
                continue
            term_words = set(term.split())
            if term in normalized_query:
                score += 10 + len(term_words)
            score += 3 * len(query_terms.intersection(term_words))

        if score > best_score:
            best_topic = topic
            best_score = score

    return best_topic if best_score >= 6 else None


def chat_actions_for_topic(topic: str | None) -> list[str]:
    """Return contextual public actions for a matched support topic."""
    if topic in {"Assignment Management", "Time Management"}:
        return ["Create my plan", "Show checklist", "Read full guide"]
    if topic in {"University Support", "Academic Stress", "International Students"}:
        return ["Find university support", "Read full guide"]
    if topic in {"Exams", "Presentations"}:
        return ["Show checklist", "Read full guide"]
    return ["Show checklist", "Find university support"]


def build_fallback_chat_response() -> dict[str, object]:
    """Build a friendly fallback response when no topic matches."""
    suggested_topics = [
        "deadlines",
        "study time",
        "exams",
        "presentations",
        "university support",
    ]
    message = (
        "I am not fully sure which study challenge this connects to yet.\n\n"
        "Try describing one concrete thing that is making university work harder "
        "right now, such as a deadline, exam, presentation, schedule problem, or "
        "who you need to contact.\n\n"
        "**Next action:** Choose one of these starting points: "
        f"{', '.join(suggested_topics)}."
    )
    return {
        "topic": None,
        "message": message,
        "actions": ["Show checklist", "Find university support"],
        "recommendations": [],
        "is_fallback": True,
        "suggested_topics": suggested_topics,
    }


def build_chat_response(
    query: str,
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
) -> dict[str, object]:
    """Build a short deterministic assistant response for the chat homepage."""
    topic = match_support_topic(query)
    if topic is None:
        return build_fallback_chat_response()

    recommendations = recommend_support(
        query=query,
        keyword_data=keyword_data,
        calendar_data=calendar_data,
        article_data=article_data,
        topic=topic,
        limit=2,
    )
    steps = action_steps_for_topic(topic)[:4]
    opening = CHAT_TOPIC_OPENINGS.get(
        topic,
        "That sounds like something worth making clearer.",
    )
    next_action = "Would you like to create a simple priority plan?"
    if topic in {"Exams", "Presentations"}:
        next_action = "Would you like a short checklist to work through?"
    elif topic in {"University Support", "Academic Stress", "International Students"}:
        next_action = "Would you like help choosing the best university contact?"

    formatted_steps = "\n".join(
        f"{index}. {step}" for index, step in enumerate(steps, start=1)
    )
    message = f"{opening}\n\n{formatted_steps}\n\n**Next action:** {next_action}"

    return {
        "topic": topic,
        "message": message,
        "actions": chat_actions_for_topic(topic),
        "recommendations": recommendations,
        "is_fallback": False,
        "suggested_topics": [],
    }


def build_support_items(
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame | None = None,
) -> list[dict[str, object]]:
    """Build public-facing recommendation items from strategy data."""
    if article_data is not None:
        items: list[dict[str, object]] = []
        for _, row in article_data.iterrows():
            topic = str(row["topic"])
            item = {
                "title": str(row["title"]),
                "summary": str(row["summary"]),
                "keyword": str(row["source_keyword"]),
                "topic": topic,
                "format": "Guide",
                "intent": str(row["intent"]),
                "safety_level": str(row["safety_level"]),
                "priority": "High" if str(row["status"]) == "Published" else "Medium",
                "next_steps": action_steps_for_topic(topic),
                "search_text": normalize_text(
                    " ".join(
                        [
                            str(row["title"]),
                            str(row["summary"]),
                            str(row["source_keyword"]),
                            topic,
                            str(row["intent"]),
                            " ".join(PUBLIC_TERMS_BY_TOPIC.get(topic, set())),
                        ]
                    )
                ),
            }
            items.append(item)
        return items

    items: list[dict[str, object]] = []
    for _, row in keyword_data.iterrows():
        keyword = str(row["Keyword"])
        topic = str(row["Topic"])
        title = calendar_title_for_keyword(keyword, calendar_data)
        item = {
            "title": title,
            "summary": f"Practical support for {keyword}.",
            "keyword": keyword,
            "topic": topic,
            "format": str(row["Suggested Content Type"]),
            "intent": str(row["Search Intent"]),
            "safety_level": str(row["Safety Level"]),
            "priority": str(row["Priority"]),
            "next_steps": action_steps_for_topic(topic),
            "search_text": normalize_text(
                " ".join(
                    [
                        title,
                        keyword,
                        topic,
                        str(row["Suggested Content Type"]),
                        " ".join(PUBLIC_TERMS_BY_TOPIC.get(topic, set())),
                    ]
                )
            ),
        }
        items.append(item)
    return items


def score_support_item(query: str, item: dict[str, object]) -> int:
    """Score one recommendation item against a public natural-language query."""
    normalized_query = normalize_text(query)
    if not normalized_query:
        priority = str(item.get("priority", ""))
        return {"Primary": 30, "High": 20, "Medium": 10}.get(priority, 5)

    query_terms = set(normalized_query.split())
    search_text = str(item["search_text"])
    score = 0

    if normalized_query in search_text:
        score += 40

    for term in query_terms:
        if term in search_text:
            score += 8

    topic_terms = PUBLIC_TERMS_BY_TOPIC.get(str(item["topic"]), set())
    for term in topic_terms:
        if normalize_text(term) in normalized_query:
            score += 15

    intent = normalize_text(str(item.get("intent", "")))
    if intent and intent in normalized_query:
        score += 6

    safety_level = str(item.get("safety_level", ""))
    if score > 0 and safety_level == "Low":
        score += 2

    if score > 0 and str(item.get("priority")) in {"Primary", "High"}:
        score += 4

    return score


def recommend_support(
    query: str,
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame | None = None,
    topic: str | None = None,
    limit: int = 6,
) -> list[dict[str, object]]:
    """Recommend support items using deterministic keyword and topic matching."""
    items = build_support_items(keyword_data, calendar_data, article_data)
    if topic and topic != "All":
        items = [item for item in items if item["topic"] == topic]

    scored = [
        (score_support_item(query, item), item)
        for item in items
    ]
    scored = [
        (score, item)
        for score, item in scored
        if score > 0 or not normalize_text(query)
    ]
    scored.sort(
        key=lambda pair: (
            pair[0],
            {"Primary": 3, "High": 2, "Medium": 1}.get(str(pair[1]["priority"]), 0),
            str(pair[1]["title"]),
        ),
        reverse=True,
    )
    return [item for _, item in scored[:limit]]


def build_summary_metrics(
    keyword_data: pd.DataFrame, calendar_data: pd.DataFrame
) -> dict[str, int]:
    """Build top-level dashboard metrics."""
    return {
        "keywords": len(keyword_data),
        "topics": keyword_data["Topic"].nunique(),
        "planned_articles": len(calendar_data),
        "medium_safety": int(keyword_data["Safety Level"].eq("Medium").sum()),
    }


def sort_by_known_order(
    data: pd.DataFrame, column: str, order: list[str]
) -> pd.DataFrame:
    """Sort a summary table by a fixed category order when possible."""
    category_order = pd.CategoricalDtype(categories=order, ordered=True)
    sorted_data = data.copy()
    sorted_data["_order"] = sorted_data[column].astype(category_order)
    sorted_data = sorted_data.sort_values(["_order", column]).drop(columns="_order")
    return sorted_data


def extract_markdown_section(markdown_text: str, heading: str) -> str:
    """Extract a section under a level-two markdown heading."""
    pattern = rf"## {re.escape(heading)}\n(?P<section>.*?)(?=\n## |\Z)"
    match = re.search(pattern, markdown_text, flags=re.S)
    if not match:
        return ""
    return match.group("section").strip()


def extract_article_preview(markdown_text: str, max_paragraphs: int = 3) -> str:
    """Build a short article preview from the draft markdown."""
    lines = [line.strip() for line in markdown_text.splitlines()]
    title = next((line for line in lines if line.startswith("# ")), "# Article preview")
    paragraphs = [
        line
        for line in lines
        if line and not line.startswith("#") and not line.startswith("|")
    ]
    preview = "\n\n".join([title, *paragraphs[:max_paragraphs]])
    return preview


def extract_seo_score(markdown_text: str) -> tuple[int, int]:
    """Extract the first score shaped like 43/50 from the SEO review."""
    match = re.search(r"\*\*(\d+)\s*/\s*(\d+)\*\*", markdown_text)
    if not match:
        return 0, 0
    return int(match.group(1)), int(match.group(2))


def extract_safety_rating(markdown_text: str) -> str:
    """Extract the overall safety rating from the safety review."""
    match = re.search(r"Overall Safety Rating:\s*([^*\n]+)", markdown_text)
    if not match:
        return "Not found"
    return match.group(1).strip()


def keyword_chart(data: pd.DataFrame, x_column: str, title: str) -> alt.Chart:
    """Build a simple horizontal count chart."""
    return (
        alt.Chart(data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Count:Q", title="Keywords"),
            y=alt.Y(f"{x_column}:N", sort="-x", title=None),
            tooltip=[x_column, "Count"],
        )
        .properties(height=max(180, min(360, 34 * max(len(data), 1))), title=title)
    )


def calendar_chart(data: pd.DataFrame) -> alt.Chart:
    """Build a content calendar status chart."""
    status_data = count_values(data, "Status")
    return (
        alt.Chart(status_data)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Count:Q", title="Articles"),
            y=alt.Y("Status:N", sort="-x", title=None),
            tooltip=["Status", "Count"],
        )
        .properties(height=180)
    )


def render_sidebar_filters(keyword_data: pd.DataFrame) -> tuple[list[str], ...]:
    """Render admin keyword filters inside the admin page."""
    with st.expander("Keyword filters", icon=":material/tune:", expanded=True):

        topics = sorted(keyword_data["Topic"].unique().tolist())
        intents = sorted(keyword_data["Search Intent"].unique().tolist())
        priorities = [
            priority
            for priority in PRIORITY_ORDER
            if priority in keyword_data["Priority"].unique()
        ]
        safety_levels = [
            level
            for level in SAFETY_ORDER
            if level in keyword_data["Safety Level"].unique()
        ]

        selected_topics = st.multiselect("Topics", topics, default=topics)
        selected_intents = st.multiselect("Search intents", intents, default=intents)
        selected_priorities = st.pills(
            "Priorities",
            priorities,
            default=priorities,
            selection_mode="multi",
        )
        selected_safety_levels = st.pills(
            "Safety levels",
            safety_levels,
            default=safety_levels,
            selection_mode="multi",
        )
        query = st.text_input(
            "Keyword search",
            placeholder="Try deadlines, exams, support...",
        )

        st.caption(
            "Public guidance only. Content should avoid diagnosis, treatment, "
            "medication advice, or crisis counselling."
        )

    return (
        selected_topics,
        selected_intents,
        selected_priorities,
        selected_safety_levels,
        query,
    )


def render_metric_row(metrics: dict[str, int]) -> None:
    """Render top-level KPI cards."""
    with st.container(horizontal=True):
        st.metric("Keywords", metrics["keywords"], border=True)
        st.metric("Content topics", metrics["topics"], border=True)
        st.metric("Planned articles", metrics["planned_articles"], border=True)
        st.metric("Medium-safety keywords", metrics["medium_safety"], border=True)


def render_public_safety_notice() -> None:
    """Render a calm non-clinical boundary for students."""
    st.caption(
        "This app offers practical study and university-support guidance. It does "
        "not provide diagnosis, treatment, medication advice, therapy, emergency "
        "counselling, or crisis support."
    )


def apply_sidebar_theme_css() -> None:
    """Apply the shared app sidebar style across every page."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #EEEAE4 0%, #E7ECEA 100%);
            border-right: 1px solid rgba(70, 88, 98, 0.10);
            box-shadow: 10px 0 28px rgba(42, 58, 68, 0.05);
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            width: 16rem !important;
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #243746;
            font-family: Poppins, Inter, sans-serif;
            font-weight: 600;
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #6B7784;
            font-size: 0.95rem;
        }

        [data-testid="stSidebar"] section {
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.28rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 999px;
            color: #61707C;
            font-family: Inter, sans-serif;
            font-size: 0.95rem;
            font-weight: 500;
            margin: 0.1rem 0;
            padding: 0.55rem 0.75rem;
            transition: background 140ms ease, color 140ms ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(168, 207, 194, 0.16);
            color: #314351;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: rgba(168, 207, 194, 0.30);
            color: #243746;
            box-shadow: inset 0 0 0 1px rgba(168, 207, 194, 0.50);
        }

        .mira-sidebar-brand {
            background: transparent;
            border: 0;
            border-radius: 0;
            box-shadow: none;
            margin: 0.25rem 0 0.85rem;
            padding: 0.2rem 0.25rem 0.35rem;
            text-align: center;
        }

        .mira-sidebar-logo {
            display: block;
            height: 74px;
            margin: 0 auto 0.35rem;
            object-fit: contain;
            width: auto;
        }

        .mira-sidebar-brand strong {
            color: #243746;
            display: block;
            font-family: Poppins, Inter, sans-serif;
            font-size: 1.02rem;
            font-weight: 600;
            letter-spacing: 0;
            line-height: 1.25;
        }

        .mira-sidebar-brand span {
            color: #7A8793;
            display: block;
            font-size: 0.86rem;
            line-height: 1.45;
            margin-top: 0.25rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_chat_theme_css() -> None:
    """Apply a calm public theme for the chat-style homepage."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@500;600;700&display=swap');

        html,
        body,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"] {
            height: 100vh;
            height: 100dvh;
            min-height: 100vh;
            min-height: 100dvh;
            overflow: hidden;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }

        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(135deg, #F8F5F1 0%, #F4F7F6 55%, #F1F5F7 100%);
            color: #243746;
        }

        [data-testid="stMain"],
        .main {
            height: 100vh;
            height: 100dvh;
            min-height: 0;
            overflow: hidden;
        }

        [data-testid="stMainBlockContainer"],
        .block-container {
            height: 100%;
            max-height: 100%;
            min-height: 0;
            overflow: hidden;
            padding-top: 0;
            padding-bottom: 0;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }

        [data-testid="stSidebar"] {
            background:
                linear-gradient(180deg, #EEEAE4 0%, #E7ECEA 100%);
            border-right: 1px solid rgba(70, 88, 98, 0.10);
            box-shadow: 10px 0 28px rgba(42, 58, 68, 0.05);
            height: 100vh;
            height: 100dvh;
            overflow: hidden;
            width: 16rem !important;
        }

        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {
            color: #243746;
            font-family: Poppins, Inter, sans-serif;
            font-weight: 600;
            letter-spacing: 0;
        }

        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: #6B7784;
            font-size: 0.95rem;
        }

        [data-testid="stSidebar"] section {
            padding-top: 1rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] {
            gap: 0.28rem;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label {
            border-radius: 999px;
            color: #61707C;
            font-family: Inter, sans-serif;
            font-size: 0.95rem;
            font-weight: 500;
            margin: 0.1rem 0;
            padding: 0.55rem 0.75rem;
            transition: background 140ms ease, color 140ms ease;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {
            display: none;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:hover {
            background: rgba(168, 207, 194, 0.16);
            color: #314351;
        }

        [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
            background: rgba(168, 207, 194, 0.30);
            color: #243746;
            box-shadow: inset 0 0 0 1px rgba(168, 207, 194, 0.50);
        }

        .mira-sidebar-brand {
            background: transparent;
            border: 0;
            border-radius: 0;
            box-shadow: none;
            margin: 0.25rem 0 0.85rem;
            padding: 0.2rem 0.25rem 0.35rem;
            text-align: center;
        }

        .mira-sidebar-logo {
            display: block;
            height: 74px;
            margin: 0 auto 0.35rem;
            object-fit: contain;
            width: auto;
        }

        .mira-sidebar-brand strong {
            color: #243746;
            display: block;
            font-family: Poppins, Inter, sans-serif;
            font-size: 1.02rem;
            font-weight: 600;
            letter-spacing: 0;
            line-height: 1.25;
        }

        .mira-sidebar-brand span {
            color: #7A8793;
            display: block;
            font-size: 0.86rem;
            line-height: 1.45;
            margin-top: 0.25rem;
        }

        .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            max-width: 840px;
            padding-left: 2rem;
            padding-right: 2rem;
        }

        .mira-landing {
            align-items: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            height: 100vh;
            height: 100dvh;
            max-height: 100vh;
            max-height: 100dvh;
            overflow: hidden;
            text-align: center;
            transform: translateY(-2vh);
            width: 100%;
        }

        .mira-chat-shell {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            height: 100vh;
            height: 100dvh;
            min-height: 0;
            overflow: hidden;
            padding: 1.2rem 0;
            width: 100%;
        }

        .mira-chat-history {
            flex: 1 1 auto;
            min-height: 0;
            overflow-y: auto;
            padding: 0.25rem 0.25rem 0.5rem;
        }

        .mira-chat-composer-area {
            flex: 0 0 auto;
        }

        .mira-header {
            text-align: center;
            margin-bottom: 0.35rem;
        }

        .mira-illustration {
            display: flex;
            justify-content: center;
            margin-bottom: 0.45rem;
        }

        .mira-illustration img {
            display: block;
            height: 118px;
            max-height: 16vh;
            max-width: 42vw;
            object-fit: contain;
            width: auto;
            filter: drop-shadow(0 8px 10px rgba(87, 105, 116, 0.08));
        }

        .mira-header h1 {
            color: #273744;
            font-family: Poppins, Inter, sans-serif;
            font-size: 38px;
            font-weight: 600;
            line-height: 1.2;
            margin: 0 0 0.35rem;
            letter-spacing: 0;
            text-shadow: 0 1px 0 rgba(255, 253, 252, 0.65);
        }

        .mira-header p {
            color: #5E6B76;
            font-size: 18px;
            font-weight: 400;
            line-height: 1.5;
            margin: 0;
        }

        .mira-gentle-prompt {
            color: #687580;
            font-size: 17px;
            font-weight: 400;
            line-height: 1.5;
            margin: 0.35rem auto 0.9rem;
            max-width: 680px;
        }

        .mira-chip-label {
            color: #7A8793;
            font-size: 13px;
            font-weight: 500;
            margin: 0.55rem 0 0.25rem;
            text-align: center;
        }

        .mira-suggestions {
            margin-top: 0.15rem;
            width: min(760px, 100%);
        }

        .mira-safety-note {
            background: transparent;
            border: 0;
            color: #7A8793;
            font-size: 13px;
            line-height: 1.55;
            margin: 0.55rem auto 0;
            max-width: 640px;
            padding: 0;
            text-align: center;
        }

        div[data-testid="stChatMessage"] {
            background: #FFFDFC;
            border: 1px solid #DDE7E3;
            border-radius: 24px;
            box-shadow: 0 12px 28px rgba(80, 96, 109, 0.06);
            padding: 0.65rem;
            margin-top: 0.75rem;
        }

        div[data-testid="stChatMessage"] p,
        div[data-testid="stChatMessage"] li {
            color: #61707C;
            font-size: 18px;
            line-height: 1.65;
        }

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
            background: #F5FAF8;
            border-color: #D5E9E2;
        }

        div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
            background: #EAC7C7;
            color: #243746;
        }

        div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
            background: #B8CBE6;
            color: #243746;
        }

        div.stButton > button {
            border-radius: 999px;
            border: 1px solid transparent;
            background: transparent;
            color: #314351;
            font-size: 16px;
            font-weight: 500;
            justify-content: flex-start;
            min-height: 2.25rem;
            padding: 0.42rem 0.72rem;
            box-shadow: none;
            transition: all 140ms ease;
        }

        div.stButton > button:hover {
            border-color: transparent;
            color: #12333f;
            background: rgba(168, 207, 194, 0.18);
            transform: none;
            box-shadow: none;
        }

        [data-testid="stForm"] {
            background: #F1F0F3;
            border: 1px solid rgba(70, 88, 98, 0.12);
            border-radius: 28px;
            box-shadow: 0 8px 26px rgba(42, 58, 68, 0.08);
            max-width: 760px;
            min-height: 104px;
            margin-left: auto;
            margin-right: auto;
            padding: 14px 16px 12px;
            width: 100%;
        }

        [data-testid="stForm"] [data-testid="stTextInput"] input {
            background: transparent;
            border: 0 !important;
            box-shadow: none !important;
            outline: 0 !important;
            color: #243746;
            font-size: 17px;
            font-weight: 400;
            line-height: 1.5;
            padding: 0.15rem 0;
        }

        [data-testid="stForm"] [data-testid="stTextInput"] input::placeholder {
            color: #8A929B;
            font-size: 17px;
            font-weight: 400;
        }

        [data-testid="stForm"] [data-testid="stTextInput"] > div {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        [data-testid="stForm"] [data-baseweb="input"],
        [data-testid="stForm"] [data-baseweb="base-input"],
        [data-testid="stForm"] [data-baseweb="input"] > div {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
        }

        [data-testid="stForm"] [data-testid="stTextInput"] {
            margin-bottom: 0.35rem;
        }

        [data-testid="stForm"] div.stButton > button {
            align-items: center;
            background: #A8CFC2;
            border: 0;
            border-radius: 999px;
            box-shadow: 0 6px 14px rgba(42, 58, 68, 0.10);
            color: #243746;
            display: inline-flex;
            height: 2.75rem;
            justify-content: center;
            margin-left: auto;
            min-height: 2.75rem;
            min-width: 2.75rem;
            max-width: 2.75rem;
            font-size: 1.35rem;
            font-weight: 600;
            line-height: 1;
            overflow: hidden;
            padding: 0 !important;
            text-align: center;
            white-space: nowrap;
            width: 2.75rem;
        }

        [data-testid="stForm"] div.stButton > button:hover {
            background: #95C4B5;
            color: #182B36;
        }

        [data-testid="stForm"] div.stButton > button p {
            display: block;
            font-size: 1.35rem;
            line-height: 1;
            margin: 0;
            padding: 0;
            white-space: nowrap;
        }

        [data-testid="stForm"] div.stButton > button span {
            font-size: 1.35rem;
            line-height: 1;
            margin: 0;
        }

        .mira-composer-hint {
            color: #7F8A94;
            font-size: 13px;
            line-height: 1;
            padding-left: 0.25rem;
        }

        .stMarkdown > p,
        .stCaptionContainer {
            color: #7A8793;
        }

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .mira-landing {
                height: 100vh;
                height: 100dvh;
                transform: translateY(-1vh);
            }
            .mira-illustration img {
                height: 92px;
                max-height: 14vh;
            }
            .mira-header h1 {
                font-size: 32px;
            }
            .mira-header p {
                font-size: 17px;
            }
            .mira-gentle-prompt,
            div[data-testid="stChatMessage"] p,
            div[data-testid="stChatMessage"] li {
                font-size: 16px;
            }
            .mira-gentle-prompt {
                margin-bottom: 0.85rem;
            }
            div.stButton > button {
                font-size: 14px;
                min-height: 2.2rem;
            }
            [data-testid="stForm"] {
                min-height: 96px;
                padding: 12px 14px 10px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_student_illustration() -> None:
    """Render the cleaned Mira character image for the public homepage."""
    image_url = load_image_data_url(CHARACTER_FILE)
    st.markdown(
        f"""
        <div class="mira-illustration" aria-hidden="true">
            <img src="{image_url}" alt="Mira student support character">
        </div>
        """,
        unsafe_allow_html=True,
    )


def initialize_chat_state() -> None:
    """Ensure chat messages exist in Streamlit session state."""
    if "messages" not in st.session_state:
        st.session_state.messages = []


def add_chat_turn(
    prompt: str,
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
) -> None:
    """Append a user message and deterministic assistant response."""
    clean_prompt = prompt.strip()
    if not clean_prompt:
        return

    response = build_chat_response(
        clean_prompt,
        keyword_data=keyword_data,
        calendar_data=calendar_data,
        article_data=article_data,
    )
    st.session_state.messages.append({"role": "user", "content": clean_prompt})
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": str(response["message"]),
            "actions": list(response["actions"]),
            "topic": response["topic"],
            "is_fallback": bool(response["is_fallback"]),
        }
    )


def set_navigation_page(page: str) -> None:
    """Move the public navigation to a selected page."""
    st.session_state.app_page = page


def render_chat_actions(actions: list[str]) -> None:
    """Render contextual action buttons for the latest assistant response."""
    if not actions:
        return

    columns = st.columns(len(actions))
    for column, action in zip(columns, actions):
        target_page = CHAT_ACTION_ROUTES.get(action, "Explore Support")
        with column:
            st.button(
                action,
                key=f"chat_action_{action}",
                on_click=set_navigation_page,
                args=(target_page,),
                width="stretch",
            )


def render_chat_messages() -> None:
    """Render the chat history as user and assistant bubbles."""
    for message in st.session_state.messages:
        role = str(message["role"])
        with st.chat_message(role):
            st.markdown(str(message["content"]))

    latest_assistant = next(
        (
            message
            for message in reversed(st.session_state.messages)
            if message["role"] == "assistant"
        ),
        None,
    )
    if latest_assistant:
        render_chat_actions(list(latest_assistant.get("actions", [])))


def render_chat_composer(
    key_prefix: str,
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
) -> None:
    """Render the unified AI-style composer."""
    with st.form(f"{key_prefix}_composer", border=False, clear_on_submit=True):
        prompt = st.text_input(
            "Message",
            placeholder="Tell Mira what feels difficult right now...",
            label_visibility="collapsed",
            key=f"{key_prefix}_composer_input",
        )
        helper, send = st.columns([8, 1], vertical_alignment="center")
        with helper:
            st.markdown(
                '<span class="mira-composer-hint">+ Study support</span>',
                unsafe_allow_html=True,
            )
        with send:
            submitted = st.form_submit_button(
                "↑",
                width="content",
            )

    if submitted and prompt.strip():
        add_chat_turn(
            prompt,
            keyword_data=keyword_data,
            calendar_data=calendar_data,
            article_data=article_data,
        )
        st.rerun()


def render_topic_cards() -> None:
    """Render public topic cards."""
    st.subheader("Choose a support area")
    cards = public_topic_cards()
    for start in range(0, len(cards), 3):
        columns = st.columns(3)
        for column, card in zip(columns, cards[start : start + 3]):
            with column:
                with st.container(border=True, height="stretch"):
                    st.markdown(f"**{card['title']}**")
                    st.write(card["summary"])
                    steps = list(card["steps"])
                    st.caption(f"Try first: {steps[0]}")


def render_recommendation_cards(recommendations: list[dict[str, object]]) -> None:
    """Render public recommendation cards."""
    if not recommendations:
        st.info(
            "I could not find a close match. Try words like deadlines, exams, "
            "presentation, support office, international student, or time management.",
            icon=":material/search:",
        )
        return

    for item in recommendations:
        with st.container(border=True):
            st.markdown(f"**{item['title']}**")
            st.write(str(item.get("summary", "")))
            st.caption(f"Support area: {item['topic']}")
            st.markdown("**Practical next steps**")
            for step in list(item["next_steps"])[:3]:
                st.write(f"- {step}")


def render_public_search(
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
    key_prefix: str,
    default_query: str = "",
    show_topic_filter: bool = False,
) -> None:
    """Render natural-language search and recommendations."""
    topic = "All"
    if show_topic_filter:
        topic_options = ["All", *[card["topic"] for card in PUBLIC_TOPIC_CARDS]]
        topic = st.selectbox("Support area", topic_options, key=f"{key_prefix}_topic")

    query = st.text_input(
        "What are you dealing with?",
        value=default_query,
        placeholder="Example: I have three deadlines next week",
        key=f"{key_prefix}_query",
    )
    recommendations = recommend_support(
        query=query,
        keyword_data=keyword_data,
        calendar_data=calendar_data,
        article_data=article_data,
        topic=topic,
    )

    st.subheader("Recommended support")
    render_recommendation_cards(recommendations)


def render_public_home(
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
) -> None:
    """Render the student-facing chat homepage."""
    apply_chat_theme_css()
    initialize_chat_state()

    if not st.session_state.messages:
        render_student_illustration()
        st.markdown(
            """
            <div class="mira-header">
                <h1>Mira Study Support</h1>
                <p>Practical support for university study challenges.</p>
            </div>
            <p class="mira-gentle-prompt">
                Tell me what feels difficult right now, and I'll help you find a calm next step.
            </p>
            """,
            unsafe_allow_html=True,
        )
        render_chat_composer(
            key_prefix="landing",
            keyword_data=keyword_data,
            calendar_data=calendar_data,
            article_data=article_data,
        )
        st.markdown(
            """
            <div class="mira-suggestions">
                <p class="mira-chip-label">Try one of these</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        for index, quick_prompt in enumerate(QUICK_PROMPTS):
            if st.button(
                quick_prompt,
                key=f"quick_prompt_{index}",
                icon=QUICK_PROMPT_ICONS[index],
                width="stretch",
            ):
                add_chat_turn(
                    quick_prompt,
                    keyword_data=keyword_data,
                    calendar_data=calendar_data,
                    article_data=article_data,
                )
                st.rerun()
        st.markdown(
            """
            <div class="mira-safety-note">
                Practical study support only, not clinical care or crisis support.
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="mira-header">
                <h1>Mira Study Support</h1>
                <p>Practical support for university study challenges.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.container(height=520, border=False):
            render_chat_messages()
        render_chat_composer(
            key_prefix="chat",
            keyword_data=keyword_data,
            calendar_data=calendar_data,
            article_data=article_data,
        )
        st.markdown(
            """
            <div class="mira-safety-note">
                Practical study support only, not clinical care or crisis support.
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_explore_support(
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_data: pd.DataFrame,
) -> None:
    """Render the support exploration page."""
    st.title("Explore support")
    st.write(
        "Describe the study situation in plain language. The app will match it to "
        "practical, non-clinical support topics."
    )
    render_public_search(
        keyword_data=keyword_data,
        calendar_data=calendar_data,
        article_data=article_data,
        key_prefix="explore",
        show_topic_filter=True,
    )


def render_assignment_planner() -> None:
    """Render a simple assignment planning page."""
    st.title("Assignment planner")
    st.write(
        "Use these steps when several assignments feel equally urgent. Start small "
        "and make the work visible."
    )
    planner_steps = [
        ("List everything", "Write each assignment, course, due date, and current progress."),
        ("Estimate the work", "Add a rough time estimate for reading, writing, editing, and submission."),
        ("Break down large tasks", "Turn one large assignment into smaller actions you can schedule."),
        ("Choose today’s next step", "Pick one useful action that can be started in 10 to 20 minutes."),
        ("Ask early", "Contact a professor, adviser, or support office if the plan is not manageable."),
    ]
    for title, description in planner_steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)
    render_public_safety_notice()


def render_articles(article_markdown: str, article_data: pd.DataFrame) -> None:
    """Render public articles without strategy metadata."""
    st.title("Articles")
    st.write("Read practical guides and see what topics are planned next.")

    with st.container(border=True):
        st.markdown(article_markdown)

    st.subheader("More guides planned")
    planned = article_data[["title", "summary", "topic", "status"]].rename(
        columns={"title": "Guide", "summary": "Summary", "topic": "Support area"}
    )
    st.dataframe(planned, hide_index=True)


def render_university_support() -> None:
    """Render university support guidance for students."""
    st.title("University support")
    st.write(
        "Different university services can help with different kinds of questions. "
        "Use this page to decide where to start."
    )
    support_cards = [
        (
            "Course professor",
            "Ask about assignment instructions, extensions, feedback, or course-specific expectations.",
        ),
        (
            "Academic adviser",
            "Ask about workload planning, study progress, course choices, or academic options.",
        ),
        (
            "Student support office",
            "Ask about university processes, documentation, accessibility, or general student services.",
        ),
        (
            "Counselling service",
            "Ask about wellbeing support available through your university. This app does not replace that support.",
        ),
    ]
    for title, description in support_cards:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(description)
    st.subheader("Simple message starter")
    st.markdown(
        """
        Hello, I am having difficulty managing my current academic workload. I have
        tried to make a plan, but I am not sure what to do next. Could you advise me
        on the best support option or next step?
        """
    )
    render_public_safety_notice()


def render_about_and_safety() -> None:
    """Render public about and safety information."""
    st.title("About and safety")
    st.write(
        "This app is a public student-support version of an AI-assisted content "
        "strategy project. It uses existing research data and article drafts to "
        "recommend practical study-support content."
    )
    with st.container(border=True):
        st.markdown("**What this app can help with**")
        st.write(
            "Planning assignments, choosing a next study step, preparing for exams "
            "or presentations, and finding a university support starting point."
        )
    with st.container(border=True):
        st.markdown("**What this app does not do**")
        st.write(
            "It does not diagnose, treat, provide therapy, provide medication advice, "
            "or provide emergency/crisis support."
        )
    render_public_safety_notice()


def render_landing_section() -> None:
    """Render a simple public landing section."""
    with st.container(border=True):
        st.subheader("Plan safer student-support content")
        st.write(
            "Explore a small AI-assisted SEO project for student study pressure, "
            "assignment planning, and university support topics. The dashboard "
            "turns research notes into filters, summaries, an editorial calendar, "
            "and review checkpoints."
        )
        st.caption(
            "This is educational content strategy, not clinical guidance. It avoids "
            "diagnosis, treatment advice, medication advice, and crisis counselling."
        )


def render_project_explanation() -> None:
    """Explain the project for public users."""
    st.subheader("How to use this dashboard")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Explore demand**")
            st.write(
                "Search and filter keywords by student need, search intent, priority, "
                "and safety level."
            )
    with col2:
        with st.container(border=True):
            st.markdown("**Review responsibly**")
            st.write(
                "Use the article preview, SEO review, and safety review before turning "
                "a keyword into public content."
            )


def render_overview(
    keyword_data: pd.DataFrame,
    filtered_keywords: pd.DataFrame,
    calendar_data: pd.DataFrame,
) -> None:
    """Render the dashboard overview."""
    render_landing_section()
    render_project_explanation()
    st.subheader("Topic and intent summaries")

    topic_summary = count_values(filtered_keywords, "Topic")
    intent_summary = count_values(filtered_keywords, "Search Intent")
    priority_summary = sort_by_known_order(
        count_values(filtered_keywords, "Priority"), "Priority", PRIORITY_ORDER
    )
    safety_summary = sort_by_known_order(
        count_values(filtered_keywords, "Safety Level"), "Safety Level", SAFETY_ORDER
    )

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("**Keyword coverage by topic**")
            if topic_summary.empty:
                st.info("No topics match the current filters.", icon=":material/info:")
            else:
                st.altair_chart(
                    keyword_chart(topic_summary, "Topic", ""), width="stretch"
                )
    with right:
        with st.container(border=True):
            st.markdown("**Keyword coverage by search intent**")
            if intent_summary.empty:
                st.info(
                    "No search intents match the current filters.",
                    icon=":material/info:",
                )
            else:
                st.altair_chart(
                    keyword_chart(intent_summary, "Search Intent", ""), width="stretch"
                )

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Priority mix**")
            if priority_summary.empty:
                st.info("No priority data to show.", icon=":material/info:")
            else:
                st.dataframe(priority_summary, hide_index=True)
    with col2:
        with st.container(border=True):
            st.markdown("**Safety level mix**")
            if safety_summary.empty:
                st.info("No safety-level data to show.", icon=":material/info:")
            else:
                st.dataframe(safety_summary, hide_index=True)

    st.caption(
        f"Showing {len(filtered_keywords)} of {len(keyword_data)} keywords after filters."
    )


def render_keyword_explorer(filtered_keywords: pd.DataFrame) -> None:
    """Render the filterable keyword table and download action."""
    st.subheader("Keyword explorer")

    if filtered_keywords.empty:
        st.warning(
            "No keywords match the current filters. Try broadening the topic, "
            "intent, priority, safety level, or search text.",
            icon=":material/warning:",
        )
        return

    st.dataframe(
        filtered_keywords,
        hide_index=True,
        column_config={
            "Keyword": st.column_config.TextColumn("Keyword", pinned=True),
            "Safety Level": st.column_config.TextColumn("Safety level"),
            "Suggested Content Type": st.column_config.TextColumn(
                "Suggested content type"
            ),
        },
    )

    st.download_button(
        "Download filtered keywords",
        data=filtered_keywords.to_csv(index=False).encode("utf-8"),
        file_name="filtered-keywords.csv",
        mime="text/csv",
        icon=":material/download:",
    )


def render_article_preview(
    filtered_keywords: pd.DataFrame,
    article_markdown: str,
) -> None:
    """Render a public article preview and content brief."""
    st.subheader("Article preview")

    with st.container(border=True):
        st.markdown(extract_article_preview(article_markdown))

    st.subheader("Content brief")

    if filtered_keywords.empty:
        st.info(
            "Choose a broader filter set to generate a content brief.",
            icon=":material/info:",
        )
        return

    selected_keyword = st.selectbox(
        "Choose a keyword",
        filtered_keywords["Keyword"].tolist(),
    )
    row = filtered_keywords.loc[
        filtered_keywords["Keyword"].eq(selected_keyword)
    ].iloc[0]

    with st.container(border=True):
        st.markdown(f"**Working title:** {selected_keyword.capitalize()}")
        st.write(f"**Topic:** {row['Topic']}")
        st.write(f"**Search intent:** {row['Search Intent']}")
        st.write(f"**Suggested format:** {row['Suggested Content Type']}")
        st.write(f"**Priority:** {row['Priority']}")
        st.write(f"**Safety level:** {row['Safety Level']}")
        st.markdown(
            """
            **Safe-content checklist**

            - Keep guidance educational, practical, and non-clinical.
            - Encourage students to contact university support for persistent distress.
            - Avoid diagnosing, prescribing, or implying guaranteed outcomes.
            - Add crisis-routing language if the topic suggests urgent risk.
            """
        )


def render_calendar(calendar_data: pd.DataFrame) -> None:
    """Render the content calendar table."""
    st.subheader("Content calendar")

    status_options = sorted(calendar_data["Status"].unique().tolist())
    selected_status = st.segmented_control(
        "Status",
        ["All", *status_options],
        default="All",
    )

    visible_calendar = calendar_data
    if selected_status != "All":
        visible_calendar = calendar_data[calendar_data["Status"].eq(selected_status)]

    if visible_calendar.empty:
        st.info(
            "No calendar items match the selected status.",
            icon=":material/info:",
        )
        return

    with st.container(border=True):
        st.markdown("**Publishing status**")
        st.altair_chart(calendar_chart(calendar_data), width="stretch")

    st.dataframe(
        visible_calendar,
        hide_index=True,
        column_config={
            "Week": st.column_config.NumberColumn("Week", format="%d"),
            "Article Title": st.column_config.TextColumn("Article title", pinned=True),
            "Safety Level": st.column_config.TextColumn("Safety level"),
        },
    )


def render_review_panel(seo_markdown: str, safety_markdown: str) -> None:
    """Render SEO score and safety review summaries."""
    st.subheader("SEO score")

    score, total = extract_seo_score(seo_markdown)
    score_ratio = score / total if total else 0

    left, right = st.columns(2)
    with left:
        st.metric("SEO review score", f"{score}/{total}" if total else "Not found")
        if total:
            st.progress(score_ratio)
    with right:
        strengths = extract_markdown_section(seo_markdown, "Strengths")
        with st.container(border=True):
            st.markdown("**SEO strengths**")
            st.markdown(strengths or "No strengths section was found.")

    st.subheader("Safety review")
    safety_rating = extract_safety_rating(safety_markdown)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall safety rating", safety_rating)
    with col2:
        improvement = extract_markdown_section(safety_markdown, "Potential Improvement")
        with st.container(border=True):
            st.markdown("**Suggested safety improvement**")
            st.markdown(improvement or "No improvement section was found.")

    st.subheader("Safety boundary")

    with st.container(border=True):
        st.warning(
            "This project is for educational and self-management content. It does "
            "not provide diagnosis, medication advice, therapy, emergency "
            "counselling, or crisis support.",
            icon=":material/health_and_safety:",
        )
        st.markdown(
            """
            **Editorial rules for public content**

            - Use supportive, low-pressure language.
            - Keep recommendations concrete and student-centered.
            - Refer students to campus services or trusted professionals when a
              concern appears ongoing, severe, or outside study skills.
            - Treat crisis, self-harm, medication, diagnosis, and therapy topics as
              out of scope for this dashboard's content recommendations.
            """
        )

    st.subheader("AI-assisted workflow")
    st.markdown(
        """
        1. Define audience and safety boundaries.
        2. Generate keyword ideas.
        3. Review intent, priority, and risk.
        4. Build content pillars and an editorial calendar.
        5. Draft content with AI support.
        6. Evaluate SEO usefulness and emotional safety.
        7. Revise with human judgment before publishing.
        """
    )


def render_admin_strategy(
    keyword_data: pd.DataFrame,
    calendar_data: pd.DataFrame,
    article_markdown: str,
    seo_markdown: str,
    safety_markdown: str,
    content_strategy_markdown: str,
    ai_workflow_markdown: str,
    prompt_library_markdown: str,
) -> None:
    """Render the internal strategy dashboard in a separate admin area."""
    st.title("Admin Dashboard")
    st.caption(
        "Internal SEO, content strategy, evaluation, and AI workflow materials. "
        "This section is intentionally separate from the student-facing pages."
    )

    selected_filters = render_sidebar_filters(keyword_data)
    filtered_keywords = filter_keywords(keyword_data, *selected_filters)
    metrics = build_summary_metrics(keyword_data, calendar_data)
    render_metric_row(metrics)

    overview_tab, keywords_tab, calendar_tab, article_tab, review_tab, workflow_tab = st.tabs(
        [
            "Overview",
            "Keywords",
            "Calendar",
            "Article",
            "Review",
            "Workflow",
        ]
    )

    with overview_tab:
        render_overview(keyword_data, filtered_keywords, calendar_data)
        with st.expander("Content strategy document", icon=":material/description:"):
            st.markdown(content_strategy_markdown)
    with keywords_tab:
        render_keyword_explorer(filtered_keywords)
    with calendar_tab:
        render_calendar(calendar_data)
    with article_tab:
        render_article_preview(filtered_keywords, article_markdown)
    with review_tab:
        render_review_panel(seo_markdown, safety_markdown)
    with workflow_tab:
        with st.expander("AI workflow", expanded=True, icon=":material/account_tree:"):
            st.markdown(ai_workflow_markdown)
        with st.expander("Prompt library", icon=":material/library_books:"):
            st.markdown(prompt_library_markdown)


def main() -> None:
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="Mira Study Support",
        page_icon=":material/school:",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    try:
        keyword_data = load_project_csv(
            KEYWORD_FILE,
            REQUIRED_KEYWORD_COLUMNS,
            required_value_columns=KEYWORD_REQUIRED_VALUE_COLUMNS,
            unique_columns=KEYWORD_UNIQUE_COLUMNS,
        )
        calendar_data = load_project_csv(
            CALENDAR_FILE,
            REQUIRED_CALENDAR_COLUMNS,
            required_value_columns=CALENDAR_REQUIRED_VALUE_COLUMNS,
        )
        article_data = load_project_csv(
            ARTICLES_FILE,
            REQUIRED_ARTICLE_COLUMNS,
            required_value_columns=ARTICLE_REQUIRED_VALUE_COLUMNS,
            unique_columns=ARTICLE_UNIQUE_COLUMNS,
        )
    except DataValidationError as error:
        st.error(str(error), icon=":material/error:")
        st.stop()

    try:
        article_markdown = load_markdown_content(ARTICLE_DRAFT_FILE)
        seo_markdown = load_markdown_content(SEO_EVALUATION_FILE)
        safety_markdown = load_markdown_content(SAFETY_EVALUATION_FILE)
        content_strategy_markdown = load_markdown_content(CONTENT_STRATEGY_FILE)
        ai_workflow_markdown = load_markdown_content(AI_WORKFLOW_FILE)
        prompt_library_markdown = load_markdown_content(PROMPT_LIBRARY_FILE)
    except ContentFileError as error:
        st.error(str(error), icon=":material/error:")
        st.stop()

    apply_sidebar_theme_css()

    sidebar_logo = load_image_data_url(CHARACTER_FILE)

    with st.sidebar:
        st.markdown(
            f"""
            <div class="mira-sidebar-brand">
                <img class="mira-sidebar-logo" src="{sidebar_logo}" alt="Mira character logo">
                <strong>Mira Study Support</strong>
                <span>Calm study help and planning.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if "app_page" not in st.session_state:
            st.session_state.app_page = "Home"
        page = st.radio(
            "Menu",
            PUBLIC_NAVIGATION,
            label_visibility="collapsed",
            key="app_page",
        )
        st.caption("Non-clinical study support.")

    if page == "Home":
        render_public_home(keyword_data, calendar_data, article_data)
    elif page == "Explore Support":
        render_explore_support(keyword_data, calendar_data, article_data)
    elif page == "Assignment Planner":
        render_assignment_planner()
    elif page == "Articles":
        render_articles(article_markdown, article_data)
    elif page == "University Support":
        render_university_support()
    elif page == "About and Safety":
        render_about_and_safety()
    elif page == "Admin Dashboard":
        render_admin_strategy(
            keyword_data=keyword_data,
            calendar_data=calendar_data,
            article_markdown=article_markdown,
            seo_markdown=seo_markdown,
            safety_markdown=safety_markdown,
            content_strategy_markdown=content_strategy_markdown,
            ai_workflow_markdown=ai_workflow_markdown,
            prompt_library_markdown=prompt_library_markdown,
        )
    else:
        st.error(
            "The selected page could not be found. Choose another page from the sidebar.",
            icon=":material/error:",
        )


if __name__ == "__main__":
    main()
