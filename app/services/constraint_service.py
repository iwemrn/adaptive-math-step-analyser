from dataclasses import dataclass

from sympy import nan, simplify, zoo
from sympy.core.expr import Expr

from app.math_core.sympy_parser import MathParseError, parse_equation, parse_sympy_expr


@dataclass(slots=True)
class ConstraintCheckResult:
    violation_code: str | None
    details: list[str]
    error_probs: dict[str, float]


def _is_invalid_numeric_object(expr: Expr) -> bool:
    simplified = simplify(expr)

    if simplified == zoo:
        return True

    if simplified == nan:
        return True

    if getattr(simplified, "is_infinite", False):
        return True

    return False


def _has_nontrivial_denominator(expr: Expr) -> bool:
    expr_text = str(expr)
    return "/" in expr_text


def check_transition_constraints(before_text: str, after_text: str) -> ConstraintCheckResult:
    try:
        before_eq = parse_equation(before_text)
        after_eq = parse_equation(after_text)
    except MathParseError as exc:
        return ConstraintCheckResult(
            violation_code="math_parse_error",
            details=[str(exc)],
            error_probs={"math_parse_error": 1.0},
        )

    for expr in (
        before_eq.left_expr,
        before_eq.right_expr,
        after_eq.left_expr,
        after_eq.right_expr,
    ):
        if _is_invalid_numeric_object(expr):
            return ConstraintCheckResult(
                violation_code="division_by_zero",
                details=["В шаге обнаружено деление на ноль."],
                error_probs={"division_by_zero": 1.0},
            )

    pairs = [
        ("левая часть", before_eq.left_expr, after_eq.left_expr),
        ("правая часть", before_eq.right_expr, after_eq.right_expr),
    ]

    for side_name, before_expr, after_expr in pairs:
        if _has_nontrivial_denominator(before_expr) and not _has_nontrivial_denominator(after_expr):
            return ConstraintCheckResult(
                violation_code="possible_domain_loss",
                details=[
                    f"В {side_name} знаменатель исчез после преобразования."
                ],
                error_probs={
                    "possible_domain_loss": 0.9,
                    "invalid_transform": 0.1,
                },
            )

    return ConstraintCheckResult(
        violation_code=None,
        details=[],
        error_probs={},
    )


def check_single_expression_constraints(expression_text: str) -> ConstraintCheckResult:
    try:
        if "=" in expression_text:
            eq = parse_equation(expression_text)
            expressions_to_check = [eq.left_expr, eq.right_expr]
        else:
            expr = parse_sympy_expr(expression_text)
            expressions_to_check = [expr]
    except MathParseError as exc:
        return ConstraintCheckResult(
            violation_code="math_parse_error",
            details=[str(exc)],
            error_probs={"math_parse_error": 1.0},
        )

    for expr in expressions_to_check:
        if _is_invalid_numeric_object(expr):
            return ConstraintCheckResult(
                violation_code="division_by_zero",
                details=["В выражении обнаружено деление на ноль."],
                error_probs={"division_by_zero": 1.0},
            )

    return ConstraintCheckResult(
        violation_code=None,
        details=[],
        error_probs={},
    )
