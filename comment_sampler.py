import argparse
import csv
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import easyocr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract usernames and comments from broadcast screenshot images and sample winners."
    )
    parser.add_argument(
        "images",
        nargs="+",
        type=Path,
        help="One or more screenshot image paths."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("comments.csv"),
        help="Where to write the extracted comments as CSV (default: comments.csv)."
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=0,
        help="How many random winners to draw from the extracted comments."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Optional random seed to make the sampling reproducible."
    )
    parser.add_argument(
        "--min-conf",
        type=float,
        default=0.3,
        help="Minimum OCR confidence required to keep a text line (default: 0.3)."
    )
    parser.add_argument(
        "--line-gap",
        type=float,
        default=120.0,
        help="Maximum vertical gap (in pixels) between lines to treat them as the same comment block."
    )
    return parser.parse_args()


@dataclass
class CommentEntry:
    source_image: str
    username: str
    comment: str


_SKIP_PATTERN = re.compile(r"^[0-9Oo〇零\s]+$")


def _is_noise(text: str) -> bool:
    cleaned = text.strip()
    return not cleaned or _SKIP_PATTERN.fullmatch(cleaned)


def _average(coord_list: Iterable[float]) -> float:
    values = list(coord_list)
    return sum(values) / len(values)


def _normalize_username(raw: str) -> str:
    collapsed = raw.strip().replace(" ", "_")
    collapsed = re.sub(r"_+", "_", collapsed)
    return collapsed


def extract_comments(image_path: Path, reader: easyocr.Reader, min_conf: float, line_gap: float) -> List[CommentEntry]:
    detections = reader.readtext(str(image_path), detail=1)
    lines = []
    for bbox, text, conf in detections:
        cleaned = text.strip()
        if conf < min_conf or not cleaned:
            continue
        ys = [pt[1] for pt in bbox]
        xs = [pt[0] for pt in bbox]
        lines.append({
            "text": cleaned,
            "conf": conf,
            "y": min(ys),
            "x": min(xs),
            "y_center": _average(ys),
            "x_center": _average(xs),
        })

    lines.sort(key=lambda item: (item["y"], item["x"]))

    groups: List[List[dict]] = []
    current: List[dict] = []
    last_y = None
    for line in lines:
        if last_y is None or line["y"] - last_y <= line_gap:
            current.append(line)
        else:
            if current:
                groups.append(current)
            current = [line]
        last_y = line["y"]
    if current:
        groups.append(current)

    comment_entries: List[CommentEntry] = []
    for group in groups:
        if not group:
            continue
        username = _normalize_username(group[0]["text"])
        comment_lines = [item["text"] for item in group[1:] if not _is_noise(item["text"]) ]
        comment_text = " ".join(comment_lines).strip()
        if not comment_text:
            continue
        comment_entries.append(CommentEntry(image_path.name, username, comment_text))

    return comment_entries


def write_csv(path: Path, comments: List[CommentEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["source_image", "username", "comment"])
        writer.writeheader()
        for entry in comments:
            writer.writerow({
                "source_image": entry.source_image,
                "username": entry.username,
                "comment": entry.comment,
            })


def main() -> None:
    args = parse_args()

    existing_images = [path for path in args.images if path.exists()]
    missing = [path for path in args.images if not path.exists()]
    if missing:
        for path in missing:
            print(f"[warning] missing image skipped: {path}")
    if not existing_images:
        raise SystemExit("No valid images provided.")

    reader = easyocr.Reader(['ch_tra', 'en'], gpu=False)

    all_comments: List[CommentEntry] = []
    for image in existing_images:
        comments = extract_comments(image, reader, args.min_conf, args.line_gap)
        if not comments:
            print(f"[warning] no comments found in {image}")
        all_comments.extend(comments)

    if not all_comments:
        raise SystemExit("No comments extracted from the provided images.")

    unique_map = {}
    for entry in all_comments:
        unique_map[(entry.username, entry.comment)] = entry
    unique_comments = list(unique_map.values())

    write_csv(args.output, unique_comments)
    print(f"Saved {len(unique_comments)} comments to {args.output}")

    if args.sample:
        sample_size = min(args.sample, len(unique_comments))
        if args.sample > len(unique_comments):
            print(f"[warning] sample size {args.sample} is larger than the number of comments; selecting {sample_size} instead.")
        if args.seed is not None:
            random.seed(args.seed)
        winners = random.sample(unique_comments, sample_size)
        print("Selected winners:")
        for idx, entry in enumerate(winners, 1):
            print(f"{idx}. {entry.username} - {entry.comment}")


if __name__ == "__main__":
    main()
