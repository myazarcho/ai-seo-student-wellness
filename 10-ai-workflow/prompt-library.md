# Step 10 — AI Prompt Library

## Purpose

This prompt library documents how AI was used to support keyword research, search-intent analysis, content planning, article drafting, SEO evaluation, and safety review.

AI was used as an assistant. Final decisions were reviewed and refined manually.

---

## Prompt 1 — Audience Persona

### Purpose

To create an initial profile of the target user.

### Prompt

You are a marketing researcher.

Create one audience persona for a safe, non-clinical student mental-wellness content platform.

Target audience:
- University students
- International students
- Master's students
- Students managing assignments, presentations, exams, and research

Include:
- Background
- Goals
- Challenges
- Search behaviour
- Preferred content style
- Support needs

Avoid:
- Diagnosis
- Medical assumptions
- Therapy language
- Unsupported claims

Use clear and simple English.

### Human Review

The persona was edited to make it more realistic for international master's students in Japan.

---

## Prompt 2 — Keyword Brainstorming

### Purpose

To generate possible SEO keyword ideas.

### Prompt

Generate 30 SEO keyword ideas for a safe, non-clinical student mental-wellness platform.

Target users:
- University students
- International students
- Graduate students

Topics:
- Academic stress
- Assignment deadlines
- Time management
- Exams
- Presentations
- University support services

For each keyword, provide:
- Topic
- Search intent
- Safety level
- Suggested content type

Avoid:
- Diagnosis
- Medication
- Therapy claims
- Crisis counselling
- Clinical treatment language

### Human Review

Keywords were manually grouped, reviewed for safety, and prioritized based on relevance to the target audience.

---

## Prompt 3 — Search-Intent Classification

### Purpose

To understand what the user wants from each keyword.

### Prompt

Classify the following SEO keywords by search intent.

Use these categories:
- Informational
- Problem-solving
- Support-seeking
- Navigational

For each keyword, explain:
1. What the user is likely experiencing
2. What answer they expect
3. What content format would be most useful

Keywords:
[PASTE KEYWORDS HERE]

Do not make medical or psychological diagnoses.

### Human Review

The search intent was checked manually to ensure the article format matched the likely user need.

---

## Prompt 4 — Content Pillar Creation

### Purpose

To organize keywords into a structured content strategy.

### Prompt

Organize the following student-support keywords into five clear content pillars.

For each pillar, provide:
- Pillar name
- User need
- Primary keywords
- Supporting keywords
- Four article ideas
- Suitable content formats

The platform provides educational and non-clinical support for university students.

Keywords:
[PASTE KEYWORDS HERE]

### Human Review

The final pillars were adjusted to avoid topic overlap and create a logical publishing sequence.

---

## Prompt 5 — SEO Article Outline

### Purpose

To create a search-intent-focused article structure.

### Prompt

Create a detailed SEO article outline for:

Title:
How to Manage Multiple Assignment Deadlines Without Feeling Overwhelmed

Primary keyword:
how to manage multiple assignment deadlines

Target audience:
University students, especially international and graduate students

Search intent:
Informational and problem-solving

Requirements:
- Clear H1, H2, and H3 structure
- Practical step-by-step guidance
- Examples
- Final checklist
- FAQ section
- University support options
- Non-clinical safety statement

Avoid:
- Diagnosis
- Medication advice
- Therapy claims
- Guaranteed outcomes
- Blaming language

### Human Review

The outline was reviewed to ensure that every section directly supported the user's problem-solving intent.

---

## Prompt 6 — Article Drafting

### Purpose

To create a first draft from the approved outline.

### Prompt

Write a first draft using the approved article outline.

Writing requirements:
- Simple English
- Short paragraphs
- Practical examples
- Supportive and realistic tone
- Approximately 1,000 words
- Natural use of the primary keyword
- No keyword stuffing
- No unsupported statistics

Safety requirements:
- No diagnosis
- No medication advice
- No therapy claims
- No promise to remove stress
- Mention appropriate university support options

### Human Review

The draft was edited for clarity, realism, tone, and safety before being added to the repository.

---

## Prompt 7 — SEO Evaluation

### Purpose

To evaluate the article's SEO quality.

### Prompt

Review the article as an SEO content editor.

Evaluate:
- Title relevance
- Search-intent match
- Primary keyword use
- Introduction quality
- Heading structure
- Readability
- Practical usefulness
- FAQ relevance
- Internal-link opportunities
- Call to action

Score each criterion from 1 to 5.

Return:
1. Evaluation table
2. Strengths
3. Weaknesses
4. Suggested meta description
5. Suggested URL slug
6. Specific improvements

Article:
[PASTE ARTICLE HERE]

### Human Review

The evaluation was compared with the original content goal before changes were accepted.

---

## Prompt 8 — Safety Review

### Purpose

To identify risky or inappropriate mental-wellness language.

### Prompt

Review the following article for emotional-safety and non-clinical content risks.

Check for:
- Diagnosis
- Medical advice
- Medication recommendations
- Therapy claims
- Overpromising
- Blaming language
- Unsupported health claims
- Missing support options
- Inappropriate crisis language

Return a table with:
- Original sentence
- Risk level
- Reason
- Safer replacement

If no issue is found, explain why the sentence is safe.

Article:
[PASTE ARTICLE HERE]

### Human Review

All suggested changes were reviewed manually before being included.

---

## Responsible AI Principle

AI outputs were not treated as final facts.

Every output was reviewed for:
- Relevance
- Accuracy
- Safety
- Tone
- Search-intent alignment
- Practical usefulness