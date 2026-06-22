from dataclasses import dataclass

from sympy import simplify

from app.math_core.sympy_parser import MathParseError, parse_equation


@dataclass(slots=True)
class DiagnosisResult:
    diagnosis_code: str
    error_probs: dict[str, float]


def _get_single_symbol(before_eq, after_eq):
    symbols = set()
    symbols.update(before_eq.left_expr.free_symbols)
    symbols.update(before_eq.right_expr.free_symbols)
    symbols.update(after_eq.left_expr.free_symbols)
    symbols.update(after_eq.right_expr.free_symbols)

    if len(symbols) == 1:
        return next(iter(symbols))
    return None


def _is_constant(expr) -> bool:
    return len(getattr(expr, "free_symbols", set())) == 0


def _detect_sign_error(before_eq, after_eq) -> bool:
    symbol = _get_single_symbol(before_eq, after_eq)
    if symbol is None:
        return False

    before_left_coeff = simplify(before_eq.left_expr.coeff(symbol))
    after_left_coeff = simplify(after_eq.left_expr.coeff(symbol))

    before_left_const = simplify(before_eq.left_expr - before_left_coeff * symbol)
    after_left_const = simplify(after_eq.left_expr - after_left_coeff * symbol)

    before_right = simplify(before_eq.right_expr)
    after_right = simplify(after_eq.right_expr)

    if not all(
        _is_constant(value)
        for value in (before_left_const, after_left_const, before_right, after_right)
    ):
        return False

    moved_constant = simplify(before_left_const - after_left_const)
    rhs_change = simplify(after_right - before_right)

    if moved_constant == 0:
        return False

    return simplify(rhs_change - moved_constant) == 0


def _detect_arithmetic_error(before_eq, after_eq) -> bool:
    symbol = _get_single_symbol(before_eq, after_eq)
    if symbol is None:
        return False

    before_nf = simplify(before_eq.left_expr - before_eq.right_expr)
    after_nf = simplify(after_eq.left_expr - after_eq.right_expr)

    before_coeff = simplify(before_nf.coeff(symbol))
    after_coeff = simplify(after_nf.coeff(symbol))

    before_const = simplify(before_nf - before_coeff * symbol)
    after_const = simplify(after_nf - after_coeff * symbol)

    if not _is_constant(before_const) or not _is_constant(after_const):
        return False

    if before_coeff == 0 or after_coeff == 0:
        return False

    if simplify(before_coeff - after_coeff) == 0:
        return False

    try:
        ratio = simplify(after_coeff / before_coeff)
    except Exception:
        return False

    if not _is_constant(ratio):
        return False

    if ratio == 0:
        return False

    expected_after_const = simplify(before_const * ratio)

    return simplify(after_const - expected_after_const) != 0


def diagnose_transition(before_text: str, after_text: str, is_valid: bool) -> DiagnosisResult:
    if is_valid:
        return DiagnosisResult(
            diagnosis_code="equivalent_transition",
            error_probs={},
        )

    try:
        before_eq = parse_equation(before_text)
        after_eq = parse_equation(after_text)
    except MathParseError:
        return DiagnosisResult(
            diagnosis_code="math_parse_error",
            error_probs={"math_parse_error": 1.0},
        )

    if _detect_sign_error(before_eq, after_eq):
        return DiagnosisResult(
            diagnosis_code="sign_error",
            error_probs={
                "sign_error": 0.85,
                "arithmetic_error": 0.10,
                "invalid_transform": 0.05,
            },
        )

    if _detect_arithmetic_error(before_eq, after_eq):
        return DiagnosisResult(
            diagnosis_code="arithmetic_error",
            error_probs={
                "arithmetic_error": 0.80,
                "sign_error": 0.10,
                "invalid_transform": 0.10,
            },
        )

    return DiagnosisResult(
        diagnosis_code="invalid_transform",
        error_probs={
            "invalid_transform": 0.85,
            "arithmetic_error": 0.10,
            "sign_error": 0.05,
        },
    )
