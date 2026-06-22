from dataclasses import dataclass

from sympy import simplify
from sympy.core.expr import Expr
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


class MathParseError(ValueError):
    pass


@dataclass(slots=True)
class ParsedEquation:
    source_text: str
    left_text: str
    right_text: str
    left_expr: Expr
    right_expr: Expr


def parse_sympy_expr(text: str) -> Expr:
    if not isinstance(text, str):
        raise MathParseError("Математическое выражение должно быть строкой.")

    value = text.strip()
    if not value:
        raise MathParseError("Пустое математическое выражение.")

    try:
        expr = parse_expr(
            value,
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except Exception as exc:
        raise MathParseError(f"Не удалось распознать выражение: {value}") from exc

    return simplify(expr)


def parse_equation(text: str) -> ParsedEquation:
    if not isinstance(text, str):
        raise MathParseError("Уравнение должно быть строкой.")

    value = text.strip()
    if not value:
        raise MathParseError("Пустое уравнение.")

    if "=" not in value:
        raise MathParseError("В шаге нет знака '=' для разбора уравнения.")

    parts = value.split("=")
    if len(parts) != 2:
        raise MathParseError("Сейчас поддерживаются только уравнения с одним знаком '='.")

    left_text, right_text = [part.strip() for part in parts]
    if not left_text or not right_text:
        raise MathParseError("Левая или правая часть уравнения пустая.")

    left_expr = parse_sympy_expr(left_text)
    right_expr = parse_sympy_expr(right_text)

    return ParsedEquation(
        source_text=value,
        left_text=left_text,
        right_text=right_text,
        left_expr=left_expr,
        right_expr=right_expr,
    )


def equation_to_normal_form(eq: ParsedEquation) -> Expr:
    return simplify(eq.left_expr - eq.right_expr)
