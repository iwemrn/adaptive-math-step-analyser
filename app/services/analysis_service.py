from app.math_core.parser import StepParseError, parse_step
from app.math_core.sympy_parser import MathParseError, parse_equation, parse_sympy_expr
from app.math_core.transitions import analyze_equation_transition
from app.services.diagnosis_service import diagnose_transition
from app.services.feedback_service import build_feedback


def analyze_step(raw_text: str) -> dict:
    try:
        parsed = parse_step(raw_text)
    except StepParseError:
        diagnosis_code = "parse_error"
        feedback = build_feedback(diagnosis_code, is_valid=False)

        return {
            "is_valid": False,
            "soft_score": 0.0,
            "math_score": 0.0,
            "logic_score": 0.0,
            "condition_score": 0.0,
            "goal_score": 0.0,
            "operation_type": "parse_error",
            "diagnosis_code": diagnosis_code,
            "feedback": feedback,
            "error_probs": {"parse_error": 1.0},
            "normalized_before": None,
            "normalized_after": None,
        }

    if parsed.operation_type == "parsed_transition":
        transition = analyze_equation_transition(parsed.before_text, parsed.after_text)
        diagnosis = diagnose_transition(
            before_text=parsed.before_text,
            after_text=parsed.after_text,
            is_valid=transition.is_valid,
        )
        feedback = build_feedback(
            diagnosis_code=diagnosis.diagnosis_code,
            is_valid=transition.is_valid,
        )

        return {
            "is_valid": transition.is_valid,
            "soft_score": transition.soft_score,
            "math_score": transition.math_score,
            "logic_score": transition.logic_score,
            "condition_score": transition.condition_score,
            "goal_score": transition.goal_score,
            "operation_type": transition.operation_type,
            "diagnosis_code": diagnosis.diagnosis_code,
            "feedback": feedback,
            "error_probs": diagnosis.error_probs,
            "normalized_before": parsed.before_text,
            "normalized_after": parsed.after_text,
        }

    try:
        if "=" in parsed.after_text:
            parse_equation(parsed.after_text)
        else:
            parse_sympy_expr(parsed.after_text)
    except MathParseError:
        diagnosis_code = "math_parse_error"
        feedback = build_feedback(diagnosis_code, is_valid=False)

        return {
            "is_valid": False,
            "soft_score": 0.0,
            "math_score": 0.0,
            "logic_score": 0.0,
            "condition_score": 0.0,
            "goal_score": 0.0,
            "operation_type": "math_parse_error",
            "diagnosis_code": diagnosis_code,
            "feedback": feedback,
            "error_probs": {"math_parse_error": 1.0},
            "normalized_before": None,
            "normalized_after": parsed.after_text,
        }

    diagnosis_code = "single_expression"
    feedback = build_feedback(diagnosis_code, is_valid=True)

    return {
        "is_valid": True,
        "soft_score": 0.6,
        "math_score": 0.6,
        "logic_score": 0.6,
        "condition_score": 0.6,
        "goal_score": 0.6,
        "operation_type": "single_expression",
        "diagnosis_code": diagnosis_code,
        "feedback": feedback,
        "error_probs": {},
        "normalized_before": None,
        "normalized_after": parsed.after_text,
    }
