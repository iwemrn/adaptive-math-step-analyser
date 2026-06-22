from dataclasses import dataclass

from app.math_core.normalizer import normalize_math_text


class StepParseError(ValueError):
    pass


@dataclass(slots=True)
class ParsedStep:
    raw_text: str
    normalized_text: str
    before_text: str | None
    after_text: str
    operation_type: str


def parse_step(raw_text: str) -> ParsedStep:
    normalized = normalize_math_text(raw_text)

    if not normalized:
        raise StepParseError("Пустой шаг решения.")

    if "=>" in normalized:
        before_text, after_text = [part.strip() for part in normalized.split("=>", 1)]

        if not before_text or not after_text:
            raise StepParseError("Шаг в формате 'до => после' заполнен не полностью.")

        return ParsedStep(
            raw_text=raw_text,
            normalized_text=normalized,
            before_text=before_text,
            after_text=after_text,
            operation_type="parsed_transition",
        )

    return ParsedStep(
        raw_text=raw_text,
        normalized_text=normalized,
        before_text=None,
        after_text=normalized,
        operation_type="single_expression",
    )
