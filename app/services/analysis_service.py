from app.math_core.parser import parse_step, StepParseError


def analyze_step(raw_text: str) -> dict:
    try:
        parsed = parse_step(raw_text)
    except StepParseError as exc:
        return {
            "is_valid": False,
            "soft_score": 0.0,
            "math_score": 0.0,
            "logic_score": 0.0,
            "condition_score": 0.0,
            "goal_score": 0.0,
            "operation_type": "parse_error",
            "feedback": {
                "type": "explain_error",
                "text": str(exc),
            },
            "error_probs": {"parse_error": 1.0},
            "normalized_before": None,
            "normalized_after": None,
        }

    if parsed.operation_type == "parsed_transition":
        return {
            "is_valid": True,
            "soft_score": 0.85,
            "math_score": 0.8,
            "logic_score": 0.9,
            "condition_score": 0.8,
            "goal_score": 0.85,
            "operation_type": parsed.operation_type,
            "feedback": {
                "type": "confirm",
                "text": "Шаг успешно распознан.",
            },
            "error_probs": {},
            "normalized_before": parsed.before_text,
            "normalized_after": parsed.after_text,
        }

    return {
        "is_valid": True,
        "soft_score": 0.6,
        "math_score": 0.6,
        "logic_score": 0.6,
        "condition_score": 0.6,
        "goal_score": 0.6,
        "operation_type": parsed.operation_type,
        "feedback": {
            "type": "hint",
            "text": "Шаг сохранён, но для более точного анализа лучше использовать формат 'до => после'.",
        },
        "error_probs": {},
        "normalized_before": None,
        "normalized_after": parsed.after_text,
    }
