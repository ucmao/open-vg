#!/usr/bin/env python3
"""
Fix existing workflows on server:
  1. Migrate node types: prompt_preset -> prompt_default_hidden, image_input -> image_default, etc.
  2. From edges, set param_mappings and param_defaults on API nodes for params connected to
     default-value nodes (Prompt  /  /  / ), so preset prompt and
     image/video defaults are saved and used at runtime.

Run from backend dir:
  python scripts/fix_workflow_param_defaults_from_edges.py           # dry run
  python scripts/fix_workflow_param_defaults_from_edges.py --apply  # write to DB
"""
import argparse
import json
import sys
from pathlib import Path

backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.models.base import SessionLocal
from app.models.workflow import Workflow

# Node type migration (old -> new)
TYPE_MAP = {
    "prompt_preset": "prompt_default_hidden",
    "image_input": "image_default",
    "video_input": "video_default",
    "media_array_input": "media_list_default",
}

# Default-value node types (after migration: new names; we also accept old names in data)
DEFAULT_VALUE_TYPES = {
    "prompt_preset",
    "prompt_default_hidden",
    "image_input",
    "image_default",
    "video_input",
    "video_default",
    "media_array_input",
    "media_list_default",
}

# For each default-value node type, the output key used in mapping (e.g. $.nodeId.output.prompt)
OUTPUT_KEY_BY_TYPE = {
    "prompt_preset": "prompt",
    "prompt_default_hidden": "prompt",
    "image_input": "image",
    "image_default": "image",
    "video_input": "video",
    "video_default": "video",
    "media_array_input": "array",
    "media_list_default": "array",
}


def migrate_node_types(nodes):
    if not nodes or not isinstance(nodes, list):
        return
    for node in nodes:
        if not isinstance(node, dict):
            continue
        old_type = node.get("type")
        new_type = TYPE_MAP.get(old_type)
        if new_type:
            node["type"] = new_type


def get_param_name_from_target_handle(target_handle):
    if not target_handle:
        return ""
    if isinstance(target_handle, str) and target_handle.startswith("input-"):
        return target_handle.replace("input-", "", 1)
    return target_handle


def fix_workflow(w):
    nodes = w.nodes
    edges = w.edges
    if not nodes or not isinstance(nodes, list):
        return False
    if isinstance(nodes, str):
        try:
            nodes = json.loads(nodes)
        except (json.JSONDecodeError, TypeError):
            return False
    if not isinstance(nodes, list):
        return False
    if isinstance(edges, str):
        try:
            edges = json.loads(edges) if edges else []
        except (json.JSONDecodeError, TypeError):
            edges = []
    if not isinstance(edges, list):
        edges = []

    node_map = {n.get("id"): n for n in nodes if n.get("id")}
    changed = False

    # 1. Migrate node types
    migrate_node_types(nodes)

    # 2. Build (target_node_id, param_name) -> (source_node, edge)
    incoming = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        target_id = edge.get("target")
        source_id = edge.get("source")
        target_handle = edge.get("targetHandle", "")
        param_name = get_param_name_from_target_handle(target_handle)
        if not target_id or not param_name:
            continue
        source_node = node_map.get(source_id)
        if not source_node:
            continue
        stype = source_node.get("type")
        if stype not in DEFAULT_VALUE_TYPES:
            continue
        incoming.setdefault(target_id, {})[param_name] = source_node

    # 3. For each api_call node, set param_mappings and param_defaults from edges
    for node in nodes:
        if not isinstance(node, dict) or node.get("type") != "api_call":
            continue
        node_id = node.get("id")
        if not node_id:
            continue
        data = node.get("data")
        if not data or not isinstance(data, dict):
            data = {}
            node["data"] = data
        param_mappings = dict(data.get("param_mappings") or {})
        param_defaults = dict(data.get("param_defaults") or {})
        incoming_for_node = incoming.get(node_id) or {}
        for param_name, source_node in incoming_for_node.items():
            stype = source_node.get("type")
            output_key = OUTPUT_KEY_BY_TYPE.get(stype, "prompt" if "prompt" in stype else "image")
            mapping = f"$.{source_node.get('id')}.output.{output_key}"
            source_value = (source_node.get("data") or {}).get("value")
            if param_mappings.get(param_name) != mapping:
                param_mappings[param_name] = mapping
                changed = True
            if source_value is not None:
                if param_defaults.get(param_name) != source_value:
                    if stype in ("media_array_input", "media_list_default") and isinstance(source_value, str):
                        try:
                            param_defaults[param_name] = json.loads(source_value)
                        except (json.JSONDecodeError, TypeError):
                            param_defaults[param_name] = source_value
                    else:
                        param_defaults[param_name] = source_value
                    changed = True
        data["param_mappings"] = param_mappings
        data["param_defaults"] = param_defaults

    w.nodes = nodes
    return changed


def main():
    parser = argparse.ArgumentParser(
        description="Fix workflows: migrate node types and set param_mappings/param_defaults from edges"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes to DB (default: dry run)")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        workflows = db.query(Workflow).all()
        updated_count = 0
        for w in workflows:
            if fix_workflow(w):
                updated_count += 1
                print(f"Workflow id={w.id} name={w.name!r}: fixed param_mappings/param_defaults")
                if args.apply:
                    db.add(w)
        if args.apply:
            db.commit()
            print(f"Committed {updated_count} workflow(s).")
        else:
            print(f"Dry run: would fix {updated_count} workflow(s). Use --apply to write.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
