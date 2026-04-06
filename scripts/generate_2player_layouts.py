#!/usr/bin/env python3
"""
Generate 2-player layout variants from 3-chef and 5-chef Overcooked layouts.

For each source layout, keeps only the 2 selected players (per LAYOUT_PLAYER_SELECTION.md),
replaces other player digits with spaces, and renumbers the kept players to 1 and 2.

Output naming: 2_on_3chefs_<base> / 2_on_5chefs_<base>
"""

import json
import os
import re
import sys

# ── Player selection mapping (keep_first → new "1", keep_second → new "2") ──
SELECTIONS = {
    # 3-chef layouts
    "3_chefs_cramped_room":            (1, 2),
    "3_chefs_coordination_ring":       (1, 3),
    "3_chefs_counter_circuit":         (1, 2),
    "3_chefs_asymmetric_advantages":   (1, 2),
    "3_chefs_forced_coordination":     (2, 3),
    "3_chefs_secret_heaven":           (1, 3),
    "3_chefs_storage_room":            (1, 3),
    "3_chefs_island_kitchen":          (2, 3),
    "3_chefs_long_onion":              (2, 3),
    "3_chefs_unequal_kitchens":        (1, 3),
    "3_chefs_clustered_kitchen":       (1, 3),
    # 5-chef layouts
    "5_chefs_counter_circuit":                (1, 4),
    "5_chefs_asymmetric_advantages":          (1, 2),
    "5_chefs_cramped_room":                   (1, 5),
    "5_chefs_coordination_ring":              (1, 4),
    "5_chefs_forced_coordination":            (2, 1),
    "5_chefs_secret_heaven":                  (1, 4),
    "5_chefs_storage_room":                   (1, 5),
    "5_chefs_central_chaos":                  (3, 5),
    "5_chefs_maze_of_ambiguity":              (1, 4),
    "5_chefs_ring_of_confusion":              (1, 2),
    "5_chefs_storage_room_lots_resources":    (1, 5),
}

LAYOUTS_DIR = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir,
    "overcooked_ai", "src", "overcooked_ai_py", "data", "layouts"
)
LAYOUTS_DIR = os.path.normpath(LAYOUTS_DIR)


def read_layout_file(path):
    """Read a .layout file (Python-literal JSON with triple-quoted grid and None)."""
    with open(path, "r") as f:
        raw = f.read()
    # Replace Python None → JSON null, triple-quoted strings → regular strings
    # Step 1: extract the triple-quoted grid value
    m = re.search(r'"""(.*?)"""', raw, re.DOTALL)
    if not m:
        raise ValueError(f"Could not find triple-quoted grid in {path}")
    grid_raw = m.group(1)
    # Normalise: strip leading/trailing whitespace per line, keep row order
    grid_lines = [line.strip() for line in grid_raw.strip().splitlines()]
    grid_str = "\n".join(grid_lines)

    # Step 2: rebuild as proper JSON
    # Replace the triple-quoted block with a JSON string
    json_grid = json.dumps(grid_str)
    before = raw[:m.start() - 0]
    after  = raw[m.end():]
    rebuilt = before + json_grid + after
    # None → null
    rebuilt = rebuilt.replace("None", "null")
    # trailing commas (lazy fix)
    rebuilt = re.sub(r",\s*([}\]])", r"\1", rebuilt)
    # Strip anything after the final closing brace (comments, etc.)
    last_brace = rebuilt.rfind("}")
    trailing_comment = ""
    if last_brace != -1:
        trailing_comment = rebuilt[last_brace + 1:].strip()
        rebuilt = rebuilt[: last_brace + 1]
    return json.loads(rebuilt), grid_lines, trailing_comment


def make_2player_grid(grid_lines, keep_a, keep_b):
    """
    Given grid_lines and which two original player numbers to keep,
    return new grid_lines with:
      - keep_a → '1'
      - keep_b → '2'
      - all other digits → ' '
    """
    all_digits = set("123456789")
    kept = {str(keep_a), str(keep_b)}
    drop = all_digits - kept
    new_lines = []
    for line in grid_lines:
        new_line = list(line)
        for i, ch in enumerate(new_line):
            if ch in drop:
                new_line[i] = " "
            elif ch == str(keep_a):
                new_line[i] = "1"
            elif ch == str(keep_b):
                new_line[i] = "2"
        new_lines.append("".join(new_line))
    return new_lines


def write_layout_file(path, data, grid_lines, trailing_comment=""):
    """Write a .layout file in the project's format (triple-quoted grid, Python None)."""
    # Build the grid with triple-quote + indentation (matching original style)
    indent = "                "
    grid_body = grid_lines[0] + "\n" + "\n".join(indent + l for l in grid_lines[1:])
    grid_block = '"""%s"""' % grid_body

    # Build orders section
    bonus = json.dumps(data.get("start_bonus_orders", []))
    all_orders = data.get("start_all_orders", [])
    if all_orders:
        order_strs = []
        for o in all_orders:
            order_strs.append(
                '        { "ingredients" : ' + json.dumps(o["ingredients"]) + "}"
            )
        all_orders_str = "[\n" + ",\n".join(order_strs) + "\n    ]"
    else:
        all_orders_str = "[]"

    rew = data.get("rew_shaping_params")
    rew_str = "None" if rew is None else json.dumps(rew)

    content = (
        "{\n"
        f'    "grid":  {grid_block},\n'
        f'    "start_bonus_orders": {bonus},\n'
        f'    "start_all_orders" : {all_orders_str},\n'
        f'    "rew_shaping_params": {rew_str}\n'
        "}\n"
    )
    if trailing_comment:
        content += trailing_comment + "\n"
    with open(path, "w") as f:
        f.write(content)


def main():
    created = []
    errors = []

    for src_name, (keep_a, keep_b) in SELECTIONS.items():
        src_path = os.path.join(LAYOUTS_DIR, src_name + ".layout")
        if not os.path.exists(src_path):
            errors.append(f"MISSING: {src_path}")
            continue

        # Determine output name: 2_on_3chefs_<base> or 2_on_5chefs_<base>
        if src_name.startswith("3_chefs_"):
            base = src_name[len("3_chefs_"):]
            dst_name = f"2_on_3chefs_{base}"
        elif src_name.startswith("5_chefs_"):
            base = src_name[len("5_chefs_"):]
            dst_name = f"2_on_5chefs_{base}"
        else:
            errors.append(f"UNKNOWN PREFIX: {src_name}")
            continue

        data, grid_lines, trailing = read_layout_file(src_path)
        new_grid = make_2player_grid(grid_lines, keep_a, keep_b)

        dst_path = os.path.join(LAYOUTS_DIR, dst_name + ".layout")
        write_layout_file(dst_path, data, new_grid, trailing)
        created.append((dst_name, keep_a, keep_b))
        print(f"  ✓ {src_name}  →  {dst_name}  (keep {keep_a},{keep_b} → 1,2)")

    print(f"\nCreated {len(created)} layout files in {LAYOUTS_DIR}")
    if errors:
        print("ERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
