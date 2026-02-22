"""Parser for D&D SRD armor tables."""

import re

from .base import slugify


# Category detection from table labels
CATEGORY_KEYWORDS_EN = {
    "light": "light",
    "medium": "medium",
    "heavy": "heavy",
    "shield": "shield",
}

CATEGORY_KEYWORDS_RU = {
    "лёгки": "light",
    "средни": "medium",
    "тяжёл": "heavy",
    "щит": "shield",
}

# Bold category rows in SRD 5.1 single table
BOLD_CATEGORIES_EN = {
    "light armor": "light",
    "medium armor": "medium",
    "heavy armor": "heavy",
    "shield": "shield",
}

BOLD_CATEGORIES_RU = {
    "лёгкие доспехи": "light",
    "средние доспехи": "medium",
    "тяжёлые доспехи": "heavy",
    "щит": "shield",
}


def _parse_ac(ac_str: str) -> tuple[int, bool, int | None]:
    """Parse AC string.

    Returns (ac_base, ac_dex_bonus, ac_max_dex).
    Examples:
        "11 + Dex modifier" → (11, True, None)
        "14 + Dex modifier (max 2)" → (14, True, 2)
        "16" → (16, False, None)
        "+2" → (2, False, None)
        "11 + модификатор Лов" → (11, True, None)
        "12 + модификатор Лов (макс. 2)" → (12, True, 2)
    """
    ac_str = ac_str.strip()

    # Shield: "+2"
    if ac_str.startswith("+"):
        m = re.match(r"\+(\d+)", ac_str)
        return (int(m.group(1)), False, None) if m else (0, False, None)

    # Extract base number
    m = re.match(r"(\d+)", ac_str)
    if not m:
        return (0, False, None)
    base = int(m.group(1))

    # Check for Dex modifier
    has_dex = bool(re.search(r"Dex|Лов", ac_str, re.IGNORECASE))
    if not has_dex:
        return (base, False, None)

    # Check for max
    max_match = re.search(r"max\s*(\d+)|макс\.?\s*(\d+)", ac_str, re.IGNORECASE)
    if max_match:
        max_dex = int(max_match.group(1) or max_match.group(2))
        return (base, True, max_dex)

    return (base, True, None)


def _parse_strength(str_str: str) -> int | None:
    """Parse strength requirement: 'Str 13' → 13, '—' → None."""
    str_str = str_str.strip()
    if str_str in ("—", "-", ""):
        return None
    m = re.search(r"(\d+)", str_str)
    return int(m.group(1)) if m else None


def _parse_stealth(stealth_str: str) -> bool:
    """Parse stealth: 'Disadvantage'/'Помеха' → True, else False."""
    s = stealth_str.strip().lower()
    return s in ("disadvantage", "помеха")


def _detect_category(label: str, lang: str) -> str | None:
    """Detect armor category from a table label line.

    Only matches actual Table:/Таблица: label lines (single line).
    """
    if "\n" in label.strip():
        return None
    label_lower = label.lower()
    if not (label_lower.startswith("table:") or label_lower.startswith("таблица:")):
        return None
    keywords = CATEGORY_KEYWORDS_RU if lang == "ru" else CATEGORY_KEYWORDS_EN
    for key, cat in keywords.items():
        if key in label_lower:
            return cat
    return None


def _parse_52_table(table_text: str, category: str, lang: str) -> list[dict]:
    """Parse SRD 5.2 armor table (separate tables per category).

    Columns: Armor | Armor Class (AC) | Strength | Stealth | Weight | Cost
    """
    armors = []
    for line in table_text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c is not None]
        while cells and cells[0] == "":
            cells.pop(0)
        while cells and cells[-1] == "":
            cells.pop()
        if len(cells) < 6:
            continue
        if "---" in cells[0]:
            continue
        first_lower = cells[0].lower()
        if first_lower in ("armor", "доспех"):
            continue

        name = cells[0].strip()
        ac_raw = cells[1].strip()
        str_raw = cells[2].strip()
        stealth_raw = cells[3].strip()
        weight = cells[4].strip()
        cost = cells[5].strip()

        ac_base, ac_dex, ac_max = _parse_ac(ac_raw)

        armors.append({
            "slug": slugify(name),
            "name": name,
            "name_en": None,
            "category": category,
            "ac_base": ac_base,
            "ac_dex_bonus": ac_dex,
            "ac_max_dex": ac_max,
            "strength_req": _parse_strength(str_raw),
            "stealth_disadvantage": _parse_stealth(stealth_raw),
            "weight": weight if weight not in ("—", "-") else None,
            "cost": cost,
        })
    return armors


def _parse_51_table(table_text: str, lang: str) -> list[dict]:
    """Parse SRD 5.1 armor table (single table with bold category rows).

    Columns: Armor | Cost | Armor Class (AC) | Strength | Stealth | Weight
    """
    armors = []
    category = "light"
    bold_map = BOLD_CATEGORIES_RU if lang == "ru" else BOLD_CATEGORIES_EN

    for line in table_text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c is not None]
        while cells and cells[0] == "":
            cells.pop(0)
        while cells and cells[-1] == "":
            cells.pop()
        if len(cells) < 6:
            continue
        if "---" in cells[0]:
            continue
        first = cells[0].strip()
        if first.lower() in ("armor", "доспех"):
            continue

        # Check for bold category row
        bold_match = re.match(r"\*\*(.+?)\*\*", first)
        if bold_match:
            cat_name = bold_match.group(1).strip().lower()
            if cat_name in bold_map:
                category = bold_map[cat_name]
            continue

        # SRD 5.1 columns: Armor | Cost | AC | Strength | Stealth | Weight
        name = first
        cost = cells[1].strip()
        ac_raw = cells[2].strip()
        str_raw = cells[3].strip()
        stealth_raw = cells[4].strip()
        weight = cells[5].strip()

        ac_base, ac_dex, ac_max = _parse_ac(ac_raw)

        armors.append({
            "slug": slugify(name),
            "name": name,
            "name_en": None,
            "category": category,
            "ac_base": ac_base,
            "ac_dex_bonus": ac_dex,
            "ac_max_dex": ac_max,
            "strength_req": _parse_strength(str_raw),
            "stealth_disadvantage": _parse_stealth(stealth_raw),
            "weight": weight if weight not in ("—", "-") else None,
            "cost": cost,
        })
    return armors


def parse_armor(text: str, lang: str) -> list[dict]:
    """Parse all armor entries from markdown text.

    Handles both SRD 5.2 (separate tables) and SRD 5.1 (single table).
    """
    armors = []

    # Check for SRD 5.2 format (multiple "Table:" labels for armor)
    table_sections = re.split(r"^(Table:.*|Таблица:.*)$", text, flags=re.MULTILINE)

    has_52_tables = False
    for section in table_sections:
        if _detect_category(section, lang) is not None:
            has_52_tables = True
            break

    if has_52_tables:
        i = 0
        while i < len(table_sections):
            section = table_sections[i]
            cat = _detect_category(section, lang)
            if cat and i + 1 < len(table_sections):
                table_body = table_sections[i + 1]
                armors.extend(_parse_52_table(table_body, cat, lang))
                i += 2
            else:
                i += 1
    else:
        # SRD 5.1: single "Table: Armor"
        table_start = None
        for marker in ["Table: Armor", "Таблица: Доспехи"]:
            idx = text.find(marker)
            if idx != -1:
                table_start = idx
                break

        if table_start is not None:
            rest = text[table_start:]
            end_match = re.search(r"\n## ", rest)
            table_text = rest[:end_match.start()] if end_match else rest
            armors = _parse_51_table(table_text, lang)

    return armors
