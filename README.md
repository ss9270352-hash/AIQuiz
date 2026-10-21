# QuizMaster AI 📖

> A calm, human-designed study space that transforms raw lecture notes into interactive quizzes, tests conceptual understanding, and lets you target and master your mistakes.

[![License: MIT](https://img.shields.io/badge/License-MIT-356B52.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-242522.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)

---

## Overview

**QuizMaster AI** helps students transform lecture slides, study outlines, and textbook summaries into focused multiple-choice quizzes. Unlike generic chatbot interfaces, QuizMaster AI provides an understated, distraction-free learning environment where you answer questions one by one, receive immediate educational explanations, and practice only the questions you got wrong.

---

## Key Features

- **Painless Note Ingestion**: Paste lecture notes directly into a clean text area or drag and drop `.txt`, `.pdf`, or `.pptx` files. PDFs are extracted page by page; PowerPoint decks slide by slide, including tables and speaker notes.
- **Customizable Quiz Generation**: Choose between 5, 10, or 15 questions and specify target difficulty (Easy, Medium, Hard).
- **Strict, Grounded AI Logic**: Questions are strictly grounded in your provided text to avoid hallucinations.
- **Immediate Feedback & Explanations**: Answers are locked after submission; concise explanations highlight *why* the correct answer is right and cite references from the notes.
- **Targeted Mistake Practice**: One-click "Practise Mistakes" initiates a new, focused round containing *only* the questions answered incorrectly, without corrupting your previous scores.
- **Session Progress Tracking**: Tracks quizzes completed, overall accuracy, and flags specific topics requiring further study.
- **100% Offline Demonstration Mode**: Works immediately without an API key using built-in Computer Science fundamentals questions.
- **Privacy First**: Notes are processed purely in-memory and are never permanently stored or uploaded to external databases.

---

## Interface Preview

```
┌──────────────────────────────────────────────────────────────────┐
│  📖 QuizMaster AI                               ● Offline Ready  │
│  [1. Study Notes]   [2. Active Quiz]   [3. Results]   [4. Prog]  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Make your notes work harder.                                    │
│  Transform lecture summaries into focused interactive quizzes.   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Lecture 4: Asymptotic Notation and Stacks vs Queues...     │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Questions: [ 5 ]   Difficulty: [ Medium ]   Format: [ MCQ ]     │
│                                                                  │
│  [ Create My Quiz ]          [ Try Sample Quiz (Offline) ]       │
└──────────────────────────────────────────────────────────────────┘
```
*(Add your browser screenshots to an `assets/` directory and embed here: `![QuizMaster Screenshot](assets/screenshot.png)`)*

---

## Technologies Used

- **Python 3.10+**: Core application and business logic.
- **Streamlit**: Web application framework styled with custom CSS for an editorial design system.
- **Google Gemini REST API / OpenAI API**: AI provider integration for structured question synthesis.
- **Pytest**: Automated test suite for scoring, retry logic, validation, and document parsing.
- **pypdf & python-pptx**: Lightweight parsers that extract text from PDF lecture files and PowerPoint decks.
- **Requests & Python-Dotenv**: Minimal, reliable dependencies for HTTP calls and configuration.

---

## Prerequisites

- Python 3.10 or higher installed on your computer.
- Git (optional, for version control).
- An AI API key from either [Google AI Studio](https://aistudio.google.com/) (recommended) or [OpenAI](https://platform.openai.com/) (optional).

---

## Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/quizmaster-ai.git
cd quizmaster-ai
```

### 2. Set Up a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
streamlit run app.py
```
Open your browser to `http://localhost:8501`.

---

## Trying the Sample Quiz (No API Key Required)

You do **not** need an API key to evaluate or demonstrate QuizMaster AI!

1. Start the app: `streamlit run app.py`.
2. On the **1. Study Notes** tab, click the **"Try Sample Quiz (Offline)"** button.
3. Test the complete quiz workflow: answer questions, inspect the feedback, check your final score, and click **"Practise Mistakes"** to review missed questions.

---

## Configuring an AI Provider

To generate quizzes from your own lecture notes:

1. Copy the example configuration file:
   ```bash
   cp .env.example .env
   # On Windows PowerShell:
   # copy .env.example .env
   ```

2. Open `.env` in any text editor and add your API key:

   **For Google Gemini (Recommended):**
   ```env
   GEMINI_API_KEY=AIzaSyYourGeminiApiKeyHere
   GEMINI_MODEL=gemini-1.5-flash
   ```

   **For OpenAI:**
   ```env
   OPENAI_API_KEY=sk-proj-YourOpenAiKeyHere
   OPENAI_MODEL=gpt-4o-mini
   ```

3. Restart the Streamlit application. The status indicator in the top header will update to **"● AI Connected (gemini)"**.

---

## Running the Automated Test Suite

QuizMaster AI includes automated tests verifying scoring accuracy, duplicate prevention, retry isolation, and offline sample questions:

```bash
python -m pytest -v
```

All tests should pass with 100% green status (10 quiz-logic tests + 10 document-parser tests).

---

## Architecture & Project Structure

```
quizmaster-ai/
├── app.py                # Streamlit UI, custom editorial CSS, and navigation flow
├── quiz_generator.py     # AI connection, prompts, response parsing, and JSON validation
├── quiz_logic.py         # Question models, answer checking, scoring, and retry sessions
├── document_parser.py    # Text extraction from .txt, .pdf, and .pptx uploads
├── sample_data.py        # 15 offline CS questions and sample lecture notes
├── requirements.txt      # Minimal production dependencies
├── .env.example          # Environment variables template with placeholders
├── .gitignore            # Git exclusion rules protecting credentials and caches
├── LICENSE               # Open-source MIT license
├── README.md             # Project documentation and guides
└── tests/
    ├── __init__.py
    ├── test_quiz_logic.py     # Automated pytest test cases for quiz logic
    └── test_document_parser.py # Automated pytest test cases for file uploads
```

---

## Privacy & Security

- **Zero Permanent Storage**: Lecture notes and quiz results reside in volatile session memory.
- **Direct AI Calls**: Notes are transmitted solely over HTTPS to your configured AI endpoint when you click "Create My Quiz".
- **No Telemetry or Third-Party Trackers**: No third-party analytical cookies or scripts are included.
- **Safe Secrets Handling**: API keys are accessed via environment variables and never logged or committed to version control.

---

## Current Limitations & Future Roadmap

- **Session Persistence**: Closing the browser tab or restarting the server resets the current session progress. Future versions can add optional local SQLite export.
- **Question Formats**: Version 1 focuses exclusively on high-signal single-choice multiple-choice questions. Future updates can introduce flashcards and short-answer prompts.
- **File Upload Types**: Supports `.txt`, `.pdf`, and `.pptx` files. Scanned / image-only PDFs have no text layer to extract (OCR is not included), images and diagrams inside files are skipped, and the old `.ppt` format must be re-saved as `.pptx` first.

---

## Troubleshooting

- **"No AI API key is configured"**: Ensure your `.env` file is located in the root directory and contains `GEMINI_API_KEY=...` without surrounding quotes.
- **"Your notes are too short"**: Enter at least 50 characters so the model has sufficient conceptual grounding to formulate questions.
- **"No readable text was found in that PDF"**: The PDF is likely scanned images of pages with no text layer. Use a text-based PDF, or paste the notes as text — OCR is not included.
- **Extracted notes exceed 30,000 characters**: Large decks/PDFs extract fully, then hit the quiz limit. Review the extracted text in the Paste Notes tab and trim it to one chapter or section.
- **Port 8501 in use**: Run Streamlit on a custom port with `streamlit run app.py --server.port 8502`.

---

## License

This project is licensed under the [MIT License](LICENSE).
