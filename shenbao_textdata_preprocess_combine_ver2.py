# -*- coding: utf-8 -*-
"""Combine and preprocess Shanghai Library Shenbao textdata CSV files.

Workflow:
1. Stage 1 appends source rows without changing source field values.
2. Stage 2 deduplicates rows by article_id and selects one representative row.
3. Stage 3 reorders the deduplicated rows and creates analysis-ready fields.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import parse_qs, urlsplit


SOURCE_PATTERN = "shenbao_textdata_*_1to*.csv"
SOURCE_COLUMNS = [
    "label",
    "page",
    "item_index",
    "list_title",
    "detail_url",
    "publish_variant",
    "date",
    "issue_page",
    "special_column",
    "h1",
    "lv1_div",
    "content-box2",
    "era_year",
    "category",
    "theme",
    "collect_error",
]
SOURCE_TO_STAGE1 = {
    "content-box2": "content_box2",
}

STAGE1_COLUMNS = [
    "stage1_index",
    "label",
    "page",
    "item_index",
    "list_title",
    "detail_url",
    "publish_variant",
    "date",
    "issue_page",
    "special_column",
    "h1",
    "lv1_div",
    "content_box2",
    "era_year",
    "category",
    "theme",
    "collect_error",
]

STAGE2_COLUMNS = [
    "dataset_label",
    "source_labels",
    "stage1_indices",
    "representative_label",
    "representative_item_index",
    "select_reason",
    "article_id",
    "qrynewstype",
    "detail_url",
    "publish_variant",
    "date",
    "issue_page",
    "special_column",
    "h1",
    "lv1_div",
    "content_box2",
    "era_year",
    "category",
    "theme",
    "collect_error",
    "collision",
    "collision_columns",
]

STAGE3_COLUMNS = [
    "dataset_label",
    "dataset_index",
    "source_labels",
    "stage1_indices",
    "representative_label",
    "representative_item_index",
    "select_reason",
    "article_id",
    "qrynewstype",
    "publish_variant",
    "date",
    "issue_page",
    "special_column",
    "era_year",
    "chinese_era_year",
    "japanese_era_year",
    "category",
    "theme",
    "collect_error",
    "collision",
    "collision_columns",
    "h1",
    "lv1_div",
    "content_box2",
    "analysis_text",
    "analysis_text_rules",
]

COLLISION_FIELDS = [
    "publish_variant",
    "date",
    "issue_page",
    "special_column",
    "h1",
    "lv1_div",
    "content_box2",
    "era_year",
    "category",
    "theme",
    "collect_error",
]

WHITESPACE_RE = re.compile(r"\s+")
CHINESE_ERA_RE = re.compile(r"([清淸][^日]*?年|民國[^日]*?年)")
JAPANESE_ERA_RE = re.compile(r"(日.*?年)")
QRYNEWSTYPE_ORDER = {"SP": 0, "SP_AD": 1, "SP_FH": 2, "SP_HK": 3}
LEFT_CORNER_BRACKET = "\u3014"  # 〔


def configure_csv_field_limit() -> None:
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            return
        except OverflowError:
            limit //= 10


def read_text(value: object) -> str:
    return "" if value is None else str(value)


def normalize_header(name: str) -> str:
    return SOURCE_TO_STAGE1.get(name, name)


def trim_text(value: str) -> str:
    return read_text(value).strip()


def unique_in_order(values: Iterable[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.append(value)
    return seen


def parse_detail_url(url: str) -> tuple[str, str]:
    if not url:
        return "", ""

    query = urlsplit(url).query
    parsed = parse_qs(query)
    article_id = parsed.get("id", [""])[0]
    qrynewstype = parsed.get("qrynewstype", [""])[0]

    if not article_id:
        match = re.search(r"[?&]id=([^&]+)", url)
        article_id = match.group(1) if match else ""
    if not qrynewstype:
        match = re.search(r"[?&]qrynewstype=([^&]+)", url)
        qrynewstype = match.group(1) if match else ""

    return article_id, qrynewstype


def default_input_dir() -> Path:
    cwd = Path.cwd()
    script_dir = Path(__file__).resolve().parent
    candidates = [
        cwd / "shenbao" / "shenbao_textdata",
        script_dir / "shenbao" / "shenbao_textdata",
        cwd / "shenbao_textdata",
        script_dir / "shenbao_textdata",
        cwd / "shlib-shenbao-dataset-workflow" / "shenbao_textdata",
        script_dir / "shlib-shenbao-dataset-workflow" / "shenbao_textdata",
    ]
    for candidate in candidates:
        if candidate.exists() and any(candidate.glob(SOURCE_PATTERN)):
            return candidate
    return cwd / "shenbao" / "shenbao_textdata"


def discover_source_files(input_dir: Path) -> list[Path]:
    files = sorted(input_dir.glob(SOURCE_PATTERN))
    excluded_words = (
        "stage1",
        "stage2",
        "stage3",
        "preprocess",
        "deduplicated",
        "preprocessed",
        "appended",
        "combined",
        "exception",
        "marker",
        "inpageordertest",
    )
    source_files = [
        path for path in files if not any(word in path.name.lower() for word in excluded_words)
    ]
    if not source_files:
        raise FileNotFoundError(
            f"No source CSV files matching {SOURCE_PATTERN!r} were found in {input_dir}"
        )
    return source_files


def open_dict_reader(path: Path) -> tuple[object, csv.DictReader]:
    handle = path.open("r", encoding="utf-8", newline="")
    reader = csv.DictReader(handle)
    fieldnames = reader.fieldnames or []
    if fieldnames and any(name.startswith("\ufeff") for name in fieldnames):
        handle.close()
        handle = path.open("r", encoding="utf-8-sig", newline="")
        reader = csv.DictReader(handle)
    return handle, reader


def read_source_rows(source_files: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    stage1_index = 1

    required_columns = set(SOURCE_COLUMNS)

    for source_file in source_files:
        handle, reader = open_dict_reader(source_file)
        try:
            fieldnames = reader.fieldnames or []
            missing = sorted(required_columns.difference(fieldnames))
            if missing:
                raise ValueError(f"{source_file} is missing required columns: {missing}")

            for row in reader:
                appended = {"stage1_index": str(stage1_index)}
                for source_column in SOURCE_COLUMNS:
                    target_column = normalize_header(source_column)
                    appended[target_column] = read_text(row.get(source_column, ""))
                rows.append(appended)
                stage1_index += 1
        finally:
            handle.close()

    return rows


def representative_reason(candidates: list[dict[str, str]]) -> tuple[dict[str, str], str]:
    remaining = list(candidates)
    first_reducing_reason = ""
    criteria: list[tuple[str, Callable[[dict[str, str]], object], object]] = [
        ("1_no_error", lambda row: trim_text(row.get("collect_error", "")) == "", True),
        ("2_page_exist", lambda row: trim_text(row.get("issue_page", "")) != "", True),
        ("3_long_theme", lambda row: len(read_text(row.get("theme", ""))), "max"),
        ("4_long_box2", lambda row: len(read_text(row.get("content_box2", ""))), "max"),
        ("5_long_h1", lambda row: len(read_text(row.get("h1", ""))), "max"),
        ("6_long_lv1_div", lambda row: len(read_text(row.get("lv1_div", ""))), "max"),
    ]

    for reason, getter, target in criteria:
        values = [getter(row) for row in remaining]
        if len(set(values)) <= 1:
            continue

        if target == "max":
            best_value = max(values)
        else:
            best_value = target

        filtered = [row for row in remaining if getter(row) == best_value]
        if filtered:
            if len(filtered) < len(remaining) and not first_reducing_reason:
                first_reducing_reason = reason
            remaining = filtered
            if len(remaining) == 1:
                return remaining[0], first_reducing_reason or reason

    selected = min(remaining, key=lambda row: int(row["stage1_index"]))
    return selected, first_reducing_reason or "7_small_index"


def classify_collision(rows: list[dict[str, str]]) -> tuple[str, str]:
    differing_columns = [
        column for column in COLLISION_FIELDS if len({read_text(row.get(column, "")) for row in rows}) > 1
    ]
    if differing_columns:
        return "T", ";".join(differing_columns)
    return "F", ""


def make_stage2_rows(stage1_rows: list[dict[str, str]], dataset_label: str) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    missing_article_ids: list[str] = []

    for row in stage1_rows:
        article_id, qrynewstype = parse_detail_url(row.get("detail_url", ""))
        if not article_id:
            missing_article_ids.append(row["stage1_index"])
        enriched = dict(row)
        enriched["article_id"] = article_id
        enriched["qrynewstype"] = qrynewstype
        groups[article_id].append(enriched)

    if missing_article_ids:
        preview = ", ".join(missing_article_ids[:20])
        raise ValueError(
            "Rows without article_id cannot be deduplicated. "
            f"stage1_index examples: {preview}"
        )

    stage2_rows: list[dict[str, str]] = []
    sorted_keys = sorted(
        groups,
        key=lambda key: min(int(row["stage1_index"]) for row in groups[key]),
    )

    for article_id in sorted_keys:
        source_rows = sorted(groups[article_id], key=lambda row: int(row["stage1_index"]))
        representative, select_reason = representative_reason(source_rows)
        collision, collision_columns = classify_collision(source_rows)

        stage2_rows.append(
            {
                "dataset_label": dataset_label,
                "source_labels": ";".join(unique_in_order(row.get("label", "") for row in source_rows)),
                "stage1_indices": ";".join(row["stage1_index"] for row in source_rows),
                "representative_label": representative.get("label", ""),
                "representative_item_index": representative.get("item_index", ""),
                "select_reason": select_reason,
                "article_id": article_id,
                "qrynewstype": representative.get("qrynewstype", ""),
                "detail_url": representative.get("detail_url", ""),
                "publish_variant": representative.get("publish_variant", ""),
                "date": representative.get("date", ""),
                "issue_page": representative.get("issue_page", ""),
                "special_column": representative.get("special_column", ""),
                "h1": representative.get("h1", ""),
                "lv1_div": representative.get("lv1_div", ""),
                "content_box2": representative.get("content_box2", ""),
                "era_year": representative.get("era_year", ""),
                "category": representative.get("category", ""),
                "theme": representative.get("theme", ""),
                "collect_error": representative.get("collect_error", ""),
                "collision": collision,
                "collision_columns": collision_columns,
            }
        )

    return stage2_rows


def issue_page_sort_key(value: str) -> tuple[int, int]:
    text = trim_text(value)
    if not text:
        return 1, sys.maxsize
    try:
        return 0, int(text)
    except ValueError:
        return 1, sys.maxsize


def split_era_year(era_year: str) -> tuple[str, str]:
    text = trim_text(era_year)
    chinese_match = CHINESE_ERA_RE.search(text)
    japanese_match = JAPANESE_ERA_RE.search(text)
    chinese = chinese_match.group(1).strip() if chinese_match else ""
    japanese = japanese_match.group(1).strip() if japanese_match else ""
    return chinese, japanese


def max_overlap_length(left: str, right: str) -> int:
    max_length = min(len(left), len(right))
    for length in range(max_length, 0, -1):
        if left[-length:] == right[:length]:
            return length
    return 0


def build_analysis_text(row: dict[str, str]) -> tuple[str, str]:
    special_column = trim_text(row.get("special_column", ""))
    qrynewstype = trim_text(row.get("qrynewstype", ""))
    h1_text = trim_text(row.get("h1", ""))
    lv1_text = trim_text(row.get("lv1_div", ""))
    content_box2_text = trim_text(row.get("content_box2", ""))

    include_h1 = True
    include_lv1 = True
    rules: list[str] = []

    if special_column == "分類廣告":
        include_h1 = False
        rules.append("1_drop_h1_for_classified_ad")

    if lv1_text == "本報訊":
        include_lv1 = False
        rules.append("2_drop_benbaoxun")

    if special_column == "" and qrynewstype == "SP" and h1_text and content_box2_text:
        overlap_length = max_overlap_length(h1_text, content_box2_text)
        if overlap_length > 0 and LEFT_CORNER_BRACKET in content_box2_text[overlap_length: overlap_length + 2]:
            rules.append("3_bracket_dedup")
            content_box2_text = trim_text(content_box2_text[overlap_length:])
            if lv1_text:
                marker_variants = (f"〔{lv1_text}〕", f"（{lv1_text}）")
                for marker in marker_variants:
                    if content_box2_text.startswith(marker):
                        rules.append("4_delete_lv1_marker")
                        content_box2_text = trim_text(content_box2_text[len(marker):])
                        break

    if not rules:
        rules.append("5_plain_merge")

    parts: list[str] = []
    if include_h1 and h1_text:
        parts.append(h1_text)
    if include_lv1 and lv1_text:
        parts.append(lv1_text)
    if content_box2_text:
        parts.append(content_box2_text)

    return " ".join(parts), ";".join(rules)


def stage3_sort_key(row: dict[str, str]) -> tuple[tuple[int, str], int, tuple[int, int], str]:
    date_text = trim_text(row.get("date", ""))
    date_key = (0, date_text) if date_text else (1, "9999-99-99")
    qry_key = QRYNEWSTYPE_ORDER.get(trim_text(row.get("qrynewstype", "")), 99)
    issue_key = issue_page_sort_key(row.get("issue_page", ""))
    article_id = trim_text(row.get("article_id", ""))
    return date_key, qry_key, issue_key, article_id


def make_stage3_rows(stage2_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sorted_rows = sorted(stage2_rows, key=stage3_sort_key)
    stage3_rows: list[dict[str, str]] = []

    for dataset_index, row in enumerate(sorted_rows, start=1):
        chinese_era_year, japanese_era_year = split_era_year(row.get("era_year", ""))
        analysis_text, analysis_text_rules = build_analysis_text(row)

        stage3_rows.append(
            {
                "dataset_label": row.get("dataset_label", ""),
                "dataset_index": str(dataset_index),
                "source_labels": row.get("source_labels", ""),
                "stage1_indices": row.get("stage1_indices", ""),
                "representative_label": row.get("representative_label", ""),
                "representative_item_index": row.get("representative_item_index", ""),
                "select_reason": row.get("select_reason", ""),
                "article_id": row.get("article_id", ""),
                "qrynewstype": row.get("qrynewstype", ""),
                "publish_variant": row.get("publish_variant", ""),
                "date": row.get("date", ""),
                "issue_page": row.get("issue_page", ""),
                "special_column": row.get("special_column", ""),
                "era_year": row.get("era_year", ""),
                "chinese_era_year": chinese_era_year,
                "japanese_era_year": japanese_era_year,
                "category": row.get("category", ""),
                "theme": row.get("theme", ""),
                "collect_error": row.get("collect_error", ""),
                "collision": row.get("collision", ""),
                "collision_columns": row.get("collision_columns", ""),
                "h1": row.get("h1", ""),
                "lv1_div": row.get("lv1_div", ""),
                "content_box2": row.get("content_box2", ""),
                "analysis_text": analysis_text,
                "analysis_text_rules": analysis_text_rules,
            }
        )

    return stage3_rows


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def count_values(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[read_text(row.get(column, ""))] += 1
    return dict(sorted(counts.items(), key=lambda item: (item[0] == "", item[0])))


def print_summary(
    source_files: list[Path],
    stage1_rows: list[dict[str, str]],
    stage2_rows: list[dict[str, str]],
    stage3_rows: list[dict[str, str]],
    output_paths: list[Path],
) -> None:
    print("Input files:")
    for source_file in source_files:
        print(f"- {source_file}")
    print()
    print(f"Stage 1 appended rows: {len(stage1_rows)}")
    print(f"Stage 2 deduplicated articles: {len(stage2_rows)}")
    print(f"Stage 3 preprocessed articles: {len(stage3_rows)}")
    print(f"Duplicate source rows removed by article_id: {len(stage1_rows) - len(stage2_rows)}")
    print()
    print("select_reason:")
    for key, value in count_values(stage2_rows, "select_reason").items():
        print(f"- {key}: {value}")
    print()
    print("collision_columns:")
    for key, value in count_values(stage2_rows, "collision_columns").items():
        label = key if key else "(none)"
        print(f"- {label}: {value}")
    print()
    print("analysis_text_rules:")
    for key, value in count_values(stage3_rows, "analysis_text_rules").items():
        print(f"- {key}: {value}")
    print()
    print("Output files:")
    for output_path in output_paths:
        print(f"- {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create staged Shenbao combined textdata CSV files for the current schema."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=None,
        help="Folder containing shenbao_textdata_*_1to*.csv source files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output folder. Defaults to <input-dir>/preprocess.",
    )
    parser.add_argument(
        "--dataset-label",
        default=None,
        help=(
            "Dataset label used in output file names and dataset_label column. "
            "If omitted, the script asks for this value before processing."
        ),
    )
    return parser.parse_args()


def get_dataset_label(value: str | None) -> str:
    dataset_label = trim_text(value or "")
    while not dataset_label:
        dataset_label = input("Enter dataset_label for this combined dataset: ").strip()

    if any(char in dataset_label for char in r'\\/:*?"<>|'):
        raise ValueError(
            "dataset_label cannot contain Windows filename-reserved characters: "
            r'\\ / : * ? " < > |'
        )
    return dataset_label


def main() -> None:
    configure_csv_field_limit()
    args = parse_args()

    input_dir = (args.input_dir if args.input_dir else default_input_dir()).resolve()
    output_dir = (args.output_dir if args.output_dir else input_dir / "preprocess").resolve()
    dataset_label = get_dataset_label(args.dataset_label)

    source_files = discover_source_files(input_dir)
    stage1_rows = read_source_rows(source_files)
    stage2_rows = make_stage2_rows(stage1_rows, dataset_label)
    stage3_rows = make_stage3_rows(stage2_rows)

    stage1_path = output_dir / f"shenbao_textdata_stage1_appended_rows_{dataset_label}.csv"
    stage2_path = output_dir / f"shenbao_textdata_stage2_deduplicated_articles_{dataset_label}.csv"
    stage3_path = output_dir / f"shenbao_textdata_stage3_preprocessed_articles_{dataset_label}.csv"

    write_csv(stage1_path, stage1_rows, STAGE1_COLUMNS)
    write_csv(stage2_path, stage2_rows, STAGE2_COLUMNS)
    write_csv(stage3_path, stage3_rows, STAGE3_COLUMNS)

    print_summary(
        source_files,
        stage1_rows,
        stage2_rows,
        stage3_rows,
        [stage1_path, stage2_path, stage3_path],
    )


if __name__ == "__main__":
    main()
