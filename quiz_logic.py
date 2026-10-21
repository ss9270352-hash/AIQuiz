"""
quiz_logic.py - Core data structures and logic for QuizMaster AI.

Handles quiz states, question validation, answer checking,
scoring, retry filtering, and session progress tracking.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Question:
    """Represents a single multiple-choice question."""
    id: str
    prompt: str
    options: Dict[str, str]  # e.g., {"A": "Option 1", "B": "Option 2", ...}
    correct_option: str       # e.g., "A"
    explanation: str
    topic: str = "General"
    source_reference: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "prompt": self.prompt,
            "options": self.options,
            "correct_option": self.correct_option,
            "explanation": self.explanation,
            "topic": self.topic,
            "source_reference": self.source_reference,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        return cls(
            id=str(data.get("id", "")),
            prompt=str(data.get("prompt", "")).strip(),
            options={k.strip().upper(): str(v).strip() for k, v in data.get("options", {}).items()},
            correct_option=str(data.get("correct_option", "")).strip().upper(),
            explanation=str(data.get("explanation", "")).strip(),
            topic=str(data.get("topic", "General")).strip() or "General",
            source_reference=data.get("source_reference"),
        )


def validate_question_data(item: Any) -> Optional[Question]:
    """
    Validates that a dictionary conforms to Question requirements:
    1. Must be a dict with id, prompt, options, correct_option, explanation.
    2. Exactly 4 distinct options with keys A, B, C, D (or similar 4 distinct keys).
    3. Exactly one valid correct_option matching an existing option key.
    4. Non-empty prompt and explanation.
    Returns Question if valid, otherwise None.
    """
    if not isinstance(item, dict):
        return None

    prompt = str(item.get("prompt", "")).strip()
    explanation = str(item.get("explanation", "")).strip()
    if not prompt or not explanation:
        return None

    raw_options = item.get("options")
    if not isinstance(raw_options, dict) and not isinstance(raw_options, list):
        return None

    # Normalize options to {"A": ..., "B": ..., "C": ..., "D": ...}
    normalized_options: Dict[str, str] = {}
    if isinstance(raw_options, list):
        if len(raw_options) != 4:
            return None
        keys = ["A", "B", "C", "D"]
        for k, text in zip(keys, raw_options):
            val = str(text).strip()
            if not val:
                return None
            normalized_options[k] = val
    else:
        # Dictionary format
        if len(raw_options) != 4:
            return None
        for k, v in raw_options.items():
            key = str(k).strip().upper()
            val = str(v).strip()
            if not val:
                return None
            normalized_options[key] = val

    # Verify that all 4 option texts are unique (distinct options)
    unique_texts = {text.lower() for text in normalized_options.values()}
    if len(unique_texts) != 4:
        return None

    correct_option = str(item.get("correct_option", "")).strip().upper()
    # Handle cases where correct_option might be written as "Option A" or matches full option text
    if correct_option not in normalized_options:
        # Check if the correct_option matched the full value of an option
        matched_key = None
        for k, v in normalized_options.items():
            if correct_option.lower() == v.lower():
                matched_key = k
                break
            if correct_option.startswith(k) and len(correct_option) <= 2:
                matched_key = k
                break
        if matched_key:
            correct_option = matched_key
        else:
            return None

    q_id = str(item.get("id", "")).strip() or f"q_{abs(hash(prompt)) % 100000}"
    topic = str(item.get("topic", "General")).strip() or "General"
    source_ref = item.get("source_reference")
    if source_ref:
        source_ref = str(source_ref).strip()

    return Question(
        id=q_id,
        prompt=prompt,
        options=normalized_options,
        correct_option=correct_option,
        explanation=explanation,
        topic=topic,
        source_reference=source_ref,
    )


def validate_and_deduplicate_questions(raw_list: Any, max_count: Optional[int] = None) -> List[Question]:
    """
    Validates a list of question candidates and removes duplicate prompts.
    """
    if not isinstance(raw_list, list):
        return []

    valid_questions: List[Question] = []
    seen_prompts = set()

    for item in raw_list:
        q = validate_question_data(item)
        if q:
            # Deduplicate by normalized prompt
            norm_prompt = "".join(ch.lower() for ch in q.prompt if ch.isalnum())
            if norm_prompt not in seen_prompts:
                seen_prompts.add(norm_prompt)
                valid_questions.append(q)
                if max_count and len(valid_questions) >= max_count:
                    break

    return valid_questions


@dataclass
class QuizSession:
    """Tracks state and results for an active or completed quiz round."""
    quiz_id: str
    title: str
    questions: List[Question]
    is_retry_round: bool = False
    current_index: int = 0
    user_answers: Dict[str, str] = field(default_factory=dict)  # question_id -> chosen_option
    is_submitted: Dict[str, bool] = field(default_factory=dict) # question_id -> True/False
    is_correct: Dict[str, bool] = field(default_factory=dict)   # question_id -> True/False

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def is_empty(self) -> bool:
        return len(self.questions) == 0

    @property
    def current_question(self) -> Optional[Question]:
        if 0 <= self.current_index < len(self.questions):
            return self.questions[self.current_index]
        return None

    @property
    def is_finished(self) -> bool:
        return len(self.questions) > 0 and self.current_index >= len(self.questions)

    @property
    def score(self) -> int:
        return sum(1 for val in self.is_correct.values() if val is True)

    @property
    def incorrect_count(self) -> int:
        return sum(1 for val in self.is_correct.values() if val is False)

    @property
    def accuracy_percentage(self) -> float:
        answered = len(self.is_correct)
        if answered == 0:
            return 0.0
        return round((self.score / answered) * 100, 1)

    def submit_answer(self, question_id: str, selected_option: str) -> bool:
        """
        Submits and checks an answer for a question.
        Guarantees that a question cannot be scored twice.
        Returns whether the answer was correct.
        """
        # If already submitted, do not re-score or alter the answer
        if self.is_submitted.get(question_id, False):
            return self.is_correct.get(question_id, False)

        q = next((item for item in self.questions if item.id == question_id), None)
        if not q:
            return False

        normalized_choice = selected_option.strip().upper()
        self.user_answers[question_id] = normalized_choice
        self.is_submitted[question_id] = True

        correct = (normalized_choice == q.correct_option)
        self.is_correct[question_id] = correct
        return correct

    def next_question(self) -> None:
        """Advances to the next question."""
        if self.current_index < len(self.questions):
            self.current_index += 1

    def get_incorrect_questions(self) -> List[Question]:
        """
        Returns the list of questions that were answered incorrectly.
        Only includes questions that have actually been submitted and marked false.
        """
        incorrect_ids = {qid for qid, is_corr in self.is_correct.items() if not is_corr}
        return [q for q in self.questions if q.id in incorrect_ids]

    def create_retry_session(self) -> Optional["QuizSession"]:
        """
        Creates a new, isolated QuizSession containing only the questions
        answered incorrectly in this round.
        """
        mistakes = self.get_incorrect_questions()
        if not mistakes:
            return None

        return QuizSession(
            quiz_id=f"{self.quiz_id}_retry_{abs(hash(str(mistakes))) % 1000}",
            title=f"Practice Mistakes ({len(mistakes)} questions)",
            questions=mistakes,
            is_retry_round=True,
            current_index=0,
            user_answers={},
            is_submitted={},
            is_correct={},
        )

    def get_topic_breakdown(self) -> Dict[str, Dict[str, int]]:
        """
        Returns a breakdown of questions per topic with counts of total, correct, and incorrect.
        Example: {'Python': {'total': 3, 'correct': 2, 'incorrect': 1}}
        """
        breakdown: Dict[str, Dict[str, int]] = {}
        for q in self.questions:
            topic = q.topic or "General"
            if topic not in breakdown:
                breakdown[topic] = {"total": 0, "correct": 0, "incorrect": 0}
            breakdown[topic]["total"] += 1
            if q.id in self.is_correct:
                if self.is_correct[q.id]:
                    breakdown[topic]["correct"] += 1
                else:
                    breakdown[topic]["incorrect"] += 1
        return breakdown


class SessionProgressTracker:
    """
    Maintains session-level statistics across multiple quizzes in memory.
    """
    def __init__(self):
        self.quizzes_completed: int = 0
        self.total_questions_answered: int = 0
        self.total_correct_answers: int = 0
        self.topic_stats: Dict[str, Dict[str, int]] = {}

    def record_completed_quiz(self, session: QuizSession) -> None:
        """Records the results of a finished quiz session."""
        if not session.is_finished:
            return

        self.quizzes_completed += 1
        for q in session.questions:
            if q.id in session.is_correct:
                self.total_questions_answered += 1
                topic = q.topic or "General"
                if topic not in self.topic_stats:
                    self.topic_stats[topic] = {"answered": 0, "correct": 0, "incorrect": 0}
                self.topic_stats[topic]["answered"] += 1
                if session.is_correct[q.id]:
                    self.total_correct_answers += 1
                    self.topic_stats[topic]["correct"] += 1
                else:
                    self.topic_stats[topic]["incorrect"] += 1

    @property
    def overall_accuracy(self) -> float:
        if self.total_questions_answered == 0:
            return 0.0
        return round((self.total_correct_answers / self.total_questions_answered) * 100, 1)

    def get_weak_topics(self) -> List[Dict[str, Any]]:
        """
        Returns list of topics sorted by lowest accuracy, for topics with at least one mistake.
        """
        weak = []
        for topic, stats in self.topic_stats.items():
            if stats["incorrect"] > 0:
                acc = round((stats["correct"] / stats["answered"]) * 100, 1)
                weak.append({
                    "topic": topic,
                    "accuracy": acc,
                    "incorrect": stats["incorrect"],
                    "answered": stats["answered"]
                })
        weak.sort(key=lambda x: (x["accuracy"], -x["incorrect"]))
        return weak
