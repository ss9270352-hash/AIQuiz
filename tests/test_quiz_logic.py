"""
test_quiz_logic.py - Automated tests for QuizMaster AI core logic.

Tests:
1. Correct answer scoring.
2. Incorrect answer scoring.
3. Preventing a question from being scored twice.
4. Selecting only incorrect questions for retry.
5. Handling an empty question list.
6. Rejecting invalid question structures (missing keys, duplicate options, bad correct key).
7. Ensuring the sample quiz works offline without an API key.
8. Verifying SessionProgressTracker and weak topics identification.
"""

import pytest
from quiz_logic import (
    Question,
    QuizSession,
    SessionProgressTracker,
    validate_question_data,
    validate_and_deduplicate_questions
)
from sample_data import get_sample_quiz, SAMPLE_QUESTIONS_RAW
from quiz_generator import extract_json_from_text


@pytest.fixture
def dummy_questions():
    return [
        Question(
            id="q1",
            prompt="What is Python?",
            options={"A": "Snake", "B": "Programming Language", "C": "Car", "D": "Food"},
            correct_option="B",
            explanation="Python is an interpreted, high-level programming language.",
            topic="Python Basics"
        ),
        Question(
            id="q2",
            prompt="What is 2 + 2 in base 10?",
            options={"A": "3", "B": "4", "C": "5", "D": "22"},
            correct_option="B",
            explanation="Basic arithmetic: 2 + 2 equals 4.",
            topic="Math"
        ),
        Question(
            id="q3",
            prompt="Which data structure operates on FIFO?",
            options={"A": "Stack", "B": "Queue", "C": "Tree", "D": "Graph"},
            correct_option="B",
            explanation="Queues operate on First-In, First-Out (FIFO).",
            topic="Data Structures"
        )
    ]


def test_correct_answer_scoring(dummy_questions):
    """Test 1: Correct answer scoring updates score and status accurately."""
    session = QuizSession(
        quiz_id="test_quiz",
        title="Test Quiz",
        questions=dummy_questions
    )

    # Submit correct answer for q1
    result = session.submit_answer("q1", "B")
    assert result is True
    assert session.score == 1
    assert session.incorrect_count == 0
    assert session.accuracy_percentage == 100.0
    assert session.is_submitted["q1"] is True
    assert session.is_correct["q1"] is True


def test_incorrect_answer_scoring(dummy_questions):
    """Test 2: Incorrect answer scoring updates score and status accurately."""
    session = QuizSession(
        quiz_id="test_quiz",
        title="Test Quiz",
        questions=dummy_questions
    )

    # Submit wrong answer for q1
    result = session.submit_answer("q1", "A")
    assert result is False
    assert session.score == 0
    assert session.incorrect_count == 1
    assert session.accuracy_percentage == 0.0
    assert session.is_submitted["q1"] is True
    assert session.is_correct["q1"] is False


def test_prevent_double_scoring(dummy_questions):
    """Test 3: Preventing a question from being scored or altered twice."""
    session = QuizSession(
        quiz_id="test_quiz",
        title="Test Quiz",
        questions=dummy_questions
    )

    # Submit correct choice first
    res1 = session.submit_answer("q1", "B")
    assert res1 is True
    assert session.score == 1

    # Attempt to submit again with different answer
    res2 = session.submit_answer("q1", "A")
    # Must preserve initial answer and not double-score
    assert session.score == 1
    assert session.user_answers["q1"] == "B"
    assert session.is_correct["q1"] is True


def test_select_only_incorrect_for_retry(dummy_questions):
    """Test 4: Selecting only incorrect questions for retry round."""
    session = QuizSession(
        quiz_id="test_quiz",
        title="Test Quiz",
        questions=dummy_questions
    )

    # Answer q1 correctly (B)
    session.submit_answer("q1", "B")
    session.next_question()

    # Answer q2 incorrectly (chose C instead of B)
    session.submit_answer("q2", "C")
    session.next_question()

    # Answer q3 correctly (B)
    session.submit_answer("q3", "B")
    session.next_question()

    assert session.is_finished is True
    assert session.score == 2
    assert session.incorrect_count == 1

    # Mistakes should contain only q2
    mistakes = session.get_incorrect_questions()
    assert len(mistakes) == 1
    assert mistakes[0].id == "q2"

    # Create retry session
    retry_session = session.create_retry_session()
    assert retry_session is not None
    assert retry_session.is_retry_round is True
    assert retry_session.total_questions == 1
    assert retry_session.questions[0].id == "q2"
    assert retry_session.current_index == 0
    assert len(retry_session.user_answers) == 0
    assert len(retry_session.is_submitted) == 0

    # Original session remains unchanged
    assert session.score == 2
    assert session.incorrect_count == 1


def test_perfect_score_retry_returns_none(dummy_questions):
    """Test that retry session is None when all questions were answered correctly."""
    session = QuizSession(
        quiz_id="test_quiz",
        title="Test Quiz",
        questions=dummy_questions
    )

    session.submit_answer("q1", "B")
    session.submit_answer("q2", "B")
    session.submit_answer("q3", "B")
    session.current_index = 3

    assert session.is_finished is True
    assert session.incorrect_count == 0
    assert session.create_retry_session() is None


def test_empty_question_list():
    """Test 5: Handling an empty question list gracefully."""
    session = QuizSession(
        quiz_id="empty_quiz",
        title="Empty Quiz",
        questions=[]
    )

    assert session.is_empty is True
    assert session.total_questions == 0
    assert session.current_question is None
    assert session.is_finished is False
    assert session.score == 0
    assert session.incorrect_count == 0
    assert session.accuracy_percentage == 0.0
    assert session.create_retry_session() is None


def test_reject_invalid_question_structures():
    """Test 6: Rejecting malformed question candidates."""
    # 1. Missing prompt
    invalid_1 = {
        "id": "bad1",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "correct_option": "A",
        "explanation": "Valid explanation"
    }
    assert validate_question_data(invalid_1) is None

    # 2. Only 3 options instead of 4
    invalid_2 = {
        "id": "bad2",
        "prompt": "Question?",
        "options": {"A": "1", "B": "2", "C": "3"},
        "correct_option": "A",
        "explanation": "Valid"
    }
    assert validate_question_data(invalid_2) is None

    # 3. Duplicate option texts (not distinct)
    invalid_3 = {
        "id": "bad3",
        "prompt": "Question?",
        "options": {"A": "Same text", "B": "Same text", "C": "Diff 1", "D": "Diff 2"},
        "correct_option": "A",
        "explanation": "Valid"
    }
    assert validate_question_data(invalid_3) is None

    # 4. Correct option key not in options
    invalid_4 = {
        "id": "bad4",
        "prompt": "Question?",
        "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
        "correct_option": "Z",
        "explanation": "Valid"
    }
    assert validate_question_data(invalid_4) is None

    # 5. Non-dict input
    assert validate_question_data("string instead of dict") is None
    assert validate_question_data(None) is None


def test_sample_quiz_works_without_api_key():
    """Test 7: Sample quiz delivers valid questions offline without an API key."""
    # Test request for 5 questions
    sample_5 = get_sample_quiz(count=5, difficulty="Medium")
    assert len(sample_5) == 5
    for q in sample_5:
        assert isinstance(q, Question)
        assert len(q.options) == 4
        assert q.correct_option in q.options
        assert len(q.explanation) > 10

    # Test request for 10 questions
    sample_10 = get_sample_quiz(count=10, difficulty="Easy")
    assert len(sample_10) == 10

    # Test request for 15 questions
    sample_15 = get_sample_quiz(count=15, difficulty="Hard")
    assert len(sample_15) == 15


def test_session_progress_tracker(dummy_questions):
    """Test 8: SessionProgressTracker records finished quizzes and weak topics."""
    tracker = SessionProgressTracker()

    session = QuizSession(
        quiz_id="quiz_1",
        title="Quiz 1",
        questions=dummy_questions
    )
    # 2 correct (Python Basics, Data Structures), 1 incorrect (Math)
    session.submit_answer("q1", "B")
    session.submit_answer("q2", "A") # incorrect
    session.submit_answer("q3", "B")
    session.current_index = 3 # finish

    tracker.record_completed_quiz(session)
    assert tracker.quizzes_completed == 1
    assert tracker.total_questions_answered == 3
    assert tracker.total_correct_answers == 2
    assert tracker.overall_accuracy == 66.7

    weak = tracker.get_weak_topics()
    assert len(weak) == 1
    assert weak[0]["topic"] == "Math"
    assert weak[0]["incorrect"] == 1


def test_extract_json_markdown():
    """Test JSON extraction from LLM response wrapped in markdown code blocks."""
    markdown_response = """
    Here is the requested quiz:
    ```json
    [
        {
            "id": "q1",
            "prompt": "Test Prompt?",
            "options": {"A": "1", "B": "2", "C": "3", "D": "4"},
            "correct_option": "B",
            "explanation": "Because 2 is correct.",
            "topic": "General"
        }
    ]
    ```
    I hope this helps!
    """
    parsed = extract_json_from_text(markdown_response)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["id"] == "q1"
