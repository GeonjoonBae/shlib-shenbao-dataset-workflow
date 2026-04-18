# -*- coding: utf-8 -*-
"""Combine and preprocess Shanghai Library Shenbao textdata CSV files.

Default workflow:
1. Append source CSV rows and preserve raw columns.
2. Deduplicate rows by article_id, selecting one representative row.
3. Split metadata and create cleaned article-level fields.
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


CSV_FIELD_LIMIT = 2_000_000
SOURCE_PATTERN = "shenbao_textdata_*_1to*.csv"
RAW_COLUMNS = [
    "label",
    "page",
    "item_index",
    "list_title",
    "publish",
    "detail_url",
    "title",
    "text",
]
RAW_COLUMNS_STAGE = [f"{name}_raw" for name in RAW_COLUMNS]

COPYRIGHT_TEXT = "Copyright c 2012 得泓資訊. All Rights Reserved."
META_MARKER = "其他紀元："
CATEGORY_MARKER = "類別："
TOPIC_MARKER = "主題："
ERROR_PREFIX = "[ERROR]"

STAGE1_COLUMNS = ["preprocess_index"] + RAW_COLUMNS_STAGE
STAGE2_COLUMNS = [
    "dataset_label",
    "source_labels",
    "preprocess_indices",
    "representative_label",
    "representative_item_index",
    "select_reason",
    "article_id",
    "qrynewstype",
    *RAW_COLUMNS_STAGE,
    "collision",
    "collision_type",
]
STAGE3_COLUMNS = [
    "dataset_label",
    "source_labels",
    "preprocess_indices",
    "representative_label",
    "representative_item_index",
    "select_reason",
    "article_id",
    "qrynewstype",
    "publish_variant",
    "publish_date",
    "page_issue",
    "publish_tail",
    "publish_exception",
    "publish_exception_reason",
    "topic",
    "chinese_era_year",
    "japanese_era_year",
    "category",
    "metadata_source",
    "title_clean",
    "title_exist",
    "title_source",
    "text_clean",
    "text_exception",
    "text_exception_reason",
    "collision",
    "collision_type",
]

WHITESPACE_RE = re.compile(r"\s+")
LIST_TITLE_SERIAL_RE = re.compile(r"^\s*\d+\.\s*")
PUBLISH_NORMAL_RE = re.compile(
    r"^(?P<variant>申報(?:_[^\s]+)?)\s+"
    r"日期：(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"版次/卷期：(?P<page>.*?)\s+版(?:\s*(?P<tail>.*))?$"
)
PUBLISH_DATE_ONLY_RE = re.compile(
    r"^日期：(?P<date>\d{4}-\d{2}-\d{2})\s+"
    r"版次/卷期：(?P<page>.*?)\s+版(?:\s*(?P<tail>.*))?$"
)
CHINESE_ERA_RE = re.compile(r"([清淸][^日類別主題]*?年|民國[^日類別主題]*?年)")
JAPANESE_ERA_RE = re.compile(r"(日[^類別主題]*?年)")


def normalize_spaces(value: str) -> str:
    return WHITESPACE_RE.sub(" ", value or "").strip()


def remove_all_spaces(value: str) -> str:
    return WHITESPACE_RE.sub("", value or "")


def read_text(value: object) -> str:
    return "" if value is None else str(value)


def strip_list_title_serial(value: str) -> str:
    return LIST_TITLE_SERIAL_RE.sub("", value or "").strip()


def remove_metadata_and_copyright(value: str) -> str:
    text = read_text(value).replace(COPYRIGHT_TEXT, "")
    marker_pos = text.find(META_MARKER)
    if marker_pos >= 0:
        text = text[:marker_pos]
    return normalize_spaces(text)


def clean_metadata_value(value: str) -> str:
    return normalize_spaces(read_text(value).replace(COPYRIGHT_TEXT, ""))


def first_nonempty_unique(values: list[str]) -> str:
    seen: list[str] = []
    for value in values:
        clean = clean_metadata_value(value)
        if clean and clean not in seen:
            seen.append(clean)
    return ";".join(seen)


def merge_values(*values: str) -> str:
    seen: list[str] = []
    for value in values:
        clean = clean_metadata_value(value)
        if clean and clean not in seen:
            seen.append(clean)
    return ";".join(seen)


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
        cwd / "shenbao_textdata",
        script_dir / "shenbao_textdata",
        cwd / "shlib-shenbao-dataset-workflow" / "shenbao_textdata",
        script_dir / "shlib-shenbao-dataset-workflow" / "shenbao_textdata",
    ]
    for candidate in candidates:
        if candidate.exists() and any(candidate.glob(SOURCE_PATTERN)):
            return candidate
    return cwd / "shenbao_textdata"


def discover_source_files(input_dir: Path) -> list[Path]:
    files = sorted(input_dir.glob(SOURCE_PATTERN))
    excluded_words = ("stage", "preprocess", "combined", "exception")
    source_files = [
        path
        for path in files
        if not any(word in path.name.lower() for word in excluded_words)
    ]
    if not source_files:
        raise FileNotFoundError(
            f"No source CSV files matching {SOURCE_PATTERN!r} were found in {input_dir}"
        )
    return source_files


def read_source_rows(source_files: list[Path]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    preprocess_index = 1

    for source_file in source_files:
        with source_file.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            missing = [column for column in RAW_COLUMNS if column not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f"{source_file} is missing required columns: {missing}")

            for row in reader:
                appended = {"preprocess_index": str(preprocess_index)}
                for column in RAW_COLUMNS:
                    appended[f"{column}_raw"] = read_text(row.get(column, ""))
                rows.append(appended)
                preprocess_index += 1

    return rows


def write_csv(path: Path, rows: list[dict[str, str]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def is_error_text(row: dict[str, str]) -> bool:
    return row.get("text_raw", "").lstrip().startswith(ERROR_PREFIX)


def text_exists(row: dict[str, str]) -> bool:
    return bool(row.get("text_raw", "").strip())


def title_exists(row: dict[str, str]) -> bool:
    return bool(row.get("title_raw", "").strip())


def representative_reason(candidates: list[dict[str, str]]) -> tuple[dict[str, str], str]:
    remaining = list(candidates)
    first_reducing_reason = ""
    criteria = [
        ("1_no_error", lambda row: not is_error_text(row), True),
        ("2_text_exists", text_exists, True),
        ("3_title_exists", title_exists, True),
        ("4_long_text", lambda row: len(row.get("text_raw", "")), "max"),
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

    selected = min(remaining, key=lambda row: int(row["preprocess_index"]))
    return selected, first_reducing_reason or "5_small_index"


def classify_collision(rows: list[dict[str, str]]) -> tuple[str, str]:
    if len(rows) == 1:
        return "F", "single_source"

    tuples = [
        (row.get("publish_raw", ""), row.get("title_raw", ""), row.get("text_raw", ""))
        for row in rows
    ]
    if len(set(tuples)) == 1:
        return "F", "all_exact"

    normalized = [
        tuple(remove_all_spaces(value) for value in row_tuple)
        for row_tuple in tuples
    ]
    if len(set(normalized)) == 1:
        return "F", "whitespace_only"

    error_flags = [is_error_text(row) for row in rows]
    if any(error_flags):
        if all(error_flags):
            return "T", "all_error"
        return "T", "error_vs_normal"

    title_flags = [title_exists(row) for row in rows]
    if any(title_flags) and not all(title_flags):
        return "T", "title_missing_vs_present"

    return "T", "other_difference"


def ordered_unique(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def make_stage2_rows(stage1_rows: list[dict[str, str]], dataset_label: str) -> list[dict[str, str]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    missing_article_ids: list[str] = []

    for row in stage1_rows:
        article_id, qrynewstype = parse_detail_url(row.get("detail_url_raw", ""))
        if not article_id:
            missing_article_ids.append(row["preprocess_index"])
        enriched = dict(row)
        enriched["article_id"] = article_id
        enriched["qrynewstype"] = qrynewstype
        groups[article_id].append(enriched)

    if missing_article_ids:
        preview = ", ".join(missing_article_ids[:20])
        raise ValueError(
            "Rows without article_id cannot be deduplicated. "
            f"preprocess_index examples: {preview}"
        )

    stage2_rows: list[dict[str, str]] = []
    for article_id in sorted(groups, key=lambda key: min(int(row["preprocess_index"]) for row in groups[key])):
        source_rows = sorted(groups[article_id], key=lambda row: int(row["preprocess_index"]))
        representative, select_reason = representative_reason(source_rows)
        collision, collision_type = classify_collision(source_rows)

        source_labels = ordered_unique([row.get("label_raw", "") for row in source_rows])
        preprocess_indices = [row["preprocess_index"] for row in source_rows]
        qrynewstypes = ordered_unique([row.get("qrynewstype", "") for row in source_rows])

        row_out = {
            "dataset_label": dataset_label,
            "source_labels": ";".join(source_labels),
            "preprocess_indices": ";".join(preprocess_indices),
            "representative_label": representative.get("label_raw", ""),
            "representative_item_index": representative.get("item_index_raw", ""),
            "select_reason": select_reason,
            "article_id": article_id,
            "qrynewstype": ";".join(qrynewstypes),
            "collision": collision,
            "collision_type": collision_type,
        }
        for column in RAW_COLUMNS_STAGE:
            row_out[column] = representative.get(column, "")
        stage2_rows.append(row_out)

    return stage2_rows


def parse_publish(publish_raw: str) -> dict[str, str]:
    publish = normalize_spaces(publish_raw)
    result = {
        "publish_variant": "",
        "publish_date": "",
        "page_issue": "",
        "publish_tail": "",
        "publish_exception": "F",
        "publish_exception_reason": "",
        "topic": "",
    }

    normal_match = PUBLISH_NORMAL_RE.match(publish)
    if normal_match:
        result.update(
            {
                "publish_variant": normal_match.group("variant").strip(),
                "publish_date": normal_match.group("date").strip(),
                "page_issue": normal_match.group("page").strip(),
                "publish_tail": normalize_spaces(normal_match.group("tail") or ""),
            }
        )
        return result

    date_match = PUBLISH_DATE_ONLY_RE.match(publish)
    if date_match:
        result.update(
            {
                "publish_date": date_match.group("date").strip(),
                "page_issue": date_match.group("page").strip(),
                "publish_tail": normalize_spaces(date_match.group("tail") or ""),
                "publish_exception": "T",
                "publish_exception_reason": "start_with_date",
            }
        )
        return result

    if publish.startswith(TOPIC_MARKER):
        result.update(
            {
                "publish_exception": "T",
                "publish_exception_reason": "topic_only",
                "topic": clean_metadata_value(publish[len(TOPIC_MARKER) :]),
            }
        )
        return result

    if publish:
        result.update(
            {
                "publish_exception": "T",
                "publish_exception_reason": "unparsed_publish",
            }
        )
    return result


def extract_between(text: str, start_marker: str, end_marker: str | None = None) -> str:
    start = text.find(start_marker)
    if start < 0:
        return ""
    start += len(start_marker)
    if end_marker:
        end = text.find(end_marker, start)
        if end >= 0:
            return text[start:end]
    return text[start:]


def extract_metadata_from_value(value: str) -> dict[str, str]:
    text = read_text(value)
    if META_MARKER not in text and CATEGORY_MARKER not in text and TOPIC_MARKER not in text:
        return {"chinese_era_year": "", "japanese_era_year": "", "category": "", "topic": ""}

    chinese_match = CHINESE_ERA_RE.search(text)
    japanese_match = JAPANESE_ERA_RE.search(text)
    category_raw = extract_between(text, CATEGORY_MARKER, TOPIC_MARKER)
    topic_raw = extract_between(text, TOPIC_MARKER)

    return {
        "chinese_era_year": clean_metadata_value(chinese_match.group(1) if chinese_match else ""),
        "japanese_era_year": clean_metadata_value(japanese_match.group(1) if japanese_match else ""),
        "category": clean_metadata_value(category_raw),
        "topic": clean_metadata_value(topic_raw),
    }


def split_title_text_metadata(title_raw: str, text_raw: str) -> dict[str, str]:
    title_has = any(marker in title_raw for marker in (META_MARKER, CATEGORY_MARKER, TOPIC_MARKER))
    text_has = any(marker in text_raw for marker in (META_MARKER, CATEGORY_MARKER, TOPIC_MARKER))

    title_meta = extract_metadata_from_value(title_raw)
    text_meta = extract_metadata_from_value(text_raw)

    if title_has and text_has:
        metadata_source = "both"
    elif title_has:
        metadata_source = "title"
    elif text_has:
        metadata_source = "text"
    else:
        metadata_source = "none"

    return {
        "chinese_era_year": first_nonempty_unique(
            [title_meta["chinese_era_year"], text_meta["chinese_era_year"]]
        ),
        "japanese_era_year": first_nonempty_unique(
            [title_meta["japanese_era_year"], text_meta["japanese_era_year"]]
        ),
        "category": first_nonempty_unique([title_meta["category"], text_meta["category"]]),
        "topic": first_nonempty_unique([title_meta["topic"], text_meta["topic"]]),
        "metadata_source": metadata_source,
    }


def make_title_fields(list_title_raw: str, title_raw: str) -> dict[str, str]:
    list_title_clean = strip_list_title_serial(list_title_raw)
    title_exists_raw = bool(title_raw.strip())
    list_exists_raw = bool(list_title_clean.strip())

    if title_exists_raw and list_exists_raw:
        title_exist = "both_exist"
        title_source = "title_raw"
        selected = title_raw
    elif title_exists_raw and not list_exists_raw:
        title_exist = "list_title_empty"
        title_source = "title_raw"
        selected = title_raw
    elif not title_exists_raw and list_exists_raw:
        title_exist = "title_empty"
        title_source = "list_title_raw"
        selected = list_title_clean
    else:
        title_exist = "both_empty"
        title_source = "missing"
        selected = ""

    return {
        "title_clean": remove_metadata_and_copyright(selected),
        "title_exist": title_exist,
        "title_source": title_source,
    }


def is_metadata_only_text(text_raw: str) -> bool:
    marker_pos = text_raw.find(META_MARKER)
    if marker_pos < 0:
        return False
    before_marker = text_raw[:marker_pos].replace(COPYRIGHT_TEXT, "").strip()
    return before_marker == ""


def make_text_fields(text_raw: str) -> dict[str, str]:
    text = read_text(text_raw)

    if text.lstrip().startswith(ERROR_PREFIX):
        return {
            "text_clean": "",
            "text_exception": "T",
            "text_exception_reason": "error_text",
        }

    if is_metadata_only_text(text):
        return {
            "text_clean": "",
            "text_exception": "T",
            "text_exception_reason": "metadata_only",
        }

    if len(text.strip()) <= 3:
        return {
            "text_clean": normalize_spaces(text.replace(COPYRIGHT_TEXT, "")),
            "text_exception": "T",
            "text_exception_reason": "short_text",
        }

    return {
        "text_clean": remove_metadata_and_copyright(text),
        "text_exception": "F",
        "text_exception_reason": "",
    }


def make_stage3_rows(stage2_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    stage3_rows: list[dict[str, str]] = []

    for row in stage2_rows:
        publish_fields = parse_publish(row.get("publish_raw", ""))
        metadata_fields = split_title_text_metadata(row.get("title_raw", ""), row.get("text_raw", ""))
        title_fields = make_title_fields(row.get("list_title_raw", ""), row.get("title_raw", ""))
        text_fields = make_text_fields(row.get("text_raw", ""))
        topic = merge_values(publish_fields.get("topic", ""), metadata_fields.get("topic", ""))

        row_out = {
            "dataset_label": row.get("dataset_label", ""),
            "source_labels": row.get("source_labels", ""),
            "preprocess_indices": row.get("preprocess_indices", ""),
            "representative_label": row.get("representative_label", ""),
            "representative_item_index": row.get("representative_item_index", ""),
            "select_reason": row.get("select_reason", ""),
            "article_id": row.get("article_id", ""),
            "qrynewstype": row.get("qrynewstype", ""),
            "publish_variant": publish_fields["publish_variant"],
            "publish_date": publish_fields["publish_date"],
            "page_issue": publish_fields["page_issue"],
            "publish_tail": publish_fields["publish_tail"],
            "publish_exception": publish_fields["publish_exception"],
            "publish_exception_reason": publish_fields["publish_exception_reason"],
            "topic": topic,
            "chinese_era_year": metadata_fields["chinese_era_year"],
            "japanese_era_year": metadata_fields["japanese_era_year"],
            "category": metadata_fields["category"],
            "metadata_source": metadata_fields["metadata_source"],
            "title_clean": title_fields["title_clean"],
            "title_exist": title_fields["title_exist"],
            "title_source": title_fields["title_source"],
            "text_clean": text_fields["text_clean"],
            "text_exception": text_fields["text_exception"],
            "text_exception_reason": text_fields["text_exception_reason"],
            "collision": row.get("collision", ""),
            "collision_type": row.get("collision_type", ""),
        }
        stage3_rows.append(row_out)

    return stage3_rows


def count_values(rows: list[dict[str, str]], column: str) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[row.get(column, "")] += 1
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
    print("collision_type:")
    for key, value in count_values(stage2_rows, "collision_type").items():
        print(f"- {key}: {value}")
    print()
    print("select_reason:")
    for key, value in count_values(stage2_rows, "select_reason").items():
        print(f"- {key}: {value}")
    print()
    print("text_exception_reason:")
    for key, value in count_values(stage3_rows, "text_exception_reason").items():
        label = key if key else "(none)"
        print(f"- {label}: {value}")
    print()
    print("Output files:")
    for output_path in output_paths:
        print(f"- {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create staged Shenbao combined textdata CSV files."
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
    dataset_label = (value or "").strip()
    while not dataset_label:
        dataset_label = input("Enter dataset_label for this combined dataset: ").strip()

    if any(char in dataset_label for char in r'\/:*?"<>|'):
        raise ValueError(
            "dataset_label cannot contain Windows filename-reserved characters: "
            r'\\ / : * ? " < > |'
        )
    return dataset_label


def main() -> None:
    csv.field_size_limit(CSV_FIELD_LIMIT)
    args = parse_args()

    input_dir = args.input_dir if args.input_dir else default_input_dir()
    input_dir = input_dir.resolve()
    output_dir = (args.output_dir if args.output_dir else input_dir / "preprocess").resolve()
    dataset_label = get_dataset_label(args.dataset_label)

    source_files = discover_source_files(input_dir)
    stage1_rows = read_source_rows(source_files)
    stage2_rows = make_stage2_rows(stage1_rows, dataset_label)
    stage3_rows = make_stage3_rows(stage2_rows)

    stage1_path = output_dir / f"shenbao_{dataset_label}_text_stage1_appended_rows.csv"
    stage2_path = output_dir / f"shenbao_{dataset_label}_text_stage2_deduplicated_articles.csv"
    stage3_path = output_dir / f"shenbao_{dataset_label}_text_stage3_preprocessed_articles.csv"

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
