"""Parser for D&D SRD condition entries."""

import re

from .base import split_blocks, extract_names


def parse_conditions(text: str, heading_level: int, lang: str,
                     after: str | None = None) -> list[dict]:
    """Parse all condition entries from markdown text.

    SRD 5.2: headings have [Condition]/[Состояние] tag — filter by tag.
    SRD 5.1: all #### headings in conditions file are conditions.
    """
    blocks = split_blocks(text, heading_level, after)
    conditions = []

    # Detect if this is 5.2 format (has [Condition] tags anywhere)
    has_tags = any("[Condition]" in h or "[Состояние]" in h for h, _ in blocks)

    for heading, body in blocks:
        if has_tags:
            # SRD 5.2: only include headings with [Condition]/[Состояние] tag
            if "[Condition]" not in heading and "[Состояние]" not in heading:
                continue
            # Remove tag from heading
            clean_heading = heading.replace("[Condition]", "").replace("[Состояние]", "").strip()
        else:
            # SRD 5.1: all headings are conditions
            clean_heading = heading.strip()

        name, name_en, slug = extract_names(clean_heading, lang)

        conditions.append({
            "slug": slug,
            "name": name,
            "name_en": name_en,
            "description_md": body.strip(),
        })

    return conditions
