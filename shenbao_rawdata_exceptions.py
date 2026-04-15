from __future__ import annotations

import csv
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
TEXTDATA_DIR = BASE_DIR / "shenbao" / "shenbao_textdata"
OUTPUT_DIR = TEXTDATA_DIR / "exceptions"

INPUT_PATTERN = re.compile(
    r"^shenbao_textdata_(xianfa|lixian|xianzheng|zhixian)_(\d+)to(\d+)\.csv$"
)
META_MARKER = "其他紀元："


def tf(value: bool) -> str:
    return "T" if value else "F"


def collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def classify_publish(publish: str) -> str:
    value = publish.strip()
    if value.startswith("申報_漢口版 日期：") or value.startswith("申報_香港版 日期："):
        return ""
    if value.startswith("主題："):
        return "topic_only"
    if value.startswith("日期："):
        return "start_with_date"
    return ""


def classify_detail_url(detail_url: str) -> str:
    value = detail_url.strip()
    if not value:
        return "no_detail_url"
    if "qrynewstype=SP_FH" in value or "qrynewstype=SP_HK" in value:
        return ""
    if "qrynewstype=SP_AD" in value:
        return "sp_ad"
    return ""


def classify_text(text: str) -> str:
    value = text.strip()
    if value.startswith("[ERROR]"):
        return "error_text"
    if value.startswith(META_MARKER):
        return "metadata_only"
    if len(collapse_whitespace(value)) <= 4:
        return "short_text"
    return ""


def process_file(path: Path, keyword: str) -> Path:
    output_path = OUTPUT_DIR / f"shenbao_textdata_{keyword}_exception_rows.csv"
    extracted_rows: list[dict[str, str]] = []

    with path.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        fieldnames = list(reader.fieldnames or [])
        extra_fields = [
            "publish_exception",
            "publish_exception_reason",
            "detail_url_exception",
            "detail_url_exception_reason",
            "text_exception",
            "text_exception_reason",
        ]
        out_fieldnames = fieldnames + extra_fields

        for row in reader:
            publish_reason = classify_publish(row.get("publish", ""))
            detail_reason = classify_detail_url(row.get("detail_url", ""))
            text_reason = classify_text(row.get("text", ""))

            has_exception = bool(publish_reason or detail_reason or text_reason)
            if not has_exception:
                continue

            row["publish_exception"] = tf(bool(publish_reason))
            row["publish_exception_reason"] = publish_reason
            row["detail_url_exception"] = tf(bool(detail_reason))
            row["detail_url_exception_reason"] = detail_reason
            row["text_exception"] = tf(bool(text_reason))
            row["text_exception_reason"] = text_reason
            extracted_rows.append(row)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(extracted_rows)

    return output_path


def main() -> None:
    matched_files = []
    for path in TEXTDATA_DIR.iterdir():
        if not path.is_file() or path.suffix.lower() != ".csv":
            continue
        match = INPUT_PATTERN.match(path.name)
        if match:
            matched_files.append((path, match.group(1)))

    matched_files.sort(key=lambda item: item[0].name)
    if not matched_files:
        raise FileNotFoundError(f"No target CSV files found in {TEXTDATA_DIR}")

    failed_outputs: list[tuple[str, str]] = []
    for path, keyword in matched_files:
        try:
            output_path = process_file(path, keyword)
            print(f"{path.name} -> {output_path.name}")
        except PermissionError as exc:
            failed_outputs.append((path.name, str(exc)))
            print(f"{path.name} -> FAILED ({exc})")

    if failed_outputs:
        print("\nLocked or unavailable output files:")
        for name, message in failed_outputs:
            print(f"- {name}: {message}")


if __name__ == "__main__":
    main()
