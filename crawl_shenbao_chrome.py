from __future__ import annotations

import argparse
import csv
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from playwright.sync_api import Frame, Locator, Page
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


START_URL = "https://z.library.sh.cn/http/80/77/30/1/10/yitlink/"
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = BASE_DIR / "shenbao" / "shenbao_rawdata"
CHROME_CANDIDATES = [
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
]

LIST_ROOT = "#main > div.main-box"
RESULT_CONTAINER_SELECTOR = f"{LIST_ROOT} > div"
RESULT_TITLE_SELECTOR = f"{LIST_ROOT} > div > h3 > a"
BLOCK_TITLE_SELECTOR = ":scope > h3 > a"
DESCENDANT_TITLE_SELECTOR = "h3 > a"
BLOCK_PUBLISH_SELECTOR = ":scope > div:nth-child(4)"
DETAIL_TEXT_XPATH = '//*[@id="content-box_contentwrapper"]/div[2]/div'
DETAIL_TEXT_SELECTORS = [
    ("xpath", DETAIL_TEXT_XPATH),
    ("css", "#content-box_contentwrapper > div:nth-child(4) > div"),
    ("css", "#content-box_contentwrapper > h1"),
]
BACK_TO_LIST_XPATH = '//*[@id="catalog2"]/ul/li[1]/a'
PAGE_SIZE_SELECT = f"{LIST_ROOT} > div:nth-child(1) > select"
CURRENT_PAGE_SELECTOR = f"{LIST_ROOT} div.page a.current"
DETAIL_URL_KEYWORD = "tm_shownews.php"
AUTH_URL_KEYWORD = "passport.library.sh.cn"
MAX_RESULT_WAIT_MS = 60000


@dataclass
class ActiveScope:
    page: Page
    scope: Page | Frame
    scope_type: str


class SessionExpiredError(RuntimeError):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch Chrome, wait for manual login/navigation, then crawl ShenBao result pages from yitlink."
    )
    parser.add_argument("--start-url", default=START_URL)
    parser.add_argument(
        "--chrome-path",
        type=Path,
        default=None,
        help="Optional path to chrome.exe. If omitted, the script tries common Chrome install locations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Output directory for shenbao_rawdata_*.csv files. Defaults to ./shenbao/shenbao_rawdata beside this script.",
    )
    parser.add_argument(
        "--label",
        type=str,
        help="Optional search label used in output filenames, e.g. xianfa or lixian.",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        default=1,
        help="Page number to record in the output for the page currently open when crawling starts.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Optional upper bound on pages to crawl. If omitted, keep going until the site stops providing results or navigation.",
    )
    parser.add_argument("--wait-seconds", type=float, default=2.0)
    parser.add_argument("--extended-wait-seconds", type=float, default=4.0)
    parser.add_argument(
        "--detail-timeout-seconds",
        type=float,
        default=4.0,
        help="Maximum time to wait for detail text after clicking a title.",
    )
    parser.add_argument(
        "--save-every",
        type=int,
        default=10,
        help="Write progress to CSV every N collected items.",
    )
    parser.add_argument(
        "--resume-file",
        type=Path,
        help="Resume from a previously saved shenbao_rawdata_*.csv file.",
    )
    parser.add_argument(
        "--resume-latest",
        action="store_true",
        help="Resume from the latest shenbao_rawdata_*.csv found in the output directory.",
    )
    return parser.parse_args()


def resolve_browser_path(args: argparse.Namespace) -> Optional[Path]:
    provided_path = getattr(args, "chrome_path", None)
    if provided_path is not None:
        return provided_path

    for candidate in CHROME_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def ensure_runtime_requirements(browser_path: Optional[Path], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)

    if browser_path is None:
        searched = ", ".join(str(path) for path in CHROME_CANDIDATES)
        raise FileNotFoundError(
            "Google Chrome executable was not found in the default locations. "
            f"Searched: {searched}. Provide the browser path explicitly with --chrome-path."
        )

    if not browser_path.exists():
        raise FileNotFoundError(f"Browser executable not found: {browser_path}")

    return browser_path


def normalize_text(value: str | None) -> str:
    return "" if value is None else " ".join(value.split())


def sanitize_label(label: str | None) -> Optional[str]:
    if not label:
        return None
    cleaned = normalize_text(label).strip()
    cleaned = re.sub(r'[<>:"/\\\\|?*]+', "", cleaned)
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or None


def prompt_for_label() -> str:
    while True:
        value = input("No --label/--resume-file/--resume-latest provided. Enter label to continue: ").strip()
        cleaned = sanitize_label(value)
        if cleaned:
            return cleaned
        print("A non-empty label is required.")


def format_elapsed(seconds: float) -> str:
    total_seconds = max(0, int(round(seconds)))
    minutes, secs = divmod(total_seconds, 60)
    return f"{minutes:02d}m {secs:02d}s"


def install_dialog_guards(context) -> None:
    context.add_init_script(
        """
        window.alert = () => {};
        window.confirm = () => true;
        window.prompt = () => '';
        window.onbeforeunload = null;
        """
    )

    def _attach(page: Page) -> None:
        def _dismiss(dialog) -> None:
            try:
                dialog.dismiss()
            except Exception:
                pass

        page.on("dialog", _dismiss)

    for existing_page in context.pages:
        _attach(existing_page)
    context.on("page", _attach)


def get_scope_url(scope: Page | Frame) -> str:
    try:
        return scope.url
    except PlaywrightError:
        return ""


def safe_page_title(page) -> str:
    try:
        return page.title()
    except PlaywrightError:
        return ""


def count_title_links(scope: Page | Frame) -> int:
    try:
        return scope.locator(RESULT_TITLE_SELECTOR).count()
    except PlaywrightError:
        return 0


def iter_scopes(context) -> list[ActiveScope]:
    scopes: list[ActiveScope] = []
    for page in context.pages:
        scopes.append(ActiveScope(page=page, scope=page, scope_type="page"))
        try:
            frames = page.frames
        except PlaywrightError:
            continue
        for frame in frames:
            scopes.append(ActiveScope(page=page, scope=frame, scope_type="frame"))
    return scopes


def debug_context_state(context) -> None:
    print(f"Open pages in context: {len(context.pages)}")
    for idx, page in enumerate(context.pages, start=1):
        page_url = get_scope_url(page) or "<unavailable>"
        page_title = safe_page_title(page)
        page_count = count_title_links(page)
        print(f"[Page {idx}] url={page_url}")
        if page_title:
            print(f"[Page {idx}] title={page_title}")
        print(f"[Page {idx}] title_links={page_count}")
        try:
            frames = page.frames
        except PlaywrightError:
            continue
        print(f"[Page {idx}] frames={len(frames)}")
        for fidx, frame in enumerate(frames, start=1):
            frame_url = get_scope_url(frame) or "<unavailable>"
            frame_count = count_title_links(frame)
            print(f"  [Frame {fidx}] url={frame_url} title_links={frame_count}")


def get_best_result_scope(context) -> ActiveScope:
    scopes = iter_scopes(context)
    if not scopes:
        raise RuntimeError("No browser pages are open.")

    best_scope = scopes[-1]
    best_count = -1
    for active in scopes:
        try:
            active.page.wait_for_load_state("domcontentloaded", timeout=2000)
        except PlaywrightTimeoutError:
            pass
        except PlaywrightError:
            continue

        title_count = count_title_links(active.scope)
        if title_count > best_count:
            best_scope = active
            best_count = title_count

    return best_scope


def find_auth_scope(context) -> Optional[ActiveScope]:
    for active in iter_scopes(context):
        url = get_scope_url(active.scope) or get_scope_url(active.page)
        if AUTH_URL_KEYWORD in url:
            return active
    return None


def wait_for_results_scope(context, timeout_ms: int = 10000) -> ActiveScope:
    deadline = time.time() + (timeout_ms / 1000)
    last_active = get_best_result_scope(context)
    while time.time() < deadline:
        auth_active = find_auth_scope(context)
        if auth_active is not None:
            raise SessionExpiredError(
                f"Authentication redirect detected: {get_scope_url(auth_active.scope) or get_scope_url(auth_active.page)}"
            )
        active = get_best_result_scope(context)
        if count_title_links(active.scope) > 0:
            return active
        last_active = active
        time.sleep(0.2)
    raise RuntimeError(
        f"Results scope not found. Best scope url={get_scope_url(last_active.scope)} title_links={count_title_links(last_active.scope)}"
    )


def wait_for_results_scope_with_fallback(
    context,
    initial_timeout_ms: int = 4000,
    max_timeout_ms: int = MAX_RESULT_WAIT_MS,
) -> ActiveScope:
    try:
        return wait_for_results_scope(context, timeout_ms=initial_timeout_ms)
    except SessionExpiredError:
        raise
    except RuntimeError:
        if max_timeout_ms <= initial_timeout_ms:
            raise
        return wait_for_results_scope(context, timeout_ms=max_timeout_ms - initial_timeout_ms)


def wait_for_result_page(context, target_page_no: int, timeout_ms: int = 10000) -> ActiveScope:
    deadline = time.time() + (timeout_ms / 1000)
    last_active = get_best_result_scope(context)
    while time.time() < deadline:
        auth_active = find_auth_scope(context)
        if auth_active is not None:
            raise SessionExpiredError(
                f"Authentication redirect detected: {get_scope_url(auth_active.scope) or get_scope_url(auth_active.page)}"
            )
        active = get_best_result_scope(context)
        if count_title_links(active.scope) > 0:
            current_page = get_current_page_number(active.scope, -1)
            if current_page == target_page_no:
                return active
        last_active = active
        time.sleep(0.2)
    raise RuntimeError(
        f"Result page {target_page_no} not reached. Best scope url={get_scope_url(last_active.scope)} current_page={get_current_page_number(last_active.scope, -1)} title_links={count_title_links(last_active.scope)}"
    )


def wait_for_result_page_with_fallback(
    context,
    target_page_no: int,
    initial_timeout_ms: int = 4000,
    max_timeout_ms: int = MAX_RESULT_WAIT_MS,
) -> ActiveScope:
    try:
        return wait_for_result_page(context, target_page_no, timeout_ms=initial_timeout_ms)
    except SessionExpiredError:
        raise
    except RuntimeError:
        if max_timeout_ms <= initial_timeout_ms:
            raise
        return wait_for_result_page(
            context,
            target_page_no,
            timeout_ms=max_timeout_ms - initial_timeout_ms,
        )


def wait_for_manual_ready(context, retry_seconds: float = 2.0) -> ActiveScope:
    while True:
        active = get_best_result_scope(context)
        try:
            active.page.wait_for_load_state("domcontentloaded", timeout=3000)
        except PlaywrightTimeoutError:
            pass
        try:
            active.page.wait_for_load_state("networkidle", timeout=5000)
        except PlaywrightTimeoutError:
            pass
        except PlaywrightError:
            pass

        current_url = get_scope_url(active.scope)
        result_blocks = get_result_blocks(active.scope)
        title_count = count_title_links(active.scope)
        print(f"Detected title links in best {active.scope_type}: {title_count}")
        if title_count > 0 and result_blocks:
            return active

        print("The current page is not ready for crawling yet.")
        print(f"Current URL: {current_url}")
        title = safe_page_title(active.page)
        if title:
            print(f"Page title: {title}")
        print("Finish login and wait until the results list is visible, then press Enter again.")
        input()
        time.sleep(retry_seconds)


def get_result_blocks(scope: Page | Frame) -> list[Locator]:
    blocks = scope.locator(RESULT_CONTAINER_SELECTOR).all()
    result_blocks: list[Locator] = []
    for block in blocks:
        try:
            if get_block_title_locator(block) is not None:
                result_blocks.append(block)
        except PlaywrightError:
            continue
    return result_blocks


def get_block_title_locator(block: Locator) -> Optional[Locator]:
    try:
        direct = block.locator(BLOCK_TITLE_SELECTOR)
        if direct.count() == 1:
            return direct.first

        descendant = block.locator(DESCENDANT_TITLE_SELECTOR)
        if descendant.count() == 1:
            return descendant.first
    except PlaywrightError:
        return None
    return None


def ensure_page_size_100(scope: Page | Frame) -> None:
    select = scope.locator(PAGE_SIZE_SELECT)
    if not select.count():
        return
    current = select.input_value()
    if current == "100":
        return
    select.select_option("100")
    time.sleep(1)


def read_list_entry(block: Locator) -> dict[str, str]:
    title_locator = get_block_title_locator(block)
    if title_locator is None:
        raise RuntimeError("Title locator could not be resolved for the current result block.")
    title = normalize_text(title_locator.inner_text())
    publish_locator = block.locator(BLOCK_PUBLISH_SELECTOR)
    if publish_locator.count():
        publish = normalize_text(publish_locator.first.inner_text())
    else:
        publish = normalize_text(block.locator("div").last.inner_text())
    return {"title": title, "publish": publish}


def extract_detail_text(scope: Page | Frame, timeout_ms: int) -> str:
    max_timeout_ms = max(timeout_ms, MAX_RESULT_WAIT_MS)
    started_at = time.time()
    while (time.time() - started_at) < (max_timeout_ms / 1000):
        for selector_type, selector in DETAIL_TEXT_SELECTORS:
            locator = scope.locator(f"{selector_type}={selector}")
            try:
                if not locator.count():
                    continue
                first = locator.first
                first.wait_for(timeout=250)
                text = normalize_text(first.inner_text())
                if text:
                    return text
            except PlaywrightTimeoutError:
                continue
            except PlaywrightError:
                continue
        time.sleep(0.2)
    raise PlaywrightTimeoutError(
        f"Detail text not found using selectors: {', '.join(selector for _, selector in DETAIL_TEXT_SELECTORS)}"
    )


def build_failure_text(message: str, detail_url: str, scope_url: str) -> str:
    parts = [f"[ERROR] {message}"]
    if detail_url:
        parts.append(f"detail_url={detail_url}")
    if scope_url:
        parts.append(f"scope_url={scope_url}")
    return " | ".join(parts)


def extract_title_index(title: str, fallback: str) -> str:
    match = re.match(r"\s*(\d+)\.", title)
    if match:
        return match.group(1)
    return fallback


def infer_page_from_title_index(item_index: int, fallback_page: int) -> int:
    if item_index <= 0:
        return fallback_page
    return ((item_index - 1) // 100) + 1


def get_current_page_number(scope: Page | Frame, fallback_page: int) -> int:
    try:
        locator = scope.locator(CURRENT_PAGE_SELECTOR).first
        if locator.count():
            text = normalize_text(locator.inner_text())
            if text.isdigit():
                return int(text)
    except PlaywrightError:
        pass
    return fallback_page


def get_local_item_offset(page_no: int, item_index: int) -> int:
    inferred = item_index - ((page_no - 1) * 100)
    if 1 <= inferred <= 100:
        return inferred
    fallback = ((item_index - 1) % 100) + 1
    return fallback


def find_detail_scope(context) -> Optional[ActiveScope]:
    for active in iter_scopes(context):
        scope_url = get_scope_url(active.scope)
        if DETAIL_URL_KEYWORD in scope_url:
            return active
        try:
            if active.scope.locator(f"xpath={DETAIL_TEXT_XPATH}").count():
                return active
        except PlaywrightError:
            continue
    return None


def wait_for_detail_scope(context, wait_seconds: float, extended_wait_seconds: float) -> ActiveScope:
    deadline = time.time() + (max(int(extended_wait_seconds * 1000), MAX_RESULT_WAIT_MS) / 1000)
    while time.time() < deadline:
        auth_active = find_auth_scope(context)
        if auth_active is not None:
            raise SessionExpiredError(
                f"Authentication redirect detected: {get_scope_url(auth_active.scope) or get_scope_url(auth_active.page)}"
            )
        active = find_detail_scope(context)
        if active is not None:
            return active
        time.sleep(0.2)
    raise RuntimeError("Detail scope not found before timeout.")


def build_output_path(output_dir: Path, rows: list[dict[str, str]], label: Optional[str]) -> Optional[Path]:
    if not rows:
        return None
    start_index = extract_title_index(rows[0]["title"], rows[0]["global_item_index"])
    end_index = extract_title_index(rows[-1]["title"], rows[-1]["global_item_index"])
    if label:
        return output_dir / f"shenbao_rawdata_{label}_{start_index}to{end_index}.csv"
    return output_dir / f"shenbao_rawdata_{start_index}to{end_index}.csv"


def get_next_page_locator(scope: Page | Frame, target_page: int) -> Locator:
    return (
        scope.locator(f'a.pagelink[pageto="{target_page}"]')
        .filter(has_text=re.compile(rf"^\s*{target_page}\s*$"))
        .first
    )


def click_next_page(context, active: ActiveScope, target_page: int, timeout_ms: int) -> ActiveScope:
    next_page = get_next_page_locator(active.scope, target_page)
    if not next_page.count():
        raise RuntimeError(f"Next page button for page {target_page} not found.")
    next_page.evaluate("(el) => el.click()")
    return wait_for_result_page_with_fallback(
        context,
        target_page,
        initial_timeout_ms=timeout_ms,
        max_timeout_ms=MAX_RESULT_WAIT_MS,
    )


def find_latest_resume_file(output_dir: Path, label: Optional[str] = None) -> Optional[Path]:
    pattern = f"shenbao_rawdata_{label}_*to*.csv" if label else "shenbao_rawdata_*to*.csv"
    candidates = list(output_dir.glob(pattern))
    if not candidates:
        return None

    def parse_end_index(path: Path) -> int:
        stem = path.stem
        try:
            return int(stem.rsplit("to", 1)[1])
        except (IndexError, ValueError):
            return -1

    candidates.sort(key=lambda path: (path.stat().st_mtime, parse_end_index(path)))
    return candidates[-1]


def infer_label_from_path(path: Path) -> Optional[str]:
    match = re.match(r"^shenbao_rawdata_(.+)_(\d+)to(\d+)$", path.stem)
    if not match:
        return None
    return match.group(1)


def confirm_resume_file(path: Path) -> bool:
    print(f"Selected resume file: {path}")
    answer = input("Proceed with this file? [y/N]: ").strip().lower()
    return answer in {"y", "yes"}


def load_resume_rows(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            page = int(row["page"])
            item_index = int(row["item_index"])
            if item_index > 100:
                global_item_index = item_index
            else:
                global_item_index = (page - 1) * 100 + item_index
            rows.append(
                {
                    "page": str(page),
                    "item_index": str(item_index),
                    "title": row["title"],
                    "publish": row["publish"],
                    "detail_url": row["detail_url"],
                    "text": row["text"],
                    "global_item_index": str(global_item_index),
                }
            )
    return rows


def get_resume_target(rows: list[dict[str, str]]) -> tuple[int, int]:
    if not rows:
        return 1, 0
    last_page = int(rows[-1]["page"])
    last_item_index = int(rows[-1]["item_index"])
    if last_item_index > 100:
        local_item_index = get_local_item_offset(last_page, last_item_index)
    else:
        local_item_index = last_item_index
    return last_page, max(0, local_item_index - 1)


def write_rows(
    output_dir: Path,
    rows: list[dict[str, str]],
    previous_path: Optional[Path],
    label: Optional[str],
) -> Optional[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = build_output_path(output_dir, rows, label)
    if path is None:
        return previous_path

    if previous_path and previous_path != path and previous_path.exists():
        previous_path.unlink()

    fieldnames = ["page", "item_index", "title", "publish", "detail_url", "text"]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output_row = {field: row[field] for field in fieldnames}
            writer.writerow(output_row)
    return path


def main() -> None:
    started_at = time.perf_counter()
    args = parse_args()
    browser_path = resolve_browser_path(args)
    browser_path = ensure_runtime_requirements(browser_path, args.output_dir)
    run_label = sanitize_label(args.label)
    if not args.resume_file and not args.resume_latest and run_label is None:
        run_label = prompt_for_label()

    rows: list[dict[str, str]] = []
    current_output_path: Optional[Path] = None
    resume_page_no = args.start_page
    resume_item_offset = 0
    is_resuming = False
    stop_due_to_auth = False

    resume_path: Optional[Path] = None
    if args.resume_file:
        resume_path = args.resume_file
    elif args.resume_latest:
        resume_path = find_latest_resume_file(args.output_dir, run_label)
        if resume_path is not None and not confirm_resume_file(resume_path):
            print("Aborted before crawl.")
            print(f"Elapsed time: {format_elapsed(time.perf_counter() - started_at)}")
            return
    elif run_label:
        resume_path = find_latest_resume_file(args.output_dir, run_label)
        if resume_path is not None:
            print(f"Found existing file for label '{run_label}': {resume_path}")

    if resume_path is not None:
        is_resuming = True
        if not resume_path.exists():
            raise FileNotFoundError(f"Resume file not found: {resume_path}")
        if run_label is None:
            run_label = infer_label_from_path(resume_path)
        rows = load_resume_rows(resume_path)
        loaded_row_count = len(rows)
        current_output_path = resume_path
        resume_page_no, resume_item_offset = get_resume_target(rows)
        if rows:
            rows = rows[:-1]
        print(f"Loaded {loaded_row_count} existing rows from: {resume_path}")
        print(f"Keeping {len(rows)} rows and replaying the last recorded row.")
        print(f"Resume target: page={resume_page_no}, item_offset={resume_item_offset} (restart from last recorded row)")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            executable_path=str(browser_path),
        )
        context = browser.new_context()
        install_dialog_guards(context)
        page = context.new_page()
        page.goto(args.start_url, wait_until="domcontentloaded")

        print("Chrome launched.")
        print("Log in manually, move to the target results page, and set page size to 100.")
        print("When the current browser tab is ready for crawling, return here and press Enter.")
        input()
        debug_context_state(context)
        active = wait_for_manual_ready(context)

        print(f"Starting crawl from {active.scope_type} URL: {get_scope_url(active.scope)}")
        print(f"Page title: {safe_page_title(active.page)}")
        ensure_page_size_100(active.scope)

        current_page_no = get_current_page_number(active.scope, args.start_page)
        if not is_resuming:
            resume_page_no = current_page_no
            resume_item_offset = 0
        elif resume_page_no < current_page_no:
            raise RuntimeError(
                f"Resume target page {resume_page_no} is earlier than the provided start page {current_page_no}."
            )

        while is_resuming and current_page_no < resume_page_no:
            current_page_no = get_current_page_number(active.scope, current_page_no)
            print(f"Advancing from page {current_page_no} to page {current_page_no + 1} for resume.")
            active = click_next_page(
                context,
                active,
                current_page_no + 1,
                timeout_ms=max(4000, int(args.extended_wait_seconds * 1000)),
            )
            ensure_page_size_100(active.scope)
            current_page_no = get_current_page_number(active.scope, current_page_no + 1)

        while True:
            result_blocks = get_result_blocks(active.scope)
            if not result_blocks:
                print(f"No result blocks found on page {current_page_no}. Stopping.")
                print(f"Current scope URL: {get_scope_url(active.scope)}")
                print(f"Page title: {safe_page_title(active.page)}")
                break

            actual_page_no = get_current_page_number(active.scope, current_page_no)
            current_page_no = actual_page_no

            print(f"Page {actual_page_no}: {len(result_blocks)} result blocks")

            item_count = len(result_blocks)
            start_item_idx = resume_item_offset if current_page_no == resume_page_no else 0
            for item_idx in range(start_item_idx, item_count):
                result_blocks = get_result_blocks(active.scope)
                if item_idx >= len(result_blocks):
                    break

                block = result_blocks[item_idx]
                global_item_index = (current_page_no - 1) * 100 + (item_idx + 1)
                list_info = {"title": f"[UNRESOLVED TITLE] {global_item_index}", "publish": ""}
                title_item_index = str(global_item_index)
                title_locator: Optional[Locator] = None
                detail_active: Optional[ActiveScope] = None
                detail_url = ""
                detail_text = ""
                failure_message = ""

                try:
                    list_info = read_list_entry(block)
                    title_locator = get_block_title_locator(block)
                    if title_locator is None:
                        raise RuntimeError("Title locator could not be resolved for click.")
                    title_item_index = extract_title_index(list_info["title"], str(global_item_index))
                    title_locator.click()
                    detail_active = wait_for_detail_scope(context, args.wait_seconds, args.extended_wait_seconds)
                    detail_url = get_scope_url(detail_active.scope) or get_scope_url(detail_active.page)
                    detail_text = extract_detail_text(
                        detail_active.scope, timeout_ms=int(args.detail_timeout_seconds * 1000)
                    )
                except SessionExpiredError as exc:
                    failure_message = f"{type(exc).__name__}: {normalize_text(str(exc))}"
                    detail_text = build_failure_text(failure_message, detail_url, "")
                    stop_due_to_auth = True
                except Exception as exc:
                    scope_url = get_scope_url(detail_active.scope) if detail_active is not None else ""
                    failure_message = f"{type(exc).__name__}: {normalize_text(str(exc))}"
                    detail_text = build_failure_text(failure_message, detail_url, scope_url)

                rows.append(
                    {
                        "page": str(actual_page_no),
                        "item_index": title_item_index,
                        "title": list_info["title"],
                        "publish": list_info["publish"],
                        "detail_url": detail_url,
                        "text": detail_text,
                        "global_item_index": title_item_index,
                    }
                )
                if failure_message:
                    print(
                        f"Failed page={actual_page_no} item={title_item_index} title={list_info['title'][:40]} reason={failure_message}"
                    )
                else:
                    print(
                        f"Collected page={actual_page_no} item={title_item_index} title={list_info['title'][:40]}"
                    )

                if detail_active is not None:
                    back_link = detail_active.scope.locator(f"xpath={BACK_TO_LIST_XPATH}")
                    if back_link.count():
                        back_link.click()
                    else:
                        detail_active.page.go_back()
                else:
                    try:
                        active.page.go_back()
                    except PlaywrightError:
                        pass

                if stop_due_to_auth:
                    current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)
                    print("Authentication redirect detected. Saved current progress and stopped.")
                    break

                try:
                    active = wait_for_results_scope_with_fallback(
                        context,
                        initial_timeout_ms=max(4000, int(args.extended_wait_seconds * 1000)),
                        max_timeout_ms=MAX_RESULT_WAIT_MS,
                    )
                    ensure_page_size_100(active.scope)
                except SessionExpiredError:
                    current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)
                    print("Authentication redirect detected while returning to the results list. Saved current progress and stopped.")
                    stop_due_to_auth = True
                    break

                if args.save_every > 0 and len(rows) % args.save_every == 0:
                    current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)

            current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)
            resume_item_offset = 0

            if stop_due_to_auth:
                break

            if args.max_pages is not None and current_page_no >= args.max_pages:
                break

            try:
                active = click_next_page(
                    context,
                    active,
                    actual_page_no + 1,
                    timeout_ms=max(4000, int(args.extended_wait_seconds * 1000)),
                )
            except SessionExpiredError:
                current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)
                print("Authentication redirect detected while moving to the next results page. Saved current progress and stopped.")
                break
            except RuntimeError:
                print(f"Next page button not found on page {actual_page_no}. Stopping.")
                print(f"Current scope URL: {get_scope_url(active.scope)}")
                break
            ensure_page_size_100(active.scope)
            current_page_no = get_current_page_number(active.scope, actual_page_no + 1)

        current_output_path = write_rows(args.output_dir, rows, current_output_path, run_label)
        if current_output_path is not None:
            print(f"Saved {len(rows)} rows to {current_output_path}")
        else:
            print("No rows were collected.")
        browser.close()
    print(f"Elapsed time: {format_elapsed(time.perf_counter() - started_at)}")


if __name__ == "__main__":
    main()
