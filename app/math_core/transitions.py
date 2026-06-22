from dataclasses import dataclass

from app.math_core.equivalence import are_equivalent_equations
from app.math_core.sympy_parser import MathParseError, parse_equation


@dataclass(slots=True)
class TransitionAnalysis:
    is_valid: bool
    operation_type: str
    soft_score: float
    math_score: float
    logic_score: float
    condition_score: float
    goal_score: float
    feedback_type: str
    feedback_text: str
    error_probs: dict


def analyze_equation_transition(before_text: str, after_text: str) -> TransitionAnalysis:
    try:
        before_eq = parse_equation(before_text)
        after_eq = parse_equation(after_text)
    except MathParseError as exc:
        return TransitionAnalysis(
            is_valid=False,
            operation_type="math_parse_error",
            soft_score=0.0,
            math_score=0.0,
            logic_score=0.0,
            condition_score=0.0,
            goal_score=0.0,
            feedback_type="explain_error",
            feedback_text=str(exc),
            error_probs={"math_parse_error": 1.0},
        )

    if are_equivalent_equations(before_eq, after_eq):
        return TransitionAnalysis(
            is_valid=True,
            operation_type="equivalent_transition",
            soft_score=0.95,
            math_score=1.0,
            logic_score=0.9,
            condition_score=0.9,
            goal_score=1.0,
            feedback_type="confirm",
            feedback_text="Преобразование математически корректно.",
            error_probs={},
        )

    return TransitionAnalysis(
        is_valid=False,
        operation_type="invalid_transition",
        soft_score=0.2,
        math_score=0.0,
        logic_score=0.4,
        condition_score=0.7,
        goal_score=0.2,
        feedback_type="explain_error",
        feedback_text="Преобразование не сохраняет равенство.",
        error_probs={"invalid_transition": 1.0},
    )
