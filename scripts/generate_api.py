#!/usr/bin/env python3
"""Generate static JSON API from D&D SRD Markdown sources.

Usage:
    python3 scripts/generate_api.py --src-root src/dnd --output-dir site/api
"""

import argparse
import json
import sys
from pathlib import Path

# Add scripts dir to path so parsers package is importable
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import SOURCES, SKIP_HEADINGS_SPELL, SKIP_HEADINGS_MONSTER
from parsers import parse_spells, parse_monsters, parse_magic_items

SYSTEM = "dnd"
SYSTEM_NAME = "Dungeons & Dragons"

VERSION_NAMES = {"srd52": "SRD 5.2.1", "srd51": "SRD 5.1"}


def resolve_cross_refs(all_data: dict) -> None:
    """Resolve spell name → slug cross-references for monsters and magic items."""
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
                entity["spells"] = resolved


def write_json(path: Path, data) -> None:
    """Write data as JSON with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate D&D SRD JSON API")
    parser.add_argument("--src-root", required=True, help="Root directory of SRD markdown sources")
    parser.add_argument("--output-dir", required=True, help="Output directory for JSON API (e.g. site/api)")
    args = parser.parse_args()

    src_root = Path(args.src_root)
    output_dir = Path(args.output_dir)

    if not src_root.is_dir():
        print(f"Error: source root '{src_root}' not found", file=sys.stderr)
        sys.exit(1)

    system_dir = output_dir / SYSTEM

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

    # Write files and collect hierarchy info
    file_count = 0

    # Collectors for hierarchical meta files
    # ver → lang → resource → slugs
    hierarchy: dict[str, dict[str, dict[str, list[str]]]] = {}

    for (ver, lang, resource), entities in sorted(all_data.items()):
        hierarchy.setdefault(ver, {}).setdefault(lang, {})[resource] = []

        slugs = []
        for entity in entities:
            slug = entity["slug"]
            slugs.append(slug)
            write_json(system_dir / ver / lang / resource / f"{slug}.json", entity)
            file_count += 1

        slugs.sort()
        hierarchy[ver][lang][resource] = slugs

        # all.json
        write_json(
            system_dir / ver / lang / resource / "all.json",
            sorted(entities, key=lambda e: e["slug"]),
        )
        file_count += 1

    # --- Hierarchical meta.json files ---

    # Level 5: /dnd/{ver}/{lang}/{resource}/meta.json — list of slugs
    for ver, langs in sorted(hierarchy.items()):
        for lang, resources in sorted(langs.items()):
            for resource, slugs in sorted(resources.items()):
                write_json(system_dir / ver / lang / resource / "meta.json", {
                    "resource": resource,
                    "total": len(slugs),
                    "slugs": slugs,
                })
                file_count += 1

    # Level 4: /dnd/{ver}/{lang}/meta.json — available resources
    for ver, langs in sorted(hierarchy.items()):
        for lang, resources in sorted(langs.items()):
            res_list = []
            for resource, slugs in sorted(resources.items()):
                res_list.append({
                    "name": resource,
                    "total": len(slugs),
                    "path": f"{resource}/",
                })
            write_json(system_dir / ver / lang / "meta.json", {
                "language": lang,
                "resources": res_list,
            })
            file_count += 1

    # Level 3: /dnd/{ver}/meta.json — available languages
    for ver, langs in sorted(hierarchy.items()):
        lang_list = []
        for lang in sorted(langs):
            lang_list.append({
                "code": lang,
                "path": f"{lang}/",
            })
        write_json(system_dir / ver / "meta.json", {
            "version": ver,
            "name": VERSION_NAMES.get(ver, ver),
            "languages": lang_list,
        })
        file_count += 1

    # Level 2: /dnd/meta.json — available versions
    ver_list = []
    for ver in sorted(hierarchy):
        ver_list.append({
            "id": ver,
            "name": VERSION_NAMES.get(ver, ver),
            "path": f"{ver}/",
        })
    write_json(system_dir / "meta.json", {
        "system": SYSTEM,
        "name": SYSTEM_NAME,
        "versions": ver_list,
    })
    file_count += 1

    # Level 1: /api/meta.json — available systems
    write_json(output_dir / "meta.json", {
        "api_version": "1.0",
        "systems": [
            {
                "id": SYSTEM,
                "name": SYSTEM_NAME,
                "path": f"{SYSTEM}/",
            },
        ],
    })
    file_count += 1

    print(f"\nDone: {file_count} JSON files written ({total_entities} entities)")


if __name__ == "__main__":
    main()
