from pathlib import Path

import pandas as pd
import streamlit as st


# Page configuration
st.set_page_config(
    page_title="Student Wellness SEO Dashboard",
    page_icon="📊",
    layout="wide",
)


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent

KEYWORD_FILE = (
    PROJECT_ROOT
    / "05-keyword-research"
    / "keyword-research.csv"
)

CALENDAR_FILE = (
    PROJECT_ROOT
    / "09-content-calendar"
    / "content-calendar.csv"
)


@st.cache_data
def load_csv(file_path: Path) -> pd.DataFrame:
    """Load a CSV file and return it as a pandas DataFrame."""
    if not file_path.exists():
        raise FileNotFoundError(
            f"Could not find the required file: {file_path}"
        )

    return pd.read_csv(file_path)


def show_metric_cards(keyword_data: pd.DataFrame) -> None:
    """Display summary metrics for the keyword dataset."""
    total_keywords = len(keyword_data)

    total_topics = (
        keyword_data["Topic"].nunique()
        if "Topic" in keyword_data.columns
        else 0
    )

    high_priority = (
        keyword_data["Priority"]
        .astype(str)
        .str.lower()
        .isin(["primary", "high"])
        .sum()
        if "Priority" in keyword_data.columns
        else 0
    )

    medium_safety = (
        keyword_data["Safety Level"]
        .astype(str)
        .str.lower()
        .eq("medium")
        .sum()
        if "Safety Level" in keyword_data.columns
        else 0
    )

    column1, column2, column3, column4 = st.columns(4)

    column1.metric("Total Keywords", total_keywords)
    column2.metric("Content Topics", total_topics)
    column3.metric("High-Priority Keywords", int(high_priority))
    column4.metric("Medium-Safety Topics", int(medium_safety))


def filter_keywords(keyword_data: pd.DataFrame) -> pd.DataFrame:
    """Create sidebar filters and return the filtered dataset."""
    st.sidebar.header("Keyword Filters")

    filtered_data = keyword_data.copy()

    if "Topic" in keyword_data.columns:
        topic_options = sorted(
            keyword_data["Topic"].dropna().unique().tolist()
        )

        selected_topics = st.sidebar.multiselect(
            "Topic",
            options=topic_options,
            default=topic_options,
        )

        filtered_data = filtered_data[
            filtered_data["Topic"].isin(selected_topics)
        ]

    if "Search Intent" in keyword_data.columns:
        intent_options = sorted(
            keyword_data["Search Intent"].dropna().unique().tolist()
        )

        selected_intents = st.sidebar.multiselect(
            "Search Intent",
            options=intent_options,
            default=intent_options,
        )

        filtered_data = filtered_data[
            filtered_data["Search Intent"].isin(selected_intents)
        ]

    if "Priority" in keyword_data.columns:
        priority_options = sorted(
            keyword_data["Priority"].dropna().unique().tolist()
        )

        selected_priorities = st.sidebar.multiselect(
            "Priority",
            options=priority_options,
            default=priority_options,
        )

        filtered_data = filtered_data[
            filtered_data["Priority"].isin(selected_priorities)
        ]

    if "Safety Level" in keyword_data.columns:
        safety_options = sorted(
            keyword_data["Safety Level"].dropna().unique().tolist()
        )

        selected_safety_levels = st.sidebar.multiselect(
            "Safety Level",
            options=safety_options,
            default=safety_options,
        )

        filtered_data = filtered_data[
            filtered_data["Safety Level"].isin(
                selected_safety_levels
            )
        ]

    search_text = st.sidebar.text_input(
        "Search keyword",
        placeholder="Example: assignment deadlines",
    )

    if search_text:
        filtered_data = filtered_data[
            filtered_data["Keyword"]
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                na=False,
            )
        ]

    return filtered_data


def main() -> None:
    """Run the Streamlit dashboard."""
    st.title("AI-Powered SEO Content Dashboard")

    st.write(
        "Explore the keyword research and content plan for a safe, "
        "non-clinical student mental-wellness platform."
    )

    st.info(
        "This project provides educational and self-management "
        "content. It does not provide diagnosis, medication advice, "
        "therapy, or emergency counselling."
    )

    try:
        keyword_data = load_csv(KEYWORD_FILE)
    except (FileNotFoundError, pd.errors.ParserError) as error:
        st.error(str(error))
        st.stop()

    show_metric_cards(keyword_data)

    filtered_keywords = filter_keywords(keyword_data)

    keyword_tab, topic_tab, calendar_tab, workflow_tab = st.tabs(
        [
            "Keyword Explorer",
            "Topic Summary",
            "Content Calendar",
            "Project Workflow",
        ]
    )

    with keyword_tab:
        st.subheader("Keyword Explorer")

        st.write(
            f"Showing {len(filtered_keywords)} of "
            f"{len(keyword_data)} keywords."
        )

        st.dataframe(
            filtered_keywords,
            use_container_width=True,
            hide_index=True,
        )

        csv_download = filtered_keywords.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download Filtered Keywords",
            data=csv_download,
            file_name="filtered-keywords.csv",
            mime="text/csv",
        )

    with topic_tab:
        st.subheader("Keywords by Topic")

        if "Topic" in filtered_keywords.columns:
            topic_summary = (
                filtered_keywords
                .groupby("Topic")
                .size()
                .reset_index(name="Keyword Count")
                .sort_values(
                    by="Keyword Count",
                    ascending=False,
                )
            )

            st.dataframe(
                topic_summary,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                topic_summary.set_index("Topic")
            )
        else:
            st.warning(
                "The Topic column was not found in the keyword file."
            )

        st.subheader("Keywords by Search Intent")

        if "Search Intent" in filtered_keywords.columns:
            intent_summary = (
                filtered_keywords
                .groupby("Search Intent")
                .size()
                .reset_index(name="Keyword Count")
                .sort_values(
                    by="Keyword Count",
                    ascending=False,
                )
            )

            st.dataframe(
                intent_summary,
                use_container_width=True,
                hide_index=True,
            )

            st.bar_chart(
                intent_summary.set_index("Search Intent")
            )

    with calendar_tab:
        st.subheader("Eight-Week Content Calendar")

        try:
            calendar_data = load_csv(CALENDAR_FILE)

            st.dataframe(
                calendar_data,
                use_container_width=True,
                hide_index=True,
            )

            if "Status" in calendar_data.columns:
                status_summary = (
                    calendar_data
                    .groupby("Status")
                    .size()
                    .reset_index(name="Article Count")
                )

                st.subheader("Publishing Status")

                st.bar_chart(
                    status_summary.set_index("Status")
                )

        except (FileNotFoundError, pd.errors.ParserError) as error:
            st.warning(str(error))

    with workflow_tab:
        st.subheader("AI-Assisted Content Workflow")

        st.markdown(
            """
            1. Define the target audience  
            2. Generate keyword ideas  
            3. Analyze search intent  
            4. Build content pillars  
            5. Create an article outline  
            6. Draft the article  
            7. Review SEO quality  
            8. Review emotional safety  
            9. Revise with human judgment  
            """
        )

        st.success(
            "Human Strategy → AI Assistance → "
            "Human Verification → Revision → Final Content"
        )


if __name__ == "__main__":
    main()