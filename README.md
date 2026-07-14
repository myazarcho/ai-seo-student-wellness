# Mira Study Support

Mira Study Support is a public Streamlit app that gives university students
short, practical, non-clinical guidance for study challenges. The homepage is a
minimal chat-style experience where a student can describe what is happening in
plain language and receive a few concrete next steps.

The repository also preserves the original AI-assisted SEO and content strategy
research behind the app. Public users see a calm student-support experience;
strategy details live in a separate Admin Dashboard area.

Portfolio framing:

> SEO finds what students need. AI helps organize and improve the content. The
> app delivers the right support without exposing the marketing machinery.

In the public interface, students only see friendly chat guidance, support
topics, article titles, summaries, and practical next steps. Technical SEO
details, search intent, safety review fields, prompts, and workflow notes are
kept in the Admin Dashboard area and repository documentation.

## Safety boundary

This project provides general educational and self-management information. It
does not provide diagnosis, medication advice, therapy, emergency counselling,
or crisis support.

Content recommendations should stay practical, supportive, and non-clinical.
Topics involving crisis risk, self-harm, diagnosis, medication, or therapy
require expert review and are outside the dashboard's recommendations.

## Target audience

University students, especially international students, who experience academic
workload, multiple deadlines, exam pressure, time-management challenges, and
uncertainty about university support services.

## Repository structure

```text
app/
  app.py
  components/
  pages/
  utils/
assets/
data/
docs/
tests/
.streamlit/
README.md
requirements.txt
.gitignore
LICENSE
```

- `app/` - Streamlit application entry point and future app modules
- `assets/` - visual assets used by the app
- `data/` - runtime CSV data used by recommendations and admin views
- `docs/` - research, strategy, article drafts, evaluations, and AI workflow notes
- `tests/` - automated checks for data validation and recommendation logic
- `.streamlit/` - Streamlit theme configuration

Documentation is organized under `docs/`:

- `docs/project-foundation/` - project scope, boundaries, problem, and goal
- `docs/audience-persona/` - target student profile
- `docs/research-strategy/` - search journey and keyword research notes
- `docs/content-strategy/` - content strategy and content calendar notes
- `docs/articles/` - article outlines and drafts
- `docs/evaluation/` - SEO and safety evaluations
- `docs/ai-workflow/` - AI workflow notes, usage log, and prompts

## Public app features

- Chat-style student-facing homepage
- Conversation history using Streamlit session state
- Quick prompt chips for common study challenges
- Natural-language matching using deterministic keyword and topic data
- Topic cards for deadlines, academic stress, time management, exams,
  presentations, university support, and international student life
- Short assistant responses with practical next steps and one clear next action
- Contextual actions for planning, checklists, articles, and university support
- Public article cards that show only titles and summaries
- Assignment planner guidance
- Clean article reader
- University support guidance
- Calm non-clinical safety note in the footer

## Admin Dashboard features

The Admin Dashboard section keeps the original internal project materials
available without showing them on the public homepage:

- Keyword explorer
- Search intent and content strategy summaries
- Content calendar
- SEO evaluation
- Safety evaluation
- AI workflow and prompt documentation

## Setup

Use Python 3.10 or newer. The dependency versions in `requirements.txt` are
pinned to the versions used to verify this dashboard.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

## Run the app

```bash
python3 -m streamlit run app/app.py
```

Streamlit will print a local URL, usually `http://localhost:8501`. The root
page opens to the Mira Study Support chat interface. Use the collapsed sidebar
to open Explore Support, Assignment Planner, Articles, University Support,
About and Safety, or Admin Dashboard.

## Deploy on Streamlit Community Cloud

This repository is ready to deploy from GitHub.

1. Push the repository to GitHub.
2. In Streamlit Community Cloud, create a new app from the GitHub repository.
3. Set the app's main file path to:

   ```text
   app/app.py
   ```

4. Leave secrets empty. This app does not require API keys or private
   credentials.
5. Deploy the app.

Deployment notes:

- Keep `requirements.txt` at the repository root so Streamlit Community Cloud
  installs the pinned dependencies.
- Keep `.streamlit/config.toml` committed for the public theme.
- Do not commit `.streamlit/secrets.toml`, `.env`, virtual environments, or
  generated cache files.
- The app reads local repository files with `pathlib`, so `app/`, `data/`,
  `docs/`, and `assets/` should remain in the same relative locations.

## Run tests

```bash
python3 -m pytest
```

The tests verify that the CSV files exist, required columns are present, invalid
CSV schemas fail clearly, and the public chat matching/recommendation logic
behaves as expected.

## License

This project includes an MIT License. If the research content should have
different reuse terms than the code, document that separately.

## CSV schemas

The app expects these files and columns:

- `data/articles.csv`
  - `title`
  - `summary`
  - `topic`
  - `intent`
  - `safety_level`
  - `source_keyword`
  - `status`

- `data/keyword-research.csv`
  - `Keyword`
  - `Topic`
  - `Search Intent`
  - `Priority`
  - `Safety Level`
  - `Suggested Content Type`
- `data/content-calendar.csv`
  - `Week`
  - `Article Title`
  - `Primary Keyword`
  - `Content Pillar`
  - `Search Intent`
  - `Content Type`
  - `Priority`
  - `Safety Level`
  - `Status`

## Project workflow

1. Define the project foundation and safety boundary.
2. Create an audience persona.
3. Write the problem statement and project goal.
4. Map the user search journey.
5. Conduct keyword research.
6. Build a content strategy.
7. Create the first SEO article outline and draft.
8. Evaluate SEO quality and emotional safety.
9. Build an editorial calendar.
10. Document AI-assisted workflow and prompt usage.
11. Turn the strategy into a public student-support chat app with a separate
    admin dashboard.
