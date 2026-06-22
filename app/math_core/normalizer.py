import re


_SYMBOL_REPLACEMENTS = {
    "−": "-",
    "–": "-",
    "—": "-",
    "×": "*",
    "·": "*",
    "÷": "/",
    "^": "**",
    "→": "=>",
    "⇒": "=>",
    "⟹": "=>",
}


def normalize_math_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("Шаг должен быть строкой.")

    normalized = text.strip()

    for source, target in _SYMBOL_REPLACEMENTS.items():
        normalized = normalized.replace(source, target)

    normalized = re.sub(r"\s+", " ", normalized)

    # Сначала нормализуем стрелку перехода
    normalized = re.sub(r"\s*=>\s*", " => ", normalized)

    # Потом обычный знак равенства, но не внутри =>
    normalized = re.sub(r"(?<!>)\s*=\s*(?!>)", " = ", normalized)

    # Чистим лишние пробелы ещё раз
    normalized = re.sub(r"\s+", " ", normalized).strip()

    return normalized
