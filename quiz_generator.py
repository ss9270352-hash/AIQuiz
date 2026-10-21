"""
quiz_generator.py - AI Provider Integration and Question Generation.

Connects to AI APIs (Google Gemini, OpenAI-compatible), builds strict prompts,
parses structured JSON, validates question candidates, and handles retries gracefully.
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

from quiz_logic import Question, validate_and_deduplicate_questions

# Load environment variables from .env if present
load_dotenv()


class AIProviderError(Exception):
    """User-friendly error indicating an issue with the AI provider or output."""
    pass


def get_api_credentials() -> Tuple[Optional[str], str, str]:
    """
    Detects configured AI provider and API key from environment variables.
    Returns (api_key, provider_name, model_name).
    """
    # Check Gemini first
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if gemini_key and gemini_key.strip():
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        return gemini_key.strip(), "gemini", model

    # Check OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key and openai_key.strip():
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return openai_key.strip(), "openai", model

    # Generic fallback
    generic_key = os.getenv("AI_API_KEY")
    if generic_key and generic_key.strip():
        provider = os.getenv("AI_PROVIDER", "gemini").lower()
        model = os.getenv("AI_MODEL", "gemini-1.5-flash" if provider == "gemini" else "gpt-4o-mini")
        return generic_key.strip(), provider, model

    return None, "none", ""


def is_api_configured() -> bool:
    """Checks whether an AI API key is configured."""
    key, _, _ = get_api_credentials()
    return key is not None and len(key) > 5


def extract_json_from_text(text: str) -> Any:
    """
    Extracts and parses JSON object or array from LLM response text,
    stripping Markdown code fences if present.
    """
    cleaned = text.strip()
    # Remove markdown code blocks if wrapped: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()

    # Sometimes models include text before or after the JSON bracket
    bracket_start = cleaned.find("[")
    bracket_end = cleaned.rfind("]")
    if bracket_start != -1 and bracket_end != -1 and bracket_end > bracket_start:
        cleaned = cleaned[bracket_start:bracket_end + 1]

    return json.loads(cleaned)


def build_system_prompt() -> str:
    return (
        "You are QuizMaster AI, an expert educational assessment specialist. "
        "Your task is to generate high-quality multiple-choice questions based STRICTLY on the "
        "provided lecture notes. Do NOT invent facts or test external knowledge that is not supported "
        "by the notes. Every question must be clear, unambiguous, and educational.\n\n"
        "Output format requirements:\n"
        "- Respond ONLY with a valid JSON array of question objects.\n"
        "- Do not include introductory text, conversational remarks, or markdown formatting outside the JSON.\n"
        "- Each question object MUST have these exact fields:\n"
        '  * "id": string identifier (e.g. "q1")\n'
        '  * "prompt": string of the question\n'
        '  * "options": dictionary with exactly 4 keys: "A", "B", "C", "D"\n'
        '  * "correct_option": string, exactly one of "A", "B", "C", or "D"\n'
        '  * "explanation": concise explanation of why the correct option is right and others are wrong\n'
        '  * "topic": short topic name (1-3 words) derived from the content\n'
        '  * "source_reference": short phrase or quote from the notes supporting this answer\n'
    )


def build_user_prompt(notes: str, count: int, difficulty: str) -> str:
    return (
        f"Generate exactly {count} multiple-choice questions from the following lecture notes.\n"
        f"Difficulty target: {difficulty}.\n\n"
        f"--- LECTURE NOTES ---\n{notes}\n--- END NOTES ---\n\n"
        f"Remember: Base all questions strictly on the text above. Return a JSON array of {count} questions."
    )


def call_gemini_api(api_key: str, model: str, prompt: str, timeout: int = 30) -> str:
    """Calls Google Gemini REST API using generateContent endpoint."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 4096,
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        raise AIProviderError("The request to the AI model timed out. Please try again with shorter notes.")
    except requests.exceptions.RequestException as e:
        raise AIProviderError(f"Network connection error while reaching the AI service: {e}")

    if response.status_code == 400:
        raise AIProviderError("The AI request was rejected. The lecture notes may be too long or contained unsupported characters.")
    elif response.status_code in (401, 403):
        raise AIProviderError("Invalid API key or unauthorized access. Please verify your GEMINI_API_KEY in the .env file.")
    elif response.status_code == 429:
        raise AIProviderError("AI rate limit reached. Please wait a moment and try again.")
    elif response.status_code >= 500:
        raise AIProviderError("The AI service is temporarily experiencing technical issues. Please try again shortly.")
    elif not response.ok:
        raise AIProviderError(f"AI service returned unexpected status ({response.status_code}).")

    data = response.json()
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise AIProviderError("The AI model did not return any content.")
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if not parts:
            raise AIProviderError("The AI response was empty.")
        return parts[0].get("text", "")
    except (KeyError, IndexError):
        raise AIProviderError("Failed to parse response structure from the AI service.")


def call_openai_api(api_key: str, model: str, prompt: str, timeout: int = 30) -> str:
    """Calls OpenAI-compatible chat completions REST API."""
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    url = f"{base_url}/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"} if "gpt-4" in model or "gpt-3.5" in model else None
    }
    # Clean None values
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        raise AIProviderError("The request to the AI model timed out. Please try again with shorter notes.")
    except requests.exceptions.RequestException as e:
        raise AIProviderError(f"Network error while reaching OpenAI service: {e}")

    if response.status_code in (401, 403):
        raise AIProviderError("Invalid OpenAI API key. Please check OPENAI_API_KEY in your .env file.")
    elif response.status_code == 429:
        raise AIProviderError("OpenAI rate limit or quota exceeded. Please check your account quota.")
    elif not response.ok:
        raise AIProviderError(f"OpenAI service returned error status {response.status_code}.")

    data = response.json()
    try:
        choice = data["choices"][0]["message"]["content"]
        return choice
    except (KeyError, IndexError):
        raise AIProviderError("Unexpected response format received from OpenAI.")


def execute_llm_call(prompt: str) -> str:
    """Dispatches prompt to the configured AI provider."""
    api_key, provider, model = get_api_credentials()
    if not api_key:
        raise AIProviderError(
            "No AI API key is configured. Please add GEMINI_API_KEY or OPENAI_API_KEY to your .env file, "
            "or test the application using the built-in sample quiz."
        )

    full_prompt = f"{build_system_prompt()}\n\n{prompt}"
    if provider == "gemini":
        return call_gemini_api(api_key, model, full_prompt)
    elif provider == "openai":
        return call_openai_api(api_key, model, prompt)
    else:
        raise AIProviderError(f"Unsupported AI provider '{provider}'. Supported providers are 'gemini' and 'openai'.")


def generate_quiz_from_notes(notes: str, count: int = 5, difficulty: str = "Medium") -> Tuple[List[Question], Optional[str]]:
    """
    Main entry point for generating quiz questions from lecture notes.
    Validates notes length, executes LLM call, parses JSON, validates questions,
    and performs a one-time corrective retry if necessary.

    Returns:
        (valid_questions, warning_message_if_fewer_questions)
    """
    stripped_notes = notes.strip()
    if len(stripped_notes) < 50:
        raise AIProviderError("Your lecture notes are too short (minimum 50 characters). Please provide more material so meaningful questions can be created.")
    if len(stripped_notes) > 30000:
        raise AIProviderError("Your notes exceed 30,000 characters. Please shorten or paste a specific section of the lecture notes.")

    # Primary attempt
    user_prompt = build_user_prompt(stripped_notes, count, difficulty)
    raw_response = execute_llm_call(user_prompt)

    questions = []
    parse_error = None
    try:
        parsed_data = extract_json_from_text(raw_response)
        # Handle case where LLM wraps array in a root dict, e.g. {"questions": [...]}
        if isinstance(parsed_data, dict):
            for key in ["questions", "quiz", "data", "items"]:
                if key in parsed_data and isinstance(parsed_data[key], list):
                    parsed_data = parsed_data[key]
                    break
        questions = validate_and_deduplicate_questions(parsed_data, max_count=count)
    except Exception as e:
        parse_error = str(e)

    # Corrective retry once if parse failed or zero valid questions returned
    if not questions:
        correction_prompt = (
            f"{user_prompt}\n\n"
            "CRITICAL: The previous output failed to produce valid questions or valid JSON. "
            "You MUST output ONLY a valid JSON array starting with '[' and ending with ']'. "
            "Ensure every question has 'id', 'prompt', 'options' (with keys A, B, C, D), 'correct_option', 'explanation', and 'topic'."
        )
        try:
            retry_raw = execute_llm_call(correction_prompt)
            parsed_retry = extract_json_from_text(retry_raw)
            if isinstance(parsed_retry, dict):
                for key in ["questions", "quiz", "data", "items"]:
                    if key in parsed_retry and isinstance(parsed_retry[key], list):
                        parsed_retry = parsed_retry[key]
                        break
            questions = validate_and_deduplicate_questions(parsed_retry, max_count=count)
        except Exception:
            pass

    if not questions:
        raise AIProviderError(
            "The AI model was unable to generate valid questions from this material. "
            "Please check that the notes contain clear educational facts and concepts, or try selecting a different question count."
        )

    warning_msg = None
    if len(questions) < count:
        warning_msg = (
            f"The AI generated {len(questions)} high-quality questions instead of the requested {count}. "
            "This happens when the lecture notes do not contain enough distinct concepts to formulate additional valid questions."
        )

    return questions, warning_msg
