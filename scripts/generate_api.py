#!/usr/bin/env python3
"""Generate static JSON API from D&D SRD Markdown sources.

Usage:
    python3 scripts/generate_api.py --src-root src/dnd --output-dir site/api/dnd
"""

import argparse
import json
import os
import sys
from pathlib import Path

# Add scripts dir to path so parsers package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import SOURCES, SKIP_HEADINGS_SPELL, SKIP_HEADINGS_MONSTER, RESOURCE_DIR
from parsers import parse_spells, parse_monsters, parse_magic_items


def resolve_cross_refs(all_data: dict) -> None:
    """Resolve spell name → slug cross-references for monsters and magic items.

    Modifies data in place: replaces spell name strings with slug strings.
    """
    # Build spell lookup: (ver, lang) → {lowercase_name: slug, lowercase_en_name: slug}
    spell_lookup: dict[tuple[str, str], dict[str, str]] = {}

    for key, entities in all_data.items():
        ver, lang, resource = key
        if resource != "spells":
            continue
        lookup = {}
        for spell in entities:
            lookup[spell["name"].lower()] = spell["slug"]
            if spell.get("name_en"):
                lookup[spell["name_en"].lower()] = spell["slug"]
        spell_lookup[(ver, lang)] = lookup

    # Resolve references in monsters and magic items
    for key, entities in all_data.items():
        ver, lang, resource = key
        if resource not in ("monsters", "animals", "magic-items"):
            continue

        lookup = spell_lookup.get((ver, lang), {})
        if not lookup:
            continue

        for entity in entities:
            if "spells" in entity and entity["spells"]:
                resolved = []
                for spell_name in entity["spells"]:
                    slug = lookup.get(spell_name.lower())
                    if slug:
                        resolved.append(slug)
                    # If not found, skip (might be a non-SRD spell)
                entity["spells"] = resolved


def write_json(path: Path, data: dict) -> None:
    """Write data as JSON with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate D&D SRD JSON API")
    parser.add_argument("--src-root", required=True, help="Root directory of SRD markdown sources")
    parser.add_argument("--output-dir", required=True, help="Output directory for JSON API")
    args = parser.parse_args()

    src_root = Path(args.src_root)
    output_dir = Path(args.output_dir)

    if not src_root.is_dir():
        print(f"Error: source root '{src_root}' not found", file=sys.stderr)
        sys.exit(1)

    # Parse all sources
    all_data: dict[tuple[str, str, str], list[dict]] = {}
    total_entities = 0

    for source in SOURCES:
        ver = source["ver"]
        lang = source["lang"]
        entity_type = source["type"]
        filepath = src_root / source["file"]
        heading_level = source["h"]
        after = source.get("after")
        out_resource = source.get("out")

        if not filepath.is_file():
            print(f"  Warning: {filepath} not found, skipping", file=sys.stderr)
            continue

        text = filepath.read_text(encoding="utf-8")

        if entity_type == "spell":
            entities = parse_spells(text, heading_level, lang, after, SKIP_HEADINGS_SPELL)
            resource = "spells"
        elif entity_type == "monster":
            entities = parse_monsters(text, heading_level, lang, after, SKIP_HEADINGS_MONSTER)
            resource = out_resource or "monsters"
        elif entity_type == "magic_item":
            entities = parse_magic_items(text, heading_level, lang, after)
            resource = "magic-items"
        else:
            print(f"  Warning: unknown type '{entity_type}', skipping", file=sys.stderr)
            continue

        key = (ver, lang, resource)
        if key in all_data:
            all_data[key].extend(entities)
        else:
            all_data[key] = entities

        count = len(entities)
        total_entities += count
        print(f"  {ver}/{lang}/{resource}: {count} entities from {source['file']}")

    # Resolve cross-references
    resolve_cross_refs(all_data)

    # Write individual JSON files
    file_count = 0
    meta: dict = {"api_version": "1.0", "versions": {}}

    for (ver, lang, resource), entities in sorted(all_data.items()):
        # Ensure version/lang structure in meta
        if ver not in meta["versions"]:
            meta["versions"][ver] = {"name": _version_name(ver), "languages": {}}
        if lang not in meta["versions"][ver]["languages"]:
            meta["versions"][ver]["languages"][lang] = {}

        slugs = []
        for entity in entities:
            slug = entity["slug"]
            slugs.append(slug)

            entity_path = output_dir / ver / lang / resource / f"{slug}.json"
            write_json(entity_path, entity)
            file_count += 1

        slugs.sort()
        meta["versions"][ver]["languages"][lang][resource] = {
            "total": len(entities),
            "slugs": slugs,
        }

        # Write all.json — full list of all entities for this resource
        all_path = output_dir / ver / lang / resource / "all.json"
        write_json(all_path, sorted(entities, key=lambda e: e["slug"]))
        file_count += 1

    # Write meta.json
    meta_path = output_dir / "meta.json"
    write_json(meta_path, meta)
    file_count += 1

    print(f"\nDone: {file_count} JSON files written ({total_entities} entities)")


def _version_name(ver: str) -> str:
    return {"srd52": "SRD 5.2.1", "srd51": "SRD 5.1"}.get(ver, ver)


if __name__ == "__main__":
    main()
