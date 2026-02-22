"""Parser for D&D SRD weapon tables."""

import re

from .base import slugify


# Table label → (category, type)
TABLE_CATEGORIES_EN = {
    "simple melee": ("simple", "melee"),
    "simple ranged": ("simple", "ranged"),
    "martial melee": ("martial", "melee"),
    "martial ranged": ("martial", "ranged"),
}

TABLE_CATEGORIES_RU = {
    "простое": "simple",
    "воинское": "martial",
    "ближнего боя": "melee",
    "дальнобойное": "ranged",
    "рукопашное": "melee",
}

# Bold category rows in SRD 5.1 single-table format
BOLD_CATEGORIES_EN = {
    "simple melee weapons": ("simple", "melee"),
    "simple ranged weapons": ("simple", "ranged"),
    "martial melee weapons": ("martial", "melee"),
    "martial ranged weapons": ("martial", "ranged"),
}

BOLD_CATEGORIES_RU = {
    "простое рукопашное оружие": ("simple", "melee"),
    "простое дальнобойное оружие": ("simple", "ranged"),
    "воинское рукопашное оружие": ("martial", "melee"),
    "воинское дальнобойное оружие": ("martial", "ranged"),
}

# Damage type mappings
DAMAGE_TYPES_RU = {
    "дробящий": "Bludgeoning",
    "колющий": "Piercing",
    "рубящий": "Slashing",
}


def _split_properties(props_str: str) -> list[str]:
    """Split properties string respecting parentheses.

    E.g. "Finesse, Light, Thrown (Range 20/60)" → ["Finesse", "Light", "Thrown (Range 20/60)"]
    """
    if not props_str or props_str.strip() in ("—", "-", ""):
        return []
    result = []
    depth = 0
    current = []
    for ch in props_str:
        if ch == "(":
            depth += 1
            current.append(ch)
        elif ch == ")":
            depth -= 1
            current.append(ch)
        elif ch == "," and depth == 0:
            token = "".join(current).strip()
            if token:
                result.append(token)
            current = []
        else:
            current.append(ch)
    token = "".join(current).strip()
    if token:
        result.append(token)
    return result


def _parse_damage(damage_str: str, lang: str) -> tuple[str, str | None]:
    """Parse damage string like '1d8 Slashing' → ('1d8', 'Slashing').

    Returns (damage_dice, damage_type).
    """
    damage_str = damage_str.strip()
    if not damage_str or damage_str in ("—", "-"):
        return ("", None)

    parts = damage_str.split(None, 1)
    dice = parts[0]
    dtype = None
    if len(parts) > 1:
        raw_type = parts[1].strip()
        if lang != "en":
            dtype = DAMAGE_TYPES_RU.get(raw_type.lower(), raw_type)
        else:
            dtype = raw_type.capitalize()
    return dice, dtype


def _parse_range_from_props(properties: list[str]) -> tuple[int | None, int | None]:
    """Extract range_normal and range_long from properties list.

    Looks for Thrown (Range 20/60) or Ammunition (Range 80/320; ...) patterns.
    Also handles RU: Метательное (дистанция 20/60), Боеприпас (дистанция 80/320; ...)
    """
    for prop in properties:
        m = re.search(r"(?:Range|дистанция)\s+(\d+)/(\d+)", prop, re.IGNORECASE)
        if m:
            return int(m.group(1)), int(m.group(2))
    return None, None


def _parse_table_rows(text: str, has_mastery: bool) -> list[dict]:
    """Parse markdown table rows into raw dicts.

    SRD 5.2 columns: Name | Damage | Properties | Mastery | Weight | Cost
    SRD 5.1 columns: Name | Cost | Damage | Weight | Properties
    """
    rows = []
    for line in text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        # Remove empty first/last cells from leading/trailing |
        cells = [c for c in cells if c or c == ""]
        if not cells:
            continue
        # Skip separator rows
        if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
            continue
        # Skip header rows
        first_lower = cells[0].lower().strip()
        if first_lower in ("name", "armor", "название", "доспех"):
            continue
        rows.append(cells)
    return rows


def _parse_52_table(table_text: str, category: str, weapon_type: str,
                    lang: str) -> list[dict]:
    """Parse SRD 5.2 weapon table (separate tables per category)."""
    weapons = []
    for line in table_text.split("\n"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        cells = [c for c in cells if c is not None]
        # Filter empty strings from split
        while cells and cells[0] == "":
            cells.pop(0)
        while cells and cells[-1] == "":
            cells.pop()
        if len(cells) < 6:
            continue
        # Skip separator and header rows
        if "---" in cells[0] or cells[0].lower() in ("name", "название"):
            continue

        name = cells[0].strip()
        damage_raw = cells[1].strip()
        props_raw = cells[2].strip()
        mastery_raw = cells[3].strip()
        weight = cells[4].strip()
        cost = cells[5].strip()

        dice, dtype = _parse_damage(damage_raw, lang)
        properties = _split_properties(props_raw)
        mastery = mastery_raw if mastery_raw and mastery_raw not in ("—", "-") else None
        range_n, range_l = _parse_range_from_props(properties)

        slug = slugify(name)

        weapons.append({
            "slug": slug,
            "name": name,
            "name_en": None,
            "category": category,
            "type": weapon_type,
            "damage_dice": dice,
            "damage_type": dtype,
            "properties": properties,
            "mastery": mastery,
            "range_normal": range_n,
            "range_long": range_l,
            "weight": weight if weight not in ("—", "-") else None,
            "cost": cost,
        })
    return weapons


def _parse_51_table(table_text: str, lang: str) -> list[dict]:
    """Parse SRD 5.1 weapon table (single table with bold category rows)."""
    weapons = []
    category = "simple"
    weapon_type = "melee"

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
        if len(cells) < 5:
            continue
        # Skip separator and header rows
        if "---" in cells[0]:
            continue
        first = cells[0].strip()
        if first.lower() in ("name", "название"):
            continue

        # Check for bold category row: **Simple Melee Weapons**
        bold_match = re.match(r"\*\*(.+?)\*\*", first)
        if bold_match:
            cat_name = bold_match.group(1).strip().lower()
            if cat_name in bold_map:
                category, weapon_type = bold_map[cat_name]
            continue

        # SRD 5.1 columns: Name | Cost | Damage | Weight | Properties
        name = first
        cost = cells[1].strip()
        damage_raw = cells[2].strip()
        weight = cells[3].strip()
        props_raw = cells[4].strip() if len(cells) > 4 else ""

        dice, dtype = _parse_damage(damage_raw, lang)
        properties = _split_properties(props_raw)
        range_n, range_l = _parse_range_from_props(properties)

        slug = slugify(name)

        weapons.append({
            "slug": slug,
            "name": name,
            "name_en": None,
            "category": category,
            "type": weapon_type,
            "damage_dice": dice,
            "damage_type": dtype,
            "properties": properties,
            "mastery": None,
            "range_normal": range_n,
            "range_long": range_l,
            "weight": weight if weight not in ("—", "-") else None,
            "cost": cost,
        })
    return weapons


def _detect_table_category(label: str, lang: str) -> tuple[str, str] | None:
    """Detect weapon category and type from a table label line.

    Only matches actual Table:/Таблица: label lines (single line).
    """
    # Must be a single-line table label, not a multi-line body section
    if "\n" in label.strip():
        return None
    label_lower = label.lower()
    # Must start with "Table:" or "Таблица:"
    if not (label_lower.startswith("table:") or label_lower.startswith("таблица:")):
        return None

    if lang == "en":
        for key, val in TABLE_CATEGORIES_EN.items():
            if key in label_lower:
                return val
    else:
        cat = None
        wtype = None
        for key, val in TABLE_CATEGORIES_RU.items():
            if key in label_lower:
                if val in ("simple", "martial"):
                    cat = val
                elif val in ("melee", "ranged"):
                    wtype = val
        if cat and wtype:
            return (cat, wtype)
    return None


def parse_weapons(text: str, lang: str) -> list[dict]:
    """Parse all weapon entries from markdown text.

    Handles both SRD 5.2 (separate tables with "Table:" labels)
    and SRD 5.1 (single table with bold category rows).
    """
    weapons = []

    # Check for SRD 5.2 format (multiple "Table:" labels)
    table_sections = re.split(r"^(Table:.*|Таблица:.*)$", text, flags=re.MULTILINE)

    is_52 = False
    for section in table_sections:
        cat_info = _detect_table_category(section, lang)
        if cat_info:
            is_52 = True
            break

    if is_52:
        # SRD 5.2: split by Table: labels
        i = 0
        while i < len(table_sections):
            section = table_sections[i]
            cat_info = _detect_table_category(section, lang)
            if cat_info and i + 1 < len(table_sections):
                category, wtype = cat_info
                table_body = table_sections[i + 1]
                weapons.extend(_parse_52_table(table_body, category, wtype, lang))
                i += 2
            else:
                i += 1
    else:
        # SRD 5.1: single "Table: Weapons" with bold category rows
        # Find the weapons table
        table_start = None
        for marker in ["Table: Weapons", "Таблица: Оружие"]:
            idx = text.find(marker)
            if idx != -1:
                table_start = idx
                break

        if table_start is not None:
            # Extract from table start to next ## heading or end
            rest = text[table_start:]
            end_match = re.search(r"\n## ", rest)
            table_text = rest[:end_match.start()] if end_match else rest
            weapons = _parse_51_table(table_text, lang)

    return weapons
